import { Github, Linkedin, Mail, Sparkles } from 'lucide-react'

export default function Footer() {
  return (
    <footer className="border-t border-white/10 mt-24">
      <div className="max-w-7xl mx-auto px-6 py-10 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-2 font-bold">
          <Sparkles className="text-accent-purple" size={18} />
          <span className="gradient-text">AI Learning</span>
        </div>
        <p className="text-sm text-slate-500 text-center">
          Built with FastAPI, React &amp; Tailwind — showcasing ML, Deep Learning, AI Agent and Automation projects.
        </p>
        <div className="flex items-center gap-4 text-slate-400">
          <a href="https://github.com/nsverma" target="_blank" rel="noreferrer" className="hover:text-white transition-colors"><Github size={20} /></a>
          <a href="https://linkedin.com/in/your-profile" target="_blank" rel="noreferrer" className="hover:text-white transition-colors"><Linkedin size={20} /></a>
          <a href="mailto:you@example.com" className="hover:text-white transition-colors"><Mail size={20} /></a>
        </div>
      </div>
    </footer>
  )
}
