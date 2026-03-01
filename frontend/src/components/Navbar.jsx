import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Dna, FlaskConical, Eye, Home } from 'lucide-react'

const navItems = [
  { path: '/', label: 'Home', icon: Home },
  { path: '/create', label: 'Create', icon: Dna },
  { path: '/lab', label: 'Evolution Lab', icon: FlaskConical },
  { path: '/dna', label: 'DNA Viewer', icon: Eye },
]

export default function Navbar() {
  const location = useLocation()

  return (
    <nav className="bg-dna-dark/80 backdrop-blur-md border-b border-dna-surfaceLight/30 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-3 group">
            <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-dna-primary to-dna-accent flex items-center justify-center group-hover:scale-110 transition-transform">
              <Dna size={20} className="text-white" />
            </div>
            <div>
              <span className="text-lg font-bold bg-gradient-to-r from-dna-primary to-dna-accent bg-clip-text text-transparent">
                Content DNA OS
              </span>
              <span className="hidden sm:inline text-xs text-gray-500 ml-2">v1.0</span>
            </div>
          </Link>

          {/* Nav Links */}
          <div className="flex items-center gap-1">
            {navItems.map(({ path, label, icon: Icon }) => {
              const active = location.pathname === path
              return (
                <Link
                  key={path}
                  to={path}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                    active
                      ? 'bg-dna-primary/20 text-dna-primary'
                      : 'text-gray-400 hover:text-white hover:bg-dna-surface/50'
                  }`}
                >
                  <Icon size={16} />
                  <span className="hidden md:inline">{label}</span>
                </Link>
              )
            })}
          </div>
        </div>
      </div>
    </nav>
  )
}
