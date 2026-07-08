import { useEffect, useRef, useState } from 'react'
import { Download, FlaskConical, LineChart, Loader2, RotateCcw } from 'lucide-react'
import api from '../services/api'
import { getDemoSchema, runDemoPredict } from '../services/demoService'

const GRID = 8
const CELL = 24 // canvas is 192x192, downsampled to 8x8

function DigitCanvas({ canvasRef }) {
  const drawing = useRef(false)

  useEffect(() => {
    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')
    ctx.fillStyle = '#0b1120'
    ctx.fillRect(0, 0, canvas.width, canvas.height)
  }, [canvasRef])

  const stroke = (e) => {
    if (!drawing.current) return
    const canvas = canvasRef.current
    const rect = canvas.getBoundingClientRect()
    const x = ((e.touches ? e.touches[0].clientX : e.clientX) - rect.left) * (canvas.width / rect.width)
    const y = ((e.touches ? e.touches[0].clientY : e.clientY) - rect.top) * (canvas.height / rect.height)
    const ctx = canvas.getContext('2d')
    ctx.fillStyle = '#f8fafc'
    ctx.beginPath()
    ctx.arc(x, y, CELL * 0.75, 0, Math.PI * 2)
    ctx.fill()
  }

  const clear = () => {
    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')
    ctx.fillStyle = '#0b1120'
    ctx.fillRect(0, 0, canvas.width, canvas.height)
  }

  return (
    <div className="flex flex-col items-start gap-2">
      <canvas
        ref={canvasRef}
        width={GRID * CELL}
        height={GRID * CELL}
        className="rounded-xl border border-slate-700 cursor-crosshair touch-none"
        style={{ width: 192, height: 192 }}
        onMouseDown={(e) => { drawing.current = true; stroke(e) }}
        onMouseMove={stroke}
        onMouseUp={() => { drawing.current = false }}
        onMouseLeave={() => { drawing.current = false }}
        onTouchStart={(e) => { drawing.current = true; stroke(e) }}
        onTouchMove={(e) => { e.preventDefault(); stroke(e) }}
        onTouchEnd={() => { drawing.current = false }}
      />
      <button type="button" onClick={clear} className="text-xs text-slate-400 hover:text-white inline-flex items-center gap-1">
        <RotateCcw size={12} /> Clear canvas
      </button>
    </div>
  )
}

function readDigitPixels(canvas) {
  const ctx = canvas.getContext('2d')
  const { data } = ctx.getImageData(0, 0, canvas.width, canvas.height)
  const pixels = []
  for (let gy = 0; gy < GRID; gy++) {
    for (let gx = 0; gx < GRID; gx++) {
      let sum = 0
      for (let y = 0; y < CELL; y++) {
        for (let x = 0; x < CELL; x++) {
          const idx = (((gy * CELL + y) * canvas.width) + gx * CELL + x) * 4
          sum += data[idx] // red channel: background ~11, ink ~248
        }
      }
      const mean = sum / (CELL * CELL)
      pixels.push(Math.max(0, Math.min(16, ((mean - 11) / (248 - 11)) * 16)))
    }
  }
  return pixels
}

const toneStyles = {
  good: 'text-emerald-400 border-emerald-400/30 bg-emerald-400/10',
  bad: 'text-rose-400 border-rose-400/30 bg-rose-400/10',
  neutral: 'text-amber-300 border-amber-300/30 bg-amber-300/10',
  info: 'text-accent-cyan border-accent-cyan/30 bg-accent-cyan/10',
}

export default function DemoPanel({ slug }) {
  const [schema, setSchema] = useState(null)
  const [values, setValues] = useState({})
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [busy, setBusy] = useState(false)
  const canvasRef = useRef(null)

  useEffect(() => {
    setSchema(null)
    setResult(null)
    setError(null)
    getDemoSchema(slug)
      .then((s) => {
        setSchema(s)
        const defaults = {}
        s.fields.forEach((f) => { if (f.default !== undefined) defaults[f.name] = f.default })
        setValues(defaults)
      })
      .catch(() => setSchema(null)) // 404 → no demo for this project
  }, [slug])

  if (!schema) return null

  const set = (name, value) => setValues((v) => ({ ...v, [name]: value }))

  const submit = async (e) => {
    e.preventDefault()
    setBusy(true)
    setError(null)
    setResult(null)
    try {
      const inputs = { ...values }
      const canvasField = schema.fields.find((f) => f.type === 'digit_canvas')
      if (canvasField && canvasRef.current) {
        inputs[canvasField.name] = readDigitPixels(canvasRef.current)
      }
      setResult(await runDemoPredict(slug, inputs))
    } catch (err) {
      setError(err.response?.data?.detail || 'Prediction failed — is the backend running?')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="glass-card p-6 mt-10 border !border-accent-purple/40">
      <div className="flex items-center gap-2 mb-1">
        <FlaskConical size={18} className="text-accent-purple" />
        <h3 className="font-bold text-white">Live Demo</h3>
        <span className="badge !text-emerald-400 !border-emerald-400/30 ml-2">real trained model</span>
      </div>
      <p className="text-sm text-slate-400 mb-5">{schema.title}</p>

      <form onSubmit={submit} className="grid sm:grid-cols-2 gap-4">
        {schema.fields.map((f) => (
          <label key={f.name} className={`flex flex-col gap-1.5 text-sm text-slate-300 ${['textarea', 'digit_canvas', 'image_choice'].includes(f.type) ? 'sm:col-span-2' : ''}`}>
            <span className="font-medium">{f.label}</span>
            {f.type === 'number' && (
              <input
                type="number"
                value={values[f.name] ?? ''}
                min={f.min} max={f.max} step={f.step}
                onChange={(e) => set(f.name, e.target.value === '' ? '' : Number(e.target.value))}
                className="bg-slate-900/60 border border-slate-700 rounded-xl px-3 py-2 text-white focus:border-accent-purple focus:outline-none"
                required
              />
            )}
            {f.type === 'select' && (
              <select
                value={values[f.name]}
                onChange={(e) => {
                  const opt = f.options.find((o) => String(o.value) === e.target.value)
                  set(f.name, opt ? opt.value : e.target.value)
                }}
                className="bg-slate-900/60 border border-slate-700 rounded-xl px-3 py-2 text-white focus:border-accent-purple focus:outline-none"
              >
                {f.options.map((o) => (
                  <option key={String(o.value)} value={String(o.value)}>{o.label}</option>
                ))}
              </select>
            )}
            {f.type === 'textarea' && (
              <textarea
                value={values[f.name] ?? ''}
                onChange={(e) => set(f.name, e.target.value)}
                rows={4}
                className="bg-slate-900/60 border border-slate-700 rounded-xl px-3 py-2 text-white focus:border-accent-purple focus:outline-none resize-y"
                required
              />
            )}
            {f.type === 'digit_canvas' && <DigitCanvas canvasRef={canvasRef} />}
            {f.type === 'image_choice' && (
              <div className="flex flex-wrap gap-2">
                {f.options.map((o) => (
                  <button
                    key={String(o.value)}
                    type="button"
                    onClick={() => set(f.name, o.value)}
                    className={`rounded-lg overflow-hidden border-2 transition-colors ${values[f.name] === o.value ? 'border-accent-purple' : 'border-slate-700 hover:border-slate-500'}`}
                    title={o.label}
                  >
                    <img
                      src={o.image}
                      alt={o.label}
                      className="w-16 h-16 object-cover"
                      style={{ imageRendering: 'pixelated' }}
                    />
                  </button>
                ))}
              </div>
            )}
            {f.help && <span className="text-xs text-slate-500">{f.help}</span>}
          </label>
        ))}

        <div className="sm:col-span-2 flex flex-wrap items-center gap-3">
          <button type="submit" disabled={busy} className="btn-primary disabled:opacity-60">
            {busy ? <Loader2 size={16} className="animate-spin" /> : <FlaskConical size={16} />}
            {schema.cta}
          </button>
          {schema.dataset_url && (
            <a
              href={`${api.defaults.baseURL}${schema.dataset_url}`}
              className="btn-secondary"
              title="Download the dataset this model was trained on"
            >
              <Download size={16} /> Training data (CSV)
            </a>
          )}
        </div>
      </form>

      {error && (
        <div className="mt-4 text-sm text-rose-400 bg-rose-400/10 border border-rose-400/30 rounded-xl px-4 py-3">
          {error}
        </div>
      )}

      {result && (
        <div className={`mt-5 rounded-xl border px-5 py-4 ${toneStyles[result.tone] || toneStyles.info}`}>
          <div className="font-bold text-base">{result.headline}</div>
          {typeof result.confidence === 'number' && (
            <div className="mt-2">
              <div className="h-1.5 rounded-full bg-slate-700/60 overflow-hidden">
                <div className="h-full rounded-full bg-current" style={{ width: `${Math.round(result.confidence * 100)}%` }} />
              </div>
              <div className="text-xs mt-1 opacity-80">confidence {Math.round(result.confidence * 100)}%</div>
            </div>
          )}
          {result.details?.length > 0 && (
            <dl className="mt-3 space-y-1.5">
              {result.details.map((d) => (
                <div key={d.label} className="flex gap-2 text-sm">
                  <dt className="text-slate-300 font-medium shrink-0">{d.label}:</dt>
                  <dd className="text-slate-400">{d.value}</dd>
                </div>
              ))}
            </dl>
          )}
        </div>
      )}

      {schema.evaluation_url && (
        <div className="mt-8 border-t border-white/10 pt-6">
          <div className="flex items-center gap-2 mb-1">
            <LineChart size={18} className="text-accent-cyan" />
            <h3 className="font-bold text-white">Model Evaluation</h3>
          </div>
          {schema.evaluation_caption && (
            <p className="text-sm text-slate-400 mb-4">{schema.evaluation_caption}</p>
          )}
          <img
            src={`${api.defaults.baseURL}${schema.evaluation_url}`}
            alt="Model evaluation graph"
            className="rounded-xl border border-slate-700 w-full max-w-3xl"
          />
        </div>
      )}
    </div>
  )
}
