import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { Search, Mail } from 'lucide-react'
import HeroSection from '../components/HeroSection'
import CategoryCard from '../components/CategoryCard'
import ProjectCard from '../components/ProjectCard'
import SkillBadge from '../components/SkillBadge'
import Loader from '../components/Loader'
import { getCategories, getProjects } from '../services/projectService'

const SKILLS = [
  'Python', 'Pandas', 'NumPy', 'Scikit-learn', 'XGBoost', 'PyTorch', 'TensorFlow',
  'HuggingFace Transformers', 'LangChain', 'FastAPI', 'SQL', 'Docker', 'React', 'Tailwind CSS',
]

export default function Home() {
  const [projects, setProjects] = useState([])
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [categoryFilter, setCategoryFilter] = useState('')

  useEffect(() => {
    Promise.all([getProjects(), getCategories()])
      .then(([projectsData, categoriesData]) => {
        setProjects(projectsData)
        setCategories(categoriesData)
      })
      .finally(() => setLoading(false))
  }, [])

  const filteredProjects = useMemo(() => {
    return projects.filter((p) => {
      const matchesSearch =
        !search ||
        p.title.toLowerCase().includes(search.toLowerCase()) ||
        p.method_or_algorithm.toLowerCase().includes(search.toLowerCase())
      const matchesCategory = !categoryFilter || p.category?.slug === categoryFilter
      return matchesSearch && matchesCategory
    })
  }, [projects, search, categoryFilter])

  return (
    <div>
      <HeroSection />

      <section className="max-w-7xl mx-auto px-6 py-10">
        <h2 className="section-heading text-center mb-3">Explore by Domain</h2>
        <p className="text-slate-400 text-center max-w-xl mx-auto mb-10">
          Every problem I've solved is organized under one of these four domains.
        </p>
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {categories.map((category) => <CategoryCard key={category.id} category={category} />)}
        </div>
      </section>

      <section className="max-w-7xl mx-auto px-6 py-10">
        <h2 className="section-heading text-center mb-3">Skills Overview</h2>
        <p className="text-slate-400 text-center max-w-xl mx-auto mb-8">
          Tools and technologies used across the projects below.
        </p>
        <div className="flex flex-wrap justify-center gap-2 max-w-3xl mx-auto">
          {SKILLS.map((skill) => <SkillBadge key={skill} label={skill} />)}
        </div>
      </section>

      <section id="projects" className="max-w-7xl mx-auto px-6 py-16">
        <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-6 mb-10">
          <div>
            <h2 className="section-heading">Problems I've Solved</h2>
            <p className="text-slate-400 mt-2">
              A recruiter-friendly summary: the problem, the method, the tools, and the result — for every project.
            </p>
          </div>
          <div className="flex gap-3">
            <div className="relative">
              <Search size={16} className="absolute left-3 top-3 text-slate-500" />
              <input
                className="input-field !pl-9 !py-2 w-56"
                placeholder="Search projects..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>
            <select className="input-field !py-2 w-44" value={categoryFilter} onChange={(e) => setCategoryFilter(e.target.value)}>
              <option value="">All Categories</option>
              {categories.map((c) => <option key={c.id} value={c.slug}>{c.name}</option>)}
            </select>
          </div>
        </div>

        {loading ? (
          <Loader label="Loading projects..." />
        ) : filteredProjects.length === 0 ? (
          <div className="glass-card p-10 text-center text-slate-400">No projects match your search.</div>
        ) : (
          <div className="grid sm:grid-cols-2 xl:grid-cols-3 gap-6">
            {filteredProjects.map((project) => <ProjectCard key={project.id} project={project} />)}
          </div>
        )}
      </section>

      <section className="max-w-4xl mx-auto px-6 py-20 text-center">
        <div className="glass-card p-10">
          <Mail className="mx-auto text-accent-cyan mb-4" size={32} />
          <h2 className="text-2xl font-bold text-white">Let's talk about your open role</h2>
          <p className="text-slate-400 mt-3 max-w-md mx-auto">
            I'm actively looking for AI/ML Engineer opportunities — happy to walk through any project above in detail.
          </p>
          <Link to="/contact" className="btn-primary mt-6 inline-flex">Get in Touch</Link>
        </div>
      </section>
    </div>
  )
}
