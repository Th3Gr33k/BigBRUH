import React, { useEffect, useState } from 'react'

type Ready = {
  status: string
  checks: Record<string, boolean>
}

export function App() {
  const [ready, setReady] = useState<Ready | null>(null)

  useEffect(() => {
    fetch('http://localhost:8000/readyz')
      .then((r) => r.json())
      .then(setReady)
      .catch(() => setReady({ status: 'offline', checks: {} }))
  }, [])

  return (
    <main style={{ fontFamily: 'Arial, sans-serif', margin: '2rem', maxWidth: 900 }}>
      <h1>SentinelForge</h1>
      <p>Self-hosted threat actor investigation and defensive disruption platform.</p>

      <h2>Platform Status</h2>
      <pre>{JSON.stringify(ready, null, 2)}</pre>

      <h2>Core Capabilities</h2>
      <ul>
        <li>Case intake and indicator tracking</li>
        <li>Passive enrichment pipeline (lawful, non-offensive)</li>
        <li>Evidence-safe workflows (hashing + audit trail)</li>
        <li>IOC export for defensive controls and sharing</li>
      </ul>

      <p><strong>Safety:</strong> Defensive-only, lawful operations.</p>
    </main>
  )
}
