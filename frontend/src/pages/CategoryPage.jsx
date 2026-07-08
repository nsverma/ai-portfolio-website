import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import * as Icons from 'lucide-react'
import ProjectCard from '../components/ProjectCard'
import Loader from '../components/Loader'
import { getProjectsByCategory, getProjectsByMethod } from '../services/projectService'

// Shared listing page for Machine Learning, Deep Learning, AI Agent and
// Automation — each just supplies its own slug/title/icon/submenu items.
export default function CategoryPage({ categorySlug, title, description, icon, items }) {
  const { method } = useParams()
  const [projects, setProjects] = useState([])
  const [loading, setLoading] = useState(true)
  const Icon = Icons[icon] || Icons.Sparkles

  useEffect(() => {
    setLoading(true)
    const request = method ? getProjectsByMethod(method) : getProjectsByCategory(categorySlug)
    request.then(setProjects).finally(() => setLoading(false))
  }, [categorySlug, method])

  return (
    <div className="max-w-7xl mx-auto px-6 py-12">
      <div className="flex items-center gap-3 mb-3">
        <div className="w-11 h-11 rounded-xl bg-gradient-to-br from-accent-blue/20 to-accent-purple/20 flex items-center justify-center">
          <Icon size={22} className="text-accent-cyan" />
        </div>
        <h1 className="section-heading">{title}</h1>
      </div>
      <p className="text-slate-400 max-w-2xl mb-10">{description}</p>

      <div className="grid grid-cols-1 lg:grid-cols-[240px_1fr] gap-8">
        <aside className="glass-card p-4 h-fit lg:sticky lg:top-24">
          <p className="text-xs uppercase tracking-wider text-slate-500 px-2 mb-2">Methods</p>
          <nav className="flex flex-col gap-1">
            <Link
              to={`/${categorySlug}`}
              className={`px-3 py-2 rounded-lg text-sm transition-colors ${
                !method ? 'bg-gradient-to-r from-accent-blue/20 to-accent-purple/20 text-white' : 'text-slate-400 hover:text-white hover:bg-white/5'
              }`}
            >
              All {title}
            </Link>
            {items.map((item) => (
              <Link
                key={item}
                to={`/${categorySlug}/${encodeURIComponent(item)}`}
                className={`px-3 py-2 rounded-lg text-sm transition-colors ${
                  method === item ? 'bg-gradient-to-r from-accent-blue/20 to-accent-purple/20 text-white' : 'text-slate-400 hover:text-white hover:bg-white/5'
                }`}
              >
                {item}
              </Link>
            ))}
          </nav>
        </aside>

        <div>
          {loading ? (
            <Loader label="Loading projects..." />
          ) : projects.length === 0 ? (
            <div className="glass-card p-10 text-center text-slate-400">
              No projects yet for {method ? `"${method}"` : title}. Add one from the{' '}
              <Link to="/dashboard/new" className="text-accent-cyan hover:underline">dashboard</Link>.
            </div>
          ) : (
            <div className="grid sm:grid-cols-2 xl:grid-cols-3 gap-6">
              {projects.map((project) => <ProjectCard key={project.id} project={project} />)}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
