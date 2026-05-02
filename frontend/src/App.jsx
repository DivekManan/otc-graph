import { useState, useEffect } from 'react'
import axios from 'axios'
import GraphView from './components/GraphView'
import ChatPanel from './components/ChatPanel'

const API = import.meta.env.VITE_API_URL || ''

export default function App() {
  const [stats, setStats] = useState(null)
  const [selectedNode, setSelectedNode] = useState(null)
  const [highlightNodes, setHighlightNodes] = useState([])

  useEffect(() => {
    axios.get(`${API}/api/stats`).then(r => setStats(r.data))
  }, [])

  const statCards = stats ? [
    { label: 'Customers', value: stats.customers, color: '#6366f1' },
    { label: 'Sales Orders', value: stats.sales_orders, color: '#0ea5e9' },
    { label: 'Deliveries', value: stats.deliveries, color: '#10b981' },
    { label: 'Billing Docs', value: stats.billing_documents, color: '#f59e0b' },
    { label: 'Payments', value: stats.payments, color: '#8b5cf6' },
    { label: 'Broken Flows', value: stats.broken_flows, color: '#ef4444' },
  ] : []

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', background: '#0f1117' }}>
      {/* Header */}
      <div style={{
        padding: '12px 24px', background: '#161b2e',
        borderBottom: '1px solid #2d3748', display: 'flex',
        alignItems: 'center', justifyContent: 'space-between', flexShrink: 0
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div style={{
            width: 36, height: 36, borderRadius: 8,
            background: 'linear-gradient(135deg, #6366f1, #0ea5e9)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: 18
          }}>⬡</div>
          <div>
            <div style={{ fontWeight: 700, fontSize: 16, color: '#f1f5f9' }}>
              Order-to-Cash Graph Explorer
            </div>
            <div style={{ fontSize: 11, color: '#64748b' }}>SAP Business Data Intelligence</div>
          </div>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          {statCards.map(s => (
            <div key={s.label} style={{
              padding: '4px 12px', borderRadius: 20,
              background: s.color + '20',
              border: `1px solid ${s.color}40`,
              fontSize: 12, display: 'flex', gap: 6, alignItems: 'center'
            }}>
              <span style={{ color: s.color, fontWeight: 700 }}>{s.value}</span>
              <span style={{ color: '#94a3b8' }}>{s.label}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Main */}
      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        <GraphView
          onNodeSelect={setSelectedNode}
          highlightNodes={highlightNodes}
          api={API}
        />
        <ChatPanel
          selectedNode={selectedNode}
          onHighlight={setHighlightNodes}
          api={API}
        />
      </div>
    </div>
  )
}