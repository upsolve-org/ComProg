// Single source of truth for the UPsolve palette used by the SVG visualizers.
export const SVG_NS = 'http://www.w3.org/2000/svg'

// Deterministic recorder: every generator pushes a frame; playback time is separate.
export class Frames {
  constructor() { this.list = [] }
  push(frame) {
    this.list.push({ vars: {}, explain: '', ...frame })
    return this.list.length - 1
  }
  get length() { return this.list.length }
}

export function splitNumbers(text) {
  return String(text ?? '').trim().split(/[\s,]+/).filter(Boolean).map(Number)
}

export function clampPreset(list, index) {
  if (!list?.length) return 0
  return Math.min(Math.max(0, Number.isInteger(index) ? index : 0), list.length - 1)
}

export function formatVars(vars) {
  return Object.entries(vars || {})
    .filter(([, value]) => value !== undefined)
    .map(([key, value]) => key + '=' + (Array.isArray(value) ? '[' + value.join(', ') + ']' : String(value)))
}

// Playback intervals per speed preset. 0.5x, 1x, 2x as required.
export const SPEEDS = [
  { id: '0.5', label: '0.5×', ms: 1600 },
  { id: '1', label: '1×', ms: 800 },
  { id: '2', label: '2×', ms: 400 }
]

export function speedOf(id) {
  return (SPEEDS.find(speed => speed.id === String(id)) ?? SPEEDS[1]).ms
}

export function svg(tag, attrs = {}, text) {
  const element = document.createElementNS(SVG_NS, tag)
  for (const [key, value] of Object.entries(attrs)) element.setAttribute(String(key), String(value))
  if (text !== undefined) element.textContent = text
  return element
}

// Rectangle-with-centred-text primitive used by arrays, grids and trees.
export function cell(g, x, y, w, h, text, className) {
  const group = svg('g', { class: 'viz-cell' + (className ? ' ' + className : '') })
  group.append(
    svg('rect', { x, y, width: w, height: h, class: 'viz-rect' }),
    svg('text', { x: x + w / 2, y: y + h / 2, class: 'viz-text', 'text-anchor': 'middle', 'dominant-baseline': 'central' }, String(text))
  )
  g.append(group)
}

export function label(g, x, y, text, className) {
  g.append(svg('text', { x, y, class: 'viz-label' + (className ? ' ' + className : ''), 'text-anchor': 'middle' }, String(text)))
}

// A frame's view: cell specs plus optional side data, read by the renderer.
export function viewFrame(view, frame) {
  return { specs: view, ...frame }
}

// Draw cell specs shared by most visualizers. `specs` entries are `{ v, i }`.
export function drawArray(g, specs, frame, { predicate = false, stride = 38, top = 22, height = 38, gap = 6 } = {}) {
  const live = frame.live
  specs.forEach((spec, index) => {
    let cls = 'viz-cell'
    if (frame.discarded?.includes(index)) cls += ' is-dim'
    if (live && live.l !== undefined && live.r !== undefined && index >= live.l && index <= live.r) cls += ' is-window'
    if (live && live.lo !== undefined && live.hi !== undefined && (index < live.lo || index > live.hi)) cls += ' is-dim'
    if (frame.found === index) cls += ' is-good'
    if (frame.active === index) cls += ' is-active'
    if (frame.dropped === index) cls += ' is-bad'
    cell(g, index * stride, top, stride - gap, height, spec.v, cls)
    if (predicate) label(g, index * stride + (stride - gap) / 2, top + height + 20, (frame.belief ?? [])[index] ?? '', (frame.belief ?? [])[index] === 'T' ? 'is-good' : 'is-bad')
    else label(g, index * stride + (stride - gap) / 2, top + height + 20, spec.i, 'is-muted')
  })
  if (live) {
    for (const [name, index] of [['lo', live.lo], ['mid', live.mid], ['hi', live.hi]]) {
      if (index !== undefined) label(g, index * stride + (stride - gap) / 2, top + height + 36, name, 'is-bright')
    }
  }
}

export const PRESETS = {
  range: [
    { text: '3 1 4 1 5', queries: [[0, 2], [1, 3], [2, 4]] },
    { text: '2 -1 4 -3', queries: [[0, 3], [2, 3], [1, 2]] }
  ],
  binary: [{ kind: 'first' }, { kind: 'any' }, { kind: 'none' }, { kind: 'all' }],
  window: [{ budget: 5 }, { budget: 8 }],
  greedy: [
    { events: [{ name: 'A', s: 1, e: 6 }, { name: 'B', s: 2, e: 3 }, { name: 'C', s: 3, e: 5 }, { name: 'D', s: 5, e: 7 }, { name: 'E', s: 7, e: 9 }] },
    { events: [{ name: 'A', s: 0, e: 9 }, { name: 'B', s: 1, e: 2 }, { name: 'C', s: 2, e: 4 }, { name: 'D', s: 4, e: 6 }, { name: 'E', s: 6, e: 7 }] }
  ],
  dsu: [{ n: 6 }, { n: 9, pairs: [[2, 3], [3, 4], [1, 2], [5, 6], [6, 7], [1, 8]] }],
  knapsack: [
    { weights: [2, 3, 4, 5], values: [3, 4, 5, 7], capacity: 5 },
    { weights: [1, 3, 4, 5], values: [1, 4, 5, 7], capacity: 7 }
  ],
  grid: [{ grid: [[0, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 0]] }, { grid: Array.from({ length: 4 }, () => [0, 0, 0, 0]) }],
  graphs: [{ mode: 'dijkstra' }, { mode: 'bfs' }],
  tree: [{ parents: [1, 1, 2, 2, 3, 3] }, { parents: [1, 2, 3, 4, 5, 6] }],
  sieve: [{ n: 30 }, { n: 45 }],
  kmp: [{ text: 'ababaca' }, { text: 'aabaabaaa' }],
  nim: [{ piles: [1, 2, 3] }, { piles: [2, 3, 5] }, { piles: [3, 3, 5, 5] }],
  parallel: [
    { agents: [4, 6], evidence: [5, 3], b: 2 },
    { agents: [5, 8, 8], evidence: [2], b: 3 }
  ]
}

export const presetLabels = {
  range: preset => preset.text,
  binary: (_, index) => ['first ≥ 5', 'find a 4', 'none ≥ 10', 'all ≤ 9'][index],
  window: preset => 'sum ≤ ' + preset.budget,
  greedy: (_, index) => (index ? 'long first event' : 'overlapping events'),
  dsu: preset => 'n = ' + preset.n,
  knapsack: preset => 'W = ' + preset.capacity,
  grid: (_, index) => (index ? 'open grid' : 'wall in the middle'),
  graphs: preset => (preset.mode === 'bfs' ? 'BFS layers' : 'Dijkstra'),
  tree: (_, index) => (index ? 'chain tree' : 'branching tree'),
  sieve: preset => 'n = ' + preset.n,
  kmp: preset => '"' + preset.text + '"',
  nim: preset => preset.piles.join(' '),
  parallel: preset => preset.agents.length + ' detective(s)'
}

export default { SVG_NS, Frames, splitNumbers, clampPreset, formatVars, SPEEDS, speedOf, svg, cell, label, viewFrame, drawArray, PRESETS, presetLabels }

// ---- 01 prefix sums ----

// Half-open windows (at most 6 values, each 0..3) so the pair queries always stay in range.
export function parseRange(text) {
  const raw = splitNumbers(text)
  if (!raw.length || raw.length > 6 || raw.some(value => value < 0 || value > 3)) return undefined
  const queries = []
  for (let index = 0; index + 1 < raw.length && queries.length < 3; index += 2) {
    queries.push([raw[index], Math.min(raw.length - 1, raw[index + 1])])
  }
  return { text: raw.join(' '), queries }
}

export function buildRange(preset) {
  const frames = new Frames()
  const values = preset.text.split(/\s+/).filter(Boolean).map(Number)
  const view = { values }
  frames.push({ view, explain: 'Start from the array; a separate prefix table will answer every range sum.' })
  const base = values.map((v, i) => ({ v, i }))
  const pref = new Array(values.length + 1).fill(0)
  for (let i = 0; i < values.length; i++) {
    pref[i + 1] = pref[i] + values[i]
    frames.push({ view, explain: 'pref[' + (i + 1) + '] = pref[' + i + '] + ' + values[i] + ' = ' + pref[i + 1] + '.', pref: pref.slice(), at: i })
  }
  for (const [lo, hi] of preset.queries) {
    frames.push({ view, pref: pref.slice(), query: [lo, hi], explain: 'Range [' + lo + ', ' + hi + '] = pref[' + (hi + 1) + '] − pref[' + lo + ']: subtract the prefix before L from the prefix through R.' })
    frames.push({ view, pref: pref.slice(), query: [lo, hi], answer: pref[hi + 1] - pref[lo], explain: 'Two lookups give ' + pref[hi + 1] + ' − ' + pref[lo] + ' = ' + (pref[hi + 1] - pref[lo]) + '.' })
  }
  void base
  return { frames: frames.list, summary: 'Each query cost two lookups.' }
}

export function renderRange(g, frame) {
  const values = frame.view.values
  const stride = 40
  const pref = frame.pref
  values.forEach((value, index) => {
    let cls = ''
    if (frame.at === index) cls = 'is-active'
    if (frame.query && index >= frame.query[0] && index <= frame.query[1]) cls = 'is-window'
    cell(g, index * stride, 22, stride - 6, 36, value, cls)
    label(g, index * stride + (stride - 6) / 2, 72, index, 'is-muted')
  })
  if (pref) {
    pref.forEach((value, index) => cell(g, index * stride, 96, stride - 6, 34, value, 'is-alt'))
    label(g, 2, 88, 'pref', 'is-left is-muted')
  }
  if (frame.query) {
    const [lo, hi] = frame.query
    g.append(svg('rect', { x: lo * stride - 2, y: 92, width: (hi - lo) * stride + stride + 2, height: 42, class: 'viz-outline' }))
    label(g, (lo * stride + (hi + 1) * stride) / 2, 152, frame.answer === undefined ? 'L … R' : '= ' + frame.answer, frame.answer === undefined ? 'is-muted' : 'is-bright')
  }
  return { width: (values.length + 1) * stride, height: 164 }
}

// ---- 01b difference array ----
export function buildDiff(preset) {
  const start = preset.text.split(/\s+/).filter(Boolean).map(Number)
  const frames = new Frames()
  const view = { start }
  const diff = new Array(start.length + 1).fill(0)
  frames.push({ view, diff: diff.slice(), explain: 'A difference array records only where values change.' })
  for (const [lo, hi, amount] of preset.queries.map(([lo, hi]) => [lo, hi, 1 + lo])) {
    diff[lo] += amount
    frames.push({ view, diff: diff.slice(), edge: lo, explain: 'Range add at ' + lo + ': +' + amount + ' — the start of every position in [L, R] rises.' })
    diff[hi + 1] -= amount
    frames.push({ view, diff: diff.slice(), edge: hi + 1, explain: 'Cancel after R: diff[' + (hi + 1) + '] -= ' + amount + '. Each update is two writes.' })
  }
  const result = []
  let running = 0
  for (let index = 0; index < start.length; index++) {
    running += diff[index]
    result.push(start[index] + running)
    frames.push({ view, diff: diff.slice(), running: running.slice ? running : running, sweep: index, result: result.slice(), explain: 'Sweep: running Δ = ' + running + ', so position ' + index + ' = ' + result[index] + '.' })
  }
  return { frames: frames.list, summary: 'final ' + result.join(' ') }
}

export function renderDiff(g, frame) {
  const values = frame.view.start
  const stride = 40
  values.forEach((value, index) => cell(g, index * stride, 22, stride - 6, 36, value, frame.sweep >= index ? 'is-good' : ''))
  frame.diff.forEach((value, index) => {
    if (index >= values.length) return
    cell(g, index * stride, 84, stride - 6, 32, value, frame.edge === index ? 'is-active' : 'is-alt')
  })
  if (frame.result) frame.result.forEach((value, index) => label(g, index * stride + (stride - 6) / 2, 140, value, 'is-bright'))
  label(g, 2, 76, 'diff', 'is-left is-muted')
  return { width: (values.length + 1) * stride, height: 150 }
}

// ---- 02 binary search ----
const BINARY_TEXT = Array.from({ length: 10 }, (_, i) => (1 + i) * 7)

// The array is constant; only what the predicate checks changes with the preset.
const BINARY_VALUES = BINARY_TEXT.map((value, index) => ({ v: value, i: index }))

export function binaryBelief(kind) {
  return BINARY_VALUES.map(({ i }) => (kind === 'none' ? 'F' : kind === 'all' ? 'T' : i >= 5 ? 'T' : 'F'))
}

export function buildBinary(preset) {
  const frames = new Frames()
  const view = { values: BINARY_VALUES, belief: binaryBelief(preset.kind) }
  const pred = index => preset.kind === 'none' ? false : preset.kind === 'all' ? true : index >= 5
  let lo = 0
  let hi = BINARY_TEXT.length - 1
  frames.push({ view, live: { lo, hi }, explain: 'Predicate ' + binaryBelief(preset.kind).join(' ') + '. Each probe halves the live window.' })
  for (let spins = 0; spins < 12 && lo <= hi; spins++) {
    const mid = (lo + hi) >> 1
    frames.push({ view, live: { lo, hi }, mid, active: mid, explain: 'mid = ' + mid + ' between lo = ' + lo + ' and hi = ' + hi + '.' })
    const truth = pred(mid)
    // For 'all' the boundary sits before index 0; for 'none' it sits past the end.
    const goLeft = preset.kind === 'all' ? true : preset.kind === 'none' ? false : truth
    if (goLeft) {
      frames.push({ view, live: { lo, hi }, mid, active: mid, discarded: Array.from({ length: hi - mid + 1 }, (_, i) => mid + i), explain: (truth ? 'pass' : 'fail') + ': the answer is at ' + mid + ' or to its left, so hi = ' + (mid - 1) + '.' })
      hi = mid - 1
    } else {
      frames.push({ view, live: { lo, hi }, mid, active: mid, discarded: Array.from({ length: mid - lo + 1 }, (_, i) => lo + i), explain: 'fail: the answer is right of ' + mid + ', so lo = ' + (mid + 1) + '.' })
      lo = mid + 1
    }
  }
  const found = lo < BINARY_TEXT.length && pred(lo) ? lo : undefined
  frames.push({ view, live: { lo, hi }, found, explain: found === undefined ? 'lo passed hi, so no value meets the predicate.' : 'lo = hi + 1 = ' + found + ': the first true index, found in ⌈log₂ 10⌉ probes.' })
  return { frames: frames.list, summary: found === undefined ? 'answer: none' : 'answer: index ' + found }
}

export function renderBinary(g, frame) {
  const stride = Math.max(22, Math.min(38, Math.floor(430 / BINARY_TEXT.length)))
  drawArray(g, frame.view.values, frame, { predicate: true, stride, belief: frame.view.belief })
  return { width: BINARY_TEXT.length * stride, height: 112 }
}

// ---- 03 sliding window ----
const WINDOW_VALUES = [2, 1, 3, 2, 4, 1, 3]

// A budget followed by up to 9 values (each 1..9); the first number is the budget.
export function parseWindow(text) {
  const raw = splitNumbers(text)
  if (raw.length < 3 || raw.length > 10) return undefined
  const budget = raw[0]
  if (!(budget > 0) || raw.slice(1).some(value => value < 1 || value > 9)) return undefined
  return { budget, values: raw.slice(1) }
}

export function buildWindow(preset) {
  const frames = new Frames()
  const values = preset.values ?? WINDOW_VALUES
  const view = { values }
  let l = 0
  let sum = 0
  let best = 0
  frames.push({ view, live: { l, r: 0 }, vars: { L: 0, R: 0, sum: 0, best: 0 }, explain: 'Find the longest window whose sum stays ≤ ' + preset.budget + '.' })
  for (let r = 0; r < values.length; r++) {
    sum += values[r]
    frames.push({ view, live: { l, r }, vars: { L: l, R: r, sum, best }, explain: 'Expand R to ' + r + ': add ' + values[r] + ', window sum = ' + sum + '.' })
    while (sum > preset.budget && l <= r) {
      const dropped = values[l]
      sum -= dropped
      frames.push({ view, live: { l, r }, dropped: l, vars: { L: l, R: r, sum, best }, explain: sum > preset.budget ? 'Sum ' + (sum + dropped) + ' exceeds ' + preset.budget + ': drop ' + dropped + ' and advance L.' : 'Shrink from the left until the sum fits.' })
      l++
    }
    if (r - l + 1 > best) {
      best = r - l + 1
      frames.push({ view, live: { l, r }, vars: { L: l, R: r, sum, best }, explain: 'Window [' + l + ', ' + r + '] fits; best length rises to ' + best + '.' })
    }
  }
  frames.push({ view, live: { l, r: values.length - 1 }, vars: { L: l, R: values.length - 1, sum, best }, explain: 'L and R each advanced at most n times, so the scan is O(n).' })
  return { frames: frames.list, summary: 'best length ' + best }
}

export function renderWindow(g, frame) {
  const values = frame.view.values
  const stride = Math.max(30, Math.min(42, Math.floor(420 / Math.max(1, values.length))))
  drawArray(g, values.map((v, i) => ({ v, i })), frame, { stride, top: 24 })
  return { width: values.length * stride, height: 112 }
}

// ---- 04 interval scheduling ----
export function buildGreedy(preset) {
  const frames = new Frames()
  const events = preset.events
  const view = { events }
  const accepted = []
  const rejected = []
  let last = -1
  frames.push({ view, explain: 'Sort by finish time so each pick frees the most room afterwards.' })
  for (const event of events) {
    if (event.s >= last) {
      accepted.push(event.name)
      last = event.e
      frames.push({ view, accepted: accepted.slice(), rejected: rejected.slice(), explain: event.name + ' starts at ' + event.s + ', ≥ the last finish ' + (last === event.e ? event.s : last) + ': accept it.' })
    } else {
      rejected.push(event.name)
      frames.push({ view, accepted: accepted.slice(), rejected: rejected.slice(), explain: event.name + ' starts at ' + event.s + ', before the last finish ' + last + ': it overlaps, so reject it.' })
    }
  }
  frames.push({ view, accepted: accepted.slice(), rejected: rejected.slice(), explain: 'Done: ' + accepted.length + ' compatible events, more than any other first pick allows.' })
  return { frames: frames.list, summary: accepted.length + ' accepted' }
}

// Events are sorted by finish time in the preset, so the display stays stable.
// One event per line: `name start end` (sorted by end, then start).
export function parseGreedy(text) {
  const events = String(text ?? '').split(/\n|;/).map((line, index) => {
    const [name, start, end] = line.trim().split(/[\s,]+/)
    if (start === undefined || end === undefined) return undefined
    const s = Number(start)
    const e = Number(end)
    if (!Number.isFinite(s) || !Number.isFinite(e) || e < s) return undefined
    return { name: (name || String.fromCharCode(65 + index)).slice(0, 4), s, e }
  }).filter(Boolean).slice(0, 6)
  if (events.length < 2) return undefined
  return { events: events.sort((a, b) => a.e - b.e || a.s - b.s) }
}

export function renderGreedy(g, frame) {
  const events = frame.view.events
  const row = 44
  const maxEnd = Math.max(...events.map(event => event.e)) + 1
  const trackLength = 420
  events.forEach((event, index) => {
    const y = index * row + 10
    const ok = frame.accepted?.includes(event.name)
    const bad = frame.rejected?.includes(event.name)
    cell(g, 0, y, 26, 26, event.name, ok ? 'is-good' : bad ? 'is-bad' : '')
    const x1 = 44 + (event.s / maxEnd) * trackLength
    const x2 = 44 + (event.e / maxEnd) * trackLength
    g.append(svg('rect', { x: x1, y: y + 6, width: Math.max(3, x2 - x1), height: 14, class: 'viz-bar' + (ok ? ' is-good' : bad ? ' is-bad' : '') }))
    label(g, 36, y + 18, event.s, 'is-muted is-right')
    label(g, x2 + 8, y + 18, 'end ' + event.e, 'is-muted is-left')
  })
  return { width: 44 + trackLength + 70, height: events.length * row + 12 }
}

// ---- 05 union-find ----
// Reads `n: a,b c,d ...`; unions are ignored when they name a vertex above n.
export function parseDsu(text) {
  const [n, ...rest] = String(text ?? '').match(/\d+/g)?.map(Number) ?? []
  if (!n || n < 2 || n > 12) return undefined
  const pairs = []
  for (let index = 0; index + 1 < rest.length; index += 2) {
    if (rest[index] >= 1 && rest[index] <= n && rest[index + 1] >= 1 && rest[index + 1] <= n) pairs.push([rest[index], rest[index + 1]])
  }
  return { n, pairs }
}

export function buildDsu(preset) {
  const n = preset.n
  const frames = new Frames()
  const parent = Array.from({ length: n + 1 }, (_, i) => i)
  const size = new Array(n + 1).fill(1)
  const view = { nodes: Array.from({ length: n }, (_, i) => i + 1) }
  const pairs = preset.pairs ?? [[2, 3], [3, 4], [1, 2], [5, 6]]
  frames.push({ view, parent: parent.slice(), size: size.slice(), explain: 'Every element is its own root; size tracks set membership.' })
  const find = start => {
    let x = start
    while (parent[x] !== x) {
      frames.push({ view, parent: parent.slice(), size: size.slice(), at: x, explain: 'parent[' + x + '] = ' + parent[x] + ', so climb from ' + x + '.' })
      x = parent[x]
    }
    let y = start
    while (parent[y] !== y) {
      const next = parent[y]
      parent[y] = x
      frames.push({ view, parent: parent.slice(), size: size.slice(), compress: y, root: x, explain: 'Path compression points ' + y + ' directly at root ' + x + '.' })
      y = next
    }
    return x
  }
  for (const [a, b] of pairs) {
    frames.push({ view, parent: parent.slice(), size: size.slice(), link: [a, b], explain: 'union(' + a + ', ' + b + '): find both roots first.' })
    const ra = find(a)
    const rb = find(b)
    if (ra === rb) {
      frames.push({ view, parent: parent.slice(), size: size.slice(), root: ra, explain: a + ' and ' + b + ' already share root ' + ra + '.' })
      continue
    }
    const [small, big] = size[ra] <= size[rb] ? [ra, rb] : [rb, ra]
    parent[small] = big
    size[big] += size[small]
    frames.push({ view, parent: parent.slice(), size: size.slice(), root: big, at: small, explain: 'Union by size: hang the smaller root ' + small + ' under ' + big + ' (size ' + size[big] + ').' })
  }
  frames.push({ view, parent: parent.slice(), size: size.slice(), explain: 'Compressed trees make later finds near constant: O(α(n)) amortised.' })
  const roots = new Set(Array.from({ length: n }, (_, i) => find(i + 1)))
  return { frames: frames.list, summary: roots.size + ' component(s)' }
}

export function renderDsu(g, frame) {
  const nodes = frame.view.nodes
  const stride = Math.min(46, Math.floor(420 / nodes.length))
  nodes.forEach((node, index) => {
    const root = frame.parent?.[node] === node
    let cls = root ? 'is-good' : ''
    if (frame.at === node) cls += ' is-active'
    if (frame.compress === node) cls += ' is-bright'
    cell(g, index * stride, 20, stride - 6, 32, node, cls)
    label(g, index * stride + (stride - 6) / 2, 70, 'p=' + (frame.parent?.[node] ?? node), 'is-muted')
  })
  return { width: nodes.length * stride, height: 84 }
}

// ---- 06 0/1 knapsack ----
// The first line is `values: ...`, the second `weights: ...`; the maximum weight acts as the capacity.
export function parseKnapsack(text) {
  const pick = key => String(text ?? '').match(new RegExp(key + '\\s*:\\s*([\\d\\s,]+)', 'i'))?.[1]
  const values = splitNumbers(pick('values'))
  const weights = splitNumbers(pick('weights'))
  if (values.length < 2 || weights.length < 2 || values.length > 5 || weights.length > 5) return undefined
  const count = Math.min(values.length, weights.length)
  const capacity = Math.max(...weights.slice(0, count))
  return { weights: weights.slice(0, count), values: values.slice(0, count), capacity }
}

export function buildKnapsack(preset) {
  const { weights, values, capacity } = preset
  const frames = new Frames()
  const view = { weights, values, capacity }
  const reachable = []
  let best = 0
  frames.push({ view, reachable: [], item: -1, explain: 'Sweep weights backwards so each item is used at most once.' })
  for (let item = 0; item < weights.length; item++) {
    for (let w = capacity; w >= weights[item]; w--) {
      const before = w === weights[item] ? 0 : (reachable[w - weights[item]] ?? -1)
      const take = before >= 0 ? before + values[item] : -1
      const keep = reachable[w] ?? -1
      if (take > keep) {
        reachable[w] = take
        best = Math.max(best, take)
        frames.push({ view, reachable: reachable.slice(), item, at: w, from: w - weights[item], explain: 'Item ' + (item + 1) + ' (w ' + weights[item] + ', v ' + values[item] + ') improves dp[' + w + '] to ' + take + '.' })
      } else {
        frames.push({ view, reachable: reachable.slice(), item, at: w, from: w - weights[item], skip: true, explain: 'Taking item ' + (item + 1) + ' at ' + w + ' gives ' + take + ', no better than ' + (keep < 0 ? 'empty' : keep) + '; keep it.' })
      }
    }
  }
  frames.push({ view, reachable: reachable.slice(), item: weights.length, explain: 'Backward sweeps keep dp 1D: best value ' + best + '.' })
  return { frames: frames.list, summary: 'best value ' + best }
}

export function renderKnapsack(g, frame) {
  const { weights, values, capacity } = frame.view
  const stride = Math.min(48, Math.floor(430 / (capacity + 1)))
  for (let w = 0; w <= capacity; w++) {
    let cls = ''
    if (frame.at === w) cls += ' is-active'
    if (frame.from === w) cls += ' is-bright'
    cell(g, w * stride, 34, stride - 6, 32, frame.reachable?.[w] ?? (frame.reachable ? '·' : ''), cls)
    label(g, w * stride + (stride - 6) / 2, 24, w, 'is-muted')
  }
  label(g, -14, 20, 'i', 'is-muted is-left')
  label(g, -14, 52, 'dp', 'is-muted is-left')
  weights.forEach((weight, index) => label(g, 20 + index * 90, 86, 'item ' + (index + 1) + ': w' + weight + ' v' + values[index], 'is-muted is-left'))
  const items = 20 + (weights.length - 1) * 90 + 66
  return { width: Math.max((capacity + 1) * stride + 6, items), height: 96 }
}

// ---- 06b grid DP paths ----
export function buildGrid(preset) {
  const grid = preset.grid
  const rows = grid.length
  const cols = grid[0].length
  const frames = new Frames()
  const view = { grid }
  const dp = Array.from({ length: rows }, () => new Array(cols).fill(0))
  frames.push({ view, dp: dp.map(row => row.slice()), cell: null, explain: 'Count paths right/down; each open cell adds the cell above and to its left.' })
  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      if (grid[r][c]) {
        frames.push({ view, dp: dp.map(row => row.slice()), cell: [r, c], explain: '(' + r + ', ' + c + ') is a wall: dp stays 0.' })
        continue
      }
      const up = r > 0 ? dp[r - 1][c] : 0
      const left = c > 0 ? dp[r][c - 1] : 0
      dp[r][c] = r === 0 && c === 0 ? 1 : up + left
      frames.push({ view, dp: dp.map(row => row.slice()), cell: [r, c], parents: [...(r > 0 ? [[r - 1, c]] : []), ...(c > 0 ? [[r, c - 1]] : [])], explain: r === 0 && c === 0 ? 'Start cell: one path to stand here.' : 'Above (' + up + ') + left (' + left + ') = ' + dp[r][c] + ' paths into (' + r + ', ' + c + ').' })
    }
  }
  frames.push({ view, dp: dp.map(row => row.slice()), cell: null, explain: 'Bottom-right holds ' + dp[rows - 1][cols - 1] + ' paths.' })
  return { frames: frames.list, summary: dp[rows - 1][cols - 1] + ' paths' }
}

export function renderGrid(g, frame) {
  const grid = frame.view.grid
  const size = Math.min(54, Math.floor(300 / grid[0].length))
  grid.forEach((row, r) => row.forEach((wall, c) => {
    const cls = wall ? 'is-wall' : frame.cell?.[0] === r && frame.cell?.[1] === c ? 'is-active' : frame.parents?.some(([pr, pc]) => pr === r && pc === c) ? 'is-bright' : ''
    cell(g, c * size, r * size, size - 5, size - 5, wall ? '#' : frame.dp?.[r]?.[c] ?? '', cls)
  }))
  return { width: grid[0].length * size, height: grid.length * size }
}

// ---- 07 graph traversal ----
const GRAPH = {
  nodes: [[40, 40], [150, 22], [150, 92], [262, 52], [262, 120], [360, 80]],
  edges: [[0, 1, 4], [0, 2, 2], [1, 3, 5], [2, 3, 8], [2, 4, 3], [3, 5, 2], [4, 5, 6], [3, 4, 1]]
}
const INF = '∞'

function relaxable(edge, dist) {
  const [a, b, weight] = edge
  return dist[a] + weight < dist[b]
}

export function buildGraph(mode) {
  const frames = new Frames()
  const n = GRAPH.nodes.length
  const dist = new Array(n).fill(Infinity)
  const parent = new Array(n).fill(-1)
  dist[0] = 0
  frames.push({ explain: mode === 'bfs' ? 'BFS walks one layer at a time; every edge costs 1.' : 'Dijkstra finalises the closest unsettled node, then relaxes its edges.', vars: { source: 0 }, dist: dist.map(d => (d === Infinity ? INF : d)) })
  const settled = new Set()
  const queue = [0]
  while (queue.length) {
    if (mode === 'dijkstra') queue.sort((a, b) => dist[a] - dist[b])
    const current = queue.shift()
    if (settled.has(current)) continue
    settled.add(current)
    frames.push({ explain: mode === 'bfs' ? 'Dequeue ' + current + ': the next vertex in its layer.' : 'Pop the minimum from the priority queue: ' + current + ' has the smallest tentative distance, so it is final.', at: current, settled: [...settled], dist: dist.map(d => (d === Infinity ? INF : d)) })
    for (const [a, b, weight] of GRAPH.edges) {
      const other = a === current ? b : b === current ? a : -1
      if (other < 0) continue
      const cost = mode === 'bfs' ? 1 : weight
      if (settled.has(other)) {
        frames.push({ explain: 'Edge ' + current + '–' + other + ': ' + other + ' is already final.', at: current, edge: [current, other], settled: [...settled], dist: dist.map(d => (d === Infinity ? INF : d)) })
        continue
      }
      const candidate = dist[current] + cost
      if (candidate < dist[other]) {
        dist[other] = candidate
        parent[other] = current
        if (!queue.includes(other)) queue.push(other)
        frames.push({ explain: 'Relax ' + current + '–' + other + (mode === 'dijkstra' ? ' (weight ' + weight + ')' : '') + ': dist[' + other + '] = ' + candidate + '.' , at: other, edge: [current, other], settled: [...settled], dist: dist.map(d => (d === Infinity ? INF : d)) })
      } else {
        frames.push({ explain: 'Edge ' + current + '–' + other + ' gives ' + candidate + ', not better than ' + (dist[other] === Infinity ? INF : dist[other]) + '.', edge: [current, other], settled: [...settled], dist: dist.map(d => (d === Infinity ? INF : d)) })
      }
    }
  }
  frames.push({ explain: 'All reachable vertices settled; dist from source is final.', dist: dist.map(d => (d === Infinity ? INF : d)), settled: [...settled] })
  return { frames: frames.list, summary: 'every vertex reached' }
}

export function renderGraph(g, frame) {
  for (const [a, b] of frame.pendingEdges ?? []) void a
  for (const [a, b, weight] of GRAPH.edges) {
    const active = frame.edge && ((frame.edge[0] === a && frame.edge[1] === b) || (frame.edge[0] === b && frame.edge[1] === a))
    g.append(svg('line', { x1: GRAPH.nodes[a][0], y1: GRAPH.nodes[a][1], x2: GRAPH.nodes[b][0], y2: GRAPH.nodes[b][1], class: 'viz-edge' + (active ? ' is-active' : ''), 'stroke-width': active ? 3 : 1.5 }))
    label(g, (GRAPH.nodes[a][0] + GRAPH.nodes[b][0]) / 2, (GRAPH.nodes[a][1] + GRAPH.nodes[b][1]) / 2 - 3, weight, 'is-muted')
  }
  GRAPH.nodes.forEach(([x, y], index) => {
    const cls = frame.at === index ? 'is-active' : frame.settled?.includes(index) ? 'is-good' : ''
    g.append(svg('circle', { cx: x, cy: y, r: 15, class: 'viz-node' + (cls ? ' ' + cls : '') }))
    label(g, x, y + 4, index, cls === 'is-active' ? 'is-bright' : '')
    label(g, x, y + 30, frame.dist?.[index] ?? '', 'is-muted')
  })
  return { width: 400, height: 150 }
}

// ---- 08 Euler tour ----
const TREE_LAYOUT = {
  branch: { parent: [-1, 0, 0, 1, 1, 2, 2], pos: [[200, 20], [110, 66], [290, 66], [62, 112], [158, 112], [242, 112], [338, 112]] },
  chain: { parent: [-1, 0, 1, 2, 3, 4, 5], pos: [[40, 24], [92, 24], [144, 24], [196, 24], [248, 24], [300, 24], [352, 24]] }
}

// Parent lists up to 7 nodes, one 1-based index per node (node 0 is the root).
// A leading -1 is accepted, and a list starting at 0 already means "parent of node 1 is node 0".
export function parseTree(text) {
  const raw = String(text ?? '').trim().split(/[\s,]+/).filter(Boolean).map(value => Number(value === '-' ? -1 : value))
  if (raw.length < 3 || raw.length > 7 || raw.some(value => Number.isNaN(value))) return undefined
  const parent = (raw[0] === -1 ? raw : [-1, ...raw]).map(index => (index > 0 ? index - 1 : index))
  if (parent.some((p, node) => p < -1 || p === node || (p === -1 && node !== 0))) return undefined
  const depth = []
  parent.forEach((p, node) => depth.push(p < 0 ? 0 : depth[p] + 1))
  // Children sit in a slot of their own, so siblings never overlap; parents centre over them.
  const children = parent.map(() => [])
  parent.forEach((p, node) => { if (p >= 0) children[p].push(node) })
  const slot = []
  let leaves = 0
  const place = node => {
    if (!children[node].length) {
      slot[node] = leaves++
      return slot[node]
    }
    const mine = children[node].map(place)
    slot[node] = (mine[0] + mine.at(-1)) / 2
    return slot[node]
  }
  place(0)
  const pos = slot.map((value, node) => [28 + value * 56, 24 + depth[node] * 46])
  return { parent, pos, width: Math.max(140, leaves * 56 + 28) }
}

export function buildTree(preset) {
  const { parent, pos, width } = parseTree((preset.parents ?? preset.parent).join(' '))
  const frames = new Frames()
  const view = { pos, parent, width }
  const children = parent.map(() => [])
  parent.forEach((p, node) => { if (p >= 0) children[p].push(node) })
  const tin = new Array(parent.length).fill(-1)
  const tout = new Array(parent.length).fill(-1)
  let clock = 0
  const order = []
  const visit = node => {
    tin[node] = clock++
    order.push(node)
    frames.push({ view, tin: tin.slice(), tout: tout.slice(), order: order.slice(), at: node, explain: 'Enter ' + node + ': tin[' + node + '] = ' + tin[node] + '; timestamps march forward.' })
    for (const child of children[node]) visit(child)
    tout[node] = clock++
    frames.push({ view, tin: tin.slice(), tout: tout.slice(), order: order.slice(), at: node, explain: 'Leave ' + node + ': tout[' + node + '] = ' + tout[node] + '; its whole subtree sits between tin and tout.' })
  }
  visit(0)
  frames.push({ view, tin: tin.slice(), tout: tout.slice(), order: order.slice(), explain: 'Subtree of node 0 covers slots [tin 0, tout ' + tout[0] + ']; every subtree is one contiguous slice.' })
  return { frames: frames.list, summary: 'tout − tin encodes subtree size' }
}

export function renderTree(g, frame) {
  const { pos, parent } = frame.view
  parent.forEach((p, node) => {
    if (p < 0) return
    g.append(svg('line', { x1: pos[p][0], y1: pos[p][1], x2: pos[node][0], y2: pos[node][1], class: 'viz-edge', 'stroke-width': 1.5 }))
  })
  pos.forEach(([x, y], node) => {
    const cls = frame.at === node ? 'is-active' : frame.tout?.[node] !== undefined && frame.tout[node] >= 0 ? 'is-good' : ''
    g.append(svg('circle', { cx: x, cy: y, r: 14, class: 'viz-node' + (cls ? ' ' + cls : '') }))
    label(g, x, y + 4, node, 'is-bright')
    if (frame.tin?.[node] >= 0) label(g, x, y + 28, frame.tin[node] + '·' + (frame.tout[node] >= 0 ? frame.tout[node] : '…'), 'is-muted')
  })
  return { width: frame.view.width ?? 400, height: Math.max(...pos.map(([, y]) => y)) + 44 }
}

// The flattening is easier to read as the 1D slot array the tour writes.
export function renderTourSlots(g, frame) {
  const stride = 34
  frame.order.forEach((node, slot) => {
    const cls = frame.at === node && frame.tout[node] < 0 ? 'is-active' : frame.tout[node] >= 0 ? 'is-good' : 'is-alt'
    cell(g, slot * stride, 6, stride - 5, 30, node, cls)
    label(g, slot * stride + (stride - 5) / 2, 48, slot, 'is-muted')
  })
  return { width: Math.max(frame.order.length, 6) * stride, height: 56 }
}

// ---- 09 sieve ----
// A single limit from 6 to 60 keeps the grid readable.
export function parseSieve(text) {
  const n = parseInt(splitNumbers(text).at(-1), 10)
  return n >= 6 && n <= 60 ? { n } : undefined
}

export function buildSieve(preset) {
  const n = preset.n
  const frames = new Frames()
  const composite = new Array(n + 1).fill(false)
  frames.push({ n, composite: composite.slice(), explain: 'Cross out everything from p² upward; smaller multiples already have smaller prime factors.' })
  for (let p = 2; p * p <= n; p++) {
    if (composite[p]) {
      frames.push({ n, p, composite: composite.slice(), explain: p + ' is already crossed out, so skip it.' })
      continue
    }
    frames.push({ n, p, composite: composite.slice(), explain: p + ' is prime: start crossing at p² = ' + p * p + '.' })
    for (let multiple = p * p; multiple <= n; multiple += p) {
      composite[multiple] = true
      frames.push({ n, p, at: multiple, composite: composite.slice(), explain: 'Cross out ' + multiple + ' (' + p + ' × ' + multiple / p + ').' })
    }
  }
  const primes = []
  for (let value = 2; value <= n; value++) if (!composite[value]) primes.push(value)
  frames.push({ n, composite: composite.slice(), explain: primes.length + ' primes survive: the rest are composites.' })
  return { frames: frames.list, summary: primes.length + ' primes ≤ ' + n, primes }
}

export function renderSieve(g, frame) {
  const n = frame.n
  const columns = 10
  const size = Math.min(40, Math.floor(330 / columns))
  for (let value = 2; value <= n; value++) {
    const slot = value - 2
    const cls = frame.at === value ? 'is-active' : frame.composite[value] ? 'is-dim' : frame.p !== undefined ? 'is-good' : ''
    cell(g, (slot % columns) * size, Math.floor(slot / columns) * size, size - 5, size - 5, value, cls)
  }
  return { width: columns * size, height: Math.ceil((n - 1) / columns) * size }
}

// ---- 10 KMP prefix function ----
// Letters only, 2 to 12 characters.
export function parseKmp(text) {
  const value = String(text ?? '').toLowerCase().replace(/[^a-z]/g, '')
  return value.length >= 2 && value.length <= 12 ? { text: value } : undefined
}

export function buildKmp(preset) {
  const text = preset.text
  const n = text.length
  const frames = new Frames()
  const pi = new Array(n).fill(0)
  const view = { text }
  frames.push({ view, pi: pi.slice(), i: 0, explain: 'pi[i] = longest proper prefix of text[0..i] that is also its suffix.' })
  let k = 0
  for (let i = 1; i < n; i++) {
    frames.push({ view, pi: pi.slice(), i, k, explain: 'Compare text[' + i + '] = “' + text[i] + '” with text[' + k + '] = “' + text[k] + '”.' })
    while (k > 0 && text[i] !== text[k]) {
      frames.push({ view, pi: pi.slice(), i, k, fallback: k, explain: 'Mismatch: fall back to k = pi[' + (k - 1) + '] = ' + pi[k - 1] + '.' })
      k = pi[k - 1]
    }
    if (text[i] === text[k]) k++
    pi[i] = k
    frames.push({ view, pi: pi.slice(), i, k, explain: 'They match, so pi[' + i + '] = ' + k + '.' })
  }
  return { frames: frames.list, summary: 'no index revisits twice: O(n)' }
}

export function renderKmp(g, frame) {
  const text = frame.view.text
  const stride = Math.min(40, Math.floor(390 / text.length))
  text.split('').forEach((char, index) => {
    let cls = ''
    if (frame.i === index) cls = 'is-active'
    else if (frame.fallback !== undefined && index < frame.fallback) cls = 'is-bad'
    else if (index < frame.k) cls = 'is-good'
    cell(g, index * stride, 18, stride - 5, 34, char, cls)
    label(g, index * stride + (stride - 5) / 2, 68, frame.pi?.[index] ?? '', 'is-muted')
    label(g, index * stride + (stride - 5) / 2, 84, index, 'is-muted')
  })
  return { width: text.length * stride, height: 96 }
}

// ---- 11 Nim xor columns ----
// Up to six pile sizes, each 0 to 15; a zero pile is already an empty column and is kept.
// `agents: ...` and `evidence: ...`; the second line may be shorter and is reused cyclically.
export function parseParallel(text) {
  const pick = key => String(text ?? '').match(new RegExp(key + '\\s*:\\s*([\\d\\s,]+)', 'i'))?.[1]
  const agents = splitNumbers(pick('agents'))
  const evidence = splitNumbers(pick('evidence'))
  if (agents.length < 1 || agents.length > 4 || evidence.length < 1) return undefined
  if (agents.some(a => !(a > 0 && a <= 99)) || evidence.some(e => !(e > 0 && e <= 9))) return undefined
  return { agents, evidence, b: agents.length }
}

// A piece that takes `e` cycles finishes at multiples of `e`, so by time `t` piece `i` is done
// floor(t / e_i) times. Real pieces cap that repeating calendar, so each detective stops at `|evidence|`.
export function piecesDone(agents, evidence, t) {
  return agents.reduce((sum, _, index) =>
    sum + Math.min(Math.floor(t / evidence[index % evidence.length]), evidence.length), 0)
}

// Smallest time at which all pieces are done. Monotone in `t`, which is exactly why binary search works.
export function earliestFinish(agents, evidence) {
  let t = 0
  while (piecesDone(agents, evidence, t) < agents.length && t < 100000) t += 1
  return t
}

export function buildParallel(preset) {
  const { agents, evidence, b } = preset
  const frames = new Frames()
  const finish = earliestFinish(agents, evidence)
  frames.push({ view: { agents, evidence, t: 0 }, vars: { t: 0, found: 0, need: b }, explain: 'Time 0: every detective starts its first piece at once.' })
  for (let time = 1; time <= finish; time++) {
    const done = Math.min(piecesDone(agents, evidence, time), b)
    frames.push({ view: { agents, evidence, t: time }, vars: { t: time, found: done, need: b }, explain: 'Time ' + time + ': ' + done + ' of ' + b + ' pieces found.' })
  }
  frames.push({ view: { agents, evidence, t: finish }, vars: { t: finish, found: b, need: b }, explain: 'Time ' + finish + ' finishes the last piece: the "done by t" check only flips once, so binary search finds ' + finish + ' in a few probes.' })
  return { frames: frames.list, summary: 'finish at minute ' + finish }
}

export function renderParallel(g, frame) {
  const { agents, evidence, t } = frame.view
  const stride = 40
  agents.forEach((_, a) => {
    label(g, 30, a * 48 + 32, 'C' + (a + 1), 'is-muted is-right')
    for (let k = 0; k < 4; k++) {
      const need = evidence[k % evidence.length]
      const found = Math.min(3, Math.floor(t / need))
      cell(g, 40 + k * (stride * 3), a * 48 + 14, stride * 3 - 8, 32,
        (k < evidence.length ? '' : '↺ ') + (k + 1) + ': ' + Math.min(found, k < evidence.length ? 3 : 1) + ' · ' + need + 'u',
        found >= (k < evidence.length ? 3 : 1) ? 'is-good' : found > 0 ? 'is-alt' : '')
    }
  })
  return { width: 40 + 4 * stride * 3, height: agents.length * 48 + 6 }
}

export function parseNim(text) {
  const piles = splitNumbers(text).slice(0, 6)
  if (!piles.length || piles.some(pile => !(pile >= 0 && pile <= 15))) return undefined
  return { piles }
}

export function buildNim(preset) {
  const piles = preset.piles
  const frames = new Frames()
  const bits = Math.max(...piles).toString(2).length || 1
  const columns = Array.from({ length: bits }, (_, bit) => piles.map(pile => (pile >> bit) & 1))
  const xor = columns.reduce((total, column) => total + (column.reduce((sum, bit) => sum + bit, 0) % 2), 0)
  frames.push({ piles, bits, column: bits - 1, explain: 'Write the piles in binary and cancel pairs of 1s in each column.' })
  for (let bit = bits - 1; bit >= 0; bit--) {
    const ones = columns[bit].reduce((sum, value) => sum + value, 0)
    frames.push({ piles, bits, column: bit, odd: ones % 2 === 1, explain: 'Bit ' + bit + ': ' + ones + ' pile(s) have it set, so this column is ' + (ones % 2 ? 'odd (1)' : 'even (0)') + '.' })
  }
  const winning = piles.reduce((a, b) => a ^ b, 0) !== 0
  frames.push({ piles, bits, column: -1, winning, explain: winning ? 'XOR sum ≠ 0: the first player can win with a winning move.' : 'XOR sum = 0: every move breaks it, so the second player wins.' })
  return { frames: frames.list, summary: 'XOR ' + piles.map(pile => pile.toString(2)).join(' ⊕ ') + ' → ' + (winning ? 'First' : 'Second') }
}

export function renderNim(g, frame) {
  const stride = 34
  frame.piles.forEach((pile, row) => {
    const bits = Math.max(1, Math.ceil(frame.bits))
    for (let bit = bits - 1; bit >= 0; bit--) {
      const on = (pile >> bit) & 1
      const x = (bits - 1 - bit) * stride
      const col = frame.column === bit ? (on ? ' is-active' : ' is-dim') : ''
      cell(g, x, row * 30, stride - 5, 26, on, on ? 'is-one' + col : 'is-zero' + col)
    }
    label(g, bits * stride + 14, row * 30 + 18, '= ' + pile, 'is-muted is-left')
  })
  return { width: (Math.max(1, Math.ceil(frame.bits)) * stride) + 56, height: frame.piles.length * 30 + 12 }
}

// ---- registry: module id → visualizer ----
// `extra` may return extra renderers; every entry shares the same control contract.
export const VISUALIZERS = {
  '01': { title: 'Prefix sums: range query in O(1)', summary: 'Build the table once, then subtract two lookups per range.', presets: PRESETS.range, labels: presetLabels.range, build: buildRange, parse: parseRange, inputLabel: 'Array, then L R window pairs', render: renderRange, extra: { diff: { title: 'Difference array: range add then sweep', summary: 'Two writes per range update; one prefix sweep at the end.', presets: PRESETS.range, labels: presetLabels.range, build: buildDiff, parse: parseRange, render: renderDiff } } },
  '02': { title: 'Binary search halves the window', summary: 'Probe the middle, discard the half that cannot hold the boundary.', presets: PRESETS.binary, labels: presetLabels.binary, build: buildBinary, render: renderBinary },
  '03': { title: 'Sliding window with a sum budget', summary: 'Move R to grow the window, move L to shrink it back under budget.', presets: PRESETS.window, labels: presetLabels.window, build: buildWindow, parse: parseWindow, inputLabel: 'Budget, then the array', render: renderWindow },
  '04': { title: 'Interval scheduling by earliest finish', summary: 'Accept an event only when it starts after the last accepted end.', presets: PRESETS.greedy, labels: presetLabels.greedy, build: buildGreedy, parse: parseGreedy, inputLabel: 'One event per line: name start end', render: renderGreedy },
  '05': { title: 'Union-Find: find, size, compress', summary: 'Compress find paths and hang smaller sets under larger roots.', presets: PRESETS.dsu, labels: presetLabels.dsu, build: buildDsu, parse: parseDsu, inputLabel: 'n, then pairs a,b c,d', render: renderDsu },
  '06': { title: '0/1 Knapsack: backward 1D sweep', summary: 'Walk weights downward so each item enters at most one row.', presets: PRESETS.knapsack, labels: presetLabels.knapsack, build: buildKnapsack, parse: parseKnapsack, inputLabel: 'values: ... then weights: ...', render: renderKnapsack, extra: { grid: { title: 'Grid DP: count paths', summary: 'Each open cell adds the paths arriving from above and from the left.', presets: PRESETS.grid, labels: presetLabels.grid, build: buildGrid, render: renderGrid } } },
  '07': { title: 'BFS layers and Dijkstra relaxation', summary: 'Settle the closest node, then relax only cheaper edges.', presets: PRESETS.graphs, labels: presetLabels.graphs, build: preset => buildGraph(preset.mode), render: renderGraph },
  '08': { title: 'Euler tour flattens a subtree', summary: 'tin and tout bracket each subtree into one contiguous slot range.', presets: PRESETS.tree, labels: presetLabels.tree, build: buildTree, parse: parseTree, inputLabel: 'Parent of each node (-1 = root)', render: renderTree, extraRender: renderTourSlots },
  '09': { title: 'Sieve crosses out from p²', summary: 'Start at p squared; smaller multiples already have smaller primes.', presets: PRESETS.sieve, labels: presetLabels.sieve, build: buildSieve, parse: parseSieve, inputLabel: 'Limit 6-60', render: renderSieve },
  '10': { title: 'KMP prefix function', summary: 'On a mismatch, fall back to the border length instead of restarting.', presets: PRESETS.kmp, labels: presetLabels.kmp, build: buildKmp, parse: parseKmp, inputLabel: 'Text, letters only', render: renderKmp },
  '12': { title: 'Binary search on time: parallel work', summary: 'Each piece costs its detective a fixed time; binary search the finishing minute.', presets: PRESETS.parallel, labels: presetLabels.parallel, build: buildParallel, parse: parseParallel, inputLabel: 'agents: ... then evidence: ...', render: renderParallel },
  '11': { title: 'Nim: XOR-sum column cancellation', summary: 'Cancel pairs of set bits; an odd column means the first player wins.', presets: PRESETS.nim, labels: presetLabels.nim, build: buildNim, parse: parseNim, inputLabel: 'Pile sizes', render: renderNim }
}

// ---- dynamic API ----
export const ERROR_FRAME = { explain: 'That preset needs different input; showing the last valid step.', vars: {} }

// Parse a learner-typed preset, falling back to the stored preset when it is unusable.
export function parsePreset(hit, text, presetIndex = 0) {
  const preset = hit?.presets[presetIndex ?? 0]
  if (!hit?.parse) return preset
  try {
    const parsed = hit.parse(String(text ?? ''))
    return parsed ?? preset
  } catch {
    return preset
  }
}

export function buildFrames(visualizer, presetIndex = 0, value = '') {
  try {
    const frames = visualizer.build(parsePreset(visualizer, value, presetIndex), presetIndex)
    return { frames: Array.isArray(frames.frames) ? frames.frames : [], summary: frames.summary ?? '', index: 0 }
  } catch {
    return { frames: [{ ...ERROR_FRAME }], summary: '', index: 0 }
  }
}

export function stepBounds(index, total) {
  return { index: Math.min(Math.max(0, index), total - 1), atStart: index <= 0, atEnd: index >= total - 1 }
}

export function getFrame(frames, index) {
  return frames[stepBounds(index, frames.length).index]
}

const reducedMotion = () => globalThis.matchMedia?.('(prefers-reduced-motion: reduce)').matches ?? false

function button(text, className, description) {
  const element = document.createElement('button')
  element.type = 'button'
  element.className = className.startsWith('viz-') ? className : 'viz-btn ' + className
  element.textContent = text
  if (description) element.setAttribute('aria-label', description)
  return element
}

// Mount one visualizer into a container. Returns the controller used by tests and app.js.
export function mountVisualizer(container, hit, options = {}) {
  const picture = document.createElement('div')
  picture.className = 'viz-picture'
  const stage = document.createElement('div')
  stage.className = 'viz-stage'
  const frameSVG = svg('svg', { class: 'viz-svg', role: 'img', 'aria-label': hit.title })
  stage.append(frameSVG)
  const extraStage = document.createElement('div')
  extraStage.className = 'viz-stage viz-stage-extra'
  const extraSVG = svg('svg', { class: 'viz-svg', role: 'img', 'aria-label': hit.title + ' (slot view)' })
  extraStage.append(extraSVG)
  picture.append(stage, extraStage)

  const readout = document.createElement('dl')
  readout.className = 'viz-vars'
  readout.setAttribute('aria-live', 'polite')
  const explain = document.createElement('p')
  explain.className = 'viz-explain'
  explain.setAttribute('aria-live', 'polite')
  const progress = document.createElement('span')
  progress.className = 'viz-count'

  const controls = document.createElement('div')
  controls.className = 'viz-controls'
  controls.setAttribute('role', 'group')
  controls.setAttribute('aria-label', 'Playback controls')
  const first = button('⏮', 'viz-first', 'Start')
  const back = button('◀ Step', 'viz-back', 'Step back')
  const play = button('▶ Play', 'viz-play')
  const next = button('Step ▶', 'viz-next', 'Step forward')
  const reset = button('↺', 'viz-reset', 'Reset to the first step')
  play.setAttribute('aria-pressed', 'false')
  controls.append(first, back, play, next, reset)
  controls.append(progress)

  const timing = document.createElement('div')
  timing.className = 'viz-timing'
  timing.append(controls)

  const speed = document.createElement('select')
  speed.className = 'viz-speed'
  speed.setAttribute('aria-label', 'Speed')
  for (const preset of SPEEDS) {
    const option = document.createElement('option')
    option.value = preset.id
    option.textContent = preset.label
    speed.append(option)
  }
  speed.value = '1'

  const presetSelect = document.createElement('select')
  presetSelect.className = 'viz-preset'
  presetSelect.setAttribute('aria-label', 'Input preset')
  hit.presets.forEach((preset, index) => {
    const option = document.createElement('option')
    option.value = String(index)
    option.textContent = hit.labels(preset, index)
    presetSelect.append(option)
  })
  const custom = document.createElement('option')
  custom.value = '-1'
  custom.textContent = 'from the lesson input'
  presetSelect.append(custom)

  const inputs = document.createElement('div')
  inputs.className = 'viz-inputs'
  inputs.append(presetSelect, speed)

  const panel = document.createElement('div')
  panel.className = 'viz-panel'
  panel.append(explain, readout, timing)

  container.append(picture, ...(options.panelSiblings ?? []), panel)

  let typed
  if (hit.parse && hit.inputLabel) {
    const field = document.createElement('div')
    field.className = 'viz-field'
    const label = document.createElement('label')
    label.textContent = hit.inputLabel
    field.append(label)
    typed = document.createElement('input')
    typed.type = 'text'
    typed.className = 'viz-typed'
    typed.setAttribute('aria-label', hit.inputLabel)
    typed.setAttribute('autocomplete', 'off')
    typed.spellcheck = false
    label.htmlFor = typed.id = 'viz-typed-' + Math.random().toString(36).slice(2, 8)
    const apply = button('Update', 'viz-apply', 'Rebuild from the typed input')
    const applyTyped = () => {
      if (!typed.value.trim()) return
      presetSelect.value = '-1'
      restart(0, typed.value)
    }
    apply.onclick = applyTyped
    typed.onkeydown = event => {
      if (event.key !== 'Enter') return
      event.preventDefault()
      applyTyped()
    }
    field.append(typed, apply)
    panel.append(field)
  }
  container.append(inputs)

  const state = { presets: 0, index: 0, timer: 0, playing: false, value: options.value ?? '' }
  let result = { frames: [{ ...ERROR_FRAME }], summary: '' }

  function updateExplanation(frame) {
    explain.textContent = frame.explain
  }

  function draw() {
    for (const target of [frameSVG, extraSVG]) target.replaceChildren()
    const frame = result.frames[state.index] ?? result.frames.at(-1)
    const one = hit.render(frameSVG, frame, { width: 400, hit })
    frameSVG.setAttribute('viewBox', '0 0 ' + one.width + ' ' + one.height)
    frameSVG.setAttribute('width', String(one.width))
    frameSVG.style.aspectRatio = one.width + ' / ' + one.height
    const two = hit.extraRender && !options.primaryOnly ? hit.extraRender(extraSVG, frame, { width: 400, hit }) : undefined
    if (extraStage.isConnected) extraStage.hidden = !two
    if (two) {
      extraSVG.setAttribute('viewBox', '0 0 ' + two.width + ' ' + two.height)
      extraSVG.setAttribute('width', String(two.width))
      extraSVG.style.aspectRatio = two.width + ' / ' + two.height
    }
    updateExplanation(frame)
    readout.replaceChildren(...formatVars(frame.vars).flatMap(pair => {
      const [key, ...rest] = pair.split('=')
      const dt = document.createElement('dt')
      dt.textContent = key
      const dd = document.createElement('dd')
      dd.textContent = rest.join('=')
      return [dt, dd]
    }))
    progress.textContent = (state.index + 1) + ' / ' + result.frames.length + (result.summary ? ' · ' + result.summary : '')
    const bounds = stepBounds(state.index, result.frames.length)
    back.disabled = first.disabled = bounds.atStart
    next.disabled = bounds.atEnd
    if (bounds.atEnd && state.playing) stopTimer()
  }

  function restart(presetIndex = 0, value = '') {
    state.value = String(value ?? '')
    result = buildFrames(hit, presetIndex, state.value)
    state.index = 0
    stopTimer()
    draw()
  }

  function go(index) {
    stopTimer()
    state.index = stepBounds(index, result.frames.length).index
    draw()
  }

  function stopTimer() {
    state.playing = false
    clearTimeout(state.timer)
    play.setAttribute('aria-pressed', 'false')
    play.textContent = '▶ Play'
  }

  function tick() {
    if (!state.playing) return
    const bounds = stepBounds(state.index + 1, result.frames.length)
    state.index = bounds.index
    draw()
    if (bounds.atEnd) return
    state.timer = setTimeout(tick, reducedMotion() ? speedOf(speed.value) / 2 : speedOf(speed.value))
  }

  function togglePlay() {
    if (state.playing) return stopTimer()
    if (stepBounds(state.index, result.frames.length).atEnd) state.index = 0
    state.playing = true
    play.setAttribute('aria-pressed', 'true')
    play.textContent = '❚❚ Pause'
    tick()
  }

  first.onclick = () => go(0)
  back.onclick = () => go(state.index - 1)
  next.onclick = () => go(state.index + 1)
  reset.onclick = () => restart(Number(presetSelect.value), state.value)
  play.onclick = togglePlay
  speed.onchange = () => { if (state.playing) { clearTimeout(state.timer); tick() } }
  // A stored preset wins over whatever text is still in the box.
  presetSelect.onchange = () => {
    state.presets = Math.max(0, Number(presetSelect.value))
    restart(state.presets, '')
  }

  stage.insertAdjacentText('beforeend', '')
  for (const [key, target] of [['ArrowRight', next], ['ArrowLeft', back], ['Home', first], ['End', () => go(result.frames.length - 1)], [' ', play]]) {
    stage.addEventListener('keydown', event => {
      if (event.key !== key) return
      event.preventDefault()
      if (typeof target === 'function') target()
      else target.click()
    })
  }
  stage.tabIndex = 0
  stage.setAttribute('role', 'application')
  stage.setAttribute('aria-label', hit.title + ' (arrow keys step, space plays)')

  restart(0)
  return {
    state,
    go,
    play: togglePlay,
    restart,
    destroy: stopTimer,
    get index() { return state.index },
    get total() { return result.frames.length },
    frame: () => result.frames[state.index]
  }
}

// Chapter ids are folder names ("03_Two_Pointers…"), so accept the two-digit prefix too.
export function createVisualizer(moduleId, extraId) {
  const key = String(moduleId ?? '')
  const hit = VISUALIZERS[key] ?? VISUALIZERS[key.match(/^\d{2}/)?.[0]]
  if (!hit) return undefined
  if (!extraId) return hit
  return { ...hit, ...hit.extra?.[extraId], title: hit.extra?.[extraId]?.title ?? hit.title }
}

// HTML tag descriptors so app.js can mount both the primary and extra view.
export { ERROR_FRAME as ERROR_FRAME_EXPORT }