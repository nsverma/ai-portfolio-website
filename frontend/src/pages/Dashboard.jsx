import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { Pencil, Trash2, Plus } from 'lucide-react'
import DashboardLayout from '../components/DashboardLayout'
import Loader from '../components/Loader'
import { deleteProject, getCategories, getProjects } from '../services/projectService'

export default function Dashboard() {
  const [projects, setProjects] = useState([])
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(true)
  const [categoryFilter, setCategoryFilter] = useState('')
  const [methodFilter, setMethodFilter] = useState('')

  const load = () => {
    setLoading(true)
    Promise.all([getProjects(), getCategories()])
      .then(([p, c]) => { setProjects(p); setCategories(c) })
      .finally(() => setLoading(false))
  }

  useEffect(load, [])

  const methods = useMemo(
    () => [...new Set(projects.map((p) => p.method_or_algorithm))].sort(),
    [projects]
  )

  const filtered = projects.filter((p) => {
    const matchCategory = !categoryFilter || p.category?.slug === categoryFilter
    const matchMethod = !methodFilter || p.method_or_algorithm === methodFilter
    return matchCategory && matchMethod
  })

  const handleDelete = async (id) => {
    if (!confirm('Delete this project? This cannot be undone.')) return
    await deleteProject(id)
    load()
  }

  return (
    <DashboardLayout>
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <h1 className="text-2xl font-bold text-white">All Projects</h1>
        <Link to="/dashboard/new" className="btn-primary">
          <Plus size={16} /> Add New Project
        </Link>
      </div>

      <div className="flex flex-wrap gap-3 mb-6">
        <select className="input-field !py-2 w-48" value={categoryFilter} onChange={(e) => setCategoryFilter(e.target.value)}>
          <option value="">All Categories</option>
          {categories.map((c) => <option key={c.id} value={c.slug}>{c.name}</option>)}
        </select>
        <select className="input-field !py-2 w-56" value={methodFilter} onChange={(e) => setMethodFilter(e.target.value)}>
          <option value="">All Methods</option>
          {methods.map((m) => <option key={m} value={m}>{m}</option>)}
        </select>
      </div>

      {loading ? (
        <Loader />
      ) : (
        <div className="glass-card overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-slate-500 border-b border-white/10">
                <th className="px-4 py-3 font-medium">Title</th>
                <th className="px-4 py-3 font-medium">Category</th>
                <th className="px-4 py-3 font-medium">Method</th>
                <th className="px-4 py-3 font-medium">Status</th>
                <th className="px-4 py-3 font-medium">Difficulty</th>
                <th className="px-4 py-3 font-medium text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((p) => (
                <tr key={p.id} className="border-b border-white/5 hover:bg-white/[0.03]">
                  <td className="px-4 py-3 text-white font-medium">{p.title}</td>
                  <td className="px-4 py-3 text-slate-400">{p.category?.name}</td>
                  <td className="px-4 py-3 text-slate-400">{p.method_or_algorithm}</td>
                  <td className="px-4 py-3">
                    <span className={`badge !py-0.5 ${p.status === 'Completed' ? '!text-emerald-400 !border-emerald-400/30' : '!text-amber-400 !border-amber-400/30'}`}>
                      {p.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-slate-400">{p.difficulty_level}</td>
                  <td className="px-4 py-3">
                    <div className="flex justify-end gap-2">
                      <Link to={`/dashboard/edit/${p.id}`} className="btn-secondary !p-2">
                        <Pencil size={14} />
                      </Link>
                      <button onClick={() => handleDelete(p.id)} className="btn-secondary !p-2 hover:!border-red-400/50 hover:!text-red-400">
                        <Trash2 size={14} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
              {filtered.length === 0 && (
                <tr><td colSpan={6} className="px-4 py-8 text-center text-slate-500">No projects match these filters.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </DashboardLayout>
  )
}
