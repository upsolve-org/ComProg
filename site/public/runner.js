// The iframe has an opaque origin. Only this wrapper can post results to its parent.
let worker
let timer

function stop() {
  clearTimeout(timer)
  worker?.terminate()
  worker = undefined
}

const workerSource = function () {
  const runtime = 'https://cdn.jsdelivr.net/pyodide/v0.28.3/full/'
  function run(py, code, input) {
    py.globals.set('_source', code)
    py.globals.set('_input', input)
    const result = py.runPython([
      'import io, sys, traceback',
      'class Output(io.StringIO):',
      '    def write(self, text):',
      '        if self.tell() + len(text) > 12000:',
      '            raise RuntimeError("Output limit exceeded")',
      '        return super().write(text)',
      '_out, _err = Output(), Output()',
      '_streams = sys.stdin, sys.stdout, sys.stderr',
      'sys.stdin, sys.stdout, sys.stderr = io.StringIO(_input + "\\n"), _out, _err',
      '_error = ""',
      'try:',
      '    exec(compile(_source, "main.py", "exec"), {"__name__": "__main__"})',
      'except SystemExit as exc:',
      '    if exc.code not in (None, 0):',
      '        _error = str(exc)',
      'except BaseException:',
      '    _error = traceback.format_exc(limit=4)',
      'finally:',
      '    sys.stdin, sys.stdout, sys.stderr = _streams',
      '[_out.getvalue(), _err.getvalue(), _error]'
    ].join('\n'))
    const [stdout, stderr, error] = result.toJs()
    result.destroy()
    return { stdout, stderr, error }
  }

  self.onmessage = async ({ data }) => {
    try {
      importScripts(runtime + 'pyodide.js')
      const py = await loadPyodide({ indexURL: runtime })
      postMessage({ ready: true })
      postMessage({ results: data.inputs.map(input => run(py, data.code, input)) })
    } catch (error) {
      postMessage({ error: String(error.message || error).slice(0, 900) })
    }
  }
}

const blob = URL.createObjectURL(new Blob(['(' + workerSource.toString() + ')()'], { type: 'text/javascript' }))

window.addEventListener('message', event => {
  if (event.source !== parent || event.data?.type !== 'run-python') return
  const { id, code, inputs } = event.data
  stop()
  const respond = result => {
    stop()
    parent.postMessage({ type: 'python-result', id, ...result }, event.origin)
  }
  worker = new Worker(blob)
  worker.onerror = () => respond({ error: 'The Python runtime could not start.' })
  worker.onmessage = ({ data }) => {
    if (data.ready) {
      clearTimeout(timer)
      timer = setTimeout(() => respond({ error: 'Execution timed out. Check your loop or input size.' }), 5000)
    } else {
      respond(data)
    }
  }
  timer = setTimeout(() => respond({ error: 'Python took too long to load. Check your connection and try again.' }), 45000)
  worker.postMessage({ code, inputs })
})
