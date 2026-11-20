import assert from 'node:assert/strict'
import test from 'node:test'
import { judgeSubmission } from './judge.mjs'
import { privateCases } from './judge-cases.mjs'
import { labs } from './labs.mjs'

const image = 'test-image'
const add = (input) => input.trim().split(/\s+/).map(Number).reduce((a, b) => a + b, 0)

test('an accepted submission returns only a verdict', async () => {
  assert.deepEqual(await judgeSubmission(0, labs[0], 'submitted code', {
    image,
    run: async (code, input) => {
      assert.equal(code, 'submitted code')
      return { status: 'ok', output: '  ' + add(input) + '\n' }
    }
  }), { status: 'accepted' })
})

test('a private failure never exposes stdin, expected output, or program output', async () => {
  assert.deepEqual(await judgeSubmission(0, labs[0], 'code', {
    image, run: async () => ({ status: 'ok', output: 'input and traceback' })
  }), { status: 'wrong_answer', stage: 'correctness' })
})

test('stress verdict stays distinct and binary search has a maximum-query workload', async () => {
  const lab = labs[2]
  const suite = privateCases(2, lab)
  const stress = suite.at(-1)
  assert.equal(stress.input.split('\n')[0], '200000 200000')
  assert.equal(stress.expected.split('\n').length, 200_000)
  let called = 0
  assert.deepEqual(await judgeSubmission(2, lab, 'code', {
    image,
    run: async (_code, input) => {
      assert.equal(input, suite[called].input)
      const { expected, stress } = suite[called++]
      return stress ? { status: 'time_limit' } : { status: 'ok', output: expected }
    }
  }), { status: 'time_limit', stage: 'stress' })
  assert.equal(called, suite.length)
})

test('all assignments have hidden edge cases and algorithmic assignments have stress cases', () => {
  for (const [index, lab] of labs.entries()) {
    const suite = privateCases(index, lab)
    assert.ok(suite.length >= 7, lab.title)
    if (index) assert.ok(suite.some(item => item.stress), lab.title)
  }
})

test('the judge stays unavailable without a configured runner', async () => {
  assert.deepEqual(await judgeSubmission(0, labs[0], 'code', {
    image: '',
    run: () => assert.fail('No executor should run')
  }), { status: 'unavailable' })
})
