import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { ArrowLeft, ExternalLink, Github, Database } from 'lucide-react'
import DemoPanel from '../components/DemoPanel'
import Loader from '../components/Loader'
import SkillBadge from '../components/SkillBadge'
import { getProjectBySlug } from '../services/projectService'

function Section({ title, children }) {
  if (!children) return null
  return (
    <div className="glass-card p-6">
      <h3 className="font-bold text-white mb-3">{title}</h3>
      <div className="text-sm text-slate-300 leading-relaxed whitespace-pre-line">{children}</div>
    </div>
  )
}

export default function ProjectDetail() {
  const { slug } = useParams()
  const [project, setProject] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(false)

  useEffect(() => {
    setLoading(true)
    getProjectBySlug(slug)
      .then(setProject)
      .catch(() => setError(true))
      .finally(() => setLoading(false))
  }, [slug])

  if (loading) return <Loader label="Loading project..." />
  if (error || !project) {
    return (
      <div className="max-w-3xl mx-auto px-6 py-20 text-center text-slate-400">
        Project not found. <Link to="/" className="text-accent-cyan hover:underline">Back to home</Link>
      </div>
    )
  }

  const steps = (project.workflow_steps || '').split('->').map((s) => s.trim()).filter(Boolean)

  return (
    <div className="max-w-5xl mx-auto px-6 py-12">
      <Link to={`/${project.category.slug}`} className="inline-flex items-center gap-2 text-sm text-slate-400 hover:text-white mb-8">
        <ArrowLeft size={16} /> Back to {project.category.name}
      </Link>

      <div className="flex flex-wrap items-center gap-3 mb-4">
        <span className="badge !text-accent-cyan !border-accent-cyan/30">{project.category.name}</span>
        <span className="badge">{project.method_or_algorithm}</span>
        <span className="badge !text-accent-purple !border-accent-purple/30">{project.difficulty_level}</span>
        <span className="badge !text-emerald-400 !border-emerald-400/30">{project.status}</span>
      </div>

      <h1 className="text-3xl sm:text-4xl font-extrabold text-white">{project.title}</h1>
      <p className="text-slate-400 mt-3 max-w-3xl">{project.short_description}</p>

      <div className="flex flex-wrap gap-3 mt-6">
        {/* View Code button hidden for now — restore to bring it back
        {project.github_url && (
          <a href={project.github_url} target="_blank" rel="noreferrer" className="btn-secondary">
            <Github size={16} /> View Code
          </a>
        )} */}
        {project.demo_url && (
          <a href={project.demo_url} target="_blank" rel="noreferrer" className="btn-primary">
            <ExternalLink size={16} /> Live Demo
          </a>
        )}
        {project.dataset_url && (
          <a href={project.dataset_url} target="_blank" rel="noreferrer" className="btn-secondary">
            <Database size={16} /> Dataset
          </a>
        )}
      </div>

      <DemoPanel slug={project.slug} />

      <div className="grid md:grid-cols-2 gap-6 mt-10">
        <Section title="Problem Statement">{project.problem_statement}</Section>
        <Section title="Business Use Case">{project.business_use_case}</Section>
        <Section title="Dataset Description">{project.dataset_description}</Section>
        <Section title="Evaluation Metrics">{project.evaluation_metrics}</Section>
      </div>

      {steps.length > 0 && (
        <div className="glass-card p-6 mt-6">
          <h3 className="font-bold text-white mb-4">Step-by-Step Workflow</h3>
          <ol className="space-y-3">
            {steps.map((step, i) => (
              <li key={i} className="flex gap-3 text-sm text-slate-300">
                <span className="w-6 h-6 rounded-full bg-gradient-to-br from-accent-blue to-accent-purple text-white text-xs font-bold flex items-center justify-center shrink-0">
                  {i + 1}
                </span>
                {step}
              </li>
            ))}
          </ol>
        </div>
      )}

      <div className="grid md:grid-cols-2 gap-6 mt-6">
        <Section title="Results">{project.results}</Section>
        <Section title="Key Learning">{project.key_learning}</Section>
      </div>

      <div className="glass-card p-6 mt-6">
        <h3 className="font-bold text-white mb-3">Tools & Technologies</h3>
        <div className="flex flex-wrap gap-2">
          {[...new Set(
            [...(project.tools_used || '').split(','), ...(project.technologies_used || '').split(',')]
              .map((t) => t.trim())
              .filter(Boolean)
          )].map((t) => <SkillBadge key={t} label={t} />)}
        </div>
      </div>
    </div>
  )
}
