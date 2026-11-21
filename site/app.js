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
  const nav = $('outline')
  $qs('.course-name').textContent = courseKey === 'cpp'
    ? 'Competitive programming in C++20' : 'Competitive programming in Python'
  if (!nav.children.length) {
    for (const item of course) {
      const group = node('details', '', 'chapter-group')
      group.append(node('summary', item.title))
      for (const step of [...steps(item), { id: 'notes', title: 'Examples & notes' }]) {
        group.append(link(step.title, lessonURL(item.id, step.id)))
      }
      nav.append(group)
    }
  }
  const route = lessonURL(lesson.id, storage.get('step:' + lesson.id) || firstStep(lesson))
  for (const [index, group] of Array.from(nav.children).entries()) {
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

function render() {
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
  reading.classList.remove('panel-enter')
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
window.addEventListener('hashchange', () => {
  if (!course || location.hash === '#main') return
  render()
  if (matches.matches) document.querySelector('.sidebar').open = false
  $('main').focus({ preventScroll: true })
  window.scrollTo(0, 0)
})
try {
  const requested = /^#(cpp|python)\//.exec(location.hash)?.[1]
  courseKey = requested ?? (storage.shared('course') === 'cpp' ? 'cpp' : 'python')
  storage.remember(courseKey)
  const response = await fetch(courseFile())
  if (!response.ok) throw new Error('Course unavailable')
  course = await response.json()
  for (const button of document.querySelectorAll('.course-switch button')) {
    const mine = button.dataset.course
    button.setAttribute('aria-pressed', String(mine === courseKey))
    button.setAttribute('aria-label', 'Study the ' + (mine === 'cpp' ? 'C++20' : 'Python') + ' course')
    // Keep the reader on the same chapter and step in the other language.
    button.onclick = () => {
      if (mine === courseKey) return
      const step = lesson && location.hash.split('/').at(-1)
      const target = lesson?.lab && ['practice', 'quiz'].includes(step)
        ? otherLessonURL(lesson.id, step)
        : '#' + mine + '/' + (lesson?.id ?? course[0].id) + '/' + firstStep(lesson ?? course[0])
      window.location.hash = target
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
