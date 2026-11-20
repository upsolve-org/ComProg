import { execFile, spawn } from 'node:child_process'
import { randomUUID } from 'node:crypto'
import { promisify } from 'node:util'
import { privateCases } from './judge-cases.mjs'

const docker = promisify(execFile)
const bootstrap = [
  'import base64, io, sys',
  'wire = sys.stdin.buffer',
  'source = base64.b64decode(wire.readline())',
  'size = int(wire.readline())',
  'sys.stdin = io.TextIOWrapper(io.BytesIO(wire.read(size)), encoding="utf-8")',
  'exec(compile(source, "main.py", "exec"), {"__name__": "__main__"})'
].join('\n')
const maxOutput = 4 * 1024 * 1024

async function runContainer(code, input, image) {
  const name = 'comprog-case-' + randomUUID()
  try {
    await docker('docker', [
      'create', '--name', name, '--pull', 'never', '-i', '--network', 'none', '--ipc', 'none',
      '--read-only', '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges=true',
      '--memory', '256m', '--memory-swap', '256m', '--cpus', '1', '--pids-limit', '32',
      '--ulimit', 'nofile=64:64', '--user', '65534:65534', '--log-driver', 'none',
      '--entrypoint', 'python', image, '-I', '-B', '-c', bootstrap
    ], { timeout: 10_000, windowsHide: true })
    return await new Promise(resolve => {
      const child = spawn('docker', ['start', '-ai', name], { windowsHide: true })
      const chunks = []
      let bytes = 0
      let forced
      const stop = status => {
        forced ??= status
        child.kill()
      }
      const timer = setTimeout(() => stop('time_limit'), 3500)
      child.stdout.on('data', chunk => {
        bytes += chunk.length
        if (bytes > maxOutput) stop('output_limit')
        else chunks.push(chunk)
      })
      child.stderr.on('data', chunk => {
        bytes += chunk.length
        if (bytes > maxOutput) stop('output_limit')
      })
      child.stdin.on('error', () => {})
      child.on('error', () => { forced = 'unavailable' })
      child.on('close', async exit => {
        clearTimeout(timer)
        if (forced) return resolve({ status: forced })
        try {
          const { stdout } = await docker('docker', ['inspect', '--format', '{{.State.Status}} {{.State.ExitCode}} {{.State.OOMKilled}}', name], { timeout: 4000, windowsHide: true })
          const [state, exitCode, oom] = stdout.trim().split(' ')
          if (state !== 'exited') return resolve({ status: 'unavailable' })
          if (oom === 'true') return resolve({ status: 'memory_limit' })
          return resolve(exit === 0 && exitCode === '0'
            ? { status: 'ok', output: Buffer.concat(chunks).toString('utf8') }
            : { status: 'runtime_error' })
        } catch {
          return resolve({ status: 'unavailable' })
        }
      })
      const data = input + '\n'
      child.stdin.end(Buffer.from(code).toString('base64') + '\n' + Buffer.byteLength(data) + '\n' + data)
    })
  } catch {
    return { status: 'unavailable' }
  } finally {
    await docker('docker', ['rm', '-f', name], { timeout: 7000, windowsHide: true }).catch(() => {})
  }
}

const normalize = output => output.trim().split(/\r?\n/).map(line => line.trim().replace(/[ \t]+/g, ' ')).join('\n')

export async function judgeSubmission(index, lab, code, {
  image = process.env.JUDGE_IMAGE,
  run = runContainer
} = {}) {
  if (!image) return { status: 'unavailable' }
  for (const { input, expected, stress } of privateCases(index, lab)) {
    const result = await run(code, input, image)
    if (result.status === 'unavailable') return { status: 'unavailable' }
    if (result.status !== 'ok') return { status: result.status, stage: stress ? 'stress' : 'correctness' }
    if (normalize(result.output) !== normalize(expected)) {
      return { status: 'wrong_answer', stage: stress ? 'stress' : 'correctness' }
    }
  }
  return { status: 'accepted' }
}
