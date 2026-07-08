import { Link } from 'react-router-dom'
import { Compass } from 'lucide-react'

export default function NotFound() {
  return (
    <div className="min-h-[70vh] flex flex-col items-center justify-center text-center px-6">
      <Compass size={48} className="text-accent-cyan mb-4" />
      <h1 className="text-4xl font-extrabold gradient-text">404</h1>
      <p className="text-slate-400 mt-2">This page doesn't exist.</p>
      <Link to="/" className="btn-primary mt-6">Back to Home</Link>
    </div>
  )
}
