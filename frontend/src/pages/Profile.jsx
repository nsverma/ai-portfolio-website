import { User, Mail, ShieldCheck, Calendar } from 'lucide-react'
import { useAuth } from '../context/AuthContext'

export default function Profile() {
  const { user } = useAuth()
  if (!user) return null

  const joined = new Date(user.created_at).toLocaleDateString(undefined, {
    year: 'numeric', month: 'long', day: 'numeric',
  })

  return (
    <div className="max-w-2xl mx-auto px-6 py-16">
      <h1 className="section-heading mb-8">My Profile</h1>
      <div className="glass-card p-8">
        <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-accent-blue to-accent-purple flex items-center justify-center text-2xl font-bold text-white mb-6">
          {user.name?.[0]?.toUpperCase()}
        </div>
        <div className="space-y-4 text-sm">
          <div className="flex items-center gap-3 text-slate-300">
            <User size={16} className="text-accent-cyan" /> {user.name}
          </div>
          <div className="flex items-center gap-3 text-slate-300">
            <Mail size={16} className="text-accent-cyan" /> {user.email}
          </div>
          <div className="flex items-center gap-3 text-slate-300">
            <ShieldCheck size={16} className="text-accent-cyan" /> Role: {user.role}
          </div>
          <div className="flex items-center gap-3 text-slate-300">
            <Calendar size={16} className="text-accent-cyan" /> Joined {joined}
          </div>
        </div>
      </div>
    </div>
  )
}
