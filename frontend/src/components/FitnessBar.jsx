import React from 'react'

export default function FitnessBar({ label, value, color = 'primary', inverted = false }) {
  const pct = Math.min(100, Math.max(0, (value || 0) * 100))

  const colorClasses = {
    primary: 'from-dna-primary to-dna-secondary',
    cyan: 'from-dna-accent to-cyan-400',
    red: 'from-red-500 to-orange-500',
    green: 'from-emerald-500 to-green-400',
  }

  const gradientClass = colorClasses[color] || colorClasses.primary

  return (
    <div className="mb-3">
      <div className="flex items-center justify-between text-xs mb-1">
        <span className="text-gray-400">{label} {inverted && '(penalty)'}</span>
        <span className={`font-mono ${inverted ? 'text-red-400' : 'text-gray-300'}`}>
          {pct.toFixed(1)}%
        </span>
      </div>
      <div className="w-full h-2 bg-dna-dark rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full bg-gradient-to-r ${gradientClass} transition-all duration-500`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  )
}
