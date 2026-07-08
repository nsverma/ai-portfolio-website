import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { UserPlus, Mail, Lock, User, AlertCircle } from 'lucide-react'
import { useAuth } from '../context/AuthContext'

export default function RegisterForm() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ name: '', email: '', password: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await register(form.name, form.email, form.password)
      navigate('/dashboard')
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not create account')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="glass-card p-8 w-full max-w-md mx-auto">
      <h2 className="text-2xl font-bold text-white mb-1">Create your account</h2>
      <p className="text-sm text-slate-400 mb-6">The first account created becomes the portfolio admin.</p>

      {error && (
        <div className="flex items-center gap-2 text-sm text-red-400 bg-red-400/10 border border-red-400/30 rounded-xl px-4 py-3 mb-4">
          <AlertCircle size={16} /> {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <div className="relative">
          <User size={16} className="absolute left-3 top-3.5 text-slate-500" />
          <input
            type="text"
            required
            placeholder="Full name"
            className="input-field !pl-10"
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
          />
        </div>
        <div className="relative">
          <Mail size={16} className="absolute left-3 top-3.5 text-slate-500" />
          <input
            type="email"
            required
            placeholder="Email address"
            className="input-field !pl-10"
            value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
          />
        </div>
        <div className="relative">
          <Lock size={16} className="absolute left-3 top-3.5 text-slate-500" />
          <input
            type="password"
            required
            minLength={6}
            placeholder="Password (min. 6 characters)"
            className="input-field !pl-10"
            value={form.password}
            onChange={(e) => setForm({ ...form, password: e.target.value })}
          />
        </div>
        <button type="submit" disabled={loading} className="btn-primary justify-center mt-2 disabled:opacity-60">
          <UserPlus size={18} /> {loading ? 'Creating account...' : 'Register'}
        </button>
      </form>

      <p className="text-sm text-slate-400 mt-6 text-center">
        Already have an account?{' '}
        <Link to="/login" className="text-accent-cyan hover:underline">Login</Link>
      </p>
    </div>
  )
}
