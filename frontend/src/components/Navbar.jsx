import { useEffect, useRef, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import * as Icons from 'lucide-react'
import { NAV_SECTIONS } from '../data/menuData'
import { useAuth } from '../context/AuthContext'

function DropdownMenu({ section, onNavigate }) {
  const [open, setOpen] = useState(false)
  const timeoutRef = useRef(null)
  const Icon = Icons[section.icon] || Icons.Sparkles

  const openMenu = () => {
    clearTimeout(timeoutRef.current)
    setOpen(true)
  }
  const closeMenu = () => {
    timeoutRef.current = setTimeout(() => setOpen(false), 150)
  }

  return (
    <div className="relative" onMouseEnter={openMenu} onMouseLeave={closeMenu}>
      <Link
        to={section.path}
        className="flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium text-slate-300 hover:text-white hover:bg-white/5 transition-colors"
      >
        <Icon size={16} className="text-accent-cyan" />
        {section.label}
        <Icons.ChevronDown size={14} className={`transition-transform ${open ? 'rotate-180' : ''}`} />
      </Link>

      {open && (
        <div className="absolute top-full left-0 mt-2 w-64 glass-card p-2 shadow-glow z-50">
          {section.items.map((item) => (
            <Link
              key={item}
              to={`${section.path}/${encodeURIComponent(item)}`}
              onClick={onNavigate}
              className="block px-3 py-2 rounded-lg text-sm text-slate-300 hover:text-white hover:bg-white/10 transition-colors"
            >
              {item}
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}

export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [mobileOpen, setMobileOpen] = useState(false)
  const [scrolled, setScrolled] = useState(false)

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 8)
    window.addEventListener('scroll', onScroll)
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  const handleLogout = async () => {
    await logout()
    navigate('/')
  }

  return (
    <header
      className={`sticky top-0 z-50 transition-all duration-300 ${
        scrolled ? 'bg-base-950/80 backdrop-blur-xl border-b border-white/10' : 'bg-transparent'
      }`}
    >
      <nav className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2 font-extrabold text-lg">
          <Icons.Sparkles className="text-accent-purple" size={22} />
          <span className="gradient-text">AI Learning</span>
        </Link>

        <div className="hidden lg:flex items-center gap-1">
          <Link to="/" className="px-3 py-2 rounded-lg text-sm font-medium text-slate-300 hover:text-white hover:bg-white/5 transition-colors">
            Home
          </Link>
          {NAV_SECTIONS.map((section) => (
            <DropdownMenu key={section.slug} section={section} />
          ))}
          <Link to="/about" className="px-3 py-2 rounded-lg text-sm font-medium text-slate-300 hover:text-white hover:bg-white/5 transition-colors">
            About Me
          </Link>
          {/* Contact page hidden for now — restore this link to bring it back
          <Link to="/contact" className="px-3 py-2 rounded-lg text-sm font-medium text-slate-300 hover:text-white hover:bg-white/5 transition-colors">
            Contact
          </Link> */}
        </div>

        <div className="hidden lg:flex items-center gap-3">
          {user ? (
            <>
              <Link to="/dashboard" className="btn-secondary !px-4 !py-2 text-sm">
                <Icons.LayoutDashboard size={16} /> Dashboard
              </Link>
              <Link to="/profile" className="btn-secondary !px-4 !py-2 text-sm">
                <Icons.User size={16} /> {user.name?.split(' ')[0]}
              </Link>
              <button onClick={handleLogout} className="btn-primary !px-4 !py-2 text-sm">
                <Icons.LogOut size={16} /> Logout
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="btn-secondary !px-4 !py-2 text-sm">Login</Link>
              <Link to="/register" className="btn-primary !px-4 !py-2 text-sm">Register</Link>
            </>
          )}
        </div>

        <button className="lg:hidden text-slate-200" onClick={() => setMobileOpen((v) => !v)}>
          {mobileOpen ? <Icons.X size={24} /> : <Icons.Menu size={24} />}
        </button>
      </nav>

      {mobileOpen && (
        <div className="lg:hidden px-6 pb-6 flex flex-col gap-2 bg-base-950/95 backdrop-blur-xl border-b border-white/10">
          <Link to="/" onClick={() => setMobileOpen(false)} className="py-2 text-slate-300">Home</Link>
          {NAV_SECTIONS.map((section) => (
            <div key={section.slug} className="py-1">
              <Link to={section.path} onClick={() => setMobileOpen(false)} className="font-semibold text-white">
                {section.label}
              </Link>
              <div className="pl-3 mt-1 flex flex-col gap-1">
                {section.items.slice(0, 5).map((item) => (
                  <Link
                    key={item}
                    to={`${section.path}/${encodeURIComponent(item)}`}
                    onClick={() => setMobileOpen(false)}
                    className="text-sm text-slate-400"
                  >
                    {item}
                  </Link>
                ))}
              </div>
            </div>
          ))}
          <Link to="/about" onClick={() => setMobileOpen(false)} className="py-2 text-slate-300">About Me</Link>
          {/* Contact page hidden for now
          <Link to="/contact" onClick={() => setMobileOpen(false)} className="py-2 text-slate-300">Contact</Link> */}
          <div className="flex gap-3 pt-3">
            {user ? (
              <>
                <Link to="/dashboard" className="btn-secondary flex-1 justify-center text-sm">Dashboard</Link>
                <button onClick={handleLogout} className="btn-primary flex-1 justify-center text-sm">Logout</button>
              </>
            ) : (
              <>
                <Link to="/login" className="btn-secondary flex-1 justify-center text-sm">Login</Link>
                <Link to="/register" className="btn-primary flex-1 justify-center text-sm">Register</Link>
              </>
            )}
          </div>
        </div>
      )}
    </header>
  )
}
