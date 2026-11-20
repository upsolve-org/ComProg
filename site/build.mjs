import { fileURLToPath } from 'node:url'
import { readdir, readFile, mkdir, cp, writeFile } from 'node:fs/promises'
import { build } from 'esbuild'
import { marked } from 'marked'
import { labs } from './labs.mjs'
import { quizzes } from './quizzes.mjs'
import { buildFilmChapters, filmNotes } from './video.mjs'

const root = new URL('../', import.meta.url)
const dist = new URL('dist/', root)
const titles = ['Getting started', 'Foundations and complexity', 'Binary and ternary search',
  'Two pointers and sliding windows', 'Sorting and greedy algorithms', 'Data structures',
  'Dynamic programming', 'Graph algorithms', 'Trees and lowest common ancestors',
  'Mathematics and number theory', 'String algorithms', 'Advanced techniques', 'Reference library']
const noteOrder = [
  'python_cp_guide codeforces_platform_guide',
  'fast_io_and_templates prefix_sums_and_diff_arrays',
  'binary_search_templates ternary_search',
  'two_pointers_templates sliding_window_templates',
  'sorting_and_custom_keys greedy_templates',
  'dsu_disjoint_set_union fenwick_tree segment_tree monotonic_stack_and_queue ordered_set_python',
  '01_knapsack_and_subsets grid_and_paths_dp lis_and_lcs interval_and_range_dp tree_dp bitmask_dp',
  'graph_traversal_bfs_dfs topological_sort shortest_path_dijkstra shortest_path_bellman_floyd minimum_spanning_tree bridges_and_articulation_points',
  'tree_basics_and_euler_tour binary_lifting_lca',
  'gcd_extended_euclidean primes_and_sieve modular_arithmetic_and_combinatorics bitwise_operations',
  'polynomial_rolling_hash kmp_prefix_function z_algorithm trie_prefix_tree',
  'constructive_algorithms mo_algorithm_and_sqrt_decomp game_theory_nim',
  'codeforces_catalog_full'
]

function clean(markdown) {
  return markdown.replace(/\r\n/g, '\n').replace(/^\uFEFF?---\n[\s\S]*?\n---\n/, '')
    .replace(/^\s*\[\[(?:ComProg\/)?Home\|[^\n]*\n/gm, '')
    .replace(/^# [^\n]+\n/m, '')
    .replace(/^⏮️[^\n]*\n/gm, '')
    .replace(/^> \[![a-z]+\]\s*/gim, '> **')
    .replace(/^> \*\*([^\n]+)$/gm, '> **$1**')
}

function chapterSections(overview) {
  const sections = [{ id: 'learn', title: 'Overview', markdown: '' }]
  for (const token of marked.lexer(overview)) {
    if (token.type === 'heading' && [2, 3].includes(token.depth)) {
      sections.push({
        id: 'section-' + sections.length,
        title: token.text.replace(/^[^\p{L}\p{N}]+/u, '').replace(/^\d+\.\s*/, ''),
        markdown: ''
      })
    } else {
      sections.at(-1).markdown += token.raw
    }
  }
  return sections.filter(section => !section.title.startsWith('Included Source Files') &&
    section.markdown.replace(/^\s*---\s*$/gm, '').trim())
}

const folders = (await readdir(root, { withFileTypes: true }))
  .filter(entry => entry.isDirectory() && /^\d{2}_/.test(entry.name))
  .map(entry => entry.name).sort()
if (folders.length !== titles.length || labs.length !== titles.length - 1 || quizzes.length !== titles.length) {
  throw new Error('Course folders and lesson definitions are out of sync.')
}

const scripts = JSON.parse((await readFile(new URL('site/video/lessons.json', root), 'utf8')).replace(/^\uFEFF/, ''))
const filmIds = new Set([...Object.keys(scripts), ...Object.values(filmNotes)])
const films = Object.fromEntries(await Promise.all(Array.from(filmIds).map(async film => {
  if (!scripts[film]) throw new Error('Missing narration script for ' + film + '.')
  const vtt = await readFile(new URL('site/public/' + film + '.vtt', root), 'utf8')
  return [film, buildFilmChapters(scripts[film], vtt, film)]
})))

const course = await Promise.all(folders.map(async (folder, index) => {
  const dir = new URL(folder + '/', root)
  const notes = (await readdir(dir)).filter(name =>
    name.endsWith('.md') && name !== 'README.md' && name !== folder + '.md').sort()
  const order = noteOrder[index].split(' ')
  const orderedNotes = await Promise.all(notes.map(async name => {
      const raw = await readFile(new URL(name, dir), 'utf8')
      const film = filmNotes[name]
      return {
        name,
        taught: order.includes(name.slice(0, -3)),
        title: raw.match(/^# (.+)$/m)?.[1].trim() ?? name,
        ...(film && { film, chapters: films[film] }),
        markdown: clean(raw).replace(/^> \*\*Implementation Note\*\*\n(?:>[^\n]*\n)+/gm, '')
          .replace(/^(?:# Test cases for run_tests\.py\n)?TEST_CASES\s*=\s*\[[^\n]*\n[\s\S]*?^\][ \t]*\n/gm, '')
          .replace(/^## [^\n]*Complexity & Analysis\r?\n- \*\*Time Complexity:\*\* See docstrings[^\n]*\n- \*\*Space Complexity:\*\* See docstrings[^\n]*\n/gm, '')
      }
    }))
  return {
    id: folder,
    title: titles[index],
    sections: chapterSections(clean(await readFile(new URL('README.md', dir), 'utf8'))),
    notes: [...order.map(stem => orderedNotes.find(note => note.name === stem + '.md')).filter(Boolean),
      ...orderedNotes.filter(note => !note.taught)],
    quizzes: quizzes[index],
    lab: labs[index] && {
      title: labs[index].title,
      task: labs[index].task
    }
  }
}))

await mkdir(dist, { recursive: true })
await cp(new URL('site/public/', root), dist, { recursive: true })
await writeFile(new URL('course.json', dist), JSON.stringify(course))
await build({
  absWorkingDir: fileURLToPath(root),
  entryPoints: ['site/app.js'], bundle: true, format: 'esm', minify: true, outdir: 'dist',
  loader: { '.woff': 'file', '.woff2': 'file', '.ttf': 'file', '.vtt': 'text' }
})
