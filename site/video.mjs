export const filmNotes = {
  'python_cp_guide.md': 'PythonGuide',
  'codeforces_platform_guide.md': 'ContestGuide',
  'fast_io_and_templates.md': 'FastIoGuide',
  'prefix_sums_and_diff_arrays.md': 'PrefixSumsGuide',
  'binary_search_templates.md': 'BinarySearchGuide',
  'ternary_search.md': 'TernarySearchGuide',
  'two_pointers_templates.md': 'TwoPointersGuide',
  'sliding_window_templates.md': 'SlidingWindowGuide',
  'sorting_and_custom_keys.md': 'SortingGuide',
  'greedy_templates.md': 'GreedyGuide',
  'dsu_disjoint_set_union.md': 'DsuGuide',
  'fenwick_tree.md': 'FenwickGuide',
  'segment_tree.md': 'SegmentTreeGuide',
  'monotonic_stack_and_queue.md': 'MonotonicGuide',
  'ordered_set_python.md': 'OrderedSetGuide',
  '01_knapsack_and_subsets.md': 'KnapsackGuide',
  'grid_and_paths_dp.md': 'GridDpGuide',
  'lis_and_lcs.md': 'LisLcsGuide',
  'interval_and_range_dp.md': 'IntervalDpGuide',
  'tree_dp.md': 'TreeDpGuide',
  'bitmask_dp.md': 'BitmaskDpGuide',
  'graph_traversal_bfs_dfs.md': 'GraphTraversalGuide',
  'topological_sort.md': 'TopoSortGuide',
  'shortest_path_dijkstra.md': 'DijkstraGuide',
  'shortest_path_bellman_floyd.md': 'BellmanFloydGuide',
  'minimum_spanning_tree.md': 'MstGuide',
  'bridges_and_articulation_points.md': 'BridgesGuide',
  'tree_basics_and_euler_tour.md': 'EulerTourGuide',
  'binary_lifting_lca.md': 'LcaGuide',
  'gcd_extended_euclidean.md': 'GcdGuide',
  'primes_and_sieve.md': 'SieveGuide',
  'modular_arithmetic_and_combinatorics.md': 'ModCombGuide',
  'bitwise_operations.md': 'BitwiseGuide',
  'polynomial_rolling_hash.md': 'RollingHashGuide',
  'kmp_prefix_function.md': 'KmpGuide',
  'z_algorithm.md': 'ZAlgoGuide',
  'trie_prefix_tree.md': 'TrieGuide',
  'constructive_algorithms.md': 'ConstructiveGuide',
  'mo_algorithm_and_sqrt_decomp.md': 'MoSqrtGuide',
  'game_theory_nim.md': 'NimGuide',
  'codeforces_catalog_full.md': 'CatalogGuide'
}

const normalize = text => String(text ?? '').replace(/\s+/g, ' ').trim()

export function parseTimestamp(value) {
  const match = /^(?:(\d{2}):)?(\d{2}):(\d{2})\.(\d{3})$/.exec(String(value).trim())
  if (!match) throw new Error('Invalid WebVTT timestamp: ' + value)
  const [, hours = '0', minutes, seconds, millis] = match
  const mins = Number(minutes)
  const secs = Number(seconds)
  if (mins >= 60 || secs >= 60) throw new Error('Out-of-range WebVTT timestamp: ' + value)
  return Number(hours) * 3600 + mins * 60 + secs + Number(millis) / 1000
}

export function formatTimestamp(seconds) {
  if (!Number.isFinite(seconds) || seconds < 0) {
    throw new Error('Invalid chapter timestamp seconds: ' + seconds)
  }
  const total = Math.floor(seconds)
  const hours = Math.floor(total / 3600)
  const minutes = Math.floor((total % 3600) / 60)
  const remainder = String(total % 60).padStart(2, '0')
  return hours ? hours + ':' + String(minutes).padStart(2, '0') + ':' + remainder : minutes + ':' + remainder
}

export function parseVtt(source, name = 'WebVTT') {
  const blocks = String(source ?? '').replace(/^\uFEFF/, '').replace(/\r\n/g, '\n').trim().split(/\n{2,}/)
  if (blocks[0]?.trim() !== 'WEBVTT') {
    throw new Error(name + ' is missing a WEBVTT header.')
  }
  const cues = []
  let previousEnd = 0
  for (const block of blocks.slice(1)) {
    const lines = block.split('\n').map(line => line.trim()).filter(Boolean)
    if (!lines.length) continue
    const timingIndex = lines[0].includes('-->') ? 0 : 1
    const timing = lines[timingIndex]
    const match = /^(\S+)\s+-->\s+(\S+)(?:\s+.*)?$/.exec(timing || '')
    if (!match) throw new Error(name + ' has a malformed cue timing: ' + (timing || block))
    const start = parseTimestamp(match[1])
    const end = parseTimestamp(match[2])
    if (end <= start || start + 1e-6 < previousEnd) {
      throw new Error(name + ' has out-of-order cue timings at ' + timing)
    }
    const text = normalize(lines.slice(timingIndex + 1).join(' '))
    if (!text) throw new Error(name + ' has an empty caption cue at ' + timing)
    previousEnd = end
    cues.push({ start, end, text })
  }
  if (!cues.length) throw new Error(name + ' contains no caption cues.')
  return cues
}

export function buildFilmChapters(beats, vtt, name = 'Film') {
  if (!Array.isArray(beats) || !beats.length) {
    throw new Error(name + ' has no narration beats.')
  }
  const cues = typeof vtt === 'string' ? parseVtt(vtt, name) : vtt
  if (!Array.isArray(cues) || !cues.length) {
    throw new Error(name + ' contains no caption cues.')
  }
  let cueIndex = 0
  const chapters = beats.map((beat, index) => {
    const [rawTitle, , rawSpeech] = Array.isArray(beat) ? beat : [beat?.title, null, beat?.speech]
    const title = normalize(rawTitle)
    const speech = normalize(rawSpeech)
    if (!title || !speech) {
      throw new Error(name + ' chapter ' + (index + 1) + ' is missing a title or narration.')
    }
    if (cueIndex >= cues.length) {
      throw new Error(name + ' captions end before chapter "' + title + '".')
    }
    const sentences = speech.split(/(?<=[.!?])\s+/).filter(Boolean)
    const start = cues[cueIndex].start
    let end = cues[cueIndex].end
    if (cues[cueIndex].text === speech) {
      cueIndex++
    } else {
      for (const sentence of sentences) {
        const cue = cues[cueIndex++]
        if (!cue) {
          throw new Error(name + ' captions end mid-chapter in "' + title + '".')
        }
        if (cue.text !== sentence) {
          throw new Error(name + ' captions do not match script in chapter "' + title + '".')
        }
        end = cue.end
      }
    }
    return {
      title,
      speech,
      start,
      end,
      stamp: formatTimestamp(start)
    }
  })
  if (cueIndex !== cues.length) {
    throw new Error(name + ' has ' + (cues.length - cueIndex) + ' extra caption cue(s) not in the script.')
  }
  return chapters
}

export function activeChapterIndex(chapters, seconds = 0) {
  const time = Number.isFinite(seconds) ? Math.max(0, seconds) : 0
  let active = 0
  for (const [index, chapter] of chapters.entries()) {
    if (time + 0.05 >= chapter.start) active = index
  }
  return active
}
