import { GraduationCap, Award, Target, Wrench } from 'lucide-react'
import SkillBadge from '../components/SkillBadge'

const SKILLS = ['Python', 'Pandas', 'NumPy', 'Scikit-learn', 'XGBoost', 'PyTorch', 'TensorFlow', 'HuggingFace', 'LangChain', 'SQL', 'FastAPI', 'React']
const TOOLS = ['Jupyter', 'Git/GitHub', 'Docker', 'VS Code', 'MLflow', 'Streamlit', 'Postman', 'AWS (basics)']
const CERTIFICATIONS = [
  'Add your certifications here (e.g., DeepLearning.AI, AWS, Google Data Analytics)',
]

export default function About() {
  return (
    <div className="max-w-4xl mx-auto px-6 py-16">
      <h1 className="section-heading">About Me</h1>
      <p className="text-slate-400 mt-4 leading-relaxed">
        {/* Replace with your own professional summary */}
        I'm an aspiring AI/Machine Learning Engineer focused on building end-to-end, production-shaped
        solutions rather than isolated notebooks. I enjoy taking a business problem all the way from
        raw data to a deployed, explainable model.
      </p>

      <div className="glass-card p-6 mt-8">
        <div className="flex items-center gap-2 mb-3">
          <Target size={18} className="text-accent-cyan" />
          <h2 className="font-bold text-white">My AI/ML Learning Journey</h2>
        </div>
        <p className="text-sm text-slate-300 leading-relaxed">
          {/* Replace with your own journey narrative */}
          Started with Python, NumPy, and Pandas fundamentals, then moved through classical ML
          (Scikit-learn), deep learning (PyTorch/TensorFlow), and most recently LLM-based AI agents
          and automation — building one complete project per stage to lock in the concepts.
        </p>
      </div>

      <div className="grid sm:grid-cols-2 gap-6 mt-6">
        <div className="glass-card p-6">
          <div className="flex items-center gap-2 mb-3">
            <Wrench size={18} className="text-accent-cyan" />
            <h2 className="font-bold text-white">Technical Skills</h2>
          </div>
          <div className="flex flex-wrap gap-2">{SKILLS.map((s) => <SkillBadge key={s} label={s} />)}</div>
        </div>
        <div className="glass-card p-6">
          <div className="flex items-center gap-2 mb-3">
            <Wrench size={18} className="text-accent-purple" />
            <h2 className="font-bold text-white">Tools & Technologies</h2>
          </div>
          <div className="flex flex-wrap gap-2">{TOOLS.map((t) => <SkillBadge key={t} label={t} />)}</div>
        </div>
      </div>

      <div className="glass-card p-6 mt-6">
        <div className="flex items-center gap-2 mb-3">
          <Award size={18} className="text-accent-cyan" />
          <h2 className="font-bold text-white">Certifications</h2>
        </div>
        <ul className="list-disc list-inside text-sm text-slate-300 space-y-1">
          {CERTIFICATIONS.map((c) => <li key={c}>{c}</li>)}
        </ul>
      </div>

      <div className="glass-card p-6 mt-6">
        <div className="flex items-center gap-2 mb-3">
          <GraduationCap size={18} className="text-accent-cyan" />
          <h2 className="font-bold text-white">Education</h2>
        </div>
        <p className="text-sm text-slate-300">{/* Replace with your education details */} Your degree, institution, and graduation year here.</p>
      </div>

      <div className="glass-card p-6 mt-6">
        <h2 className="font-bold text-white mb-3">Career Goal</h2>
        <p className="text-sm text-slate-300 leading-relaxed">
          {/* Replace with your own career goal */}
          Looking for an AI/ML Engineer role where I can take models from prototype to production and
          keep learning from real-world data and deployment constraints.
        </p>
      </div>
    </div>
  )
}
