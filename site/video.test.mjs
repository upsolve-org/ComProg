import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import test from 'node:test'
import { activeChapterIndex, buildFilmChapters, filmNotes, parseVtt } from './video.mjs'

const root = new URL('../', import.meta.url)
const scripts = JSON.parse((await readFile(new URL('site/video/lessons.json', root), 'utf8')).replace(/^\uFEFF/, ''))

test('lesson videos derive chapter timestamps from narration scripts and WebVTT cues', async () => {
  const pythonVtt = await readFile(new URL('site/public/PythonGuide.vtt', root), 'utf8')
  const contestVtt = await readFile(new URL('site/public/ContestGuide.vtt', root), 'utf8')

  const pythonChapters = buildFilmChapters(scripts.PythonGuide, pythonVtt, 'PythonGuide')
  assert.deepEqual(
    pythonChapters.map(({ title, stamp, start }) => ({ title, stamp, start })),
    [
      { title: 'Choose a runtime', stamp: '0:00', start: 0 },
      { title: 'Read the input', stamp: '0:12', start: 12.85 },
      { title: 'Count the work', stamp: '0:25', start: 25.3 },
      { title: 'Choose an operation', stamp: '0:37', start: 37.833 }
    ]
  )

  const contestChapters = buildFilmChapters(scripts.ContestGuide, contestVtt, 'ContestGuide')
  assert.deepEqual(
    contestChapters.map(({ title, stamp, start }) => ({ title, stamp, start })),
    [
      { title: 'Choose a round', stamp: '0:00', start: 0 },
      { title: 'Read the standings', stamp: '0:12', start: 12.7 },
      { title: 'Trace a submission', stamp: '0:25', start: 25.433 },
      { title: 'Upsolve after the round', stamp: '0:38', start: 38.05 }
    ]
  )

  assert.equal(Object.keys(filmNotes).length, 41)
  for (const [noteName, filmId] of Object.entries(filmNotes)) {
    assert.ok(scripts[filmId], `Missing script for ${filmId} (${noteName})`)
    const vtt = await readFile(new URL('site/public/' + filmId + '.vtt', root), 'utf8')
    const chapters = buildFilmChapters(scripts[filmId], vtt, filmId)
    assert.equal(chapters.length, 4, `${filmId} should have 4 chapters`)
    assert.equal(chapters[0].stamp, '0:00')
  }
})

test('mismatched captions, missing cues, extra cues, and invalid timings fail chapter building', async () => {
  const pythonVtt = await readFile(new URL('site/public/PythonGuide.vtt', root), 'utf8')

  assert.throws(
    () => buildFilmChapters(scripts.PythonGuide, pythonVtt.replace('PyPy can speed up', 'C++ can speed up'), 'PythonGuide'),
    /captions do not match script/
  )

  const editedBeats = structuredClone(scripts.PythonGuide)
  editedBeats[2][2] = 'Different script text. Changing interpreters cannot remove that repeated work. First look for a way to reuse a result.'
  assert.throws(
    () => buildFilmChapters(editedBeats, pythonVtt, 'PythonGuide'),
    /captions do not match script/
  )

  const truncatedVtt = pythonVtt.replace(/\r\n/g, '\n').trim().split(/\n{2,}/).slice(0, -1).join('\n\n')
  assert.throws(
    () => buildFilmChapters(scripts.PythonGuide, truncatedVtt, 'PythonGuide'),
    /captions end mid-chapter/
  )

  const extraCueVtt = pythonVtt.trim() + '\n\n00:00:49.500 --> 00:00:51.000\nExtra trailing caption.\n'
  assert.throws(
    () => buildFilmChapters(scripts.PythonGuide, extraCueVtt, 'PythonGuide'),
    /extra caption cue/
  )

  assert.throws(
    () => parseVtt('WEBVTT\n\n00:00:05.000 --> 00:00:03.000\nBackwards cue.\n', 'BrokenVTT'),
    /out-of-order cue timings/
  )
})

test('activeChapterIndex tracks the current chapter across playback timestamps', async () => {
  const pythonVtt = await readFile(new URL('site/public/PythonGuide.vtt', root), 'utf8')
  const chapters = buildFilmChapters(scripts.PythonGuide, pythonVtt, 'PythonGuide')

  // Every assertion reads the boundary from the built chapters, so re-timed captions cannot break it.
  const starts = chapters.map(chapter => chapter.start)
  assert.equal(activeChapterIndex(chapters, 0), 0)
  assert.equal(activeChapterIndex(chapters, starts[1] - 0.1), 0)
  assert.equal(activeChapterIndex(chapters, starts[1]), 1)
  assert.equal(activeChapterIndex(chapters, starts[2]), 2)
  assert.equal(activeChapterIndex(chapters, starts[3]), 3)
  assert.equal(activeChapterIndex(chapters, 48.5), 3)
})
