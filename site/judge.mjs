import { execFile, spawn } from 'node:child_process'
import { randomUUID } from 'node:crypto'
import { promisify } from 'node:util'
import { privateCases } from './judge-cases.mjs'

const docker = promisify(execFile)
const bootstrap = [
  'import base64, io, sys',
  'wire = sys.stdin.buffer',
  'source = base64.b64decode(wire.readline())',
  'size = int(wire.readline())',
  'sys.stdin = io.TextIOWrapper(io.BytesIO(wire.read(size)), encoding="utf-8")',
  'exec(compile(source, "main.py", "exec"), {"__name__": "__main__"})'
].join('\n')
const cppBootstrap = [
  'mkdir -p /tmp/comprog',
  'cd /tmp/comprog',
  'base64 -d > main.cpp',
  '/usr/bin/g++ -O2 -std=gnu++20 -o main main.cpp 2> build.log || { cat build.log >&2; exit 42; }',
  'head -n 1 build.log >&2',
  './main'
].join('\n')
const maxOutput = 4 * 1024 * 1024
const sources = { python: 'main.py', cpp: 'main.cpp' }

async function runContainer(code, input, image, { language = 'python', timeout = 3500 } = {}) {
  const name = 'comprog-case-' + randomUUID()
  const proc = language === 'cpp'
    ? ['--entrypoint', 'sh', image, '-c', cppBootstrap]
    : ['--entrypoint', 'python', image, '-I', '-B', '-c', bootstrap]
  try {
    await docker('docker', [
      'create', '--name', name, '--pull', 'never', '-i', '--network', 'none', '--ipc', 'none',
      '--read-only', '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges=true',
      '--memory', '256m', '--memory-swap', '256m', '--cpus', '1', '--pids-limit', '32',
      '--ulimit', 'nofile=64:64', '--user', '65534:65534', '--log-driver', 'none',
      ...proc
    ], { timeout: 10_000, windowsHide: true })
    return await new Promise(resolve => {
      const child = spawn('docker', ['start', '-ai', name], { windowsHide: true })
      const chunks = []
      const errors = []
      let bytes = 0
      let forced
      const stop = status => {
        forced ??= status
        child.kill()
      }
      const timer = setTimeout(() => stop('time_limit'), timeout)
      child.stdout.on('data', chunk => {
        bytes += chunk.length
        if (bytes > maxOutput) stop('output_limit')
        else chunks.push(chunk)
      })
      child.stderr.on('data', chunk => {
        bytes += chunk.length
        if (bytes > maxOutput) stop('output_limit')
        else if (errors.length < 64) errors.push(chunk)
      })
      child.stdin.on('error', () => {})
      child.on('error', () => { forced = 'unavailable' })
      child.on('close', async exit => {
        clearTimeout(timer)
        if (forced) return resolve({ status: forced })
        try {
          const { stdout } = await docker('docker', ['inspect', '--format', '{{.State.Status}} {{.State.ExitCode}} {{.State.OOMKilled}}', name], { timeout: 4000, windowsHide: true })
          const [state, exitCode, oom] = stdout.trim().split(' ')
          if (state !== 'exited') return resolve({ status: 'unavailable' })
          if (oom === 'true') return resolve({ status: 'memory_limit' })
          if (exit !== 0 || exitCode !== '0') {
            const diagnostic = Buffer.concat(errors).toString('utf8')
            if (language === 'cpp' && exitCode === '42' && diagnostic.includes(': error:')) {
              return resolve({ status: 'compile_error', message: sanitize(diagnostic, code) })
            }
            return resolve({ status: 'runtime_error' })
          }
          return resolve({ status: 'ok', output: Buffer.concat(chunks).toString('utf8') })
        } catch {
          return resolve({ status: 'unavailable' })
        }
      })
      const data = input + '\n'
      child.stdin.end(Buffer.from(code).toString('base64') + '\n' + Buffer.byteLength(data) + '\n' + data)
    })
  } catch {
    return { status: 'unavailable' }
  } finally {
    await docker('docker', ['rm', '-f', name], { timeout: 7000, windowsHide: true }).catch(() => {})
  }
}

// Submission text as the compiler sees it, so diagnostics can be filtered of judge noise.
function errorText(code) {
  return code
}

function sanitize(diagnostic, code) {
  const source = code.replace(/\r\n/g, '\n').split('\n')
  const lines = diagnostic.replace(/\r\n/g, '\n').replace(/\x1b\[[0-9;]*m/g, '').split('\n')
  const kept = []
  for (const line of lines) {
    const where = /^main\.cpp:(\d+):\d+: /.exec(line)
    if (where) {
      const text = source[Number(where[1]) - 1]
      kept.push(text === undefined ? line : line + '\n  ' + text.trim())
    } else if (/^\s*\^|^\s*\|/.test(line) && kept.length) {
      kept[kept.length - 1] += '\n' + line
    }
  }
  let message = [...new Set(kept)].slice(0, 8).join('\n')
  if (message.length > 1500) message = message.slice(0, 1500) + '\n…'
  return message || lines.filter(line => line.trim()).slice(0, 8).join('\n')
}

const normalize = output => output.trim().split(/\r?\n/).map(line => line.trim().replace(/[ \t]+/g, ' ')).join('\n')

export async function judgeSubmission(index, lab, code, {
  image = process.env.JUDGE_IMAGE,
  run = runContainer,
  language = 'python',
  timeout = language === 'cpp' ? 7000 : 3500
} = {}) {
  if (!image) return { status: 'unavailable' }
  for (const { input, expected, stress } of privateCases(index, lab)) {
    const result = await run(code, input, image, { language, timeout })
    if (result.status === 'unavailable') return { status: 'unavailable' }
    if (result.status === 'compile_error') return { status: 'compile_error', message: result.message }
    if (result.status !== 'ok') return { status: result.status, stage: stress ? 'stress' : 'correctness' }
    if (normalize(result.output) !== normalize(expected)) {
      return { status: 'wrong_answer', stage: stress ? 'stress' : 'correctness' }
    }
  }
  return { status: 'accepted' }
}

const compileOnly = [
  'mkdir -p /tmp/comprog',
  'cd /tmp/comprog',
  'base64 -d > main.cpp',
  '/usr/bin/g++ -O2 -std=gnu++20 -o main main.cpp'
].join('\n')

async function compileContainer(code, image) {
  const name = 'comprog-build-' + randomUUID()
  try {
    await docker('docker', [
      'create', '--name', name, '--pull', 'never', '--network', 'none', '--ipc', 'none',
      '--read-only', '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges=true',
      '--memory', '512m', '--memory-swap', '512m', '--cpus', '1', '--pids-limit', '64',
      '--ulimit', 'nofile=64:64', '--user', '65534:65534', '--log-driver', 'none',
      '--entrypoint', 'sh', image, '-c', compileOnly
    ], { timeout: 10_000, windowsHide: true })
    const { stdout, stderr, exit } = await docker('docker', ['start', '-a', name], {
      timeout: 20_000, windowsHide: true, maxBuffer: 2 * 1024 * 1024
    }).catch(error => ({ stdout: '', stderr: String(error.stderr ?? ''), exit: 1 }))
    if (exit === 0 && !stderr.trim()) return { status: 'ok' }
    await docker('docker', ['cp', name + ':/tmp/comprog/main', ':'], { windowsHide: true }).catch(() => {})
    const diagnostic = stderr || stdout
    return { status: 'compile_error', message: sanitize(diagnostic, code) }
  } catch {
    return { status: 'unavailable' }
  } finally {
    await docker('docker', ['rm', '-f', name], { timeout: 7000, windowsHide: true }).catch(() => {})
  }
}

export async function judgeCppSubmission(index, lab, code, {
  image = process.env.CPP_JUDGE_IMAGE,
  run = runContainer,
  build = compileContainer
} = {}) {
  if (!image) return { status: 'unavailable' }
  const compiled = await build(code, image)
  if (compiled.status !== 'ok') return compiled
  for (const { input, expected, stress } of privateCases(index, lab)) {
    const result = await run(code, input, image, { language: 'cpp' })
    if (result.status === 'unavailable') return { status: 'unavailable' }
    if (result.status === 'compile_error') return { status: 'compile_error', message: result.message }
    if (result.status !== 'ok') return { status: result.status, stage: stress ? 'stress' : 'correctness' }
    if (normalize(result.output) !== normalize(expected)) {
      return { status: 'wrong_answer', stage: stress ? 'stress' : 'correctness' }
    }
  }
  return { status: 'accepted' }
}

// One case through the C++ path: sample input, stdout back to the browser.
export async function runCpp(code, input, { image = process.env.CPP_JUDGE_IMAGE, run = runContainer } = {}) {
  if (!image) return { status: 'unavailable' }
  const result = await run(code, input, image, { language: 'cpp' })
  if (result.status === 'compile_error') return { status: 'compile_error', message: result.message }
  return result
}

export { sources }