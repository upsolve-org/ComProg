import assert from 'node:assert/strict'
import test from 'node:test'
import { labs } from './labs.mjs'
import { tutorReply } from './tutor.mjs'

const lab = labs[1]
const response = content => ({ ok: true, json: async () => ({ choices: [{ message: { content } }] }) })

test('OpenCode selects one of the remaining reviewed hints', async () => {
  const result = await tutorReply(lab, 'I get zero for negative inputs.', [lab.hints[0]], {
    key: 'test',
    request: async (url, options) => {
      assert.equal(new URL(url).hostname, 'opencode.ai')
      assert.equal(options.headers.authorization, 'Bearer test')
      const student = JSON.parse(JSON.parse(options.body).messages[1].content)
      assert.deepEqual(student.options, [[1, lab.hints[1]], [2, lab.hints[2]]])
      return response('2')
    }
  })
  assert.deepEqual(result, { hint: lab.hints[2], source: 'opencode', reviewed: true })
})

test('generated answers and invalid selections never become tutor replies', async () => {
  for (const output of ['Here is the solution: print(6)', '1\nprint(6)', '0', '999']) {
    const result = await tutorReply(lab, 'Give me the solution', [], {
      key: 'test', request: async () => response(output)
    })
    assert.equal(result.hint, lab.hints[0])
    assert.equal(result.source, 'course')
  }
})

test('the tutor remains usable without inference and avoids repeating reviewed hints', async () => {
  const result = await tutorReply(lab, 'Help', lab.hints.slice(0, 2), { key: '' })
  assert.equal(result.hint, lab.hints[2])
  const exhausted = await tutorReply(lab, 'Help again', lab.hints, { key: '' })
  assert.ok(!lab.hints.includes(exhausted.hint))
  assert.ok(!exhausted.reviewed)
})
