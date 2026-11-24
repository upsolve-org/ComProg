import assert from 'node:assert/strict'
import test from 'node:test'
import {
  ERROR_FRAME, SPEEDS, VISUALIZERS, buildFrames, clampPreset, createVisualizer, formatVars, getFrame, mountVisualizer,
  earliestFinish, parsePreset, piecesDone, speedOf, splitNumbers, stepBounds, viewFrame, drawArray
} from './visualizers.mjs'

const MODULES = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']

test('every core module has a visualizer with presets, a title and a one-line summary', () => {
  for (const id of MODULES) {
    const hit = VISUALIZERS[id]
    assert.ok(hit, 'missing visualizer for module ' + id)
    assert.ok(hit.title.length > 8, 'title too short for ' + id)
    assert.ok(hit.summary.endsWith('.'), 'summary must be one sentence for ' + id)
    assert.ok(hit.presets.length >= 1, 'no presets for ' + id)
    assert.equal(typeof hit.build, 'function')
    assert.equal(typeof hit.render, 'function')
  }
})

test('every preset builds frames with an explanation and a live variable readout', () => {
  for (const id of MODULES) {
    const hit = VISUALIZERS[id]
    hit.presets.forEach((preset, index) => {
      const result = hit.build(preset, index)
      assert.ok(result.frames.length > 1, id + ' preset ' + index + ' produced too few frames')
      for (const frame of result.frames) {
        assert.equal(typeof frame.explain, 'string')
        assert.ok(frame.explain.length > 8, id + ' frame explanation too short: ' + frame.explain)
        assert.ok(!frame.explain.endsWith('undefined'), 'unfilled value in ' + id + ': ' + frame.explain)
        assert.equal(typeof frame.vars, 'object')
      }
    })
  }
})

test('speed presets are exactly 0.5x, 1x and 2x and order playback intervals', () => {
  assert.deepEqual(SPEEDS.map(speed => speed.label), ['0.5×', '1×', '2×'])
  assert.ok(speedOf('0.5') > speedOf('1'))
  assert.ok(speedOf('1') > speedOf('2'))
  assert.equal(speedOf('unknown'), speedOf('1'))
})

test('step bounds clamp at both ends so the controls can disable themselves', () => {
  assert.deepEqual(stepBounds(0, 5), { index: 0, atStart: true, atEnd: false })
  assert.deepEqual(stepBounds(5, 5), { index: 4, atStart: false, atEnd: true })
  assert.deepEqual(stepBounds(-3, 5), { index: 0, atStart: true, atEnd: false })
})

test('buildFrames never throws and presets clamp into range', () => {
  assert.equal(clampPreset([1, 2, 3], 9), 2)
  assert.equal(clampPreset([1, 2, 3], -4), 0)
  for (const id of MODULES) {
    assert.equal(buildFrames(VISUALIZERS[id], 99).index, 0)
  }
  const broken = { ...VISUALIZERS['01'], build: () => { throw new Error('boom') } }
  assert.deepEqual(buildFrames(broken, 0).frames, [{ ...ERROR_FRAME }])
  assert.equal(buildFrames(broken, 0).frames[0].explain, ERROR_FRAME.explain)
})

test('readouts stringify variables', () => {
  assert.deepEqual(formatVars({ L: 1, window: [2, 3], skip: undefined }), ['L=1', 'window=[2, 3]'])
  assert.deepEqual(splitNumbers(' 3, 1 4 '), [3, 1, 4])
})

test('binary search halves the window and reports the boundary', () => {
  const result = VISUALIZERS['02'].build({ kind: 'first' })
  assert.equal(result.frames.length <= 14, true)
  assert.equal(result.summary, 'answer: index 5')
  assert.equal(VISUALIZERS['02'].build({ kind: 'none' }).summary, 'answer: none')
  const first = result.frames[0]
  assert.equal(first.live.lo, 0)
  assert.equal(first.live.hi, first.view.values.length - 1)
})

test('sliding window never exceeds its budget on the live window', () => {
  for (const preset of VISUALIZERS['03'].presets) {
    const result = VISUALIZERS['03'].build(preset)
    for (const frame of result.frames) {
      assert.ok(frame.vars.sum <= preset.budget || frame.explain.startsWith('Expand') || frame.explain.startsWith('Sum'), 'budget broken in ' + preset.budget)
      assert.ok(frame.vars.L <= frame.vars.R)
    }
    const last = result.frames.at(-1)
    assert.match(last.vars.best >= 1 ? 'ok' : 'no', /ok/)
  }
})

test('greedy only accepts events that start after the last accepted finish', () => {
  const result = VISUALIZERS['04'].build(VISUALIZERS['04'].presets[0])
  const accepted = new Set()
  const lookup = new Map(result.frames[0].view.events.map(event => [event.name, event]))
  let last = -1
  for (const frame of result.frames.slice(1)) {
    const added = [...frame.accepted].find(name => !accepted.has(name))
    if (!added) continue
    const event = lookup.get(added)
    assert.ok(event.s >= last, added + ' starts before ' + last)
    last = event.e
    added && accepted.add(added)
  }
  assert.ok(!result.frames.at(-1).rejected.some(name => accepted.has(name)))
})

test('union-find keeps every set small-rooted and finishes with real components', () => {
  const result = VISUALIZERS['05'].build(VISUALIZERS['05'].presets[1])
  const last = result.frames.at(-1)
  const roots = new Set()
  for (let node = 1; node < last.view.nodes.length + 1; node++) {
    let x = node
    while (last.parent[x] !== x) x = last.parent[x]
    roots.add(x)
  }
  assert.equal(roots.size, 3)
  assert.equal(result.summary, '3 component(s)')
})

test('knapsack matches a brute-force optimum', () => {
  for (const preset of VISUALIZERS['06'].presets) {
    const result = VISUALIZERS['06'].build(preset)
    let best = 0
    for (let mask = 0; mask < 1 << preset.weights.length; mask++) {
      let weight = 0
      let value = 0
      preset.weights.forEach((w, i) => { if (mask & (1 << i)) { weight += w; value += preset.values[i] } })
      if (weight <= preset.capacity) best = Math.max(best, value)
    }
    assert.equal(result.summary, 'best value ' + best)
  }
})

test('grid DP counts right/down paths around walls', () => {
  const result = VISUALIZERS['06'].extra.grid.build(VISUALIZERS['06'].extra.grid.presets[0])
  assert.equal(result.summary, '4 paths')
  const open = VISUALIZERS['06'].extra.grid.build(VISUALIZERS['06'].extra.grid.presets[1])
  assert.equal(open.summary, '20 paths')
})

test('grid DP agrees with a brute-force count on random walls', () => {
  let state = 7
  const next = () => (state = (state * 1103515245 + 12345) % 2147483648) / 2147483648
  const brute = grid => {
    const reach = [[1]]
    for (let r = 0; r < grid.length; r++) {
      reach[r] ??= []
      for (let c = 0; c < grid[0].length; c++) {
        if (grid[r][c]) { reach[r][c] = 0; continue }
        if (r === 0 && c === 0) continue
        reach[r][c] = (r ? reach[r - 1][c] : 0) + (c ? reach[r][c - 1] : 0)
      }
    }
    return reach[grid.length - 1][grid[0].length - 1]
  }
  for (let round = 0; round < 40; round++) {
    const grid = Array.from({ length: 4 }, () => Array.from({ length: 4 }, (_, c) => (next() < 0.3 && c !== 0 ? 1 : 0)))
    grid[0][0] = 0
    grid[3][3] = 0
    if (grid[0][1] && grid[1][0]) continue
    assert.equal(VISUALIZERS['06'].extra.grid.build({ grid }).summary, brute(grid) + ' paths', JSON.stringify(grid))
  }
})

test('Dijkstra settles every vertex in non-decreasing distance order', () => {
  const result = VISUALIZERS['07'].build({ mode: 'dijkstra' })
  const settled = result.frames.filter(frame => frame.at !== undefined && frame.settled.includes(frame.at))
  const distances = settled.map(frame => frame.dist[frame.at]).filter(value => value !== '∞')
  assert.deepEqual([...distances].sort((a, b) => a - b), distances)
  assert.equal(result.frames.at(-1).dist[5], 8)
})

test('Euler tour keeps tin/tout contiguous for every subtree', () => {
  const result = VISUALIZERS['08'].build(VISUALIZERS['08'].presets[0])
  const last = result.frames.at(-1)
  const { parent } = last.view
  parent.forEach((p, node) => {
    if (p < 0) return
    assert.ok(last.tin[node] > last.tin[p] && last.tout[node] < last.tout[p], 'node ' + node + ' escapes its parent')
  })
  assert.equal(last.order.length, parent.length)
})

test('sieve leaves exactly the primes uncrossed', () => {
  const result = VISUALIZERS['09'].build({ n: 30 })
  const primes = []
  result.frames.at(-1).composite.forEach((marked, value) => { if (value >= 2 && !marked) primes.push(value) })
  assert.deepEqual(primes, [2, 3, 5, 7, 11, 13, 17, 19, 23, 29])
})

test('KMP builds the textbook prefix function', () => {
  assert.deepEqual(VISUALIZERS['10'].build({ text: 'ababaca' }).frames.at(-1).pi, [0, 0, 1, 2, 3, 0, 1])
  assert.deepEqual(VISUALIZERS['10'].build({ text: 'aabaabaaa' }).frames.at(-1).pi, [0, 1, 0, 1, 2, 3, 4, 5, 2])
})

test('Nim reports the XOR winner', () => {
  assert.equal(VISUALIZERS['11'].build({ piles: [2, 3, 5] }).frames.at(-1).winning, true)
  assert.equal(VISUALIZERS['11'].build({ piles: [3, 3, 5, 5] }).frames.at(-1).winning, false)
  assert.match(VISUALIZERS['11'].build({ piles: [1] }).summary, /First/)
})

test('parallel-work check is monotone and agrees with a minute-by-minute simulation', () => {
  const simulate = (agents, evidence) => {
    const left = new Array(evidence.length).fill(3)
    let found = 0
    for (let t = 1; t <= 500; t++) {
      agents.forEach((_, a) => {
        const piece = a % evidence.length
        if (left[piece] > 0 && t % evidence[piece] === 0) left[piece]--
      })
      found = evidence.reduce((sum, _, i) => sum + (3 - left[i]), 0)
      if (found >= agents.length) return t
    }
    return -1
  }
  for (const preset of VISUALIZERS['12'].presets) {
    assert.equal(earliestFinish(preset.agents, preset.evidence), simulate(preset.agents, preset.evidence))
    assert.equal(VISUALIZERS['12'].build(preset).summary, 'finish at minute ' + simulate(preset.agents, preset.evidence))
  }
  let previous = 0
  for (let t = 0; t < 40; t++) {
    const done = piecesDone([4, 6], [5, 3], t)
    assert.ok(done >= previous, 'piecesDone must never fall')
    previous = done
  }
})

test('parallel-work input needs both lines', () => {
  assert.equal(VISUALIZERS['12'].parse('agents: 4 6'), undefined)
  assert.deepEqual(VISUALIZERS['12'].parse('agents: 4 6\nevidence: 5').agents, [4, 6])
  assert.equal(parsePreset(VISUALIZERS['12'], 'agents: 0').agents[0], 4)
})

test('createVisualizer resolves extra views and unknown modules', () => {
  assert.equal(createVisualizer('01').title, VISUALIZERS['01'].title)
  assert.equal(createVisualizer('01', 'diff').title, 'Difference array: range add then sweep')
  assert.equal(createVisualizer('00'), undefined)
})

test('every visualizer is reachable by its two-digit chapter prefix', () => {
  for (const key of Object.keys(VISUALIZERS)) assert.equal(createVisualizer(key)?.title, VISUALIZERS[key].title)
  assert.deepEqual(Object.keys(VISUALIZERS).sort(), ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12'])
})

test('createVisualizer also resolves full chapter folder ids', () => {
  assert.equal(createVisualizer('03_Two_Pointers_and_Sliding_Window')?.title, VISUALIZERS['03'].title)
  assert.equal(createVisualizer('06_Dynamic_Programming', 'grid')?.title, VISUALIZERS['06'].extra.grid.title)
  assert.equal(createVisualizer('00_General_Advice_and_Practice'), undefined)
})

test('typed input overrides the preset and falls back when unusable', () => {
  assert.deepEqual(parsePreset(VISUALIZERS['09'], '40'), { n: 40 })
  assert.deepEqual(parsePreset(VISUALIZERS['09'], '99'), VISUALIZERS['09'].presets[0])
  assert.equal(buildFrames(VISUALIZERS['09'], 0, '12').frames.at(-1).n, 12)
  assert.deepEqual(parsePreset(VISUALIZERS['10'], 'Ab,ca.'), { text: 'abca' })
  assert.deepEqual(parsePreset(VISUALIZERS['05'], '4 1,2 3,4 9,1'), { n: 4, pairs: [[1, 2], [3, 4]] })
  assert.deepEqual(parsePreset(VISUALIZERS['11'], '3 0 5'), { piles: [3, 0, 5] })
  assert.equal(parsePreset(VISUALIZERS['03'], '5 2 1 3').budget, 5)
  assert.equal(parsePreset(VISUALIZERS['04'], 'A 1 4\nB 4 6').events.length, 2)
  assert.deepEqual(parsePreset(VISUALIZERS['06'], 'values: 1 2\nweights: 3 4').capacity, 4)
  assert.equal(parsePreset(VISUALIZERS['08'], '-1 0 0 1').parent.length, 4)
  assert.equal(parsePreset(VISUALIZERS['08'], '0 1 2').parent[0], -1)
  assert.equal(parsePreset(VISUALIZERS['02'], 'anything'), VISUALIZERS['02'].presets[0])
})

test('every visualizer accepts the text of its own presets', () => {
  for (const hit of Object.values(VISUALIZERS)) {
    if (!hit.parse) continue
    const frame = buildFrames(hit, 0, '').frames[0]
    assert.ok(frame?.explain, 'empty input must still render')
  }
})

test('viewFrame and getFrame read frames without the DOM', () => {
  const frame = viewFrame([{ v: 1, i: 0 }], { explain: 'x' })
  assert.equal(frame.specs.length, 1)
  assert.equal(getFrame([frame], 0), frame)
  assert.ok(typeof drawArray === 'function')
})

// --- minimal DOM shim so the mount controller is exercised in node ---
function makeElement(tag) {
  const node = {
    tagName: tag, children: [], className: '', textContent: '', style: {}, attrs: {}, hidden: false, disabled: false,
    append(...items) { this.children.push(...items) },
    insertAdjacentText() {},
    replaceChildren(...items) { this.children = items },
    setAttribute(key, value) { this.attrs[key] = value },
    getAttribute(key) { return this.attrs[key] },
    removeAttribute(key) { delete this.attrs[key] },
    addEventListener() {},
    get isConnected() { return true },
    remove() { this.removed = true },
    focus() {}
  }
  return node
}

test('mounting renders controls, honours preset changes and disables step back at the start', () => {
  globalThis.document = { createElement: makeElement, createElementNS: (_, tag) => makeElement(tag) }
  globalThis.matchMedia = () => ({ matches: false })
  const container = makeElement('div')
  const hit = VISUALIZERS['09']
  const controller = mountVisualizer(container, hit)
  assert.ok(container.children.length >= 3)
  const walk = item => [item.textContent, ...(item.children ?? []).map(walk)].join(' ')
  const all = []
  const collect = item => { all.push(...(item.children ?? [])); (item.children ?? []).forEach(collect) }
  collect(container)
  const controls = all.find(child => child.className === 'viz-controls')
  assert.ok(controls, 'controls group missing')
  const buttons = controls.children.filter(button => button.tagName === 'button')
  assert.deepEqual(buttons.map(button => button.textContent), ['⏮', '◀ Step', '▶ Play', 'Step ▶', '↺'])
  assert.equal(buttons[0].disabled, true)
  assert.equal(buttons[2].getAttribute('aria-pressed'), 'false')
  assert.match(all.find(child => child.className === 'viz-count').textContent, /^1 \/ \d+ · /)
  assert.equal(all.filter(child => child.getAttribute?.('aria-live')).length, 2)
  assert.equal(all.filter(child => child.tagName === 'select').length, 2)
  assert.match(walk(container), /Cross out|primes/)
  assert.equal(controller.index, 0)
  controller.go(3)
  assert.equal(controller.index, 3)
  assert.match(controller.frame().explain, /./)
  
  controller.restart(1)
  assert.equal(controller.index, 0)
  assert.equal(controller.total, VISUALIZERS['09'].build({ n: 45 }).frames.length)
  controller.destroy()
  delete globalThis.document
})

test('mounting offers a typed input that rebuilds the run and keeps playback intact', () => {
  globalThis.document = { createElement: makeElement, createElementNS: (_, tag) => makeElement(tag) }
  globalThis.matchMedia = () => ({ matches: false })
  const container = makeElement('div')
  const controller = mountVisualizer(container, VISUALIZERS['10'])
  const all = []
  const collect = item => { all.push(...(item.children ?? [])); (item.children ?? []).forEach(collect) }
  collect(container)
  const field = all.find(child => child.className === 'viz-field')
  assert.ok(field, 'typed input missing')
  const typed = all.find(child => child.className === 'viz-typed')
  const apply = all.find(child => child.className === 'viz-apply')
  assert.ok(typed && apply)
  controller.go(2)
  typed.value = 'abcab'
  apply.onclick()
  assert.equal(controller.index, 0)
  assert.equal(controller.frame().view.text, 'abcab')
  assert.equal(controller.total, VISUALIZERS['10'].build({ text: 'abcab' }).frames.length)
  const presetSelect = all.find(child => child.className === 'viz-preset')
  assert.equal(presetSelect.value, '-1')
  presetSelect.onchange()
  controller.destroy()
  delete globalThis.document
})

test('every frame of every visualizer renders into an SVG without throwing', () => {
  globalThis.document = { createElement: makeElement, createElementNS: (_, tag) => makeElement(tag) }
  globalThis.matchMedia = () => ({ matches: false })
  const views = []
  for (const key of Object.keys(VISUALIZERS)) {
    views.push([key, VISUALIZERS[key]])
    for (const [extraId, extra] of Object.entries(VISUALIZERS[key].extra ?? {})) views.push([key + '/' + extraId, extra])
  }
  for (const [name, hit] of views) {
    hit.presets.forEach((preset, presetIndex) => {
      for (const frame of buildFrames(hit, presetIndex).frames) {
        const stage = makeElement('svg')
        const size = hit.render(stage, frame, { width: 400, hit })
        assert.ok(size.width > 0 && size.height > 0, name + ' rendered an empty stage')
        assert.ok(stage.children.length > 0, name + ' rendered no shapes')
        if (hit.extraRender) hit.extraRender(makeElement('svg'), frame, { width: 400, hit })
      }
    })
  }
  delete globalThis.document
})