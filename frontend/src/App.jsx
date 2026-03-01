import React from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import CreatePage from './components/CreatePage'
import EvolutionLab from './components/EvolutionLab'
import DNAViewer from './components/DNAViewer'
import LandingPage from './components/LandingPage'

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-dna-darker">
        <Navbar />
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/create" element={<CreatePage />} />
            <Route path="/lab" element={<EvolutionLab />} />
            <Route path="/dna" element={<DNAViewer />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}
