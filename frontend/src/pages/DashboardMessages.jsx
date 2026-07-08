import { useEffect, useState } from 'react'
import { Mail } from 'lucide-react'
import DashboardLayout from '../components/DashboardLayout'
import Loader from '../components/Loader'
import { getContactMessages } from '../services/projectService'

export default function DashboardMessages() {
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getContactMessages().then(setMessages).finally(() => setLoading(false))
  }, [])

  return (
    <DashboardLayout>
      <h1 className="text-2xl font-bold text-white mb-6">Contact Messages</h1>
      {loading ? (
        <Loader />
      ) : messages.length === 0 ? (
        <div className="glass-card p-10 text-center text-slate-400">No messages yet.</div>
      ) : (
        <div className="flex flex-col gap-4">
          {messages.map((m) => (
            <div key={m.id} className="glass-card p-5">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2 font-semibold text-white">
                  <Mail size={16} className="text-accent-cyan" /> {m.name}
                </div>
                <span className="text-xs text-slate-500">
                  {new Date(m.created_at).toLocaleString()}
                </span>
              </div>
              <p className="text-sm text-accent-cyan mb-2">{m.email}</p>
              <p className="text-sm text-slate-300">{m.message}</p>
            </div>
          ))}
        </div>
      )}
    </DashboardLayout>
  )
}
