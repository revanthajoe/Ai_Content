import React from 'react'
import { motion } from 'framer-motion'
import { Users, MessageCircle, TrendingUp } from 'lucide-react'

const SEGMENT_EMOJIS = {
  'Gen Z India': '🧑‍💻',
  'Urban Professionals': '👔',
  'Rural Digital India': '🌾',
  'College Students': '🎓',
  'Business Owners': '💼',
}

const SEGMENT_COLORS = {
  'Gen Z India': 'from-violet-500 to-purple-500',
  'Urban Professionals': 'from-blue-500 to-cyan-500',
  'Rural Digital India': 'from-green-500 to-emerald-500',
  'College Students': 'from-orange-500 to-amber-500',
  'Business Owners': 'from-rose-500 to-pink-500',
}

export default function AudiencePanel({ data }) {
  if (!data?.segments) return null

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {data.segments.map((seg, i) => (
          <motion.div
            key={seg.segment}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            className="bg-dna-dark rounded-xl border border-dna-surfaceLight/20 p-4 space-y-3"
          >
            <div className="flex items-center gap-2">
              <span className="text-lg">{SEGMENT_EMOJIS[seg.segment] || '👥'}</span>
              <h4 className="text-sm font-semibold text-white">{seg.segment}</h4>
            </div>

            {/* Engagement Score Bar */}
            <div>
              <div className="flex items-center justify-between text-xs mb-1">
                <span className="text-gray-400 flex items-center gap-1"><TrendingUp size={12} /> Engagement</span>
                <span className="text-white font-medium">{seg.engagement_score}/10</span>
              </div>
              <div className="h-2 bg-dna-surfaceLight/30 rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${seg.engagement_score * 10}%` }}
                  transition={{ duration: 0.6, delay: i * 0.1 }}
                  className={`h-full rounded-full bg-gradient-to-r ${SEGMENT_COLORS[seg.segment] || 'from-dna-primary to-dna-secondary'}`}
                />
              </div>
            </div>

            {/* Reaction */}
            <div className="flex items-start gap-2">
              <MessageCircle size={12} className="text-gray-500 mt-0.5 shrink-0" />
              <p className="text-xs text-gray-400 italic leading-relaxed">"{seg.reaction}"</p>
            </div>

            {/* Sample Comment */}
            {seg.sample_comment && (
              <div className="bg-dna-surfaceLight/10 rounded-lg p-2.5">
                <p className="text-xs text-gray-300">💬 {seg.sample_comment}</p>
              </div>
            )}
          </motion.div>
        ))}
      </div>

      {data.overall_score !== undefined && (
        <div className="flex items-center justify-center gap-3 py-3 bg-dna-dark rounded-xl border border-dna-surfaceLight/20">
          <Users size={16} className="text-dna-accent" />
          <span className="text-sm text-gray-400">Overall Audience Score:</span>
          <span className="text-xl font-bold text-dna-accent">{data.overall_score}/10</span>
        </div>
      )}
    </div>
  )
}
