import { basicSetup, EditorView } from 'codemirror'
import { python } from '@codemirror/lang-python'
import { cpp } from '@codemirror/lang-cpp'
import { oneDark } from '@codemirror/theme-one-dark'
import { marked } from 'marked'
import math from 'marked-katex-extension'
import DOMPurify from 'dompurify'
import filmScripts from './video/lessons.json'
import pythonVtt from './public/PythonGuide.vtt'
import contestVtt from './public/ContestGuide.vtt'
import { activeChapterIndex, buildFilmChapters, filmNotes } from './video.mjs'
import { detectLanguage, highlightHTML, languageBadge } from './highlight.mjs'
import { createVisualizer, mountVisualizer } from './visualizers.mjs'
import { filterAndSortProblems, ratingTier, unpackProblems } from './codeforces.mjs'
import '@fontsource-variable/geist/wght.css'
import '@fontsource/jetbrains-mono/latin-400.css'
import 'katex/dist/katex.min.css'
import './style.css'

const $ = id => document.getElementById(id)
const $qs = selector => document.querySelector(selector)
const filmChapters = {
  PythonGuide: buildFilmChapters(filmScripts.PythonGuide, pythonVtt, 'PythonGuide'),
  ContestGuide: buildFilmChapters(filmScripts.ContestGuide, contestVtt, 'ContestGuide')
}
const starter = '# Read from standard input and print your result.\n'
let courseKey = 'python'
const storage = {
  key(key) { return 'comprog:' + (courseKey === 'cpp' ? 'cpp:' : '') + key },
  get(key) {
    try { return localStorage.getItem(this.key(key)) } catch { return null }
  },
  set(key, value) {
    try { localStorage.setItem(this.key(key), value) } catch { /* Storage is optional. */ }
  },
  remove(key) {
    try { localStorage.removeItem(this.key(key)) } catch { /* Storage is optional. */ }
  },
  // Course-independent prefs (the switcher itself) skip the prefix.
  shared(key) {
    try { return localStorage.getItem('comprog:' + key) } catch { return null }
  },
  remember(value) {
    try { localStorage.setItem('comprog:course', value) } catch { /* Storage is optional. */ }
  }
}
function node(tag, text, className) {
  const element = document.createElement(tag)
  if (text) element.textContent = text
  if (className) element.className = className
  return element
}
function link(text, href, className) {
  const element = node('a', text, className)
  element.href = href
  return element
}
const lessonURL = (id, tab = 'practice') => '#' + (courseKey === 'cpp' ? 'cpp' : 'python') + '/' + id + '/' + tab
const otherLessonURL = (id, tab = 'practice') =>
  '#' + (courseKey === 'cpp' ? 'python' : 'cpp') + '/' + id + '/' + tab
const courseFile = () => courseKey === 'cpp' ? '/course-cpp.json' : '/course.json'
// C++ assignments ship their own starter, so a reset restores that, not the Python shell.
const starterFor = chapter => courseKey === 'cpp'
  ? (chapter?.lab?.starter ?? '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    \n}\n')
  : starter
marked.use(math({ throwOnError: false, nonStandard: true }))

let course
let lesson
let editor
let activeRun
let runId = 0
let runnerReady = false
const chats = new Map()
const pendingHints = new Set()
const runner = $('runner')
const matches = matchMedia('(max-width: 830px)')
const outline = document.querySelector('.sidebar')
const outlinePreference = () => matches.matches ? 'outline-mobile' : 'outline-desktop'
function restoreOutline() {
  const stored = storage.get(outlinePreference())
  outline.open = stored === null ? !matches.matches : stored === 'open'
}
restoreOutline()
outline.querySelector(':scope > summary').addEventListener('click', event => {
  event.preventDefault()
  outline.open = !outline.open
  storage.set(outlinePreference(), outline.open ? 'open' : 'closed')
})
outline.addEventListener('toggle', () => storage.set(outlinePreference(), outline.open ? 'open' : 'closed'))
matches.addEventListener('change', restoreOutline)
$('progress-label').textContent = '0 of 12 exercises'
runner.addEventListener('load', () => {
  runnerReady = true
  if (activeRun) runner.contentWindow.postMessage(activeRun.message, '*')
})
// Also handle a frame that finished loading before the module executed.
if (document.readyState === 'complete') runnerReady = true
window.addEventListener('load', () => { runnerReady = true })

function renderMarkdown(source) {
  const markdown = source.replace(/(^```[^\n]*\n[\s\S]*?^```[^\n]*$)|\[\[([^\]|]+)(?:\|([^\]]+))?\]\]/gm, (match, code, path, label) => {
    if (code) return match
    const parts = path.replace(/^ComProg\//, '').split('#')[0].split('/')
    const file = parts.at(-1)
    const target = course.find(item => item.id === parts[0]) ?? lesson
    const noteName = file.endsWith('.md') ? file : file.replace(/\.py$/, '') + '.md'
    const note = target.notes.find(item => item.name === noteName)
    if (note) return '[' + (label || note.title) + '](' + lessonURL(target.id, note.name) + ')'
    if (parts[0] === 'Home') return '[Course outline](' + lessonURL(course[0].id) + ')'
    if (course.some(item => item.id === parts[0])) {
      return '[' + (label || target.title) + '](' + lessonURL(target.id, firstStep(target)) + ')'
    }
    return label || path
  })
  $('reading').innerHTML = DOMPurify.sanitize(marked.parse(markdown), { FORBID_TAGS: ['img'] })
  enhanceCodeBlocks()
}

// Wrap every rendered block in a dark well with a language badge and a copy button.
function enhanceCodeBlocks() {
  for (const pre of $('reading').querySelectorAll('pre')) {
    if (pre.closest('.code-block')) continue
    const code = pre.querySelector(':scope > code')
    const source = (code ?? pre).textContent
    const language = detectLanguage((code?.className ?? '').match(/language-([\w+#-]+)/)?.[1]
      ?? pre.getAttribute('data-language'))
    if (code) code.innerHTML = highlightHTML(code.textContent, language)
    pre.tabIndex = 0
    const wrapper = node('div', '', 'code-block')
    wrapper.dataset.language = language
    const head = node('div', '', 'code-head')
    const copy = node('button', 'Copy', 'code-copy')
    copy.type = 'button'
    copy.setAttribute('aria-label', 'Copy code to clipboard')
    copy.onclick = async () => {
      const original = copy.textContent
      try {
        await navigator.clipboard.writeText(source.replace(/\n$/, ''))
        copy.textContent = 'Copied ✓'
        copy.classList.add('is-copied')
      } catch {
        copy.textContent = 'Press Ctrl+C'
        copy.classList.add('is-failed')
      }
      setTimeout(() => {
        copy.textContent = original
        copy.classList.remove('is-copied', 'is-failed')
      }, 1600)
    }
    head.append(node('span', languageBadge(language), 'code-lang'), copy)
    pre.replaceWith(wrapper)
    wrapper.append(head, pre)
  }
}

// Drop one visualizer into a chapter's Overview step (01–11).
function mountVisualizerPanel(chapter) {
  const reading = $('reading')
  const hit = createVisualizer(chapter.id)
  if (!hit) return
  const panel = node('section', '', 'visualizer')
  panel.setAttribute('aria-label', 'Interactive demonstration')
  const head = node('div', '', 'viz-head-bar')
  const titleWrap = node('div')
  titleWrap.append(node('span', 'Interactive · step through ' + chapter.title.toLowerCase(), 'viz-kicker'),
    node('h2', hit.title, 'viz-title'))
  head.append(titleWrap, node('p', hit.summary, 'viz-summary'))
  const mountPoint = node('div', '', 'viz-mount')
  panel.append(head, mountPoint)
  reading.append(panel)
  // "Examples & notes" is another reading step, so its runs must stop too.
  for (const key of Object.keys(hit.extra ?? {})) {
    activeVisualizers.push(mountVisualizer(mountPoint, createVisualizer(chapter.id, key)))
  }
  activeVisualizers.push(mountVisualizer(mountPoint, hit))
}

function steps(chapter) {
  const material = [...chapter.sections, ...chapter.notes.filter(note => note.taught)
    .map(note => ({ id: note.name, title: note.title, markdown: note.markdown }))]
  if (chapter.quizzes?.length) material.push({ id: 'quiz', title: 'Chapter quiz' })
  if (chapter.lab) material.push({ id: 'practice', title: 'Assignment' })
  return material
}

const currentChapter = () => steps(lesson)
const firstStep = chapter => steps(chapter)[0].id
const accepted = id => Boolean(storage.get('accepted:' + id))
const quizAnswer = (chapterId, qIndex) => {
  const raw = storage.get('quiz:' + chapterId + ':' + qIndex)
  return raw === null ? null : Number(raw)
}
const quizScore = chapter => {
  const items = chapter.quizzes ?? []
  return items.filter((item, i) => quizAnswer(chapter.id, i) === item.answer).length
}
const statuses = new Map()
const submissions = new Set()
let editorChapter
let activeVisualizers = []
let lastRoute
let cfDataset = null
let cfLoading = false
const cfState = {
  tags: [],
  tagMode: 'all',
  minRating: 0,
  maxRating: 9999,
  includeUnrated: false,
  search: '',
  sort: 'rating-asc',
  onlySolved: 'all',
  showAllTags: false,
  page: 1,
  pageSize: 50,
  spotlight: null
}

function getSolvedProblems() {
  try {
    const raw = localStorage.getItem('comprog:cf:solved')
    return new Set(raw ? JSON.parse(raw) : [])
  } catch {
    return new Set()
  }
}

function saveSolvedProblems(set) {
  try {
    localStorage.setItem('comprog:cf:solved', JSON.stringify(Array.from(set)))
  } catch { /* Storage is optional */ }
}

async function loadCodeforcesData(forceRefresh = false) {
  if (cfDataset && !forceRefresh) return cfDataset
  const endpoints = forceRefresh
    ? [['/api/codeforces/refresh', { method: 'POST', headers: { 'content-type': 'application/json' }, body: '{}' }], ['/api/codeforces'], ['/codeforces-problems.json']]
    : [['/api/codeforces'], ['/codeforces-problems.json']]
  for (const [url, opts] of endpoints) {
    try {
      const res = await fetch(url, opts)
      if (!res.ok) continue
      const packed = await res.json()
      if (packed?.items?.length) {
        cfDataset = unpackProblems(packed)
        return cfDataset
      }
    } catch { /* Try next fallback */ }
  }
  throw new Error('Could not load Codeforces problemset.')
}

function isTrainingRoute() {
  const raw = location.hash.slice(1)
  return raw === 'training' || raw === 'python/training' || raw === 'cpp/training'
}

// "#cpp/<chapter>/<step>" or "#python/<chapter>/<step>". A bare "#<chapter>/<step>"
// is a legacy Python link and never switches the active course.
function readRoute() {
  const parts = location.hash.slice(1).split('/')
  if (parts[0] === 'cpp' || parts[0] === 'python') {
    if (!course || courseKey !== parts[0]) courseKey = parts[0]
    return parts.slice(1)
  }
  return parts
}

function renderQuizBlock(chapter, indices, inline = false) {
  const allQuizzes = chapter.quizzes ?? []
  if (!allQuizzes.length) return null
  const wrapper = node('section', '', inline ? 'quiz-section quiz-inline' : 'quiz-section quiz-full')
  wrapper.setAttribute('aria-label', inline ? 'Concept check quiz' : 'Chapter quiz')

  const head = node('div', '', 'quiz-header')
  const titleWrap = node('div', '', 'quiz-title-wrap')
  const kicker = node('span', inline ? 'CHECKPOINT // ACTIVE RECALL' : 'ASSESSMENT // CHAPTER QUIZ', 'quiz-kicker')
  const heading = node('h3', inline ? 'Quick concept check' : 'Test your chapter understanding', 'quiz-heading')
  titleWrap.append(kicker, heading)

  const metaWrap = node('div', '', 'quiz-meta')
  const scoreBadge = node('span', '', 'quiz-score')
  const updateScoreBadge = () => {
    const solved = quizScore(chapter)
    scoreBadge.textContent = solved + ' / ' + allQuizzes.length + ' Mastered'
    scoreBadge.classList.toggle('is-complete', solved === allQuizzes.length)
  }
  updateScoreBadge()
  metaWrap.append(scoreBadge)

  if (inline) {
    metaWrap.append(link('All chapter quizzes →', lessonURL(chapter.id, 'quiz'), 'quiz-all-link'))
  } else {
    const resetBtn = node('button', 'Reset quiz', 'quiz-reset')
    resetBtn.type = 'button'
    resetBtn.onclick = () => {
      for (let i = 0; i < allQuizzes.length; i++) storage.remove('quiz:' + chapter.id + ':' + i)
      render()
    }
    metaWrap.append(resetBtn)
  }
  head.append(titleWrap, metaWrap)
  wrapper.append(head)

  const list = node('div', '', 'quiz-list')
  for (const qIndex of indices) {
    const item = allQuizzes[qIndex]
    if (!item) continue
    const card = node('article', '', 'quiz-card')
    const qLabel = node('div', 'Q' + (qIndex + 1) + ' OF ' + allQuizzes.length, 'quiz-number')
    const prompt = node('p', item.question, 'quiz-prompt')
    const optionsGrid = node('div', '', 'quiz-options')
    const feedback = node('div', '', 'quiz-feedback')
    feedback.hidden = true

    const applyState = () => {
      const chosen = quizAnswer(chapter.id, qIndex)
      const answered = chosen !== null && !Number.isNaN(chosen)
      const isCorrect = answered && chosen === item.answer
      card.classList.toggle('is-answered', answered)
      card.classList.toggle('is-correct', isCorrect)
      card.classList.toggle('is-wrong', answered && !isCorrect)
      for (const [optIndex, btn] of Array.from(optionsGrid.children).entries()) {
        const selected = answered && chosen === optIndex
        const rightOption = answered && optIndex === item.answer
        btn.classList.toggle('selected', selected)
        btn.classList.toggle('correct', rightOption)
        btn.classList.toggle('wrong', selected && !isCorrect)
        btn.setAttribute('aria-pressed', selected ? 'true' : 'false')
      }
      if (answered) {
        feedback.hidden = false
        feedback.className = 'quiz-feedback ' + (isCorrect ? 'is-correct' : 'is-wrong')
        const status = node('strong', isCorrect ? '✓ Correct — ' : '✕ Not quite — ')
        const exp = node('span', item.explanation)
        feedback.replaceChildren(status, exp)
      } else {
        feedback.hidden = true
      }
      updateScoreBadge()
      renderProgress()
    }

    for (const [optIndex, optText] of item.options.entries()) {
      const btn = node('button', '', 'quiz-option')
      btn.type = 'button'
      const letter = node('span', String.fromCharCode(65 + optIndex), 'quiz-option-key')
      const text = node('span', optText, 'quiz-option-text')
      btn.append(letter, text)
      btn.onclick = () => {
        storage.set('quiz:' + chapter.id + ':' + qIndex, String(optIndex))
        applyState()
      }
      optionsGrid.append(btn)
    }

    card.append(qLabel, prompt, optionsGrid, feedback)
    applyState()
    list.append(card)
  }
  wrapper.append(list)
  return wrapper
}

function renderProgress() {
  const practice = course.filter(item => item.lab)
  const count = practice.filter(item => accepted(item.id)).length
  $('progress').max = practice.length
  $('progress').value = count
  $('progress-label').textContent = count + ' of ' + practice.length + ' accepted'
  const onTraining = isTrainingRoute()
  for (const button of document.querySelectorAll('.course-switch button')) {
    const active = !onTraining && button.dataset.course === courseKey
    button.setAttribute('aria-pressed', String(active))
  }
  const trainNavBtn = $('training-nav')
  if (trainNavBtn) {
    trainNavBtn.classList.toggle('is-active', onTraining)
    if (onTraining) trainNavBtn.setAttribute('aria-current', 'page')
    else trainNavBtn.removeAttribute('aria-current')
  }
  const shell = $qs('.shell')
  if (shell) shell.classList.toggle('is-training-page', onTraining)
  outline.hidden = onTraining
  const progressWrap = $qs('.progress')
  if (progressWrap) progressWrap.hidden = onTraining
  $qs('.course-name').textContent = onTraining
    ? 'Codeforces Problemset Arena'
    : (courseKey === 'cpp' ? 'Competitive programming in C++20' : 'Competitive programming in Python')

  const nav = $('outline')
  if (!nav.children.length || nav.dataset.course !== courseKey) {
    nav.replaceChildren()
    nav.dataset.course = courseKey
    delete nav.dataset.chapter
    for (const item of course) {
      const group = node('details', '', 'chapter-group')
      group.append(node('summary', item.title))
      for (const step of [...steps(item), { id: 'notes', title: 'Examples & notes' }]) {
        group.append(link(step.title, lessonURL(item.id, step.id)))
      }
      nav.append(group)
    }
  }
  if (onTraining) return
  const route = lessonURL(lesson.id, storage.get('step:' + lesson.id) || firstStep(lesson))
  for (const [index, group] of Array.from(nav.querySelectorAll('.chapter-group')).entries()) {
    const item = course[index]
    if (item === lesson && nav.dataset.chapter !== item.id) group.open = true
    const quizDone = item.quizzes?.length && quizScore(item) === item.quizzes.length
    const labDone = accepted(item.id)
    group.firstChild.textContent = (labDone ? '✓ ' : quizDone ? '◆ ' : '') + item.title
    for (const anchor of group.querySelectorAll('a')) {
      const active = anchor.hash === route
      anchor.classList.toggle('current', active)
      if (active) anchor.setAttribute('aria-current', 'page')
      else anchor.removeAttribute('aria-current')
    }
  }
  nav.dataset.chapter = lesson.id
}

function renderTraining() {
  const reading = $('reading')
  reading.querySelector('video')?.pause()
  reading.replaceChildren()
  activeVisualizers.forEach(visualizer => visualizer.destroy())
  activeVisualizers = []
  lesson = lesson ?? course[0]
  document.title = 'Codeforces Training Arena | ComProg'
  $('title').textContent = 'Codeforces Training Arena'
  $('position').textContent = 'Training // Problemset Filter & Rating Explorer'
  $('tabs').replaceChildren(
    link('← Back to Course Lessons', lessonURL(lesson.id, firstStep(lesson)), 'assignment-jump')
  )
  $('workspace').hidden = true
  $('tutor').hidden = true
  $('check').hidden = true
  $('layout').classList.remove('with-editor')
  $('layout').classList.add('is-full-width')
  reading.classList.remove('is-video', 'is-quiz', 'panel-enter')
  reading.classList.add('is-training')
  void reading.offsetWidth
  reading.classList.add('panel-enter')
  $('pagination').replaceChildren()
  renderProgress()

  const container = node('div', '', 'cf-arena')
  reading.append(container)

  if (!cfDataset) {
    const loadingBox = node('div', 'Loading 11,500+ Codeforces problems, tags, and ratings…', 'cf-loading')
    container.append(loadingBox)
    if (!cfLoading) {
      cfLoading = true
      loadCodeforcesData().then(() => {
        cfLoading = false
        if (isTrainingRoute()) renderTraining()
      }).catch(err => {
        cfLoading = false
        loadingBox.textContent = err.message || 'Could not load Codeforces problemset.'
      })
    }
    return
  }

  const { problems, tags, tagCounts } = cfDataset
  const solvedIds = getSolvedProblems()

  // Top Header & Stats Deck
  const topBar = node('div', '', 'cf-top-bar')
  const statsRow = node('div', '', 'cf-stats-row')
  const totalStat = node('div', '', 'cf-stat-card')
  totalStat.append(node('span', 'TOTAL PROBLEMS', 'cf-stat-label'), node('strong', problems.length.toLocaleString(), 'cf-stat-val'))
  const tagsStat = node('div', '', 'cf-stat-card')
  tagsStat.append(node('span', 'TOPIC TAGS', 'cf-stat-label'), node('strong', String(tags.length), 'cf-stat-val'))
  const matchStatVal = node('strong', '0', 'cf-stat-val is-accent')
  const matchStat = node('div', '', 'cf-stat-card')
  matchStat.append(node('span', 'MATCHING FILTER', 'cf-stat-label'), matchStatVal)
  const solvedStatVal = node('strong', String(solvedIds.size), 'cf-stat-val')
  const solvedStat = node('div', '', 'cf-stat-card')
  solvedStat.append(node('span', 'SOLVED BY YOU', 'cf-stat-label'), solvedStatVal)
  statsRow.append(totalStat, tagsStat, matchStat, solvedStat)

  const actionBtns = node('div', '', 'cf-actions')
  const randomBtn = node('button', 'Pick Random 🎲', 'primary cf-random-btn')
  randomBtn.type = 'button'
  const syncBtn = node('button', 'Sync Codeforces ↻', 'cf-sync-btn')
  syncBtn.type = 'button'
  syncBtn.onclick = async () => {
    syncBtn.disabled = true
    syncBtn.textContent = 'Syncing…'
    try {
      await loadCodeforcesData(true)
      renderTraining()
    } catch {
      syncBtn.textContent = 'Sync Failed'
      setTimeout(() => { syncBtn.textContent = 'Sync Codeforces ↻'; syncBtn.disabled = false }, 1800)
    }
  }
  actionBtns.append(randomBtn, syncBtn)
  topBar.append(statsRow, actionBtns)

  // Controls Deck: Search, Tag Dropdown, Sort by Rating, Min/Max Rating, Status
  const controls = node('div', '', 'cf-controls-grid')

  // 1. Search Box
  const searchGroup = node('div', '', 'cf-control-group')
  const searchLabel = node('label', 'Search Problem ID or Title', 'cf-control-label')
  searchLabel.htmlFor = 'cf-search'
  const searchInput = node('input', '', 'cf-input')
  searchInput.id = 'cf-search'
  searchInput.type = 'search'
  searchInput.placeholder = 'e.g. 4A, 1999G2, Watermelon, Dijkstra…'
  searchInput.value = cfState.search
  searchGroup.append(searchLabel, searchInput)

  // 2. Tag Selector Dropdown
  const tagSelectGroup = node('div', '', 'cf-control-group')
  const tagSelectLabel = node('label', 'Filter by Tag', 'cf-control-label')
  tagSelectLabel.htmlFor = 'cf-tag-select'
  const tagSelect = node('select', '', 'cf-select')
  tagSelect.id = 'cf-tag-select'
  const allTagOpt = node('option', `All Tags (${problems.length.toLocaleString()})`)
  allTagOpt.value = ''
  tagSelect.append(allTagOpt)
  for (const t of tags) {
    const opt = node('option', `${t} (${(tagCounts[t] ?? 0).toLocaleString()})`)
    opt.value = t
    tagSelect.append(opt)
  }
  tagSelect.value = cfState.tags[0] ?? ''
  tagSelectGroup.append(tagSelectLabel, tagSelect)

  // 3. Sort By Selector
  const sortGroup = node('div', '', 'cf-control-group')
  const sortLabel = node('label', 'Sort Problems By', 'cf-control-label')
  sortLabel.htmlFor = 'cf-sort-select'
  const sortSelect = node('select', '', 'cf-select')
  sortSelect.id = 'cf-sort-select'
  const sortOptions = [
    ['rating-asc', 'Rating: Low → High (800 → 3500)'],
    ['rating-desc', 'Rating: High → Low (3500 → 800)'],
    ['solved-desc', 'Most Solved First'],
    ['solved-asc', 'Least Solved First'],
    ['contest-desc', 'Newest Contests First'],
    ['contest-asc', 'Oldest / Classic First']
  ]
  for (const [val, labelText] of sortOptions) {
    const opt = node('option', labelText)
    opt.value = val
    sortSelect.append(opt)
  }
  sortSelect.value = cfState.sort
  sortGroup.append(sortLabel, sortSelect)

  // 4. Rating Range (Min / Max)
  const rangeGroup = node('div', '', 'cf-control-group')
  const rangeLabel = node('label', 'Rating Range (Min – Max)', 'cf-control-label')
  const rangeRow = node('div', '', 'cf-range-row')
  const minSelect = node('select', '', 'cf-select')
  minSelect.id = 'cf-min-rating'
  minSelect.setAttribute('aria-label', 'Minimum rating')
  const minAny = node('option', 'Min: Any')
  minAny.value = '0'
  minSelect.append(minAny)
  const maxSelect = node('select', '', 'cf-select')
  maxSelect.id = 'cf-max-rating'
  maxSelect.setAttribute('aria-label', 'Maximum rating')
  const maxAny = node('option', 'Max: Any')
  maxAny.value = '9999'
  maxSelect.append(maxAny)
  for (let r = 800; r <= 3500; r += 100) {
    const oMin = node('option', `≥ ${r}`)
    oMin.value = String(r)
    minSelect.append(oMin)
    const oMax = node('option', `≤ ${r}`)
    oMax.value = String(r)
    maxSelect.append(oMax)
  }
  minSelect.value = String(cfState.minRating)
  maxSelect.value = String(cfState.maxRating)
  rangeRow.append(minSelect, maxSelect)
  rangeGroup.append(rangeLabel, rangeRow)

  // 5. Status & Multi-Tag Mode
  const statusGroup = node('div', '', 'cf-control-group')
  const statusLabel = node('label', 'Progress & Tag Match', 'cf-control-label')
  const statusRow = node('div', '', 'cf-range-row')
  const statusSelect = node('select', '', 'cf-select')
  statusSelect.id = 'cf-status-select'
  statusSelect.setAttribute('aria-label', 'Problem status filter')
  for (const [val, txt] of [['all', 'All Problems'], ['unsolved', 'Unsolved Only'], ['solved', 'Solved Only']]) {
    const o = node('option', txt)
    o.value = val
    statusSelect.append(o)
  }
  statusSelect.value = cfState.onlySolved
  const modeSelect = node('select', '', 'cf-select')
  modeSelect.id = 'cf-tag-mode'
  modeSelect.setAttribute('aria-label', 'Multiple tag match mode')
  for (const [val, txt] of [['all', 'Match ALL Tags'], ['any', 'Match ANY Tag']]) {
    const o = node('option', txt)
    o.value = val
    modeSelect.append(o)
  }
  modeSelect.value = cfState.tagMode
  statusRow.append(statusSelect, modeSelect)
  statusGroup.append(statusLabel, statusRow)

  controls.append(searchGroup, tagSelectGroup, sortGroup, rangeGroup, statusGroup)

  // Quick Rating Tier Pills
  const tierBar = node('div', '', 'cf-tier-bar')
  const tiers = [
    { label: 'All Rated', min: 0, max: 9999, unrated: false, cls: '' },
    { label: '800–1100 Newbie', min: 800, max: 1100, unrated: false, cls: 'cf-newbie' },
    { label: '1200–1300 Pupil', min: 1200, max: 1300, unrated: false, cls: 'cf-pupil' },
    { label: '1400–1500 Specialist', min: 1400, max: 1500, unrated: false, cls: 'cf-specialist' },
    { label: '1600–1800 Expert', min: 1600, max: 1800, unrated: false, cls: 'cf-expert' },
    { label: '1900–2000 CM', min: 1900, max: 2000, unrated: false, cls: 'cf-cm' },
    { label: '2100–2300 Master', min: 2100, max: 2300, unrated: false, cls: 'cf-master' },
    { label: '2400+ GM', min: 2400, max: 9999, unrated: false, cls: 'cf-gm' },
    { label: '+ Include Unrated', min: 0, max: 9999, unrated: true, cls: 'cf-unrated' }
  ]
  const tierBtns = tiers.map(tier => {
    const btn = node('button', tier.label, 'cf-tier-pill ' + tier.cls)
    btn.type = 'button'
    btn.onclick = () => {
      cfState.minRating = tier.min
      cfState.maxRating = tier.max
      cfState.includeUnrated = tier.unrated
      minSelect.value = String(tier.min)
      maxSelect.value = String(tier.max)
      cfState.page = 1
      cfState.spotlight = null
      refreshTable()
    }
    tierBar.append(btn)
    return { btn, tier }
  })

  // Interactive Tag Pills Cloud
  const tagCloudWrap = node('div', '', 'cf-tag-cloud-wrap')
  const tagCloudHead = node('div', '', 'cf-tag-cloud-head')
  const tagCloudTitle = node('span', 'FILTER BY TOPIC TAGS (CLICK TO TOGGLE MULTIPLE)', 'cf-control-label')
  const tagCloudActions = node('div', '', 'cf-tag-cloud-actions')
  const clearTagsBtn = node('button', 'Clear filters', 'cf-mini-btn')
  clearTagsBtn.type = 'button'
  clearTagsBtn.onclick = () => {
    cfState.tags = []
    cfState.minRating = 0
    cfState.maxRating = 9999
    cfState.includeUnrated = false
    cfState.search = ''
    cfState.onlySolved = 'all'
    cfState.page = 1
    cfState.spotlight = null
    searchInput.value = ''
    tagSelect.value = ''
    minSelect.value = '0'
    maxSelect.value = '9999'
    statusSelect.value = 'all'
    refreshTable()
  }
  const toggleAllTagsBtn = node('button', cfState.showAllTags ? 'Show Top 18 Tags' : `Show All ${tags.length} Tags`, 'cf-mini-btn')
  toggleAllTagsBtn.type = 'button'
  const tagCloud = node('div', '', 'cf-tag-cloud')

  function buildTagPills() {
    tagCloud.replaceChildren()
    const visibleTags = cfState.showAllTags ? tags : tags.slice(0, 18)
    for (const t of visibleTags) {
      const active = cfState.tags.includes(t)
      const pill = node('button', '', 'cf-tag-pill' + (active ? ' is-active' : ''))
      pill.type = 'button'
      pill.setAttribute('aria-pressed', String(active))
      pill.append(node('span', t, 'cf-tag-name'), node('span', String(tagCounts[t] ?? 0), 'cf-tag-count'))
      pill.onclick = () => {
        if (cfState.tags.includes(t)) {
          cfState.tags = cfState.tags.filter(x => x !== t)
        } else {
          cfState.tags = [...cfState.tags, t]
        }
        tagSelect.value = cfState.tags[0] ?? ''
        cfState.page = 1
        cfState.spotlight = null
        refreshTable()
      }
      tagCloud.append(pill)
    }
  }
  toggleAllTagsBtn.onclick = () => {
    cfState.showAllTags = !cfState.showAllTags
    toggleAllTagsBtn.textContent = cfState.showAllTags ? 'Show Top 18 Tags' : `Show All ${tags.length} Tags`
    buildTagPills()
  }
  tagCloudActions.append(toggleAllTagsBtn, clearTagsBtn)
  tagCloudHead.append(tagCloudTitle, tagCloudActions)
  tagCloudWrap.append(tagCloudHead, tagCloud)

  const spotlightBox = node('div', '', 'cf-spotlight')
  spotlightBox.hidden = true

  const tableWrap = node('div', '', 'cf-table-wrap')
  const pagerWrap = node('div', '', 'cf-pager')

  function refreshTable() {
    buildTagPills()
    for (const { btn, tier } of tierBtns) {
      const active = cfState.minRating === tier.min && cfState.maxRating === tier.max && cfState.includeUnrated === tier.unrated
      btn.classList.toggle('is-active', active)
    }

    const filtered = filterAndSortProblems(problems, {
      tags: cfState.tags,
      tagMode: cfState.tagMode,
      minRating: cfState.minRating,
      maxRating: cfState.maxRating,
      includeUnrated: cfState.includeUnrated,
      search: cfState.search,
      sort: cfState.sort,
      onlySolved: cfState.onlySolved,
      solvedIds
    })

    matchStatVal.textContent = filtered.length.toLocaleString()
    solvedStatVal.textContent = solvedIds.size.toLocaleString()

    randomBtn.onclick = () => {
      if (!filtered.length) return
      const pick = filtered[Math.floor(Math.random() * filtered.length)]
      cfState.spotlight = pick
      renderSpotlight()
    }

    function renderSpotlight() {
      if (!cfState.spotlight) {
        spotlightBox.hidden = true
        return
      }
      const p = cfState.spotlight
      const tier = ratingTier(p.rating)
      spotlightBox.hidden = false
      spotlightBox.replaceChildren()
      const head = node('div', '', 'cf-spotlight-head')
      head.append(
        node('span', 'RANDOM TRAINING PICK // ' + p.id, 'quiz-kicker'),
        node('span', p.rating ? `★ ${p.rating} (${tier.label})` : 'Unrated', 'cf-rating-badge ' + tier.className)
      )
      const titleLink = link(`${p.id} — ${p.name} ↗`, p.url, 'cf-spotlight-title')
      titleLink.target = '_blank'
      titleLink.rel = 'noopener noreferrer'
      const tagRow = node('div', '', 'cf-row-tags')
      for (const t of p.tags) {
        tagRow.append(node('span', t, 'cf-row-tag'))
      }
      spotlightBox.append(head, titleLink, tagRow)
    }
    renderSpotlight()

    const totalPages = Math.max(1, Math.ceil(filtered.length / cfState.pageSize))
    if (cfState.page > totalPages) cfState.page = totalPages
    const startIdx = (cfState.page - 1) * cfState.pageSize
    const pageItems = filtered.slice(startIdx, startIdx + cfState.pageSize)

    const table = node('table', '', 'cf-table')
    const thead = node('thead')
    const htr = node('tr')
    for (const h of ['Status', 'ID', 'Problem', 'Topic Tags', 'Rating', 'Solved']) {
      htr.append(node('th', h))
    }
    thead.append(htr)

    const tbody = node('tbody')
    if (!pageItems.length) {
      const emptyTr = node('tr')
      const td = node('td', 'No problems match these filters. Try broadening your rating range or clearing a tag.', 'cf-empty-cell')
      td.colSpan = 6
      emptyTr.append(td)
      tbody.append(emptyTr)
    } else {
      for (const p of pageItems) {
        const isSolved = solvedIds.has(p.id)
        const tr = node('tr', '', isSolved ? 'is-solved' : '')

        // 1. Solved Toggle
        const tdStatus = node('td', '', 'cf-td-status')
        const checkBtn = node('button', isSolved ? '✓' : '○', 'cf-solve-btn' + (isSolved ? ' is-solved' : ''))
        checkBtn.type = 'button'
        checkBtn.title = isSolved ? 'Mark as unsolved' : 'Mark as solved'
        checkBtn.setAttribute('aria-label', (isSolved ? 'Solved ' : 'Mark solved ') + p.id)
        checkBtn.setAttribute('aria-pressed', String(isSolved))
        checkBtn.onclick = () => {
          if (solvedIds.has(p.id)) solvedIds.delete(p.id)
          else solvedIds.add(p.id)
          saveSolvedProblems(solvedIds)
          refreshTable()
        }
        tdStatus.append(checkBtn)

        // 2. Problem ID
        const tdId = node('td', '', 'cf-td-id')
        const idLink = link(p.id, p.url, 'cf-id-link')
        idLink.target = '_blank'
        idLink.rel = 'noopener noreferrer'
        tdId.append(idLink)

        // 3. Title
        const tdName = node('td', '', 'cf-td-name')
        const nameLink = link(p.name + ' ↗', p.url, 'cf-problem-link')
        nameLink.target = '_blank'
        nameLink.rel = 'noopener noreferrer'
        tdName.append(nameLink)

        // 4. Tags
        const tdTags = node('td', '', 'cf-td-tags')
        const tagsWrap = node('div', '', 'cf-row-tags')
        for (const t of p.tags) {
          const active = cfState.tags.includes(t)
          const tBtn = node('button', t, 'cf-row-tag' + (active ? ' is-active' : ''))
          tBtn.type = 'button'
          tBtn.onclick = () => {
            if (cfState.tags.includes(t)) cfState.tags = cfState.tags.filter(x => x !== t)
            else cfState.tags = [...cfState.tags, t]
            tagSelect.value = cfState.tags[0] ?? ''
            cfState.page = 1
            refreshTable()
          }
          tagsWrap.append(tBtn)
        }
        tdTags.append(tagsWrap)

        // 5. Rating
        const tdRating = node('td', '', 'cf-td-rating')
        const tier = ratingTier(p.rating)
        const rBadge = node('span', p.rating ? `★ ${p.rating}` : 'Unrated', 'cf-rating-badge ' + tier.className)
        rBadge.title = tier.label
        tdRating.append(rBadge)

        // 6. Solved Count
        const tdSolved = node('td', '×' + p.solvedCount.toLocaleString(), 'cf-td-solved')

        tr.append(tdStatus, tdId, tdName, tdTags, tdRating, tdSolved)
        tbody.append(tr)
      }
    }
    table.append(thead, tbody)
    tableWrap.replaceChildren(table)

    // Pagination controls
    pagerWrap.replaceChildren()
    const prevBtn = node('button', '← Prev Page', 'cf-page-btn')
    prevBtn.type = 'button'
    prevBtn.disabled = cfState.page <= 1
    prevBtn.onclick = () => { cfState.page--; refreshTable(); window.scrollTo(0, 0) }
    const pageInfo = node('span', `Page ${cfState.page} of ${totalPages} (${filtered.length.toLocaleString()} problems)`, 'cf-page-info')
    const nextBtn = node('button', 'Next Page →', 'cf-page-btn')
    nextBtn.type = 'button'
    nextBtn.disabled = cfState.page >= totalPages
    nextBtn.onclick = () => { cfState.page++; refreshTable(); window.scrollTo(0, 0) }
    pagerWrap.append(prevBtn, pageInfo, nextBtn)
  }

  searchInput.oninput = () => {
    cfState.search = searchInput.value
    cfState.page = 1
    refreshTable()
  }
  tagSelect.onchange = () => {
    cfState.tags = tagSelect.value ? [tagSelect.value] : []
    cfState.page = 1
    refreshTable()
  }
  sortSelect.onchange = () => {
    cfState.sort = sortSelect.value
    cfState.page = 1
    refreshTable()
  }
  minSelect.onchange = () => {
    cfState.minRating = Number(minSelect.value) || 0
    cfState.page = 1
    refreshTable()
  }
  maxSelect.onchange = () => {
    cfState.maxRating = Number(maxSelect.value) || 9999
    cfState.page = 1
    refreshTable()
  }
  statusSelect.onchange = () => {
    cfState.onlySolved = statusSelect.value
    cfState.page = 1
    refreshTable()
  }
  modeSelect.onchange = () => {
    cfState.tagMode = modeSelect.value
    cfState.page = 1
    refreshTable()
  }

  container.append(topBar, controls, tierBar, tagCloudWrap, spotlightBox, tableWrap, pagerWrap)
  refreshTable()
}

function render() {
  if (isTrainingRoute()) {
    lastRoute = location.hash
    renderTraining()
    return
  }
  if (lastRoute !== location.hash) {
    const parts = readRoute()
    const prefixed = parts[0] === 'cpp' || parts[0] === 'python'
    const key = prefixed ? parts[0] : 'python'
    const chapterId = prefixed ? parts[1] : parts[0]
    const step = prefixed ? parts[2] : parts[1]
    if (location.hash === '#main' || !chapterId || !course.some(item => item.id === chapterId)) {
      location.replace(lessonURL(course[0].id))
      return
    }
    // Write the canonical prefixed route once, keeping legacy links working.
    const canonical = lessonURL(chapterId, step || firstStep(course.find(item => item.id === chapterId)))
    if (location.hash !== canonical) {
      history.replaceState(null, '', canonical)
      lastRoute = canonical
    } else {
      lastRoute = location.hash
    }
  }
  const [, id, selected] = location.hash.slice(1).split('/')
  const previousChapter = lesson
  lesson = course.find(item => item.id === id) ?? course.find(item => item.id === storage.get('resume')) ?? course[0]
  const index = course.indexOf(lesson)
  const sequence = currentChapter()
  const tab = selected || (id ? firstStep(lesson) : storage.get('step:' + lesson.id) || firstStep(lesson))
  const note = lesson.notes.find(item => item.name === tab)
  const section = sequence.find(item => item.id === tab) ?? sequence[0]
  const stepIndex = sequence.indexOf(section)
  const practice = Boolean(lesson.lab && tab === 'practice')
  const isQuizTab = tab === 'quiz' && Boolean(lesson.quizzes?.length)
  const film = note && (note.film ?? filmNotes[note.name])
  const chapters = note && (note.chapters ?? (film && filmChapters[film]))
  const isVideo = Boolean(film && chapters)
  const showEditor = Boolean(practice)
  const reading = $('reading')
  reading.querySelector('video')?.pause()
  reading.replaceChildren()
  activeVisualizers.forEach(visualizer => visualizer.destroy())
  activeVisualizers = []
  storage.set('resume', lesson.id)
  storage.set('step:' + lesson.id, tab)
  document.title = (note?.title ?? section.title) + ' | ' + lesson.title + ' | ComProg'
  $('title').textContent = lesson.title
  $('position').textContent = lesson.lab ? 'Chapter ' + (index + 1) + ' / ' + (course.length - 1) : 'Reference'
  // Reading, video and quiz steps never show the editor; the assignment is one click away.
  const jump = lesson.lab && !practice ? link('Open Assignment →', lessonURL(lesson.id, 'practice'), 'assignment-jump') : null
  if (jump) {
    jump.setAttribute('aria-label', 'Open the assignment for ' + lesson.title)
    if (accepted(lesson.id)) jump.classList.add('is-done')
  }
  const label = node('label', 'Lesson', 'sr-only')
  label.htmlFor = 'lesson-step'
  const select = node('select')
  select.id = 'lesson-step'
  for (const [i, item] of sequence.entries()) {
    const option = node('option', (i + 1) + '. ' + item.title)
    option.value = item.id
    select.append(option)
  }
  const notesOption = node('option', 'Examples & notes')
  notesOption.value = 'notes'
  select.append(notesOption)
  select.value = tab === 'notes' || (note && !note.taught) ? 'notes' : section.id
  select.onchange = () => { location.hash = lessonURL(lesson.id, select.value) }
  $('tabs').replaceChildren(label, ...(jump ? [jump] : []), select)

  $('workspace').hidden = !showEditor
  $('tutor').hidden = !practice
  $('check').hidden = !practice
  $('layout').classList.toggle('with-editor', showEditor)
  $('layout').classList.toggle('is-full-width', !showEditor)
  reading.classList.toggle('is-video', isVideo)
  reading.classList.toggle('is-quiz', isQuizTab)
  reading.classList.remove('is-training', 'panel-enter')
  void reading.offsetWidth
  reading.classList.add('panel-enter')
  reading.replaceChildren()
  if (practice) {
    reading.append(node('h2', lesson.lab.title), node('p', lesson.lab.task),
      node('p', courseKey === 'cpp'
        ? 'Run your own input to compile and execute with g++ -O2 -std=gnu++20, then submit for hidden correctness and stress checks.'
        : 'Run your own input in the editor, then submit for hidden correctness and stress checks.', 'assignment-note'))
    if (previousChapter !== lesson) $('question').value = ''
    $('ask').querySelector('button').disabled = pendingHints.has(lesson.id)
    renderChat()
  } else if (isQuizTab) {
    reading.append(
      node('h2', 'Chapter quiz: ' + lesson.title),
      node('p', 'Check your understanding of the key concepts, complexity bounds, and edge cases in this chapter before moving to the coding assignment.'),
      renderQuizBlock(lesson, lesson.quizzes.map((_, i) => i), false)
    )
  } else if (note) {
    renderMarkdown(note.markdown)
    if (isVideo) {
      const notes = node('details', '', 'film-notes')
      notes.append(node('summary', 'Read the full lesson'), ...reading.childNodes)
      enhanceCodeBlocks()
      const videoStage = node('div', '', 'video-stage')
      const video = node('video')
      video.controls = true
      video.playsInline = true
      video.preload = 'metadata'
      video.src = '/' + film + '.mp4'
      video.setAttribute('aria-label', note.title)
      const captions = node('track')
      captions.kind = 'captions'
      captions.srclang = 'en'
      captions.label = 'English'
      captions.src = '/' + film + '.vtt'
      video.append(captions)
      const chapterNav = node('nav', '', 'film-chapters')
      chapterNav.setAttribute('aria-label', 'Video chapters')
      let pendingTime
      const buttons = chapters.map(chapter => {
        const button = node('button', '', 'film-chapter')
        button.type = 'button'
        button.dataset.time = String(chapter.start)
        button.append(node('span', chapter.stamp, 'chapter-time'), ' ', node('span', chapter.title, 'chapter-title'))
        button.onclick = () => {
          pendingTime = chapter.start
          video.currentTime = chapter.start
          markChapter(chapter.start)
        }
        chapterNav.append(button)
        return button
      })
      function markChapter(seconds) {
        const current = activeChapterIndex(chapters, seconds)
        for (const [i, button] of buttons.entries()) {
          const active = i === current
          button.classList.toggle('current', active)
          if (active) button.setAttribute('aria-current', 'true')
          else button.removeAttribute('aria-current')
        }
      }
      markChapter(0)
      video.addEventListener('loadedmetadata', () => {
        if (pendingTime !== undefined && Math.abs(video.currentTime - pendingTime) > 0.05) {
          video.currentTime = pendingTime
        }
        markChapter(pendingTime ?? video.currentTime)
      })
      video.addEventListener('timeupdate', () => {
        if (pendingTime !== undefined) {
          if (Math.abs(video.currentTime - pendingTime) <= 0.25) pendingTime = undefined
          else return
        }
        markChapter(video.currentTime)
      })
      video.addEventListener('seeked', () => {
        const time = pendingTime ?? video.currentTime
        pendingTime = undefined
        markChapter(time)
      })
      videoStage.append(video, chapterNav)
      const transcript = node('details', '', 'film-notes')
      transcript.append(node('summary', 'Narration transcript'))
      for (const { title, speech } of chapters) {
        transcript.append(node('h3', title), node('p', speech))
      }
      reading.replaceChildren(videoStage, transcript, notes)
    }
    reading.prepend(node('h2', note.title))
    if (lesson.quizzes?.length) {
      const qIdx = Math.max(0, stepIndex) % lesson.quizzes.length
      reading.append(renderQuizBlock(lesson, [qIdx], true))
    }
  } else if (tab === 'notes') {
    const list = node('ul', '', 'notes-list')
    for (const item of lesson.notes) {
      const entry = node('li')
      entry.append(link(item.title, lessonURL(lesson.id, item.name)))
      list.append(entry)
    }
    reading.append(node('h2', 'Examples & notes'), list)
  } else {
    renderMarkdown(section.markdown)
    if (section.id === 'learn') mountVisualizerPanel(lesson)
    reading.prepend(node('h2', section.title))
    if (lesson.quizzes?.length) {
      const qIdx = Math.max(0, stepIndex) % lesson.quizzes.length
      reading.append(renderQuizBlock(lesson, [qIdx], true))
    }
  }
  if (editorChapter !== lesson) {
    editor?.destroy()
    editor = undefined
    editorChapter = lesson
    if (lesson.lab) renderEditor(lesson.id)
  }
  if (lesson.lab) updateConsole()
  const previous = sequence[stepIndex - 1]
  const next = sequence[stepIndex + 1]
  const pagination = $('pagination')
  pagination.replaceChildren()
  if (tab === 'notes' || (note && !note.taught)) {
    pagination.append(link('Back to lessons', lessonURL(lesson.id, firstStep(lesson))))
  } else {
    if (previous) pagination.append(link('Previous lesson', lessonURL(lesson.id, previous.id)))
    else if (index > 0) {
      const chapter = course[index - 1]
      pagination.append(link('Previous chapter', lessonURL(chapter.id, steps(chapter).at(-1).id)))
    }
    if (next) pagination.append(link(next.id === 'practice' ? 'Open assignment' : next.id === 'quiz' ? 'Take chapter quiz' : 'Next lesson', lessonURL(lesson.id, next.id)))
    else if (index < course.length - 1) {
      const chapter = course[index + 1]
      pagination.append(link(chapter.lab ? 'Next chapter' : 'Reference library', lessonURL(chapter.id, firstStep(chapter))))
    }
  }
  renderProgress()
}

function renderEditor(id) {
  const chapter = course.find(item => item.id === id)
  editor = new EditorView({
    parent: $('editor'), doc: storage.get('code:' + id) ?? starterFor(chapter),
    extensions: [basicSetup, courseKey === 'cpp' ? cpp() : python(), oneDark, EditorView.lineWrapping,
      EditorView.contentAttributes.of({
        'aria-label': (courseKey === 'cpp' ? 'C++' : 'Python') + ' code', spellcheck: 'false'
      }),
      EditorView.updateListener.of(update => {
        if (update.docChanged) storage.set('code:' + id, update.state.doc.toString())
      })]
  })
  $('filename').textContent = courseKey === 'cpp' ? 'main.cpp' : 'main.py'
  $('workspace').setAttribute('aria-label', (courseKey === 'cpp' ? 'C++' : 'Python') + ' workspace')
  $('output').textContent = statuses.get(id) ??
    (accepted(id) ? 'Accepted on a previous submission.' : 'Run your code to see its output.')
  $('stdin').value = storage.get('input:' + id) ?? ''
}

function updateConsole() {
  const busy = submissions.has(lesson.id) || activeRun?.chapter === lesson
  $('run').disabled = $('check').disabled = busy
  $('output').textContent = statuses.get(lesson.id) ??
    (accepted(lesson.id) ? 'Accepted on a previous submission.' : 'Run your code to see its output.')
}

function run() {
  if (courseKey === 'cpp') return runCpp()
  const code = editor.state.doc.toString()
  if (code.length > 30_000) {
    $('output').textContent = 'Code must be 30,000 characters or fewer.'
    return
  }
  const message = { type: 'run-python', id: ++runId, code, inputs: [$('stdin').value] }
  if (activeRun) statuses.set(activeRun.chapter.id, 'Run canceled when another run started.')
  activeRun = { message, chapter: lesson }
  statuses.set(lesson.id, 'Running Python…')
  updateConsole()
  if (runnerReady) runner.contentWindow.postMessage(message, '*')
}

// C++ has no in-page interpreter: the server compiles and runs one sample case.
async function runCpp() {
  const { id } = lesson
  const code = editor.state.doc.toString()
  if (code.length > 30_000) {
    $('output').textContent = 'Code must be 30,000 characters or fewer.'
    return
  }
  if (!code.trim()) {
    $('output').textContent = 'Write some C++ first.'
    return
  }
  const ticket = ++runId
  if (activeRun) statuses.set(activeRun.chapter.id, 'Run canceled when another run started.')
  activeRun = { message: { id: ticket }, chapter: lesson }
  statuses.set(id, 'Compiling and running with g++…')
  updateConsole()
  try {
    const response = await fetch('/api/run-cpp', {
      method: 'POST', headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ lesson: id, code, sample: 0 })
    })
    const result = await response.json().catch(() => ({}))
    if (activeRun?.message.id !== ticket) return
    statuses.set(id, runVerdict(result, response.ok))
  } catch {
    if (activeRun?.message.id !== ticket) return
    statuses.set(id, verdicts.unavailable)
  } finally {
    if (activeRun?.message.id === ticket) {
      activeRun = undefined
      if (lesson.id === id) updateConsole()
    }
  }
}

function runVerdict(result, ok) {
  if (result?.status === 'unavailable' || !ok && !result?.status) return verdicts.unavailable
  if (result.status === 'ok') {
    const text = [result.output ?? ''].join('').replace(/\s+$/, '')
    return text || 'No output.'
  }
  if (result.status === 'compile_error') {
    return 'Compile error:\n' + (result.message || 'g++ rejected the code.')
  }
  if (result.status === 'runtime_error') return 'Runtime error. Try a different input and check your bounds.'
  return compileVerdicts[result.status] ?? result.error ?? verdicts.unavailable
}

const verdicts = {
  accepted: 'Accepted. Your submission passed the hidden checks.',
  wrong_answer: 'Wrong answer.',
  time_limit: 'Time limit exceeded. Recheck the cost of your approach.',
  memory_limit: 'Memory limit exceeded.',
  runtime_error: 'Runtime error. Try debugging with your own input.',
  output_limit: 'Output limit exceeded.',
  unavailable: 'The submission judge is unavailable. You can still run your own input.'
}
const compileVerdicts = {
  time_limit: 'Time limit exceeded. Recheck the cost of your approach.',
  memory_limit: 'Memory limit exceeded.',
  output_limit: 'Output limit exceeded.',
  unavailable: verdicts.unavailable
}
async function submit() {
  const { id } = lesson
  const code = editor.state.doc.toString()
  if (!code.trim() || code.length > 30_000) {
    $('output').textContent = 'Enter ' + (courseKey === 'cpp' ? 'C++' : 'Python') + ' code of up to 30,000 characters.'
    return
  }
  submissions.add(id)
  statuses.set(id, 'Checking your submission…')
  updateConsole()
  try {
    const response = await fetch('/api/submit', {
      method: 'POST', headers: { 'content-type': 'application/json' },
      body: JSON.stringify(courseKey === 'cpp' ? { lesson: id, code, course: 'cpp' } : { lesson: id, code })
    })
    const result = await response.json()
    if (result.status === 'accepted') storage.set('accepted:' + id, '1')
    const stage = { stress: 'Large-input check. ', correctness: 'Correctness check. ' }[result.stage] ?? ''
    statuses.set(id, stage + (verdicts[result.status] || result.error || verdicts.unavailable))
  } catch {
    statuses.set(id, verdicts.unavailable)
  } finally {
    submissions.delete(id)
    if (lesson.id === id) updateConsole()
    renderProgress()
  }
}

window.addEventListener('message', event => {
  const data = event.data
  if (event.source !== runner.contentWindow || data?.type !== 'python-result' ||
      !activeRun || data.id !== activeRun.message.id) return
  const { chapter } = activeRun
  activeRun = undefined
  const result = data.results?.[0]
  const outputs = result && [result.stdout, result.stderr, result.error]
  const message = outputs?.every(value => typeof value === 'string')
    ? outputs.filter(Boolean).join('\n') || 'No output.'
    : String(data.error || 'The runtime returned an invalid result.')
  statuses.set(chapter.id, message)
  if (lesson === chapter) updateConsole()
})

function renderChat() {
  const history = chats.get(courseKey + ':' + lesson.id) ?? []
  $('conversation').replaceChildren(...history.map(({ who, text }) => {
    const message = node('div', '', who === 'You' ? 'learner-message' : 'tutor-message')
    message.append(node('strong', who), node('p', text))
    return message
  }))
  $('conversation').scrollTop = $('conversation').scrollHeight
}
$('run').onclick = run
$('check').onclick = submit
$('stdin').oninput = () => storage.set('input:' + lesson.id, $('stdin').value)
$('reset').onclick = () => {
  const fresh = starterFor(lesson)
  if (editor.state.doc.toString() === fresh || !confirm('Replace your current code with the starter?')) return
  editor.dispatch({ changes: { from: 0, to: editor.state.doc.length, insert: fresh } })
  editor.focus()
}
$('ask').addEventListener('submit', async event => {
  event.preventDefault()
  const question = $('question').value.trim()
  if (!question) return
  const id = lesson.id
  const chatKey = courseKey + ':' + id
  const history = chats.get(chatKey) ?? []
  const previous = history.filter(item => item.reviewed).map(item => item.text).slice(0, 3)
  history.push({ who: 'You', text: question })
  chats.set(chatKey, history)
  $('question').value = ''
  const button = $('ask').querySelector('button')
  pendingHints.add(id)
  button.disabled = true
  renderChat()
  try {
    const response = await fetch('/api/tutor', {
      method: 'POST', headers: { 'content-type': 'application/json' },
      body: JSON.stringify(courseKey === 'cpp' ? { lesson: id, question, previous, course: 'cpp' } : { lesson: id, question, previous })
    })
    const result = await response.json()
    history.push({ who: 'Tutor', text: result.hint || result.error, reviewed: result.reviewed })
  } catch {
    history.push({ who: 'Tutor', text: 'The tutor is unavailable. Try again in a moment.' })
  } finally {
    pendingHints.delete(id)
    if (lesson.id === id) {
      button.disabled = false
      renderChat()
    }
  }
})
const courses = {}
async function ensureCourse(key) {
  if (!courses[key]) {
    const response = await fetch(key === 'cpp' ? '/course-cpp.json' : '/course.json')
    if (!response.ok) throw new Error('Course unavailable')
    courses[key] = await response.json()
  }
  courseKey = key
  course = courses[key]
  storage.remember(courseKey)
}

window.addEventListener('hashchange', async () => {
  if (!course || location.hash === '#main') return
  const requested = /^#(cpp|python)\//.exec(location.hash)?.[1]
  if (requested && requested !== courseKey) {
    await ensureCourse(requested)
  }
  render()
  if (matches.matches) document.querySelector('.sidebar').open = false
  $('main').focus({ preventScroll: true })
  window.scrollTo(0, 0)
})
try {
  const requested = /^#(cpp|python)\//.exec(location.hash)?.[1]
  const initialKey = requested ?? (storage.shared('course') === 'cpp' ? 'cpp' : 'python')
  await ensureCourse(initialKey)
  for (const button of document.querySelectorAll('.course-switch button')) {
    const mine = button.dataset.course
    button.setAttribute('aria-pressed', String(!isTrainingRoute() && mine === courseKey))
    button.setAttribute('aria-label', 'Study the ' + (mine === 'cpp' ? 'C++20' : 'Python') + ' course')
    // Keep the reader on the same chapter and step in the other language, or exit training back to the course.
    button.onclick = async () => {
      const onTrain = isTrainingRoute()
      if (mine === courseKey && !onTrain) return
      await ensureCourse(mine)
      const currentId = lesson?.id
      const targetChapter = course.find(item => item.id === currentId) ?? course[0]
      const step = !onTrain && lesson && location.hash.split('/').at(-1)
      const targetStep = (!onTrain && targetChapter?.lab && ['practice', 'quiz'].includes(step))
        ? step
        : firstStep(targetChapter)
      const target = '#' + mine + '/' + targetChapter.id + '/' + targetStep
      if (window.location.hash === target) render()
      else window.location.hash = target
      window.scrollTo(0, 0)
      $('main').focus({ preventScroll: true })
    }
  }
  document.querySelector('.course-switch')?.classList.add('is-ready')
  render()
} catch {
  $('title').textContent = 'Could not load the course'
  $('reading').textContent = 'Refresh the page to try again.'
}
