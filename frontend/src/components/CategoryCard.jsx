import { Link } from 'react-router-dom'
import * as Icons from 'lucide-react'

export default function CategoryCard({ category }) {
  const Icon = Icons[category.icon] || Icons.Sparkles

  return (
    <Link to={`/${category.slug}`} className="glass-card p-6 group">
      <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-accent-blue/20 to-accent-purple/20 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
        <Icon size={24} className="text-accent-cyan" />
      </div>
      <h3 className="font-bold text-white text-lg">{category.name}</h3>
      <p className="text-sm text-slate-400 mt-2">{category.description}</p>
      <span className="inline-flex items-center gap-1 text-sm text-accent-cyan mt-4 font-medium">
        Explore <Icons.ArrowRight size={14} className="group-hover:translate-x-1 transition-transform" />
      </span>
    </Link>
  )
}
