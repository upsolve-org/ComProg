import assert from 'node:assert/strict'
import test from 'node:test'
import {
  buildSignedUrl,
  filterAndSortProblems,
  packProblems,
  parseProblemsetHTML,
  ratingTier,
  scrapeCodeforcesProblems,
  unpackProblems
} from './codeforces.mjs'

const sampleProblems = [
  { id: '4A', contestId: 4, index: 'A', name: 'Watermelon', rating: 800, tags: ['brute force', 'math'], solvedCount: 550000 },
  { id: '71A', contestId: 71, index: 'A', name: 'Way Too Long Words', rating: 800, tags: ['strings'], solvedCount: 490000 },
  { id: '455A', contestId: 455, index: 'A', name: 'Boredom', rating: 1500, tags: ['dp'], solvedCount: 95000 },
  { id: '20C', contestId: 20, index: 'C', name: 'Dijkstra?', rating: 1900, tags: ['graphs', 'shortest paths'], solvedCount: 72000 },
  { id: '1999G2', contestId: 1999, index: 'G2', name: 'Ruler (hard version)', rating: 1700, tags: ['binary search', 'interactive', 'math'], solvedCount: 18000 },
  { id: '2100F', contestId: 2100, index: 'F', name: 'Unrated Mystery', rating: null, tags: ['dp', 'graphs'], solvedCount: 300 }
]

test('packProblems and unpackProblems preserve tags, ratings, and URLs', () => {
  const packed = packProblems(sampleProblems)
  assert.equal(packed.total, 6)
  assert.ok(packed.tags.includes('math'))
  assert.equal(packed.tagCounts.math, 2)

  const unpacked = unpackProblems(packed)
  assert.equal(unpacked.problems.length, 6)
  assert.equal(unpacked.problems[0].id, '4A')
  assert.equal(unpacked.problems[0].rating, 800)
  assert.deepEqual(unpacked.problems[0].tags, ['brute force', 'math'])
  assert.equal(unpacked.problems[0].url, 'https://codeforces.com/problemset/problem/4/A')
  assert.equal(unpacked.problems[5].rating, null)
})

test('filterAndSortProblems filters per tag and sorts by rating ascending and descending', () => {
  const byMathAsc = filterAndSortProblems(sampleProblems, { tags: ['math'], sort: 'rating-asc' })
  assert.deepEqual(byMathAsc.map(p => p.id), ['4A', '1999G2'])

  const byMathDesc = filterAndSortProblems(sampleProblems, { tags: ['math'], sort: 'rating-desc' })
  assert.deepEqual(byMathDesc.map(p => p.id), ['1999G2', '4A'])

  const multiTagAll = filterAndSortProblems(sampleProblems, { tags: ['math', 'binary search'], tagMode: 'all' })
  assert.deepEqual(multiTagAll.map(p => p.id), ['1999G2'])

  const multiTagAny = filterAndSortProblems(sampleProblems, { tags: ['dp', 'strings'], tagMode: 'any', sort: 'rating-asc' })
  assert.deepEqual(multiTagAny.map(p => p.id), ['71A', '455A'])

  const rangeFiltered = filterAndSortProblems(sampleProblems, { minRating: 1400, maxRating: 1800, sort: 'rating-asc' })
  assert.deepEqual(rangeFiltered.map(p => p.id), ['455A', '1999G2'])

  const withUnrated = filterAndSortProblems(sampleProblems, { tags: ['dp'], includeUnrated: true, sort: 'rating-asc' })
  assert.deepEqual(withUnrated.map(p => p.id), ['455A', '2100F'])

  const searched = filterAndSortProblems(sampleProblems, { search: 'dijkstra' })
  assert.deepEqual(searched.map(p => p.id), ['20C'])

  const solvedOnly = filterAndSortProblems(sampleProblems, { onlySolved: 'solved', solvedIds: new Set(['455A']) })
  assert.deepEqual(solvedOnly.map(p => p.id), ['455A'])
})

test('scrapeCodeforcesProblems merges problems and solved counts from API response', async () => {
  const list = await scrapeCodeforcesProblems({
    apiKey: '0b15d623a1cf566781d4bd1f22e88279bdffac02',
    fetchImpl: async () => ({
      ok: true,
      json: async () => ({
        status: 'OK',
        result: {
          problems: [
            { contestId: 4, index: 'A', name: 'Watermelon', rating: 800, tags: ['brute force', 'math'] },
            { contestId: 455, index: 'A', name: 'Boredom', rating: 1500, tags: ['dp'] }
          ],
          problemStatistics: [
            { contestId: 4, index: 'A', solvedCount: 550123 },
            { contestId: 455, index: 'A', solvedCount: 95100 }
          ]
        }
      })
    })
  })
  assert.equal(list.length, 2)
  assert.equal(list[0].id, '4A')
  assert.equal(list[0].solvedCount, 550123)
  assert.equal(list[1].rating, 1500)
})

test('buildSignedUrl and parseProblemsetHTML and ratingTier handle edge cases', () => {
  const publicUrl = buildSignedUrl('problemset.problems', {}, 'key-only', '')
  assert.equal(publicUrl, 'https://codeforces.com/api/problemset.problems')
  const signedUrl = buildSignedUrl('problemset.problems', { tags: 'dp' }, 'myKey', 'mySecret')
  assert.match(signedUrl, /apiKey=myKey/)
  assert.match(signedUrl, /apiSig=123456[0-9a-f]{128}/)

  const html = `
    <tr>
      <td class="id"><a href="/problemset/problem/4/A">4A</a></td>
      <td><a href="/problemset/problem/4/A">Watermelon</a><a class="notice">math</a><a class="notice">brute force</a></td>
      <td><span class="ProblemRating">800</span></td>
      <td><a title="Participants solved the problem">x550000</a></td>
    </tr>`
  const parsed = parseProblemsetHTML(html)
  assert.equal(parsed.length, 1)
  assert.equal(parsed[0].id, '4A')
  assert.equal(parsed[0].name, 'Watermelon')
  assert.equal(parsed[0].rating, 800)
  assert.deepEqual(parsed[0].tags, ['math', 'brute force'])

  assert.equal(ratingTier(800).className, 'cf-newbie')
  assert.equal(ratingTier(1500).className, 'cf-specialist')
  assert.equal(ratingTier(2400).className, 'cf-gm')
})
