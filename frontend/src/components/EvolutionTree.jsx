import React from 'react'
import { motion } from 'framer-motion'
import { GitBranch, Trophy, XCircle } from 'lucide-react'

/**
 * Renders the evolution tree as a visual hierarchy.
 */
export default function EvolutionTree({ tree, onSelectNode }) {
  if (!tree?.root) return null

  return (
    <div className="bg-dna-surface/50 rounded-2xl border border-dna-surfaceLight/30 p-6">
      <h3 className="text-lg font-semibold text-white mb-6 flex items-center gap-2">
        <GitBranch size={18} className="text-dna-primary" />
        Evolution Tree
      </h3>
      <div className="overflow-x-auto pb-4">
        <div className="min-w-[600px]">
          <TreeNode node={tree.root} onSelect={onSelectNode} depth={0} />
        </div>
      </div>
    </div>
  )
}

function TreeNode({ node, onSelect, depth }) {
  const strategyColors = {
    hook_amplification: 'border-orange-500/50 bg-orange-500/10',
    angle_shift: 'border-blue-500/50 bg-blue-500/10',
    story_reframe: 'border-purple-500/50 bg-purple-500/10',
    counterpoint_injection: 'border-red-500/50 bg-red-500/10',
    summary_distillation: 'border-emerald-500/50 bg-emerald-500/10',
    platform_formatting: 'border-cyan-500/50 bg-cyan-500/10',
  }

  const nodeColor = node.strategy
    ? strategyColors[node.strategy] || 'border-dna-surfaceLight/40 bg-dna-dark'
    : 'border-dna-primary/40 bg-dna-primary/10'

  return (
    <div className="flex flex-col items-center">
      {/* Node */}
      <motion.div
        whileHover={{ scale: 1.05 }}
        onClick={() => onSelect?.(node)}
        className={`cursor-pointer rounded-xl border-2 ${nodeColor} p-3 min-w-[160px] max-w-[220px] text-center transition-all hover:shadow-lg relative ${
          node.is_winner ? 'ring-2 ring-dna-success ring-offset-2 ring-offset-dna-dark' : ''
        }`}
      >
        {node.is_winner && (
          <Trophy size={14} className="absolute -top-2 -right-2 text-dna-success" />
        )}
        <div className="text-xs text-gray-500 font-mono mb-1">
          Gen {node.generation}
        </div>
        {node.strategy && (
          <div className="text-xs font-medium text-dna-accent capitalize mb-1">
            {node.strategy.replace(/_/g, ' ')}
          </div>
        )}
        <div className="text-xs text-gray-300 line-clamp-2 mb-2">
          {node.content.substring(0, 60)}...
        </div>
        <div className="text-xs font-mono text-dna-primary">
          Fitness: {(node.fitness.total * 100).toFixed(1)}%
        </div>
      </motion.div>

      {/* Children */}
      {node.children && node.children.length > 0 && (
        <>
          {/* Connector line down */}
          <div className="w-0.5 h-6 bg-gradient-to-b from-dna-primary/60 to-dna-primary/20" />
          {/* Horizontal branch line */}
          {node.children.length > 1 && (
            <div className="h-0.5 bg-dna-primary/30" style={{
              width: `${Math.min(node.children.length * 200, 800)}px`,
            }} />
          )}
          <div className="flex gap-4 mt-0">
            {node.children.map((child) => (
              <div key={child.id} className="flex flex-col items-center">
                <div className="w-0.5 h-4 bg-dna-primary/30" />
                <TreeNode node={child} onSelect={onSelect} depth={depth + 1} />
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  )
}
