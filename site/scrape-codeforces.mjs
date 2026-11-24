import { writeFile } from 'node:fs/promises'
import { scrapeCodeforcesProblems, packProblems } from './codeforces.mjs'

const outUrl = new URL('./public/codeforces-problems.json', import.meta.url)

console.log('Scraping Codeforces problemset (tags + ratings + solved counts)...')
const problems = await scrapeCodeforcesProblems({
  apiKey: process.env.CF_API_KEY,
  apiSecret: process.env.CF_API_SECRET
})
const packed = packProblems(problems)
await writeFile(outUrl, JSON.stringify(packed))
const ratedCount = problems.filter(p => p.rating !== null).length
console.log(`Saved ${packed.total} problems (${ratedCount} rated, ${packed.tags.length} unique tags) to site/public/codeforces-problems.json`)
