// Server-only inputs and oracles. A container sees one input at a time.
const pack = (values, header = values.length) => header + '\n' + values.join(' ')
const lines = (header, rows) => header + '\n' + rows.join('\n')
const gcd = (a, b) => b ? gcd(b, a % b) : a
const make = (input, expected, stress = false) => ({ input, expected: String(expected), stress })

const boundaries = [
  () => [make('1000000000 -999999999', 1), make('-43 42', -1)],
  () => [make('6\n-6 2 -1 3 -9 1', 4), make('4\n-10 -9 -12 -11', -9),
    make(pack(Array.from({ length: 1_000_000 }, (_, i) => i % 2 ? -1 : 2)), 500_001, true)],
  () => {
    const n = 200_000
    const values = Array.from({ length: n }, (_, i) => (i >> 1) * 2)
    const queries = Array.from({ length: n }, (_, i) => (i * 7919) % 202_001 - 1000)
    return [make('4 5\n-2 -2 0 7\n-3 -2 -1 7 8', '0\n0\n2\n3\n-1'),
      make(pack(values, n + ' ' + n) + '\n' + queries.join(' '),
        queries.map(x => x > values.at(-1) ? -1 : Math.max(0, Math.ceil(x / 2) * 2)).join('\n'), true)]
  },
  () => [make('5 1\n-5 8 3 8 -5', 8), make('4 3\n-2 -3 -4 1', -6),
    make(pack(Array.from({ length: 200_000 }, (_, i) => i % 2 ? -1 : 2), '200000 100000'), 50_000, true)],
  () => [make('4\n0 7\n1 2\n2 3\n3 4', 3), make('3\n-5 -2\n-3 0\n0 1', 2),
    make(lines(200_000, Array.from({ length: 200_000 }, (_, i) => [199999 - i, 200000 - i].join(' '))), 200_000, true)],
  () => [make('4 5\n1 1\n2 1\n1 2\n3 4\n2 4', '4\n3\n3\n2\n1'),
    make(lines('200000 200000', Array.from({ length: 200_000 }, (_, i) =>
      i < 100_000 ? (i + 2) + ' ' + (i + 1) : '1 ' + (i - 99_998))),
    Array.from({ length: 200_000 }, (_, i) => Math.max(100_000, 199999 - i)).join('\n'), true)],
  () => {
    const n = 100
    const row = Array(n).fill(1)
    for (let i = 1; i < n; i++) for (let j = 1; j < n; j++) row[j] = (row[j] + row[j - 1]) % 1_000_000_007
    return [make('3 3\n.#.\n###\n.#.', 0), make('2 3\n...\n#..', 2),
      make(lines('100 100', Array(n).fill('.'.repeat(n))), row.at(-1), true)]
  },
  () => [make('5 5\n1 2\n2 3\n3 1\n4 5\n1 2', -1),
    make('5 5\n1 2\n2 5\n1 3\n3 4\n4 5', 2),
    make(lines('200000 199999', Array.from({ length: 199_999 }, (_, i) => '1 ' + (i + 2))), 1, true),
    make(lines('200000 199999', Array.from({ length: 199_999 }, (_, i) => (i + 1) + ' ' + (i + 2))), 199_999, true)],
  () => [make('6\n1 5 5 2 2', '5 4 0 0 2 0'),
    make(pack(Array.from({ length: 199_999 }, (_, i) => i + 1), 200_000),
      Array.from({ length: 200_000 }, (_, i) => 199_999 - i).join(' '), true)],
  () => {
    const k = 999_983 * 997
    const values = Array.from({ length: 200_000 }, (_, i) => i % 2
      ? 999_900_000 - i * 17 : 1009 * (i + 1))
    // Use a large prime as k on the stress case to expose divisor enumeration.
    const kStress = 999_999_937
    return [make('4 18\n1 9 25 35', 3), make('3 ' + k + '\n999983 997 2', 1),
      make(pack(values, values.length + ' ' + kStress), values.filter(x => gcd(x, kStress) === 1).length, true)]
  },
  () => [make('abababab\nabab', 3), make('aaaabaaaab\nab', 2),
    make('a'.repeat(200_000) + '\n' + 'a'.repeat(99_999) + 'b', 0, true),
    make('a'.repeat(200_000) + '\n' + 'a'.repeat(100_000), 100_001, true)],
  () => [make('4\n0 8 9 1', 'Second'), make('3\n0 0 4', 'First'),
    make(pack(Array(200_000).fill(1_000_000_000)), 'Second', true)]
]

function variants(index) {
  let state = 58193 + index
  const random = max => {
    state = (Math.imul(state, 1664525) + 1013904223) >>> 0
    return state % max
  }
  return Array.from({ length: 3 }, () => {
    const values = Array.from({ length: 5 + random(12) }, () => random(41) - 20)
    switch (index) {
      case 0: return make(values.slice(0, 2).join(' '), values[0] + values[1])
      case 1: return make(pack(values), Math.max(...values.flatMap((_, i) =>
        values.slice(i).map((__, offset) => values.slice(i, i + offset + 1).reduce((a, b) => a + b, 0)))))
      case 2: {
        const sorted = values.toSorted((a, b) => a - b)
        return make(pack(sorted, values.length + ' ' + values.length) + '\n' + values.join(' '),
          values.map(x => sorted.findIndex(value => value >= x)).join('\n'))
      }
      case 3: {
        const k = 1 + random(values.length)
        return make(pack(values, values.length + ' ' + k), Math.max(...values.slice(k - 1).map((_, i) =>
          values.slice(i, i + k).reduce((a, b) => a + b, 0))))
      }
      case 9: {
        const positive = values.map(x => x + 21), k = 1 + random(41)
        return make(pack(positive, values.length + ' ' + k), positive.filter(x => gcd(x, k) === 1).length)
      }
      case 10: {
        const text = values.map(x => 'abc'[Math.abs(x) % 3]).join('')
        const pattern = text.slice(1, 4)
        return make(text + '\n' + pattern, [...text].filter((_, i) => text.startsWith(pattern, i)).length)
      }
      case 11: {
        const sizes = values.map(x => Math.abs(x))
        return make(pack(sizes), sizes.reduce((a, b) => a ^ b, 0) ? 'First' : 'Second')
      }
      default: return suiteVariation(index, values.length, random)
    }
  })
}

function suiteVariation(index, n, random) {
  if (index === 4) {
    const events = Array.from({ length: n }, () => {
      const start = random(12) - 6
      return [start, start + 1 + random(6)]
    })
    const finish = events.toSorted((a, b) => a[1] - b[1])
    const best = [0]
    for (const [i, [start]] of finish.entries()) {
      const previous = finish.slice(0, i).findLastIndex(event => event[1] <= start)
      best.push(Math.max(best[i], best[previous + 1] + 1))
    }
    return make(lines(n, events.map(row => row.join(' '))), best.at(-1))
  }
  if (index === 5) {
    let groups = Array.from({ length: n }, (_, i) => i)
    const edges = Array.from({ length: 2 * n }, () => [random(n), random(n)])
    const answers = edges.map(([u, v]) => {
      groups = groups.map(id => id === groups[v] ? groups[u] : id)
      return new Set(groups).size
    })
    return make(lines(n + ' ' + edges.length, edges.map(([u, v]) => (u + 1) + ' ' + (v + 1))), answers.join('\n'))
  }
  if (index === 6) {
    const size = 3 + random(4)
    const grid = Array.from({ length: size }, () => Array.from({ length: size }, () => random(5) === 0 ? '#' : '.').join(''))
    function count(r, c) {
      if (grid[r]?.[c] !== '.') return 0
      return r === size - 1 && c === size - 1 ? 1 : count(r + 1, c) + count(r, c + 1)
    }
    return make(lines(size + ' ' + size, grid), count(0, 0))
  }
  if (index === 7) {
    const edges = Array.from({ length: n }, (_, i) => [i, (i + 1 + random(n - 1)) % n])
    const distance = Array.from({ length: n }, (_, u) => Array.from({ length: n }, (_, v) => u === v ? 0 : Infinity))
    for (const [u, v] of edges) distance[u][v] = distance[v][u] = 1
    for (let k = 0; k < n; k++) for (let u = 0; u < n; u++) for (let v = 0; v < n; v++) {
      distance[u][v] = Math.min(distance[u][v], distance[u][k] + distance[k][v])
    }
    return make(lines(n + ' ' + edges.length, edges.map(([u, v]) => (u + 1) + ' ' + (v + 1))),
      Number.isFinite(distance[0][n - 1]) ? distance[0][n - 1] : -1)
  }
  const parents = Array.from({ length: n - 1 }, (_, i) => random(i + 1))
  const descendants = Array(n).fill(0)
  for (let vertex = 1; vertex < n; vertex++) {
    for (let current = vertex; current > 0; current = parents[current - 1]) descendants[parents[current - 1]]++
  }
  return make(pack(parents.map(parent => parent + 1), n), descendants.join(' '))
}

export function privateCases(index, lab) {
  const legacy = lab.cases.map(([input, output]) => make(input, output))
  return [...legacy, ...variants(index), ...boundaries[index]()]
}
