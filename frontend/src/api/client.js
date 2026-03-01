const API_BASE = '/api'

export async function evolveContent(content, platform = 'general', strategy = null) {
  const body = { content, platform }
  if (strategy) body.strategy = strategy

  const res = await fetch(`${API_BASE}/evolve`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) throw new Error(`API error: ${res.status}`)
  return res.json()
}

export async function evolveInLab(content, platform = 'general', generations = 3, strategies = null) {
  const body = { content, platform, generations }
  if (strategies) body.strategies = strategies

  const res = await fetch(`${API_BASE}/evolve/lab`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) throw new Error(`API error: ${res.status}`)
  return res.json()
}

export async function getStrategies() {
  const res = await fetch(`${API_BASE}/strategies`)
  if (!res.ok) throw new Error(`API error: ${res.status}`)
  return res.json()
}

export async function getPlatforms() {
  const res = await fetch(`${API_BASE}/platforms`)
  if (!res.ok) throw new Error(`API error: ${res.status}`)
  return res.json()
}
