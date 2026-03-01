import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { FlaskConical, Play, Trophy, GitBranch, XCircle, AlertCircle, ChevronDown } from 'lucide-react'
import { evolveInLab } from '../api/client'
import EvolutionTree from './EvolutionTree'
import FitnessChart from './FitnessChart'
import DNACard from './DNACard'
import DNADrift from './DNADrift'

export default function EvolutionLab() {
  const [content, setContent] = useState('')
  const [platform, setPlatform] = useState('general')
  const [generations, setGenerations] = useState(3)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [selectedNode, setSelectedNode] = useState(null)

  const handleEvolve = async () => {
    if (content.length < 10) return
    setLoading(true)
    setError(null)
    setSelectedNode(null)
    try {
      const data = await evolveInLab(content, platform, generations)
      setResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-dna-accent to-cyan-400 flex items-center justify-center">
            <FlaskConical size={22} />
          </div>
          <span className="bg-gradient-to-r from-dna-accent to-dna-primary bg-clip-text text-transparent">
            Evolution Lab
          </span>
        </h1>
        <p className="text-gray-400 mt-2">
          Multi-generation evolution engine. Watch content evolve through strategy-based sibling competition.
        </p>
      </div>

      {/* Input */}
      <div className="bg-dna-surface/50 rounded-2xl border border-dna-surfaceLight/30 p-6 space-y-5">
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">Seed Content</label>
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="Enter your seed content to evolve across multiple generations..."
            className="w-full h-36 bg-dna-dark rounded-xl border border-dna-surfaceLight/40 p-4 text-white placeholder-gray-500 resize-none focus:outline-none focus:border-dna-accent/60 focus:ring-1 focus:ring-dna-accent/30 transition-all"
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Platform</label>
            <select
              value={platform}
              onChange={(e) => setPlatform(e.target.value)}
              className="w-full bg-dna-dark rounded-xl border border-dna-surfaceLight/40 p-3 text-white focus:outline-none focus:border-dna-accent/60"
            >
              {['general','twitter','linkedin','instagram','blog','email','youtube'].map(p => (
                <option key={p} value={p}>{p.charAt(0).toUpperCase() + p.slice(1)}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Generations: {generations}
            </label>
            <input
              type="range"
              min="1"
              max="10"
              value={generations}
              onChange={(e) => setGenerations(Number(e.target.value))}
              className="w-full accent-dna-accent"
            />
            <div className="flex justify-between text-xs text-gray-500">
              <span>1</span><span>5</span><span>10</span>
            </div>
          </div>
        </div>

        <button
          onClick={handleEvolve}
          disabled={content.length < 10 || loading}
          className="w-full py-3 rounded-xl bg-gradient-to-r from-dna-accent to-cyan-400 text-dna-dark font-bold hover:scale-[1.02] transition-transform disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <div className="animate-spin w-5 h-5 border-2 border-dna-dark/30 border-t-dna-dark rounded-full" />
              Running Evolution...
            </>
          ) : (
            <>
              <Play size={18} />
              Launch Evolution ({generations} generations)
            </>
          )}
        </button>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-4 flex items-center gap-3 text-red-400">
          <AlertCircle size={18} />{error}
        </div>
      )}

      {/* Results */}
      <AnimatePresence>
        {result && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-8"
          >
            {/* Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {[
                { label: 'Generations', value: result.tree.total_generations, color: 'text-dna-primary' },
                { label: 'Mutations', value: result.tree.total_mutations, color: 'text-dna-accent' },
                { label: 'Rejected', value: result.tree.total_rejected, color: 'text-dna-danger' },
                { label: 'Winning Strategy', value: result.tree.winning_strategy?.replace(/_/g, ' ') || 'N/A', color: 'text-dna-success' },
              ].map((stat) => (
                <div key={stat.label} className="bg-dna-surface/50 rounded-xl border border-dna-surfaceLight/30 p-4 text-center">
                  <div className="text-xs text-gray-400">{stat.label}</div>
                  <div className={`text-xl font-bold mt-1 ${stat.color} capitalize`}>{stat.value}</div>
                </div>
              ))}
            </div>

            {/* Winner */}
            <div className="bg-gradient-to-r from-dna-success/10 to-emerald-500/5 rounded-2xl border border-dna-success/30 p-6 glow-border-success">
              <h3 className="text-lg font-semibold text-dna-success flex items-center gap-2 mb-3">
                <Trophy size={20} />
                Evolutionary Winner
              </h3>
              <div className="text-xs text-gray-400 mb-2">
                Strategy: <span className="text-dna-accent capitalize">{result.winner.strategy?.replace(/_/g, ' ')}</span> | 
                Fitness: <span className="text-dna-success font-bold">{(result.winner.fitness.total * 100).toFixed(1)}%</span>
              </div>
              <p className="text-white whitespace-pre-wrap text-sm">{result.winner.content}</p>
            </div>

            {/* Fitness Chart */}
            <FitnessChart data={result.generation_fitness} />

            {/* Evolution Tree */}
            <EvolutionTree tree={result.tree} onSelectNode={setSelectedNode} />

            {/* Selected Node Detail */}
            {selectedNode && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                className="bg-dna-surface/50 rounded-2xl border border-dna-primary/30 p-6 space-y-4"
              >
                <h3 className="text-lg font-semibold text-white">
                  Node Detail — Gen {selectedNode.generation}
                  {selectedNode.strategy && (
                    <span className="ml-2 text-sm text-dna-accent capitalize">
                      ({selectedNode.strategy.replace(/_/g, ' ')})
                    </span>
                  )}
                  {selectedNode.is_winner && <Trophy size={16} className="inline ml-2 text-dna-success" />}
                </h3>
                <p className="text-gray-300 text-sm whitespace-pre-wrap">{selectedNode.content}</p>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                  <DNACard title="DNA Profile" dna={selectedNode.dna} accent />
                  {selectedNode.dna_drift?.length > 0 && (
                    <DNADrift drifts={selectedNode.dna_drift} />
                  )}
                </div>
              </motion.div>
            )}

            {/* Rejected Mutations */}
            {result.rejected_mutations?.length > 0 && (
              <div className="bg-dna-surface/50 rounded-2xl border border-dna-surfaceLight/30 p-6">
                <h3 className="text-lg font-semibold text-gray-300 flex items-center gap-2 mb-4">
                  <XCircle size={18} className="text-dna-danger" />
                  Rejected Mutations ({result.rejected_mutations.length})
                </h3>
                <div className="space-y-3">
                  {result.rejected_mutations.map((mut, i) => (
                    <div key={i} className="bg-dna-dark rounded-xl p-4 border border-red-500/10">
                      <div className="flex items-center justify-between text-sm mb-2">
                        <span className="text-gray-400 capitalize">{mut.strategy.replace(/_/g, ' ')}</span>
                        <span className="text-red-400 text-xs">{mut.rejection_reason}</span>
                      </div>
                      <p className="text-gray-500 text-xs line-clamp-2">{mut.content}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
