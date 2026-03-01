import React from 'react'
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Area,
  AreaChart,
} from 'recharts'
import { TrendingUp } from 'lucide-react'

export default function FitnessChart({ data }) {
  if (!data || data.length === 0) return null

  const chartData = data.map((d) => ({
    generation: `Gen ${d.generation}`,
    fitness: +(d.best_fitness * 100).toFixed(1),
    strategy: d.strategy?.replace(/_/g, ' ') || 'origin',
  }))

  return (
    <div className="bg-dna-surface/50 rounded-2xl border border-dna-surfaceLight/30 p-6">
      <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
        <TrendingUp size={18} className="text-dna-accent" />
        Fitness Over Generations
      </h3>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData}>
            <defs>
              <linearGradient id="fitGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#06b6d4" stopOpacity={0.3} />
                <stop offset="100%" stopColor="#06b6d4" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="generation" tick={{ fill: '#94a3b8', fontSize: 12 }} />
            <YAxis domain={[0, 100]} tick={{ fill: '#94a3b8', fontSize: 12 }} tickFormatter={(v) => `${v}%`} />
            <Tooltip
              contentStyle={{
                background: '#1e293b',
                border: '1px solid #334155',
                borderRadius: '12px',
                color: '#e2e8f0',
              }}
              formatter={(value, name) => [`${value}%`, 'Fitness']}
              labelFormatter={(label) => label}
            />
            <Area type="monotone" dataKey="fitness" stroke="#06b6d4" fill="url(#fitGrad)" strokeWidth={2} />
            <Line type="monotone" dataKey="fitness" stroke="#06b6d4" strokeWidth={2} dot={{ r: 5, fill: '#06b6d4' }} activeDot={{ r: 7 }} />
          </AreaChart>
        </ResponsiveContainer>
      </div>
      {/* Strategy legend */}
      <div className="flex flex-wrap gap-2 mt-4">
        {chartData.map((d, i) => (
          <span key={i} className="text-xs px-2 py-1 rounded bg-dna-dark border border-dna-surfaceLight/30 text-gray-400">
            {d.generation}: <span className="text-dna-accent capitalize">{d.strategy}</span> ({d.fitness}%)
          </span>
        ))}
      </div>
    </div>
  )
}
