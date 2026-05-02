import { useEffect, useRef, useState } from 'react'
import { Network } from 'vis-network'
import axios from 'axios'

const GROUP_COLORS = {
  customer:    { background: '#6366f1', border: '#4f46e5', font: { color: '#fff' } },
  product:     { background: '#10b981', border: '#059669', font: { color: '#fff' } },
  sales_order: { background: '#0ea5e9', border: '#0284c7', font: { color: '#fff' } },
  delivery:    { background: '#f59e0b', border: '#d97706', font: { color: '#fff' } },
  billing:     { background: '#8b5cf6', border: '#7c3aed', font: { color: '#fff' } },
  payment:     { background: '#ec4899', border: '#db2777', font: { color: '#fff' } },
  journal:     { background: '#64748b', border: '#475569', font: { color: '#fff' } },
}

export default function GraphView({ onNodeSelect, highlightNodes, api }) {
  const containerRef = useRef(null)
  const networkRef = useRef(null)
  const nodesRef = useRef(new Map())
  const edgesRef = useRef(new Map())
  const [loading, setLoading] = useState(true)
  const [tooltip, setTooltip] = useState(null)

  useEffect(() => {
    axios.get(`${api}/api/graph`).then(res => {
      const { nodes, edges } = res.data
      initNetwork(nodes, edges)
      setLoading(false)
    })
  }, [])

  const initNetwork = (nodes, edges) => {
    const visNodes = nodes.map(n => ({
      id: n.id,
      label: n.label,
      title: n.title,
      ...GROUP_COLORS[n.group],
      shape: 'dot',
      size: n.group === 'customer' ? 20 : n.group === 'sales_order' ? 16 : 12,
    }))
    const visEdges = edges.map((e, i) => ({
      id: `e${i}`, from: e.from, to: e.to,
      label: e.label, arrows: 'to',
      color: { color: '#3d4a5c', hover: '#64748b' },
      font: { size: 9, color: '#64748b', align: 'middle' },
      width: 1.5
    }))

    visNodes.forEach(n => nodesRef.current.set(n.id, n))
    visEdges.forEach(e => edgesRef.current.set(e.id, e))

    const ds = { nodes: visNodes, edges: visEdges }
    const options = {
      physics: { solver: 'forceAtlas2Based', stabilization: { iterations: 150 } },
      layout: { improvedLayout: false },
      interaction: { hover: true, tooltipDelay: 200, hideEdgesOnDrag: true },
      edges: { smooth: { type: 'continuous' } },
    }

    if (networkRef.current) networkRef.current.destroy()
    networkRef.current = new Network(containerRef.current, ds, options)

    networkRef.current.on('click', async (params) => {
      if (params.nodes.length > 0) {
        const nid = params.nodes[0]
        onNodeSelect(nid)
        // Expand node
        try {
          const res = await axios.get(`${api}/api/graph/expand/${nid}`)
          const { nodes: newNodes, edges: newEdges } = res.data
          const dsRef = networkRef.current.body.data

          newNodes.forEach(n => {
            if (!nodesRef.current.has(n.id)) {
              const vn = {
                id: n.id, label: n.label, title: n.title,
                ...GROUP_COLORS[n.group],
                shape: 'dot', size: 12
              }
              nodesRef.current.set(n.id, vn)
              dsRef.nodes.add(vn)
            }
          })
          newEdges.forEach((e, i) => {
            const eid = `exp_${nid}_${i}`
            if (!edgesRef.current.has(eid)) {
              const ve = {
                id: eid, from: e.from, to: e.to, label: e.label,
                arrows: 'to',
                color: { color: '#3d4a5c' },
                font: { size: 9, color: '#64748b', align: 'middle' },
                width: 1.5
              }
              edgesRef.current.set(eid, ve)
              dsRef.edges.add(ve)
            }
          })
        } catch {}
      }
    })
  }

  // Legend
  const legendItems = Object.entries(GROUP_COLORS).map(([k, v]) => (
    <div key={k} style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 11 }}>
      <div style={{
        width: 10, height: 10, borderRadius: '50%',
        background: v.background
      }} />
      <span style={{ color: '#94a3b8', textTransform: 'capitalize' }}>
        {k.replace('_', ' ')}
      </span>
    </div>
  ))

  return (
    <div style={{ flex: 1, position: 'relative', background: '#0f1117' }}>
      {loading && (
        <div style={{
          position: 'absolute', inset: 0, display: 'flex',
          alignItems: 'center', justifyContent: 'center',
          background: '#0f1117', zIndex: 10, flexDirection: 'column', gap: 12
        }}>
          <div style={{ fontSize: 32 }}>⬡</div>
          <div style={{ color: '#64748b', fontSize: 14 }}>Building graph...</div>
        </div>
      )}
      <div ref={containerRef} style={{ width: '100%', height: '100%' }} />
      
      {/* Legend */}
      <div style={{
        position: 'absolute', bottom: 16, left: 16,
        background: '#161b2e', border: '1px solid #2d3748',
        borderRadius: 8, padding: '10px 14px',
        display: 'flex', flexDirection: 'column', gap: 6
      }}>
        <div style={{ fontSize: 10, color: '#475569', fontWeight: 600, marginBottom: 2 }}>
          ENTITY TYPES
        </div>
        {legendItems}
      </div>

      {/* Hint */}
      <div style={{
        position: 'absolute', top: 12, left: 12,
        background: '#161b2e88', border: '1px solid #2d374860',
        borderRadius: 6, padding: '6px 10px', fontSize: 11, color: '#64748b'
      }}>
        Click any node to expand its relationships
      </div>
    </div>
  )
}