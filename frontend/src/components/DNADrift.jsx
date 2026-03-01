import React from 'react'
import { ArrowRight } from 'lucide-react'

export default function DNADrift({ drifts }) {
  if (!drifts || drifts.length === 0) return null

  return (
    <div className="bg-dna-surface/50 rounded-2xl border border-dna-surfaceLight/30 p-6">
      <h3 className="text-sm font-semibold text-gray-300 mb-4">🧬 DNA Drift</h3>
      <div className="space-y-3">
        {drifts.map((drift, i) => (
          <div key={i} className="bg-dna-dark rounded-xl p-3 border border-dna-surfaceLight/20">
            <div className="text-xs text-gray-500 font-mono mb-1">{drift.field}</div>
            <div className="flex items-center gap-2 text-xs">
              <span className="px-2 py-0.5 bg-red-500/10 text-red-400 rounded border border-red-500/20">
                {drift.old_value}
              </span>
              <ArrowRight size={12} className="text-gray-500 flex-shrink-0" />
              <span className="px-2 py-0.5 bg-green-500/10 text-green-400 rounded border border-green-500/20">
                {drift.new_value}
              </span>
            </div>
            {drift.impact && (
              <p className="text-[10px] text-gray-500 mt-2 leading-relaxed">{drift.impact}</p>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
