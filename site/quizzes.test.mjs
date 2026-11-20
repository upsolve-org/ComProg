import assert from 'node:assert/strict'
import test from 'node:test'
import { quizzes } from './quizzes.mjs'

test('every chapter has a multi-question quiz with valid choices and explanations', () => {
  assert.equal(quizzes.length, 13)
  for (const [chapterIndex, items] of quizzes.entries()) {
    assert.ok(Array.isArray(items) && items.length >= 3, `Chapter ${chapterIndex} should have at least 3 quiz questions`)
    for (const [qIndex, item] of items.entries()) {
      assert.ok(typeof item.question === 'string' && item.question.length > 15, `Invalid question text at ${chapterIndex}:${qIndex}`)
      assert.ok(Array.isArray(item.options) && item.options.length === 4, `Expected 4 options at ${chapterIndex}:${qIndex}`)
      assert.ok(new Set(item.options).size === 4, `Duplicate options at ${chapterIndex}:${qIndex}`)
      assert.ok(Number.isInteger(item.answer) && item.answer >= 0 && item.answer < 4, `Invalid answer index at ${chapterIndex}:${qIndex}`)
      assert.ok(typeof item.explanation === 'string' && item.explanation.length > 20, `Missing explanation at ${chapterIndex}:${qIndex}`)
    }
  }
})
