import React from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Dna, FlaskConical, Eye, Zap, Shield, GitBranch, Globe, Users, ThumbsUp, Share2 } from 'lucide-react'

const features = [
  {
    icon: Dna,
    title: 'DNA Extraction',
    desc: 'Extract intent, tone, emotion, keywords, and structure from any content.',
    color: 'from-indigo-500 to-purple-500',
  },
  {
    icon: Zap,
    title: '7 Mutation Strategies',
    desc: 'Hook Amplification, Angle Shift, Story Reframe, Counterpoint, Distillation, Platform Formatting, and Regional Adaptation.',
    color: 'from-cyan-500 to-blue-500',
  },
  {
    icon: Globe,
    title: 'Multi-Language Bharat',
    desc: 'Evolve content in Hindi, Tamil, Telugu, Bengali, Marathi, Kannada, Gujarati, and English.',
    color: 'from-orange-500 to-amber-500',
  },
  {
    icon: Users,
    title: 'Audience Simulation',
    desc: 'AI-powered reactions from 5 Indian audience segments — Gen Z, Professionals, Rural Digital, Students, Business Owners.',
    color: 'from-rose-500 to-pink-500',
  },
  {
    icon: Shield,
    title: 'Similarity Guard',
    desc: 'Anti-repetition enforcement prevents degenerative evolution via semantic similarity thresholds.',
    color: 'from-emerald-500 to-green-500',
  },
  {
    icon: GitBranch,
    title: 'Evolution Trees',
    desc: 'Strategy-based sibling competition across generations. Visualize full content lineage.',
    color: 'from-amber-500 to-orange-500',
  },
  {
    icon: ThumbsUp,
    title: 'Feedback Loop',
    desc: 'Rate evolutions with thumbs up/down. The system learns which strategies work best for you.',
    color: 'from-violet-500 to-purple-500',
  },
  {
    icon: Share2,
    title: 'Share & Export',
    desc: 'Copy evolved content instantly. Share via Twitter or native share. Export your evolution results.',
    color: 'from-teal-500 to-cyan-500',
  },
]

const container = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { staggerChildren: 0.1 } },
}
const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0 },
}

export default function LandingPage() {
  return (
    <div className="space-y-16 pb-16">
      {/* Hero */}
      <motion.section
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="text-center pt-12"
      >
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-dna-primary/10 border border-dna-primary/30 text-dna-primary text-sm mb-6">
          <Dna size={14} />
          Evolutionary AI for Bharat 🇮🇳
        </div>
        <h1 className="text-5xl md:text-6xl font-extrabold leading-tight">
          <span className="bg-gradient-to-r from-dna-primary via-dna-secondary to-dna-accent bg-clip-text text-transparent">
            Content DNA OS
          </span>
        </h1>
        <p className="mt-4 text-xl text-gray-400 max-w-2xl mx-auto">
          An evolutionary operating system that treats content like a living organism.
          Mutate, score, select, and evolve — built for India's diverse audiences.
        </p>
        <div className="mt-8 flex items-center justify-center gap-4">
          <Link
            to="/create"
            className="px-6 py-3 rounded-xl bg-gradient-to-r from-dna-primary to-dna-secondary text-white font-semibold hover:scale-105 transition-transform shadow-lg shadow-dna-primary/25"
          >
            Start Evolving
          </Link>
          <Link
            to="/lab"
            className="px-6 py-3 rounded-xl border border-dna-surfaceLight text-gray-300 hover:bg-dna-surface/50 font-medium transition-all"
          >
            Open Lab
          </Link>
        </div>
      </motion.section>

      {/* Architecture Diagram */}
      <motion.section
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
        className="bg-dna-surface/50 rounded-2xl border border-dna-surfaceLight/30 p-8"
      >
        <h2 className="text-center text-lg font-semibold text-gray-300 mb-6">Evolution Pipeline</h2>
        <div className="flex flex-col md:flex-row items-center justify-center gap-4 text-sm">
          {['Content Input', 'DNA Extraction', 'Multi-Strategy Mutation', 'Similarity Guard', 'Fitness Scoring', 'Winner Selection'].map((step, i) => (
            <React.Fragment key={step}>
              <div className="bg-dna-dark rounded-xl px-4 py-3 border border-dna-surfaceLight/40 text-center min-w-[140px]">
                <div className="text-dna-accent font-mono text-xs mb-1">Step {i + 1}</div>
                <div className="text-white font-medium">{step}</div>
              </div>
              {i < 5 && (
                <div className="text-dna-primary font-bold text-lg hidden md:block">→</div>
              )}
            </React.Fragment>
          ))}
        </div>
      </motion.section>

      {/* Features */}
      <motion.section variants={container} initial="hidden" animate="show">
        <h2 className="text-center text-2xl font-bold mb-8">
          <span className="bg-gradient-to-r from-dna-primary to-dna-accent bg-clip-text text-transparent">
            Core Capabilities
          </span>
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {features.map((f) => (
            <motion.div
              key={f.title}
              variants={item}
              className="bg-dna-surface/50 rounded-2xl border border-dna-surfaceLight/30 p-6 hover:border-dna-primary/40 transition-colors"
            >
              <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${f.color} flex items-center justify-center mb-4`}>
                <f.icon size={20} className="text-white" />
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">{f.title}</h3>
              <p className="text-gray-400 text-sm">{f.desc}</p>
            </motion.div>
          ))}
        </div>
      </motion.section>

      {/* CTA */}
      <section className="text-center">
        <div className="bg-gradient-to-r from-dna-primary/10 to-dna-accent/10 rounded-2xl border border-dna-primary/20 p-10">
          <h2 className="text-2xl font-bold text-white mb-3">This is not content generation.</h2>
          <p className="text-gray-400 mb-6">This is content <span className="text-dna-accent font-semibold">selection</span> through evolutionary pressure — optimized for <span className="text-orange-400 font-semibold">Bharat</span>.</p>
          <Link
            to="/lab"
            className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-dna-primary to-dna-accent text-white font-semibold hover:scale-105 transition-transform"
          >
            <FlaskConical size={18} />
            Enter the Evolution Lab
          </Link>
        </div>
      </section>
    </div>
  )
}
