import { createServer } from 'node:http'
import { createReadStream } from 'node:fs'
import { readFile, readdir, stat } from 'node:fs/promises'
import { labs } from './labs.mjs'
import { cppLabs } from './labs-cpp.mjs'
import { tutorReply } from './tutor.mjs'
import { judgeSubmission, judgeCppSubmission, runCpp } from './judge.mjs'
import { scrapeCodeforcesProblems, packProblems } from './codeforces.mjs'

const dist = new URL('../dist/', import.meta.url)
const types = {
  html: 'text/html; charset=utf-8', css: 'text/css; charset=utf-8',
  js: 'text/javascript; charset=utf-8', json: 'application/json; charset=utf-8',
  woff: 'font/woff', woff2: 'font/woff2', ttf: 'font/ttf', png: 'image/png', vtt: 'text/vtt', mp4: 'video/mp4'
}
const assets = new Map((await readdir(dist, { withFileTypes: true }))
  .filter(file => file.isFile() && types[file.name.split('.').pop()])
  .map(file => ['/' + file.name, file.name]))
const curriculum = JSON.parse(await readFile(new URL('course.json', dist), 'utf8'))
const cppCurriculum = JSON.parse(await readFile(new URL('course-cpp.json', dist), 'utf8'))
const exercises = new Map(labs.map((lab, index) => [curriculum[index].id, lab]))
const cppExercises = new Map(cppLabs.map((lab, index) => [cppCurriculum[index].id, lab]))
const judgeIndices = new Map(labs.map((_, index) => [curriculum[index].id, index]))
const limits = new Map()
let budget = { until: 0, count: 0 }
let inFlight = 0
let judgeInFlight = 0
let judgeBudget = { until: 0, count: 0 }
let runBudget = { until: 0, count: 0 }
let cfCache = null
let cfLastRefresh = 0
let cfRefreshPromise = null
const cdn = 'https://cdn.jsdelivr.net'

try {
  cfCache = await readFile(new URL('codeforces-problems.json', dist))
  cfLastRefresh = Date.now()
} catch { /* Will scrape on first request if missing */ }

async function refreshCodeforcesCache() {
  if (cfRefreshPromise) return cfRefreshPromise
  cfRefreshPromise = (async () => {
    try {
      const problems = await scrapeCodeforcesProblems({
        apiKey: process.env.CF_API_KEY,
        apiSecret: process.env.CF_API_SECRET
      })
      const packed = packProblems(problems)
      cfCache = Buffer.from(JSON.stringify(packed), 'utf8')
      cfLastRefresh = Date.now()
      return packed
    } finally {
      cfRefreshPromise = null
    }
  })()
  return cfRefreshPromise
}

function allowance(ip) {
  const now = Date.now()
  if (now >= budget.until) {
    budget = { until: now + 60_000, count: 0 }
    limits.clear()
  }
  const count = limits.get(ip) ?? 0
  if (count >= 12 || budget.count >= 40 || inFlight >= 4) return false
  limits.set(ip, count + 1)
  budget.count++
  return true
}

function json(res, status, data) {
  res.writeHead(status, { 'content-type': types.json, 'cache-control': 'no-store' })
  res.end(JSON.stringify(data))
}

async function readJSON(req, limit) {
  const chunks = []
  let bytes = 0
  for await (const chunk of req) {
    bytes += chunk.length
    if (bytes > limit) return null
    chunks.push(chunk)
  }
  return JSON.parse(Buffer.concat(chunks).toString('utf8'))
}

function refused(req) {
  if (req.headers['sec-fetch-site'] && req.headers['sec-fetch-site'] !== 'same-origin') return 'origin'
  if (!req.headers['content-type']?.startsWith('application/json')) return 'type'
  return ''
}

// Sample input comes from the course definition, not the browser.
function sampleInput(lab, sample) {
  const cases = lab.cases ?? []
  if (Number.isInteger(sample) && sample >= 0 && sample < cases.length) return cases[sample][0]
  return cases[0]?.[0] ?? ''
}

createServer(async (req, res) => {
  res.setHeader('x-content-type-options', 'nosniff')
  res.setHeader('referrer-policy', 'no-referrer')
  const path = req.url.split('?')[0]
  if (path === '/api/codeforces' && ['GET', 'HEAD'].includes(req.method)) {
    if (!cfCache || Date.now() - cfLastRefresh > 6 * 3600_000) {
      await refreshCodeforcesCache().catch(() => {})
    }
    if (!cfCache) return json(res, 503, { error: 'Codeforces problemset unavailable.' })
    res.writeHead(200, { 'content-type': types.json, 'cache-control': 'public, max-age=300' })
    return res.end(req.method === 'HEAD' ? undefined : cfCache)
  }
  if (path === '/api/codeforces/refresh' && req.method === 'POST') {
    const why = refused(req)
    if (why === 'origin') return json(res, 403, { error: 'Refresh from the course.' })
    if (Date.now() - cfLastRefresh < 30_000 && cfCache) {
      res.writeHead(200, { 'content-type': types.json, 'cache-control': 'no-store' })
      return res.end(cfCache)
    }
    try {
      await refreshCodeforcesCache()
      res.writeHead(200, { 'content-type': types.json, 'cache-control': 'no-store' })
      return res.end(cfCache)
    } catch {
      return json(res, 503, { error: 'Could not refresh from Codeforces right now.' })
    }
  }
  if (path === '/api/submit' && req.method === 'POST') {
    const why = refused(req)
    if (why === 'origin') return json(res, 403, { error: 'Submit from the course.' })
    if (why === 'type') return json(res, 415, { error: 'Send a JSON request.' })
    let body
    try { body = await readJSON(req, 200_000) } catch { return json(res, 400, { error: 'Invalid submission.' }) }
    const language = body?.course === 'cpp' ? 'cpp' : 'python'
    const index = judgeIndices.get(body?.lesson)
    const known = language === 'cpp' ? cppExercises.has(body?.lesson) : index !== undefined
    if (!known || typeof body.code !== 'string' || !body.code.trim() || body.code.length > 30_000) {
      return json(res, 400, { error: 'Enter ' + (language === 'cpp' ? 'C++' : 'Python') + ' code of up to 30,000 characters.' })
    }
    if (language === 'cpp' ? !process.env.CPP_JUDGE_IMAGE : !process.env.JUDGE_IMAGE) {
      return json(res, 503, { status: 'unavailable' })
    }
    const now = Date.now()
    if (now >= judgeBudget.until) judgeBudget = { until: now + 60_000, count: 0 }
    if (judgeInFlight >= 2 || judgeBudget.count >= 12) {
      return json(res, 429, { error: 'The judge is busy. Try again shortly.' })
    }
    judgeInFlight++
    judgeBudget.count++
    try {
      const result = language === 'cpp'
        ? await judgeCppSubmission(index, cppLabs[index], body.code)
        : await judgeSubmission(index, labs[index], body.code)
      return json(res, result.status === 'unavailable' ? 503 : 200, result)
    } catch {
      return json(res, 503, { status: 'unavailable' })
    } finally {
      judgeInFlight--
    }
  }
  if (path === '/api/run-cpp' && req.method === 'POST') {
    const why = refused(req)
    if (why === 'origin') return json(res, 403, { error: 'Run from the course.' })
    if (why === 'type') return json(res, 415, { error: 'Send a JSON request.' })
    let body
    try { body = await readJSON(req, 60_000) } catch { return json(res, 400, { error: 'Invalid program.' }) }
    const lab = cppExercises.get(body?.lesson)
    if (!lab || typeof body.code !== 'string' || !body.code.trim() || body.code.length > 30_000) {
      return json(res, 400, { error: 'Enter C++ code of up to 30,000 characters.' })
    }
    if (!process.env.CPP_JUDGE_IMAGE) return json(res, 503, { status: 'unavailable' })
    const now = Date.now()
    if (now >= runBudget.until) runBudget = { until: now + 60_000, count: 0 }
    if (runBudget.count >= 8) {
      return json(res, 429, { error: 'Too many runs. Try again in a minute.' })
    }
    runBudget.count++
    try {
      const result = await runCpp(body.code, sampleInput(lab, body.sample))
      return json(res, result.status === 'unavailable' ? 503 : 200, result)
    } catch {
      return json(res, 503, { status: 'unavailable' })
    }
  }
  if (path === '/api/tutor' && req.method === 'POST') {
    if (req.headers['sec-fetch-site'] && req.headers['sec-fetch-site'] !== 'same-origin') {
      return json(res, 403, { error: 'Open the tutor from the course.' })
    }
    if (!req.headers['content-type']?.startsWith('application/json')) {
      return json(res, 415, { error: 'Send a JSON request.' })
    }
    let body = ''
    let bytes = 0
    try {
      for await (const chunk of req) {
        bytes += chunk.length
        if (bytes > 12_000) return json(res, 413, { error: 'Shorten your question and try again.' })
        body += chunk
      }
      const { lesson, question, previous, course } = JSON.parse(body)
      const lab = (course === 'cpp' ? cppExercises : exercises).get(lesson)
      if (!lab || typeof question !== 'string' || !question.trim() || question.length > 1600 ||
          !Array.isArray(previous) || previous.length > 3 || previous.some(hint => !lab.hints.includes(hint))) {
        return json(res, 400, { error: 'Enter a question of up to 1,600 characters.' })
      }
      if (!allowance(req.socket.remoteAddress)) {
        return json(res, 429, { error: 'The tutor is busy. Try again in a minute.' })
      }
      inFlight++
      try {
        return json(res, 200, await tutorReply(lab, question, previous))
      } finally {
        inFlight--
      }
    } catch {
      return json(res, 400, { error: 'The tutor could not read this request.' })
    }
  }
  const file = assets.get(path === '/' ? '/index.html' : path)
  if (!file || !['GET', 'HEAD'].includes(req.method)) return json(res, 404, { error: 'Page not found.' })
  const runner = file === 'runner.html'
  res.setHeader('content-security-policy', runner
    ? "sandbox allow-scripts; default-src 'none'; script-src 'self' blob: " + cdn + " 'wasm-unsafe-eval'; worker-src blob:; connect-src " + cdn + "; base-uri 'none'; form-action 'none'"
    : "default-src 'self'; style-src 'self' 'unsafe-inline'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'")
  try {
    if (file.endsWith('.mp4')) {
      const url = new URL(file, dist)
      const { size } = await stat(url)
      const range = /^bytes=(\d+)-(\d*)$/.exec(req.headers.range || '')
      const start = range ? Number(range[1]) : 0
      const end = range?.[2] ? Math.min(Number(range[2]), size - 1) : size - 1
      if (start > end) {
        res.writeHead(416, { 'content-range': 'bytes */' + size })
        return res.end()
      }
      if (range) res.setHeader('content-range', 'bytes ' + start + '-' + end + '/' + size)
      res.writeHead(range ? 206 : 200, { 'content-type': 'video/mp4', 'accept-ranges': 'bytes', 'content-length': end - start + 1 })
      if (req.method === 'HEAD') return res.end()
      const stream = createReadStream(url, { start, end })
      res.on('close', () => stream.destroy())
      stream.on('error', () => res.destroy())
      return stream.pipe(res)
    }
    const data = await readFile(new URL(file, dist))
    res.writeHead(200, { 'content-type': types[file.split('.').pop()], 'cache-control': 'no-cache' })
    res.end(req.method === 'HEAD' ? undefined : data)
  } catch {
    json(res, 500, { error: 'Course asset unavailable.' })
  }
}).listen(Number(process.env.PORT || 3000), process.env.HOST || '127.0.0.1', function () {
  console.log('ComProg listening on http://' + this.address().address + ':' + this.address().port)
})
