import { readFile, writeFile, mkdir, stat } from 'node:fs/promises'
import { join } from 'node:path'

const folder = process.argv[2]
await mkdir(folder, { recursive: true })
const headers = { 'x-goog-api-key': process.env.GEMINI_API_KEY, 'content-type': 'application/json' }
const base = 'https://generativelanguage.googleapis.com/v1beta/'
const listing = await fetch(base + 'models?pageSize=1000', { headers })
if (!listing.ok) throw Error('Gemini model lookup HTTP ' + listing.status + ': ' + (await listing.json()).error?.status)
const allModels = (await listing.json()).models
const candidates = [
  'gemini-3.1-flash-tts-preview',
  'gemini-3.8-flash-tts',
  'gemini-3.8-flash-lite-tts',
  'gemini-2.5-flash-preview-tts',
  'gemini-2.5-pro-preview-tts'
].map(x => 'models/' + x).filter(id => allModels.some(m => m.name === id))

if (!candidates.length) throw Error('No supported Gemini speech model available')

const lessons = JSON.parse((await readFile(new URL('lessons.json', import.meta.url), 'utf8')).replace(/^\uFEFF/, ''))
const queue = []
for (const [name, beats] of Object.entries(lessons)) {
  for (const [index, [, , script]] of beats.entries()) {
    const outPath = join(folder, name + index + '.wav')
    try {
      const info = await stat(outPath)
      if (info.size > 10000) continue
    } catch { /* Needs recording */ }
    queue.push({ name, index, script, outPath })
  }
}

console.log(`Recording ${queue.length} clips across ${candidates.length} Gemini TTS models...`)

async function recordClip(item, attempt = 0) {
  const model = candidates[(item.index + attempt) % candidates.length]
  try {
    const response = await fetch(base + model + ':generateContent', {
      method: 'POST',
      headers,
      body: JSON.stringify({
        contents: [{ parts: [{ text: item.script }] }],
        generationConfig: {
          responseModalities: ['AUDIO'],
          speechConfig: { voiceConfig: { prebuiltVoiceConfig: { voiceName: 'Kore' } } }
        }
      })
    })
    const result = await response.json()
    if (!response.ok) {
      if (attempt < 8 && (response.status === 429 || response.status >= 500)) {
        await new Promise(r => setTimeout(r, 800 * (attempt + 1)))
        return recordClip(item, attempt + 1)
      }
      throw Error('Gemini speech HTTP ' + response.status + ': ' + result.error?.status)
    }
    const audio = result.candidates?.[0]?.content?.parts?.find(p => p.inlineData)?.inlineData
    if (!audio?.data) {
      if (attempt < 6) {
        await new Promise(r => setTimeout(r, 600 * (attempt + 1)))
        return recordClip(item, attempt + 1)
      }
      throw Error('Missing inline audio data for ' + item.name + ' beat ' + item.index)
    }
    let data = Buffer.from(audio.data, 'base64')
    if (data.toString('ascii', 0, 4) !== 'RIFF') {
      const rate = Number(audio.mimeType?.match(/rate=(\d+)/)?.[1] || 24000)
      const h = Buffer.alloc(44)
      h.write('RIFF'); h.writeUInt32LE(data.length + 36, 4); h.write('WAVEfmt ', 8)
      h.writeUInt32LE(16, 16); h.writeUInt16LE(1, 20); h.writeUInt16LE(1, 22)
      h.writeUInt32LE(rate, 24); h.writeUInt32LE(rate * 2, 28); h.writeUInt16LE(2, 32)
      h.writeUInt16LE(16, 34); h.write('data', 36); h.writeUInt32LE(data.length, 40)
      data = Buffer.concat([h, data])
    }
    await writeFile(item.outPath, data)
    console.log(item.name, item.index + 1, 'recorded')
  } catch (err) {
    if (attempt < 6) {
      await new Promise(r => setTimeout(r, 800 * (attempt + 1)))
      return recordClip(item, attempt + 1)
    }
    throw err
  }
}

const concurrency = 10
let cursor = 0
await Promise.all(Array.from({ length: concurrency }, async () => {
  while (cursor < queue.length) {
    const item = queue[cursor++]
    await recordClip(item)
  }
}))
console.log('All narration clips recorded.')
