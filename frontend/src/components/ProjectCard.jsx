import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { ExternalLink, Github, Layers } from 'lucide-react'
import * as Icons from 'lucide-react'

const CATEGORY_ICON = {
  'machine-learning': 'BrainCircuit',
  'deep-learning': 'Network',
  'ai-agent': 'Bot',
  automation: 'Workflow',
}

const STATUS_STYLE = {
  Completed: 'text-emerald-400 border-emerald-400/30 bg-emerald-400/10',
  'In Progress': 'text-amber-400 border-amber-400/30 bg-amber-400/10',
}

export default function ProjectCard({ project }) {
  const Icon = Icons[CATEGORY_ICON[project.category?.slug]] || Layers

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      className="glass-card p-6 flex flex-col h-full"
    >
      <div className="flex items-center justify-between mb-4">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-accent-blue/20 to-accent-purple/20 flex items-center justify-center">
          <Icon size={20} className="text-accent-cyan" />
        </div>
        <span className={`text-xs font-medium px-2.5 py-1 rounded-full border ${STATUS_STYLE[project.status] || STATUS_STYLE.Completed}`}>
          {project.status}
        </span>
      </div>

      <h3 className="font-bold text-lg text-white leading-snug">{project.title}</h3>
      <p className="text-xs text-accent-cyan mt-1 font-medium">{project.method_or_algorithm}</p>
      <p className="text-sm text-slate-400 mt-3 flex-1">{project.short_description}</p>

      <div className="flex flex-wrap gap-2 mt-4">
        {(project.technologies_used || '')
          .split(',')
          .filter(Boolean)
          .slice(0, 3)
          .map((tech) => (
            <span key={tech} className="badge !py-0.5 !text-[11px]">{tech.trim()}</span>
          ))}
        <span className="badge !py-0.5 !text-[11px] !text-accent-purple !border-accent-purple/30">
          {project.difficulty_level}
        </span>
      </div>

      <div className="flex items-center gap-2 mt-5 pt-5 border-t border-white/10">
        <Link to={`/projects/${project.slug}`} className="btn-primary flex-1 !py-2 !text-sm justify-center">
          View Details
        </Link>
        {project.github_url && (
          <a href={project.github_url} target="_blank" rel="noreferrer" className="btn-secondary !p-2.5" title="GitHub">
            <Github size={16} />
          </a>
        )}
        {project.demo_url && (
          <a href={project.demo_url} target="_blank" rel="noreferrer" className="btn-secondary !p-2.5" title="Live Demo">
            <ExternalLink size={16} />
          </a>
        )}
      </div>
    </motion.div>
  )
}
