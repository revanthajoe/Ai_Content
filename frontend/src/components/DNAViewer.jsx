import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { Eye, Dna, Sparkles, AlertCircle } from 'lucide-react'
import DNACard from './DNACard'
import FitnessBar from './FitnessBar'

export default function DNAViewer() {
  const [content, setContent] = useState('')
  const [loading, setLoading] = useState(false)
  const [dna, setDna] = useState(null)
  const [fitness, setFitness] = useState(null)
  const [error, setError] = useState(null)

  const handleExtract = async () => {
    if (content.length < 10) return
    setLoading(true)
    setError(null)
    try {
      const [dnaRes, fitRes] = await Promise.all([
        fetch('/api/dna/extract', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(content),
        }).then(r => r.json()),
        fetch('/api/fitness/score', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(content),
        }).then(r => r.json()),
      ])
      setDna(dnaRes)
      setFitness(fitRes)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
            <Eye size={22} />
          </div>
          <span className="bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
            DNA Viewer
          </span>
        </h1>
        <p className="text-gray-400 mt-2">Analyze the genetic blueprint of any content piece.</p>
      </div>

      <div className="bg-dna-surface/50 rounded-2xl border border-dna-surfaceLight/30 p-6 space-y-5">
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="Paste content to analyze its DNA..."
          className="w-full h-36 bg-dna-dark rounded-xl border border-dna-surfaceLight/40 p-4 text-white placeholder-gray-500 resize-none focus:outline-none focus:border-purple-500/60 focus:ring-1 focus:ring-purple-500/30"
        />
        <button
          onClick={handleExtract}
          disabled={content.length < 10 || loading}
          className="w-full py-3 rounded-xl bg-gradient-to-r from-purple-500 to-pink-500 text-white font-semibold hover:scale-[1.02] transition-transform disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        >
          {loading ? (
            <div className="animate-spin w-5 h-5 border-2 border-white/30 border-t-white rounded-full" />
          ) : (
            <>
              <Dna size={18} />
              Extract DNA
            </>
          )}
        </button>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-4 flex items-center gap-3 text-red-400">
          <AlertCircle size={18} />{error}
        </div>
      )}

      {dna && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          <DNACard title="Content DNA Profile" dna={dna} accent />

          {fitness && (
            <div className="bg-dna-surface/50 rounded-2xl border border-dna-surfaceLight/30 p-6">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <Sparkles size={18} className="text-dna-accent" />
                Fitness Score: <span className="text-dna-accent">{(fitness.total * 100).toFixed(1)}%</span>
              </h3>
              <FitnessBar label="Length" value={fitness.length_score} />
              <FitnessBar label="Structural Clarity" value={fitness.structural_clarity} />
              <FitnessBar label="Intent Alignment" value={fitness.intent_alignment} />
              <FitnessBar label="Novelty Bonus" value={fitness.novelty_bonus} color="cyan" />
              <FitnessBar label="Repetition Penalty" value={fitness.repetition_penalty} color="red" inverted />
            </div>
          )}
        </motion.div>
      )}
    </div>
  )
}
