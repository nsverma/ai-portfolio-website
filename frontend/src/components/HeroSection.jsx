import { motion } from 'framer-motion'
import { ArrowRight, Github, Linkedin } from 'lucide-react'
import { Link } from 'react-router-dom'

export default function HeroSection() {
  return (
    <section className="relative overflow-hidden pt-20 pb-24 px-6">
      <div className="absolute top-10 left-1/4 w-72 h-72 bg-accent-blue/20 rounded-full blur-[100px] animate-pulse-slow" />
      <div className="absolute top-32 right-1/4 w-72 h-72 bg-accent-purple/20 rounded-full blur-[100px] animate-pulse-slow" />

      <div className="relative max-w-5xl mx-auto text-center">
        <motion.span
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="badge mx-auto mb-6 !text-accent-cyan !border-accent-cyan/30"
        >
          Passionate About AI & Building Intelligent Systems
        </motion.span>

        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="text-4xl sm:text-6xl font-extrabold tracking-tight leading-tight"
        >
          Your Name<br />
          <span className="gradient-text">AI / Machine Learning Portfolio</span>
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="mt-6 max-w-2xl mx-auto text-slate-400 text-lg"
        >
          I build end-to-end Machine Learning, Deep Learning, AI Agent and Automation
          solutions — from problem statement to a deployed, working product. Every
          project below solves a real business problem, not a toy dataset.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="mt-10 flex flex-wrap items-center justify-center gap-4"
        >
          <a href="#projects" className="btn-primary">
            View Projects <ArrowRight size={18} />
          </a>
          <a href="https://github.com/nsverma" target="_blank" rel="noreferrer" className="btn-secondary">
            <Github size={18} /> GitHub
          </a>
          <a href="https://linkedin.com/in/your-profile" target="_blank" rel="noreferrer" className="btn-secondary">
            <Linkedin size={18} /> LinkedIn
          </a>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="mt-16 grid grid-cols-2 sm:grid-cols-4 gap-4 max-w-3xl mx-auto"
        >
          {[
            ['6+', 'End-to-End Projects'],
            ['4', 'Domains Covered'],
            ['15+', 'Algorithms Applied'],
            ['100%', 'Deployed & Documented'],
          ].map(([stat, label]) => (
            <div key={label} className="glass-card px-4 py-5">
              <div className="text-2xl font-extrabold gradient-text">{stat}</div>
              <div className="text-xs text-slate-400 mt-1">{label}</div>
            </div>
          ))}
        </motion.div>
      </div>
    </section>
  )
}
