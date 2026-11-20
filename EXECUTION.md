# Execution plan: deploying ComProg as the club site

Companion to PLAN.md. Both are in review: the content plan reached APPROVED, this
file is on REVISE. `PLAN.md`'s status line reads approved and is authoritative for
design only — no code until this file is approved.

## Host facts (probed, read-only)

- `Pandev` 66.181.46.15, Ubuntu 22.04.5, 4 vCPU, 15.6 GB RAM, 47 GB free, root SSH.
- Docker 29.8.1, **rootful**, overlayfs, cgroup v2 via systemd, AppArmor + seccomp
  `builtin` active. No Podman, no pypy. `python3`, `git`, `caddy` present.
- **Host is already in production:** `learn.upsolve.study` is a Next.js app behind
  the host Caddy on :80/:443, with TLS, HSTS and a Supabase stack on the box.
  Containers bound to 127.0.0.1: 8000 (envoy), 5432, 6543 (pooler).
- Caddy runs as a service owning :80/:443, so the site is added by a vhost file
  beside `/etc/caddy/Caddyfile`, not by our own proxy.
- `/srv/learn` is another project's directory. Ours is `/srv/comprog`, owned by a
  dedicated `comprog` system user, never root, never `/srv/learn`.

### Probe evidence (read-only, run 2026-11-20)

| Check | Result |
|---|---|
| `ss -tln \| grep -c ':8790 '` | `0` — free |
| `stat /var/run/docker.sock` | `660 root:docker`; group `docker` gid 999, no members |
| `grep import /etc/caddy/Caddyfile` | none; no `*.d` snippet dir, so vhosts are appended files |
| `docker ps -q \| wc -l` | 11 |
| load average | 0.28 / 0.33 / 0.36 |

## Deviance from PLAN.md, decided by the latest answers

1. **Rootful Docker, not rootless.** PLAN.md assumed rootless/Podman. We keep
   rootful and the isolation rests on: non-root `comprog` user in the compose
   group, no socket mount in job containers, caps dropped, `no-new-privileges`,
   seccomp/AppArmor defaults kept, cgroup limits per job.
2. **Shared token for the pilot, not invites — explicitly approved deviance from
   G1.** PLACEHOLDER token in a `0600` env file, rotated by hand before the pilot
   and after it. Because there is no member id: global rate limit only (2/min/IP,
   30/min total), and progress lives in `localStorage` until invites land. HTTPS is
   mandatory, not negotiated — see the TLS rule below. The pilot stays private
   (token-gated) until G3 passes. Invites stay the first post-pilot item.
3. **PyPy image is yours to name.** PLACEHOLDER below; PR 2 does not build the
   worker until the tag + digest are filled in.
4. **G1 moves to PR 2** (probed to be carried by infra), **G2 is signed off before
   PR 1** implements the suite. PLAN.md §3 gates stay as written; only their PR
   assignment moves here.

## Socket trust model

The host Docker socket is host-root. Only `launcher` (§launcher interface) reaches
it, via the `docker` group (gid 999, currently memberless — we add `launcher` only,
not the API). Job containers get **no socket**. Verified in PR 3: API container has no socket,
a job cannot see one, the launcher alone can kill per-case cgroups, and
credentials and expected outputs are outside the sandbox.

## Resource budget corrections

The worker's `--memory 1g` governs the worker only; separately launched job
containers sit outside it. So: jobs are children of the worker's cgroup, the
worker's cgroup holds the aggregate, and the global semaphore is enforced in the
worker, not the API. Headroom is measured with two concurrent jobs on the box.

## TLS and exposure

Let's Encrypt serves IP certificates over HTTP-01 (no domain needed), but only under
its `shortlived` profile: 160-hour certs, TLS-ALPN-01 must be disabled, and Caddy
needs `default_sni` set to the literal IP because a client sends no SNI to an IP.
Host has Caddy v2.11.9, and IP certs need ≥ 2.10.1.

IP vhost (appended file, `comprog.caddyfile`):

```
66.181.46.15 {
	respond /healthz 200
	reverse_proxy 127.0.0.1:8790
	tls {
		issuer acme {
			profile shortlived
			disable_tlsalpn_challenge
		}
	}
}
```

Required prerequisites (verified needed, not yet in place):

- the config has **no global options block**, so `import` and `default_sni` cannot
  be added yet without creating one. PR 2 adds `{ default_sni 66.181.46.15 }` plus
  `import /etc/caddy/comprog/*.caddyfile` on top of the `learn.upsolve.study` block
  and validates the whole file before reload;
- TLS-ALPN-01 must be disabled and the profile set `shortlived`, both issuer-level.

Staged exposure, no circular gate:

1. load a health-only vhost (`respond 200` only, no proxy), reload;
2. `curl --resolve`-free probe to `https://66.181.46.15/healthz` until
   `ssl_verify_result=0`;
3. only then add the `reverse_proxy 127.0.0.1:8790` handle and reload;
4. until step 2 passes, the app is reached over `http://` and only with the token
   kept off that path for test members (owner-only traffic).

Interim owner path: an SSH tunnel,
`ssh -N -L 127.0.0.1:8790:127.0.0.1:8790 Pandev`, so the owner hits
`http://127.0.0.1:8790` on their own machine. The client bind address is explicit
because `GatewayPorts yes` on the client otherwise widens the laptop-side listener
to the whole LAN. Nothing is published on :80 for the app, the token never crosses
plain WAN HTTP, and loopback binding already matches how every other service on the
box is reached. The tunnel is torn down at step 3.

Renewal alert: threshold is measured, not assumed. PR 3 records the served
certificate's `notAfter` and the observed renewal moment, sets the alert from that
gap, and the check reads the live cert expiry rather than a fixed day count — the
2/3 renewal ratio leaves ~53 h, and ACME Renewal Information can move it.

## Launcher interface

The API never holds the socket. `launcher` is a separate process, the only
container in the socket group, reached over a Unix socket on a shared named volume.

Request constrained to fixed job settings: image is pinned by digest, flag set,
caps, tmp quota and per-case cgroup name all come from server config; a submission
supplies bytes only.

The launcher itself has no network and is the only process that can create, kill
or sweep job cgroups. Verified in PR 3: API container has no `/var/run/docker.sock`,
a job cannot see one, and a malformed submission still produces the configured
limits.

## Budget on a shared box

- Global: 2 concurrent jobs, 16 queued, hard-refuse beyond that.
- Per job: 2 s wall, 256 MB, 128 pids, 64 KB output, 64 MB tmp, no swap.
- Worker container: `--cpus 2 --memory 1g`, capped so a job storm cannot starve
  `learn.upsolve.study`.
- Host ports used: `8790` (API), loopback only. `8791`, `8792` already taken.

## PR batching

Four stacked PRs off `main`, each merges before the next.

**PR 1 — harness.** `run_tests.py` gains `--json` and a failing exit code;
`TEST_CASES` untouched. YAML fixtures with public/private split, Kadane suite per
PLAN.md §3 with brute-force oracle and constant million generator, `10⁶` case
generated at check time not committed. Fix `ternary_search.py` to a real unimodal
demo. Fix `practice_examples.py:26` (`n=8` → `9`). Kadane statement page as a
lesson note. No server contact.

**PR 2 — infra.** API service (`POST /runs`, `POST /submissions`) with no socket,
`launcher` (§launcher interface) holding it, compose file, Dockerfile with
`PYTHONHASHSEED=0`, `MPLBACKEND=Agg`, PyPy digest pinned, rate limit, compose
project name `comprog` (teardown by exact project, never a prefix), `comprog` user
and `/srv/comprog`, token env file at `0600`. Caddy vhost added beside the existing
one; with no domain it serves `https://66.181.46.15` and the vhost is dropped once
a domain exists.

**PR 3 — G3 probe.** Scripts in `deploy/probe/` plus a recorded `RESULTS.md`:
known-good accepted, `setsid` grandchild on normal exit → cgroup empty, reaped,
tmp clean, infinite loop SIGKILLed inside the deadline, known-bad rejected, next
job normal after each kill, tenant without the socket can start a job. Both
reference solutions and the DSU smoke problem measured against the caps. Gate
stays closed until every line passes on the box.

**PR 4 — pages `01` and `02`.** Astro + Starlight, conversion script, wiki-link,
callout, math and anchor handling, ready gate. Deploy is `learn`'s pattern:
build locally, rsync artifacts to `/srv/comprog/web`, no toolchain on the box.

## Rollback

The stack is dependent: PR 3 needs PR 2 deployed, PR 4 needs PR 3 passing. Rollback
is therefore **reverse order**, not independent revert. The Caddy vhost is a
separate appended file, so `learn.upsolve.study` only needs:

- `caddy validate` of the whole config before any reload, then a Learn smoke test
  after it;
- teardown by exact compose project (`docker compose -p comprog down`), never
  `docker system prune` or a name prefix;
- two-concurrent-job headroom measured before exposure (cgroup-enforced, §budget).

## Open placeholders

- PyPy image tag + digest (yours; does not block PR 1).
- Domain (cosmetic: TLS works on the IP, and a domain only avoids a pinned IP).