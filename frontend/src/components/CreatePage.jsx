import React, { useState, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Dna, Sparkles, ArrowRight, TrendingUp, TrendingDown,
  AlertCircle, Copy, Check, ThumbsUp, ThumbsDown, Share2,
  Globe, Loader2
} from 'lucide-react'
import { evolveContent, submitFeedback, simulateAudience } from '../api/client'
import DNACard from './DNACard'
import FitnessBar from './FitnessBar'
import StepProgress from './StepProgress'
import AudiencePanel from './AudiencePanel'

const STRATEGIES = [
  { value: null, label: 'Auto (Random)', desc: 'Let the system pick' },
  { value: 'hook_amplification', label: 'Hook Amplification', desc: 'Bold, attention-grabbing lead' },
  { value: 'angle_shift', label: 'Angle Shift', desc: 'Contrarian perspective' },
  { value: 'story_reframe', label: 'Story Reframe', desc: 'Narrative arc structure' },
  { value: 'counterpoint_injection', label: 'Counterpoint', desc: "Devil's advocate tension" },
  { value: 'summary_distillation', label: 'Distillation', desc: 'Essential core insight' },
  { value: 'platform_formatting', label: 'Platform Format', desc: 'Platform-optimized layout' },
  { value: 'regional_adaptation', label: 'Regional Adapt', desc: 'Indian audience focus' },
]

const PLATFORMS = [
  { value: 'general', label: 'General' },
  { value: 'twitter', label: 'Twitter/X' },
  { value: 'linkedin', label: 'LinkedIn' },
  { value: 'instagram', label: 'Instagram' },
  { value: 'blog', label: 'Blog' },
  { value: 'email', label: 'Email' },
  { value: 'youtube', label: 'YouTube' },
]

const LANGUAGES = [
  { value: 'english', label: 'English' },
  { value: 'hindi', label: 'Hindi' },
  { value: 'tamil', label: 'Tamil' },
  { value: 'telugu', label: 'Telugu' },
  { value: 'bengali', label: 'Bengali' },
  { value: 'marathi', label: 'Marathi' },
  { value: 'kannada', label: 'Kannada' },
  { value: 'gujarati', label: 'Gujarati' },
]

const STEPS = [
  'Extracting DNA',
  'Applying Mutation',
  'Scoring Fitness',
  'Checking Similarity',
  'Selecting Winner',
]

export default function CreatePage() {
  const [content, setContent] = useState('')
  const [strategy, setStrategy] = useState(null)
  const [platform, setPlatform] = useState('general')
  const [language, setLanguage] = useState('english')
  const [loading, setLoading] = useState(false)
  const [currentStep, setCurrentStep] = useState(-1)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [copied, setCopied] = useState(null)
  const [feedback, setFeedback] = useState(null)
  const [audienceData, setAudienceData] = useState(null)
  const [audienceLoading, setAudienceLoading] = useState(false)

  const handleEvolve = async () => {
    if (content.length < 10) return
    setLoading(true)
    setError(null)
    setResult(null)
    setFeedback(null)
    setAudienceData(null)
    try {
      for (let i = 0; i < STEPS.length; i++) {
        setCurrentStep(i)
        await new Promise(r => setTimeout(r, 400 + Math.random() * 300))
      }
      const data = await evolveContent(content, platform, strategy, language)
      setResult(data)
      setCurrentStep(-1)
    } catch (err) {
      setError(err.message)
      setCurrentStep(-1)
    } finally {
      setLoading(false)
    }
  }

  const handleCopy = useCallback(async (text, which) => {
    await navigator.clipboard.writeText(text)
    setCopied(which)
    setTimeout(() => setCopied(null), 2000)
  }, [])

  const handleFeedback = async (rating) => {
    if (!result) return
    setFeedback(rating)
    try {
      await submitFeedback('single', result.evolved.id, result.evolved.strategy, rating)
    } catch {}
  }

  const handleAudienceSim = async () => {
    if (!result) return
    setAudienceLoading(true)
    try {
      const data = await simulateAudience(result.evolved.content, platform)
      setAudienceData(data)
    } catch {}
    setAudienceLoading(false)
  }

  const handleShare = () => {
    const text = `Check out this AI-evolved content from Content DNA OS!\n\n${result.evolved.content.substring(0, 200)}...`
    const url = window.location.origin
    if (navigator.share) {
      navigator.share({ title: 'Content DNA OS', text, url }).catch(() => {})
    } else {
      const twitterUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}&url=${encodeURIComponent(url)}`
      window.open(twitterUrl, '_blank', 'noopener,noreferrer')
    }
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-dna-primary to-dna-secondary flex items-center justify-center">
            <Dna size={22} />
          </div>
          <span className="bg-gradient-to-r from-dna-primary to-dna-accent bg-clip-text text-transparent">
            Create &amp; Evolve
          </span>
        </h1>
        <p className="text-gray-400 mt-2">Input your content. Apply a mutation strategy. See its DNA transform.</p>
      </div>

      <div className="bg-dna-surface/50 rounded-2xl border border-dna-surfaceLight/30 p-6 space-y-5">
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">Your Content</label>
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="Paste your content here... (minimum 10 characters)"
            className="w-full h-40 bg-dna-dark rounded-xl border border-dna-surfaceLight/40 p-4 text-white placeholder-gray-500 resize-none focus:outline-none focus:border-dna-primary/60 focus:ring-1 focus:ring-dna-primary/30 transition-all"
          />
          <div className="text-xs text-gray-500 mt-1">{content.length} characters · {content.split(/\s+/).filter(Boolean).length} words</div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Mutation Strategy</label>
            <select
              value={strategy || ''}
              onChange={(e) => setStrategy(e.target.value || null)}
              className="w-full bg-dna-dark rounded-xl border border-dna-surfaceLight/40 p-3 text-white focus:outline-none focus:border-dna-primary/60"
            >
              {STRATEGIES.map((s) => (
                <option key={s.value || 'auto'} value={s.value || ''}>
                  {s.label} — {s.desc}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Target Platform</label>
            <select
              value={platform}
              onChange={(e) => setPlatform(e.target.value)}
              className="w-full bg-dna-dark rounded-xl border border-dna-surfaceLight/40 p-3 text-white focus:outline-none focus:border-dna-primary/60"
            >
              {PLATFORMS.map((p) => (
                <option key={p.value} value={p.value}>{p.label}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2 flex items-center gap-1">
              <Globe size={14} /> Language
            </label>
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="w-full bg-dna-dark rounded-xl border border-dna-surfaceLight/40 p-3 text-white focus:outline-none focus:border-dna-primary/60"
            >
              {LANGUAGES.map((l) => (
                <option key={l.value} value={l.value}>{l.label}</option>
              ))}
            </select>
          </div>
        </div>

        <button
          onClick={handleEvolve}
          disabled={content.length < 10 || loading}
          className="w-full py-3.5 rounded-xl bg-gradient-to-r from-dna-primary to-dna-secondary text-white font-semibold hover:scale-[1.02] transition-transform disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center gap-2 text-lg"
        >
          {loading ? (
            <><Loader2 size={20} className="animate-spin" /> Evolving...</>
          ) : (
            <><Sparkles size={20} /> Evolve Content</>
          )}
        </button>
      </div>

      {loading && currentStep >= 0 && <StepProgress steps={STEPS} currentStep={currentStep} />}

      {error && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-4 flex items-center gap-3 text-red-400">
          <AlertCircle size={18} />{error}
        </div>
      )}

      <AnimatePresence>
        {result && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="space-y-6">
            {/* Fitness Delta */}
            <div className="bg-dna-surface/50 rounded-2xl border border-dna-surfaceLight/30 p-6">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                {result.fitness_delta.improved ? <TrendingUp className="text-dna-success" size={20} /> : <TrendingDown className="text-dna-warning" size={20} />}
                Fitness Delta
              </h3>
              <div className="grid grid-cols-3 gap-4 text-center">
                <div><div className="text-sm text-gray-400">Original</div><div className="text-2xl font-bold text-white">{(result.fitness_delta.parent_fitness * 100).toFixed(1)}%</div></div>
                <div><div className="text-sm text-gray-400">Delta</div><div className={`text-2xl font-bold ${result.fitness_delta.improved ? 'text-dna-success' : 'text-dna-warning'}`}>{result.fitness_delta.delta > 0 ? '+' : ''}{(result.fitness_delta.delta * 100).toFixed(1)}%</div></div>
                <div><div className="text-sm text-gray-400">Evolved</div><div className="text-2xl font-bold text-dna-accent">{(result.fitness_delta.child_fitness * 100).toFixed(1)}%</div></div>
              </div>
            </div>

            {/* Content comparison */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-dna-surface/50 rounded-2xl border border-dna-surfaceLight/30 p-6">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-sm font-medium text-gray-400">Original</h3>
                  <button onClick={() => handleCopy(result.original, 'original')} className="text-gray-500 hover:text-white transition-colors p-1" title="Copy">
                    {copied === 'original' ? <Check size={16} className="text-dna-success" /> : <Copy size={16} />}
                  </button>
                </div>
                <p className="text-gray-300 whitespace-pre-wrap text-sm">{result.original}</p>
              </div>

              <div className="bg-dna-surface/50 rounded-2xl border border-dna-primary/30 p-6 glow-border">
                <div className="flex items-center justify-between mb-1">
                  <h3 className="text-sm font-medium text-dna-primary">Evolved — {result.evolved.strategy.replace(/_/g, ' ')}</h3>
                  <div className="flex items-center gap-1">
                    <button onClick={() => handleCopy(result.evolved.content, 'evolved')} className="text-gray-500 hover:text-white transition-colors p-1" title="Copy">
                      {copied === 'evolved' ? <Check size={16} className="text-dna-success" /> : <Copy size={16} />}
                    </button>
                    <button onClick={handleShare} className="text-gray-500 hover:text-dna-accent transition-colors p-1" title="Share">
                      <Share2 size={16} />
                    </button>
                  </div>
                </div>
                <div className="text-xs text-gray-500 mb-3">
                  Similarity: {(result.evolved.similarity_to_parent * 100).toFixed(1)}% |{result.evolved.accepted ? ' ✅ Accepted' : ` ❌ ${result.evolved.rejection_reason}`}
                </div>
                <p className="text-white whitespace-pre-wrap text-sm">{result.evolved.content}</p>
                <div className="mt-4 pt-3 border-t border-dna-surfaceLight/20 flex items-center gap-3">
                  <span className="text-xs text-gray-500">Rate:</span>
                  <button onClick={() => handleFeedback(1)} className={`p-1.5 rounded-lg transition-all ${feedback === 1 ? 'bg-dna-success/20 text-dna-success' : 'text-gray-500 hover:text-dna-success hover:bg-dna-success/10'}`}><ThumbsUp size={16} /></button>
                  <button onClick={() => handleFeedback(-1)} className={`p-1.5 rounded-lg transition-all ${feedback === -1 ? 'bg-red-500/20 text-red-400' : 'text-gray-500 hover:text-red-400 hover:bg-red-500/10'}`}><ThumbsDown size={16} /></button>
                  {feedback !== null && <span className="text-xs text-dna-accent">Recorded!</span>}
                </div>
              </div>
            </div>

            {/* DNA Comparison */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <DNACard title="Original DNA" dna={result.dna_original} />
              <DNACard title="Evolved DNA" dna={result.dna_evolved} accent />
            </div>

            {/* DNA Drift */}
            {result.dna_drift?.length > 0 && (
              <div className="bg-dna-surface/50 rounded-2xl border border-dna-surfaceLight/30 p-6">
                <h3 className="text-lg font-semibold text-white mb-4">🧬 DNA Drift Analysis</h3>
                <div className="space-y-3">
                  {result.dna_drift.map((drift, i) => (
                    <div key={i} className="bg-dna-dark rounded-xl p-4 border border-dna-surfaceLight/20">
                      <div className="flex items-center gap-2 text-sm mb-1">
                        <span className="text-gray-400 font-mono">{drift.field}</span>
                      </div>
                      <div className="flex items-center gap-3 text-sm">
                        <span className="px-2 py-0.5 bg-red-500/10 text-red-400 rounded">{drift.old_value}</span>
                        <ArrowRight size={12} className="text-gray-500" />
                        <span className="px-2 py-0.5 bg-green-500/10 text-green-400 rounded">{drift.new_value}</span>
                      </div>
                      {drift.impact && <p className="text-xs text-gray-500 mt-2">{drift.impact}</p>}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Fitness Breakdown */}
            <div className="bg-dna-surface/50 rounded-2xl border border-dna-surfaceLight/30 p-6">
              <h3 className="text-lg font-semibold text-white mb-4">📊 Fitness Breakdown</h3>
              <FitnessBar label="Length" value={result.evolved.fitness.length_score} />
              <FitnessBar label="Structural Clarity" value={result.evolved.fitness.structural_clarity} />
              <FitnessBar label="Intent Alignment" value={result.evolved.fitness.intent_alignment} />
              <FitnessBar label="Strategy Diversity" value={result.evolved.fitness.strategy_diversity} />
              <FitnessBar label="Novelty Bonus" value={result.evolved.fitness.novelty_bonus} color="cyan" />
              <FitnessBar label="Repetition Penalty" value={result.evolved.fitness.repetition_penalty} color="red" inverted />
              <FitnessBar label="Similarity Penalty" value={result.evolved.fitness.similarity_penalty} color="red" inverted />
            </div>

            {/* Audience Simulation */}
            <div className="bg-dna-surface/50 rounded-2xl border border-dna-surfaceLight/30 p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-white">🎯 Audience Simulation</h3>
                <button onClick={handleAudienceSim} disabled={audienceLoading} className="px-4 py-2 rounded-lg bg-gradient-to-r from-amber-500 to-orange-500 text-white text-sm font-medium hover:scale-105 transition-transform disabled:opacity-50 flex items-center gap-2">
                  {audienceLoading ? <Loader2 size={14} className="animate-spin" /> : <Sparkles size={14} />}
                  Simulate Reactions
                </button>
              </div>
              {audienceData ? <AudiencePanel data={audienceData} /> : (
                <p className="text-gray-500 text-sm">Click "Simulate Reactions" to see how different Indian audience segments would react.</p>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
