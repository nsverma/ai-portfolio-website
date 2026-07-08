import { useState } from 'react'
import { Mail, Github, Linkedin, Send, CheckCircle2 } from 'lucide-react'
import { submitContactMessage } from '../services/projectService'

export default function Contact() {
  const [form, setForm] = useState({ name: '', email: '', message: '' })
  const [status, setStatus] = useState('idle')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setStatus('sending')
    try {
      await submitContactMessage(form)
      setStatus('sent')
      setForm({ name: '', email: '', message: '' })
    } catch {
      setStatus('error')
    }
  }

  return (
    <div className="max-w-5xl mx-auto px-6 py-16 grid md:grid-cols-2 gap-10">
      <div>
        <h1 className="section-heading">Contact</h1>
        <p className="text-slate-400 mt-4">
          Open to AI/ML Engineer roles and happy to walk through any project in more depth.
        </p>

        <div className="flex flex-col gap-3 mt-8">
          <a href="mailto:you@example.com" className="glass-card p-4 flex items-center gap-3 !hover:translate-y-0">
            <Mail className="text-accent-cyan" size={20} /> you@example.com
          </a>
          <a href="https://www.linkedin.com/in/sudhanshu-verma-66695927/" target="_blank" rel="noreferrer" className="glass-card p-4 flex items-center gap-3">
            <Linkedin className="text-accent-cyan" size={20} /> linkedin.com/in/sudhanshu-verma-66695927
          </a>
          <a href="https://github.com/nsverma" target="_blank" rel="noreferrer" className="glass-card p-4 flex items-center gap-3">
            <Github className="text-accent-cyan" size={20} /> github.com/nsverma
          </a>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="glass-card p-6 flex flex-col gap-4 h-fit">
        <h2 className="font-bold text-white text-lg">Send a Message</h2>
        {status === 'sent' && (
          <div className="flex items-center gap-2 text-sm text-emerald-400 bg-emerald-400/10 border border-emerald-400/30 rounded-xl px-4 py-3">
            <CheckCircle2 size={16} /> Message sent — thank you!
          </div>
        )}
        {status === 'error' && (
          <div className="text-sm text-red-400 bg-red-400/10 border border-red-400/30 rounded-xl px-4 py-3">
            Something went wrong. Please try again.
          </div>
        )}
        <input required placeholder="Your name" className="input-field" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
        <input required type="email" placeholder="Your email" className="input-field" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
        <textarea required rows={5} placeholder="Your message" className="input-field" value={form.message} onChange={(e) => setForm({ ...form, message: e.target.value })} />
        <button type="submit" disabled={status === 'sending'} className="btn-primary justify-center disabled:opacity-60">
          <Send size={16} /> {status === 'sending' ? 'Sending...' : 'Send Message'}
        </button>
      </form>
    </div>
  )
}
