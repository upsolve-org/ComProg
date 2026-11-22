const CF_API_BASE = 'https://codeforces.com/api/problemset.problems'
const CF_HTML_BASE = 'https://codeforces.com/problemset'

function sha512Hex(input) {
  if (typeof process !== 'undefined' && typeof process.getBuiltinModule === 'function') {
    const crypto = process.getBuiltinModule('node:crypto')
    if (crypto?.createHash) return crypto.createHash('sha512').update(input).digest('hex')
  }
  return ''
}

export function buildSignedUrl(method, params = {}, apiKey = '', apiSecret = '') {
  const query = new URLSearchParams(params)
  if (apiKey && apiSecret) {
    const rand = '123456'
    query.set('apiKey', apiKey)
    query.set('time', String(Math.floor(Date.now() / 1000)))
    const sorted = Array.from(query.entries())
      .sort(([a, va], [b, vb]) => (a === b ? va.localeCompare(vb) : a.localeCompare(b)))
      .map(([k, v]) => `${k}=${v}`)
      .join('&')
    const sigBase = `${rand}/${method}?${sorted}#${apiSecret}`
    const hash = sha512Hex(sigBase)
    return `https://codeforces.com/api/${method}?${sorted}&apiSig=${rand}${hash}`
  }
  const qs = query.toString()
  return `https://codeforces.com/api/${method}${qs ? '?' + qs : ''}`
}

// Fallback HTML scraper for Codeforces problemset pages if the JSON API is unreachable.
export function parseProblemsetHTML(html) {
  const problems = []
  const rowRegex = /<tr[^>]*>([\s\S]*?)<\/tr>/gi
  let match
  while ((match = rowRegex.exec(html)) !== null) {
    const row = match[1]
    const idMatch = /href="\/problemset\/problem\/(\d+)\/([A-Za-z0-9]+)"[^>]*>\s*([0-9A-Za-z]+)\s*<\/a>/i.exec(row)
    if (!idMatch) continue
    const contestId = Number(idMatch[1])
    const index = idMatch[2].trim()
    const titleRe = new RegExp(`href="/problemset/problem/${contestId}/${index}"[^>]*>\\s*([^<]+)<\\/a>`, 'gi')
    let name = index
    let tMatch
    while ((tMatch = titleRe.exec(row)) !== null) {
      const candidate = tMatch[1].trim()
      if (candidate !== `${contestId}${index}`) name = candidate
    }
    const tags = []
    const tagRe = /class="notice"[^>]*>\s*([^<]+)<\/a>/gi
    let tagMatch
    while ((tagMatch = tagRe.exec(row)) !== null) {
      tags.push(tagMatch[1].trim())
    }
    const ratingMatch = /class="ProblemRating"[^>]*>\s*(\d+)\s*<\/span>/i.exec(row)
    const solvedMatch = /title="Participants solved the problem"[^>]*>\s*(?:<img[^>]*>)?\s*x(\d+)/i.exec(row)
    problems.push({
      id: `${contestId}${index}`,
      contestId,
      index,
      name,
      rating: ratingMatch ? Number(ratingMatch[1]) : null,
      tags,
      solvedCount: solvedMatch ? Number(solvedMatch[1]) : 0
    })
  }
  return problems
}

export async function scrapeCodeforcesProblems({
  apiKey = process.env.CF_API_KEY ?? '',
  apiSecret = process.env.CF_API_SECRET ?? '',
  fetchImpl = fetch
} = {}) {
  const url = buildSignedUrl('problemset.problems', {}, apiKey, apiSecret)
  const response = await fetchImpl(url, {
    headers: {
      'user-agent': 'ComProg-Training-Scraper/1.0 (+https://comprog.upsolve.study)',
      accept: 'application/json'
    }
  })
  if (!response.ok) {
    throw new Error(`Codeforces HTTP ${response.status}`)
  }
  const payload = await response.json()
  if (payload?.status !== 'OK' || !payload?.result?.problems) {
    throw new Error(payload?.comment || 'Invalid Codeforces API response')
  }

  const solvedMap = new Map()
  for (const stat of payload.result.problemStatistics ?? []) {
    solvedMap.set(`${stat.contestId}:${stat.index}`, Number(stat.solvedCount) || 0)
  }

  const seen = new Set()
  const problems = []
  for (const raw of payload.result.problems) {
    if (!raw.contestId || !raw.index || !raw.name) continue
    const key = `${raw.contestId}:${raw.index}`
    if (seen.has(key)) continue
    seen.add(key)
    problems.push({
      id: `${raw.contestId}${raw.index}`,
      contestId: Number(raw.contestId),
      index: String(raw.index),
      name: String(raw.name).trim(),
      rating: Number.isFinite(raw.rating) ? Number(raw.rating) : null,
      tags: Array.isArray(raw.tags) ? raw.tags.map(t => String(t).trim()).filter(Boolean) : [],
      solvedCount: solvedMap.get(key) ?? 0
    })
  }
  return problems
}

// Compact wire representation so 11,500+ problems transfer fast and decode in <5ms.
export function packProblems(problems) {
  const tagCounts = new Map()
  for (const p of problems) {
    for (const tag of p.tags ?? []) {
      tagCounts.set(tag, (tagCounts.get(tag) ?? 0) + 1)
    }
  }
  const tags = Array.from(tagCounts.entries())
    .sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))
    .map(([tag]) => tag)
  const tagIndex = new Map(tags.map((t, i) => [t, i]))

  const items = problems.map(p => [
    p.contestId,
    p.index,
    p.name,
    p.rating ?? 0,
    (p.tags ?? []).map(t => tagIndex.get(t)).filter(i => i !== undefined),
    p.solvedCount ?? 0
  ])
  return {
    updatedAt: new Date().toISOString(),
    total: items.length,
    tags,
    tagCounts: Object.fromEntries(tags.map(t => [t, tagCounts.get(t)])),
    items
  }
}

export function unpackProblems(packed) {
  if (!packed || !Array.isArray(packed.items)) return { tags: [], tagCounts: {}, problems: [] }
  const tags = packed.tags ?? []
  const problems = packed.items.map(([contestId, index, name, rating, tagIds, solvedCount]) => ({
    id: `${contestId}${index}`,
    contestId,
    index,
    name,
    rating: rating > 0 ? rating : null,
    tags: (tagIds ?? []).map(i => tags[i]).filter(Boolean),
    solvedCount: solvedCount ?? 0,
    url: `https://codeforces.com/problemset/problem/${contestId}/${index}`
  }))
  return {
    updatedAt: packed.updatedAt ?? null,
    tags,
    tagCounts: packed.tagCounts ?? {},
    problems
  }
}

export function ratingTier(rating) {
  if (!rating) return { label: 'Unrated', className: 'cf-unrated' }
  if (rating < 1200) return { label: 'Newbie', className: 'cf-newbie' }
  if (rating < 1400) return { label: 'Pupil', className: 'cf-pupil' }
  if (rating < 1600) return { label: 'Specialist', className: 'cf-specialist' }
  if (rating < 1900) return { label: 'Expert', className: 'cf-expert' }
  if (rating < 2100) return { label: 'Candidate Master', className: 'cf-cm' }
  if (rating < 2400) return { label: 'Master', className: 'cf-master' }
  return { label: 'Grandmaster', className: 'cf-gm' }
}

export function filterAndSortProblems(problems, {
  tags = [],
  tagMode = 'all',
  minRating = 0,
  maxRating = 9999,
  includeUnrated = false,
  search = '',
  sort = 'rating-asc',
  onlySolved = 'all',
  solvedIds = new Set()
} = {}) {
  const activeTags = Array.isArray(tags) ? tags.filter(Boolean) : (tags ? [tags] : [])
  const query = String(search ?? '').trim().toLowerCase()
  const minR = Number(minRating) || 0
  const maxR = Number(maxRating) || 9999

  const filtered = problems.filter(p => {
    if (p.rating === null) {
      if (!includeUnrated) return false
    } else if (p.rating < minR || p.rating > maxR) {
      return false
    }
    if (activeTags.length) {
      const pTags = p.tags ?? []
      const matches = tagMode === 'any'
        ? activeTags.some(t => pTags.includes(t))
        : activeTags.every(t => pTags.includes(t))
      if (!matches) return false
    }
    if (onlySolved === 'solved' && !solvedIds.has(p.id)) return false
    if (onlySolved === 'unsolved' && solvedIds.has(p.id)) return false
    if (query) {
      const idText = p.id.toLowerCase()
      const nameText = p.name.toLowerCase()
      if (!idText.includes(query) && !nameText.includes(query)) return false
    }
    return true
  })

  filtered.sort((a, b) => {
    if (sort === 'rating-asc') {
      const ra = a.rating ?? 99999
      const rb = b.rating ?? 99999
      if (ra !== rb) return ra - rb
      return b.solvedCount - a.solvedCount || b.contestId - a.contestId
    }
    if (sort === 'rating-desc') {
      const ra = a.rating ?? -1
      const rb = b.rating ?? -1
      if (ra !== rb) return rb - ra
      return b.solvedCount - a.solvedCount || b.contestId - a.contestId
    }
    if (sort === 'solved-desc') {
      if (b.solvedCount !== a.solvedCount) return b.solvedCount - a.solvedCount
      return (a.rating ?? 99999) - (b.rating ?? 99999)
    }
    if (sort === 'solved-asc') {
      if (a.solvedCount !== b.solvedCount) return a.solvedCount - b.solvedCount
      return (a.rating ?? 99999) - (b.rating ?? 99999)
    }
    if (sort === 'contest-asc') {
      return a.contestId - b.contestId || a.index.localeCompare(b.index)
    }
    // contest-desc (newest first)
    return b.contestId - a.contestId || a.index.localeCompare(b.index)
  })

  return filtered
}

export function validateHandle(raw) {
  const clean = String(raw ?? '').trim()
  if (!/^[A-Za-z0-9_.-]{3,24}$/.test(clean)) return ''
  return clean
}

export async function fetchCodeforcesAccount(handle, {
  apiKey = process.env.CF_API_KEY ?? '',
  apiSecret = process.env.CF_API_SECRET ?? '',
  fetchImpl = fetch
} = {}) {
  const cleanHandle = validateHandle(handle)
  if (!cleanHandle) {
    throw new Error('Enter a valid Codeforces handle (3–24 letters, digits, _, ., -).')
  }
  const infoUrl = buildSignedUrl('user.info', { handles: cleanHandle }, apiKey, apiSecret)
  const statusUrl = buildSignedUrl('user.status', { handle: cleanHandle }, apiKey, apiSecret)
  const headers = {
    'user-agent': 'ComProg-Training-Scraper/1.0 (+https://comprog.upsolve.study)',
    accept: 'application/json'
  }
  const [infoRes, statusRes] = await Promise.all([
    fetchImpl(infoUrl, { headers }),
    fetchImpl(statusUrl, { headers })
  ])

  const infoPayload = await infoRes.json().catch(() => null)
  if (!infoRes.ok || infoPayload?.status !== 'OK' || !infoPayload?.result?.[0]) {
    throw new Error(infoPayload?.comment || `Codeforces user "${cleanHandle}" was not found.`)
  }
  const statusPayload = await statusRes.json().catch(() => null)
  if (!statusRes.ok || statusPayload?.status !== 'OK' || !Array.isArray(statusPayload?.result)) {
    throw new Error(statusPayload?.comment || `Could not load submissions for "${cleanHandle}".`)
  }

  const user = infoPayload.result[0]
  const solvedKeys = new Set()
  const solvedIds = new Set()
  for (const sub of statusPayload.result) {
    if (sub?.verdict !== 'OK' || !sub?.problem) continue
    const p = sub.problem
    if (p.contestId && p.index) {
      const id = `${p.contestId}${p.index}`
      solvedIds.add(id)
      solvedKeys.add(id)
    } else if (p.name) {
      solvedKeys.add(`name:${p.name}`)
    }
  }

  return {
    handle: String(user.handle || cleanHandle),
    rating: Number.isFinite(user.rating) ? Number(user.rating) : null,
    maxRating: Number.isFinite(user.maxRating) ? Number(user.maxRating) : null,
    rank: user.rank ? String(user.rank) : 'unrated',
    maxRank: user.maxRank ? String(user.maxRank) : 'unrated',
    avatar: user.titlePhoto || user.avatar || '',
    solvedCount: solvedKeys.size,
    solvedIds: Array.from(solvedIds),
    updatedAt: new Date().toISOString()
  }
}

export function sortLeaderboard(entries) {
  const list = Array.isArray(entries) ? [...entries] : []
  list.sort((a, b) => {
    const sa = Number(a.solvedCount) || 0
    const sb = Number(b.solvedCount) || 0
    if (sb !== sa) return sb - sa
    const ra = Number.isFinite(a.rating) ? a.rating : -1
    const rb = Number.isFinite(b.rating) ? b.rating : -1
    if (rb !== ra) return rb - ra
    const ma = Number.isFinite(a.maxRating) ? a.maxRating : -1
    const mb = Number.isFinite(b.maxRating) ? b.maxRating : -1
    if (mb !== ma) return mb - ma
    return String(a.handle ?? '').localeCompare(String(b.handle ?? ''))
  })
  return list.map((item, idx) => ({
    position: idx + 1,
    handle: item.handle,
    rating: item.rating ?? null,
    maxRating: item.maxRating ?? null,
    rank: item.rank ?? 'unrated',
    maxRank: item.maxRank ?? 'unrated',
    avatar: item.avatar ?? '',
    solvedCount: Number(item.solvedCount) || 0,
    updatedAt: item.updatedAt ?? null
  }))
}

export function upsertLeaderboardEntry(entries, profile) {
  const map = new Map()
  for (const item of Array.isArray(entries) ? entries : []) {
    if (item?.handle) map.set(String(item.handle).toLowerCase(), item)
  }
  const key = String(profile.handle).toLowerCase()
  const existing = map.get(key)
  map.set(key, {
    handle: profile.handle,
    rating: profile.rating ?? null,
    maxRating: profile.maxRating ?? null,
    rank: profile.rank ?? 'unrated',
    maxRank: profile.maxRank ?? 'unrated',
    avatar: profile.avatar ?? '',
    solvedCount: Number(profile.solvedCount) || 0,
    firstLinkedAt: existing?.firstLinkedAt ?? profile.updatedAt ?? new Date().toISOString(),
    updatedAt: profile.updatedAt ?? new Date().toISOString()
  })
  return sortLeaderboard(Array.from(map.values()))
}
