// Deterministic, dependency-free tokenizer for the lesson and chapter code blocks.
// Tokens are classified as keyword, builtin, string, comment, number or plain text;
// the renderer escapes each fragment, so there is no CDN request and no CSP change.

const SHARED_TEXT = ('True False None self').split(' ')

const LANGUAGES = {
  python: {
    keywords: ('and as assert async await break class continue def del elif else except finally for from global '
      + 'if import in is lambda match nonlocal not or pass raise return try while with yield case').split(' '),
    builtins: (SHARED_TEXT.join(' ') + ' abs all any bin bool bytes callable chr dict divmod enumerate filter float format '
      + 'frozenset getattr hasattr hash hex id input int isinstance iter len list map max min next object oct open ord '
      + 'pow print range repr reversed round set setattr slice sorted str sum tuple type zip Exception ValueError '
      + 'IndexError KeyError StopIteration TypeError RuntimeError ZeroDivisionError NotImplementedError collections '
      + 'deque defaultdict Counter heapq bisect math sys itertools functools lru_cache reduce').split(' '),
    tripleQuotes: true
  },
  cpp: {
    keywords: ('alignas alignof auto bool break case catch char class const constexpr const_cast continue default '
      + 'delete do double dynamic_cast else enum explicit export extern float for friend goto if inline int long '
      + 'mutable namespace new noexcept nullptr operator private protected public register reinterpret_cast return '
      + 'short signed sizeof static static_assert static_cast struct switch template this throw try typedef typename '
      + 'union unsigned using virtual void volatile while').split(' '),
    builtins: (SHARED_TEXT.join(' ') + ' std cout cin cerr endl vector map set unordered_map unordered_set pair queue '
      + 'priority_queue stack deque string sort min max swap push_back emplace_back lower_bound upper_bound size_t '
      + 'int64_t uint64_t printf scanf memset fill accumulate begin end').split(' '),
    tripleQuotes: false,
    blockComments: true
  }
}

const ALIASES = { py: 'python', python3: 'python', cxx: 'cpp', 'c++': 'cpp', c: 'cpp' }
const WORD = /[A-Za-z_][A-Za-z0-9_]*/y
const NUMBER = /\d[\d_]*(?:\.\d+)?/y

// Maps a fence info string (```python) to a known language; anything else renders as plain text.
export function detectLanguage(info) {
  const key = String(info ?? '').trim().toLowerCase().split(/\s+/)[0]
  const language = ALIASES[key] ?? key
  return LANGUAGES[language] ? language : 'code'
}

export function languageBadge(language) {
  return { python: 'PYTHON', cpp: 'C++' }[language] ?? 'CODE'
}

function rawTokens(source) {
  const tokens = []
  const text = String(source ?? '')
  let index = 0
  const push = (type, value) => tokens.push({ type, text: value })
  while (index < text.length) {
    const char = text[index]
    if (char === '#') {
      const stop = text.indexOf('\n', index)
      push('comment', text.slice(index, stop < 0 ? text.length : stop))
      index = stop < 0 ? text.length : stop
      continue
    }
    if (char === '/' && text[index + 1] === '*') {
      const stop = text.indexOf('*/', index + 2)
      push('comment', text.slice(index, stop < 0 ? text.length : stop + 2))
      index = stop < 0 ? text.length : stop + 2
      continue
    }
    if (char === '/' && text[index + 1] === '/') {
      const stop = text.indexOf('\n', index)
      push('comment', text.slice(index, stop < 0 ? text.length : stop))
      index = stop < 0 ? text.length : stop
      continue
    }
    if (char === '"' || char === "'") {
      const triple = text.slice(index, index + 3) === char.repeat(3)
      const stop = triple ? char.repeat(3) : char
      let end = index + stop.length
      while (end < text.length) {
        if (text[end] === '\\') { end += 2; continue }
        if (text.startsWith(stop, end)) { end += stop.length; break }
        end++
      }
      push('string', text.slice(index, Math.min(end, text.length)))
      index = Math.min(end, text.length)
      continue
    }
    if (char >= '0' && char <= '9') {
      NUMBER.lastIndex = index
      const match = NUMBER.exec(text)
      push('number', match ? match[0] : char)
      index += match ? match[0].length : 1
      continue
    }
    WORD.lastIndex = index
    const word = WORD.exec(text)
    if (word) {
      push(null, word[0])
      index += word[0].length
      continue
    }
    push(null, char)
    index++
  }
  return tokens
}

export function highlight(source, language = 'code') {
  const table = LANGUAGES[language]
  const tokens = rawTokens(source)
  if (!table) return tokens
  const keyword = new Set(table.keywords)
  const builtin = new Set(table.builtins)
  let previous = null
  for (const token of tokens) {
    if (!/^[A-Za-z_]/.test(token.text)) continue
    const lower = token.text.toLowerCase()
    if (keyword.has(lower)) token.type = 'keyword'
    else if (builtin.has(lower)) token.type = 'builtin'
    previous = token.text
  }
  return tokens
}

export function escapeHTML(text) {
  return String(text).replace(/[&<>"]/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[char])
}

export function highlightHTML(source, language = 'code') {
  return highlight(source, language).map(token => {
    const html = escapeHTML(token.text)
    return token.type ? '<span class="tok-' + token.type + '">' + html + '</span>' : html
  }).join('')
}