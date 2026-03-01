import React from 'react'
import { Dna } from 'lucide-react'

const TRAIT_COLORS = {
  intent: 'bg-indigo-500/20 text-indigo-400 border-indigo-500/30',
  tone: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
  emotional_signal: 'bg-pink-500/20 text-pink-400 border-pink-500/30',
  platform_alignment: 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30',
  structure_type: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
  keyword_clusters: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
}

export default function DNACard({ title, dna, accent = false }) {
  if (!dna) return null

  const borderClass = accent ? 'border-dna-accent/30' : 'border-dna-surfaceLight/30'

  return (
    <div className={`bg-dna-surface/50 rounded-2xl border ${borderClass} p-6`}>
      <h3 className="text-sm font-semibold text-gray-300 mb-4 flex items-center gap-2">
        <Dna size={16} className={accent ? 'text-dna-accent' : 'text-dna-primary'} />
        {title}
      </h3>
      <div className="space-y-3">
        {['intent', 'tone', 'emotional_signal', 'platform_alignment', 'structure_type'].map((field) => (
          <div key={field} className="flex items-center justify-between">
            <span className="text-xs text-gray-500 font-mono">{field}</span>
            <span className={`text-xs px-2 py-0.5 rounded border ${TRAIT_COLORS[field]}`}>
              {String(dna[field]).replace(/_/g, ' ')}
            </span>
          </div>
        ))}
        {dna.keyword_clusters && dna.keyword_clusters.length > 0 && (
          <div>
            <span className="text-xs text-gray-500 font-mono block mb-1">keywords</span>
            <div className="flex flex-wrap gap-1">
              {dna.keyword_clusters.map((kw, i) => (
                <span
                  key={i}
                  className={`text-xs px-2 py-0.5 rounded border ${TRAIT_COLORS.keyword_clusters}`}
                >
                  {kw}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
