import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import test from 'node:test'
import { cppQuizzes } from './quizzes-cpp.mjs'
import { cppLabs } from './labs-cpp.mjs'
import { judgeCppSubmission, runCpp } from './judge.mjs'

const root = new URL('../', import.meta.url)

test('C++20 course has 13 chapters of 3 valid quiz questions each', () => {
  assert.equal(cppQuizzes.length, 13)
  for (const [chapterIndex, items] of cppQuizzes.entries()) {
    assert.equal(items.length, 3, `C++ chapter ${chapterIndex} should have 3 quiz questions`)
    for (const [qIndex, item] of items.entries()) {
      assert.ok(typeof item.question === 'string' && item.question.length > 15, `Invalid question at ${chapterIndex}:${qIndex}`)
      assert.ok(Array.isArray(item.options) && item.options.length === 4, `Expected 4 options at ${chapterIndex}:${qIndex}`)
      assert.ok(new Set(item.options).size === 4, `Duplicate options at ${chapterIndex}:${qIndex}`)
      assert.ok(Number.isInteger(item.answer) && item.answer >= 0 && item.answer < 4, `Invalid answer at ${chapterIndex}:${qIndex}`)
      assert.ok(typeof item.explanation === 'string' && item.explanation.length > 20, `Missing explanation at ${chapterIndex}:${qIndex}`)
    }
  }
})

test('C++20 course has 12 labs with starter templates and hints', () => {
  assert.equal(cppLabs.length, 12)
  for (const [index, lab] of cppLabs.entries()) {
    assert.ok(typeof lab.title === 'string' && lab.title.length > 3, `Missing title at lab ${index}`)
    assert.ok(typeof lab.task === 'string' && lab.task.length > 15, `Missing task at lab ${index}`)
    assert.ok(Array.isArray(lab.hints) && lab.hints.length >= 3, `Expected >= 3 hints at lab ${index}`)
    assert.ok(typeof lab.starter === 'string' && lab.starter.includes('#include'), `Missing C++ starter at lab ${index}`)
  }
})

test('built dist/course-cpp.json contains all 13 modules, 12 labs, and 39 quizzes', async () => {
  const courseCpp = JSON.parse(await readFile(new URL('dist/course-cpp.json', root), 'utf8'))
  assert.equal(courseCpp.length, 13)
  assert.equal(courseCpp.filter(ch => ch.lab).length, 12)
  assert.equal(courseCpp.reduce((sum, ch) => sum + (ch.quizzes?.length ?? 0), 0), 39)
  assert.ok(courseCpp.every(ch => ch.sections.length > 0 && ch.notes.length > 0))
})

test('C++ judge and runner stay unavailable without CPP_JUDGE_IMAGE and propagate compile errors', async () => {
  assert.deepEqual(await runCpp('int main(){}', '', { image: '' }), { status: 'unavailable' })
  assert.deepEqual(await judgeCppSubmission(0, cppLabs[0], 'int main(){}', { image: '' }), { status: 'unavailable' })

  const compileFail = await judgeCppSubmission(0, cppLabs[0], 'bad code', {
    image: 'mock-cpp',
    build: async () => ({ status: 'compile_error', message: 'main.cpp:1:1: error: expected unqualified-id' }),
    run: async () => { throw new Error('should not run after compile_error') }
  })
  assert.equal(compileFail.status, 'compile_error')
  assert.match(compileFail.message, /expected unqualified-id/)

  const accepted = await judgeCppSubmission(0, cppLabs[0], 'int main(){}', {
    image: 'mock-cpp',
    build: async () => ({ status: 'ok' }),
    run: async (_code, input) => {
      const [a, b] = input.trim().split(/\s+/).map(BigInt)
      return { status: 'ok', output: String(a + b) + '\n' }
    }
  })
  assert.deepEqual(accepted, { status: 'accepted' })
})
