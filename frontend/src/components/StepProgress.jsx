import React from 'react'
import { motion } from 'framer-motion'
import { Check, Loader2 } from 'lucide-react'

export default function StepProgress({ steps, currentStep }) {
  return (
    <div className="bg-dna-surface/50 rounded-2xl border border-dna-surfaceLight/30 p-6">
      <div className="flex items-center gap-2 mb-4">
        <Loader2 size={18} className="animate-spin text-dna-primary" />
        <h3 className="text-sm font-medium text-gray-400">Evolution in progress...</h3>
      </div>
      <div className="space-y-3">
        {steps.map((step, i) => {
          const done = i < currentStep
          const active = i === currentStep
          return (
            <motion.div
              key={i}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.1 }}
              className={`flex items-center gap-3 px-4 py-2.5 rounded-xl transition-all ${
                active ? 'bg-dna-primary/10 border border-dna-primary/30' :
                done ? 'bg-dna-success/5 border border-dna-success/20' :
                'border border-transparent'
              }`}
            >
              <div className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold shrink-0 ${
                done ? 'bg-dna-success/20 text-dna-success' :
                active ? 'bg-dna-primary/20 text-dna-primary' :
                'bg-dna-surfaceLight/30 text-gray-500'
              }`}>
                {done ? <Check size={14} /> : active ? <Loader2 size={14} className="animate-spin" /> : i + 1}
              </div>
              <span className={`text-sm ${
                done ? 'text-dna-success' :
                active ? 'text-white font-medium' :
                'text-gray-500'
              }`}>
                {step}
              </span>
              {active && (
                <motion.div
                  className="ml-auto flex gap-1"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                >
                  {[0, 1, 2].map(j => (
                    <motion.div
                      key={j}
                      className="w-1.5 h-1.5 rounded-full bg-dna-primary"
                      animate={{ opacity: [0.3, 1, 0.3] }}
                      transition={{ duration: 1, repeat: Infinity, delay: j * 0.2 }}
                    />
                  ))}
                </motion.div>
              )}
            </motion.div>
          )
        })}
      </div>
    </div>
  )
}
