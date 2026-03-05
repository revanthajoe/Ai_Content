// Use environment variable for API Gateway, fallback to relative /api for local/nginx
const API_BASE = import.meta.env.VITE_API_BASE || '/api'

async function handleResponse(res) {
  if (!res.ok) {
    let detail = `API error: ${res.status}`
    try {
      const err = await res.json()
      if (err.detail) detail = typeof err.detail === 'string' ? err.detail : JSON.stringify(err.detail)
    } catch {}
    throw new Error(detail)
  }
  return res.json()
}

export async function evolveContent(content, platform = 'general', strategy = null, language = 'english') {
  const body = { content, platform, language }
  if (strategy) body.strategy = strategy

  const res = await fetch(`${API_BASE}/evolve`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  return handleResponse(res)
}

export async function evolveInLab(content, platform = 'general', generations = 3, strategies = null, language = 'english') {
  const body = { content, platform, generations, language }
  if (strategies) body.strategies = strategies

  const res = await fetch(`${API_BASE}/evolve/lab`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  return handleResponse(res)
}

export async function extractDNA(content) {
  const res = await fetch(`${API_BASE}/dna/extract`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content }),
  })
  return handleResponse(res)
}

export async function scoreFitness(content) {
  const res = await fetch(`${API_BASE}/fitness/score`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content }),
  })
  return handleResponse(res)
}

export async function simulateAudience(content, platform = 'general') {
  const res = await fetch(`${API_BASE}/audience/simulate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content, platform }),
  })
  return handleResponse(res)
}

export async function submitFeedback(contentId, mutationId, strategy, rating) {
  const res = await fetch(`${API_BASE}/feedback`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      content_id: contentId,
      mutation_id: mutationId,
      strategy,
      rating,
    }),
  })
  return handleResponse(res)
}

export async function getSharedEvolution(contentId) {
  const res = await fetch(`${API_BASE}/share/${encodeURIComponent(contentId)}`)
  return handleResponse(res)
}

export async function getStrategies() {
  const res = await fetch(`${API_BASE}/strategies`)
  return handleResponse(res)
}

export async function getPlatforms() {
  const res = await fetch(`${API_BASE}/platforms`)
  return handleResponse(res)
}

export async function getEvolutionHistory() {
  const res = await fetch(`${API_BASE}/evolutions`)
  return handleResponse(res)
}
