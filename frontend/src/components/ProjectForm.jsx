import { useEffect, useState } from 'react'
import { Save } from 'lucide-react'
import { ML_METHODS, DL_METHODS, AGENT_TYPES, AUTOMATION_TYPES } from '../data/menuData'

const METHODS_BY_CATEGORY = {
  'machine-learning': ML_METHODS,
  'deep-learning': DL_METHODS,
  'ai-agent': AGENT_TYPES,
  automation: AUTOMATION_TYPES,
}

const EMPTY_PROJECT = {
  title: '', slug: '', category_id: '', method_or_algorithm: '',
  short_description: '', problem_statement: '', dataset_description: '',
  business_use_case: '', workflow_steps: '', tools_used: '', technologies_used: '',
  evaluation_metrics: '', results: '', key_learning: '',
  difficulty_level: 'Beginner', status: 'Completed',
  github_url: '', demo_url: '', dataset_url: '', image_url: '',
}

const slugify = (text) =>
  text.toLowerCase().trim().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '')

export default function ProjectForm({ categories, initialData, onSubmit, submitLabel = 'Save Project' }) {
  const [form, setForm] = useState({ ...EMPTY_PROJECT, ...initialData })
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    if (initialData) setForm({ ...EMPTY_PROJECT, ...initialData })
  }, [initialData])

  const update = (field) => (e) => {
    const value = e.target.value
    setForm((prev) => {
      const next = { ...prev, [field]: value }
      if (field === 'title' && !initialData) next.slug = slugify(value)
      return next
    })
  }

  const selectedCategory = categories?.find((c) => c.id === Number(form.category_id))
  const methodOptions = selectedCategory ? METHODS_BY_CATEGORY[selectedCategory.slug] || [] : []

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSaving(true)
    try {
      await onSubmit({ ...form, category_id: Number(form.category_id) })
    } finally {
      setSaving(false)
    }
  }

  const textArea = (field, label, rows = 3) => (
    <div>
      <label className="text-sm text-slate-400 mb-1 block">{label}</label>
      <textarea rows={rows} className="input-field" value={form[field] || ''} onChange={update(field)} />
    </div>
  )

  return (
    <form onSubmit={handleSubmit} className="glass-card p-6 flex flex-col gap-5">
      <div className="grid sm:grid-cols-2 gap-5">
        <div>
          <label className="text-sm text-slate-400 mb-1 block">Title *</label>
          <input required className="input-field" value={form.title} onChange={update('title')} />
        </div>
        <div>
          <label className="text-sm text-slate-400 mb-1 block">Slug *</label>
          <input required className="input-field" value={form.slug} onChange={update('slug')} />
        </div>
        <div>
          <label className="text-sm text-slate-400 mb-1 block">Category *</label>
          <select required className="input-field" value={form.category_id} onChange={update('category_id')}>
            <option value="">Select category</option>
            {categories?.map((c) => (
              <option key={c.id} value={c.id}>{c.name}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="text-sm text-slate-400 mb-1 block">Method / Algorithm *</label>
          <input
            required
            list="method-options"
            className="input-field"
            value={form.method_or_algorithm}
            onChange={update('method_or_algorithm')}
            placeholder="e.g. Random Forest"
          />
          <datalist id="method-options">
            {methodOptions.map((m) => <option key={m} value={m} />)}
          </datalist>
        </div>
        <div>
          <label className="text-sm text-slate-400 mb-1 block">Difficulty Level</label>
          <select className="input-field" value={form.difficulty_level} onChange={update('difficulty_level')}>
            <option>Beginner</option>
            <option>Intermediate</option>
            <option>Advanced</option>
          </select>
        </div>
        <div>
          <label className="text-sm text-slate-400 mb-1 block">Status</label>
          <select className="input-field" value={form.status} onChange={update('status')}>
            <option>Completed</option>
            <option>In Progress</option>
          </select>
        </div>
      </div>

      {textArea('short_description', 'Short Description *', 2)}
      {textArea('problem_statement', 'Problem Statement')}
      {textArea('dataset_description', 'Dataset Description')}
      {textArea('business_use_case', 'Business Use Case')}
      {textArea('workflow_steps', 'Step-by-Step Workflow (use -> between steps)')}

      <div className="grid sm:grid-cols-2 gap-5">
        <div>
          <label className="text-sm text-slate-400 mb-1 block">Tools Used (comma separated)</label>
          <input className="input-field" value={form.tools_used} onChange={update('tools_used')} />
        </div>
        <div>
          <label className="text-sm text-slate-400 mb-1 block">Technologies Used (comma separated)</label>
          <input className="input-field" value={form.technologies_used} onChange={update('technologies_used')} />
        </div>
      </div>

      {textArea('evaluation_metrics', 'Evaluation Metrics', 2)}
      {textArea('results', 'Results', 2)}
      {textArea('key_learning', 'Key Learning', 2)}

      <div className="grid sm:grid-cols-2 gap-5">
        <div>
          <label className="text-sm text-slate-400 mb-1 block">GitHub URL</label>
          <input className="input-field" value={form.github_url} onChange={update('github_url')} />
        </div>
        <div>
          <label className="text-sm text-slate-400 mb-1 block">Live Demo URL</label>
          <input className="input-field" value={form.demo_url} onChange={update('demo_url')} />
        </div>
        <div>
          <label className="text-sm text-slate-400 mb-1 block">Dataset URL</label>
          <input className="input-field" value={form.dataset_url} onChange={update('dataset_url')} />
        </div>
        <div>
          <label className="text-sm text-slate-400 mb-1 block">Image URL</label>
          <input className="input-field" value={form.image_url} onChange={update('image_url')} />
        </div>
      </div>

      <button type="submit" disabled={saving} className="btn-primary justify-center disabled:opacity-60">
        <Save size={18} /> {saving ? 'Saving...' : submitLabel}
      </button>
    </form>
  )
}
