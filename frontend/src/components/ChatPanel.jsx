import { useState, useRef, useEffect } from 'react'
import axios from 'axios'

const SAMPLE_QUESTIONS = [
  "Which products are associated with the highest number of billing documents?",
  "Show all sales orders with broken or incomplete flows",
  "Trace the full flow of billing document BILL000001",
  "Which customers have the highest total order value?",
  "List deliveries that are in transit",
  "What is the total revenue from all payments?",
]

export default function ChatPanel({ selectedNode, onHighlight, api }) {
  const [messages, setMessages] = useState([{
    role: 'assistant',
    content: "👋 Hello! I'm your Order-to-Cash data analyst. Ask me anything about your business data — orders, deliveries, billing, payments, and more.",
    sql: null, data: null
  }])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  useEffect(() => {
    if (selectedNode) {
      setInput(`Tell me about node ${selectedNode}`)
    }
  }, [selectedNode])

  const send = async (text) => {
    const q = text || input.trim()
    if (!q) return
    setInput('')
    setMessages(m => [...m, { role: 'user', content: q }])
    setLoading(true)
    try {
      const res = await axios.post(`${api}/api/chat`, { message: q })
      const { answer, sql, data } = res.data
      setMessages(m => [...m, { role: 'assistant', content: answer, sql, data }])
    } catch {
      setMessages(m => [...m, {
        role: 'assistant',
        content: 'Connection error. Please check the backend server.',
        sql: null, data: null
      }])
    }
    setLoading(false)
  }

  return (
    <div style={{
      width: 400, display: 'flex', flexDirection: 'column',
      background: '#161b2e', borderLeft: '1px solid #2d3748'
    }}>
      {/* Header */}
      <div style={{
        padding: '14px 16px', borderBottom: '1px solid #2d3748',
        display: 'flex', alignItems: 'center', gap: 10
      }}>
        <div style={{
          width: 32, height: 32, borderRadius: '50%',
          background: 'linear-gradient(135deg, #6366f1, #0ea5e9)',
          display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 16
        }}>🤖</div>
        <div>
          <div style={{ fontWeight: 600, fontSize: 14, color: '#f1f5f9' }}>Data Analyst AI</div>
          <div style={{ fontSize: 11, color: '#22c55e' }}>● Connected to OTC Database</div>
        </div>
      </div>

      {/* Sample Questions */}
      <div style={{
        padding: '10px 12px', borderBottom: '1px solid #1e2640',
        display: 'flex', gap: 6, flexWrap: 'wrap'
      }}>
        {SAMPLE_QUESTIONS.slice(0, 3).map(q => (
          <button key={q} onClick={() => send(q)} style={{
            background: '#1e2640', border: '1px solid #2d3748',
            borderRadius: 12, padding: '3px 10px', fontSize: 10,
            color: '#94a3b8', cursor: 'pointer', transition: 'all 0.2s'
          }}
          onMouseEnter={e => e.target.style.borderColor = '#6366f1'}
          onMouseLeave={e => e.target.style.borderColor = '#2d3748'}
          >{q.length > 35 ? q.slice(0,35)+'...' : q}</button>
        ))}
      </div>

      {/* Messages */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '12px 14px', display: 'flex', flexDirection: 'column', gap: 12 }}>
        {messages.map((m, i) => (
          <MessageBubble key={i} message={m} />
        ))}
        {loading && (
          <div style={{
            alignSelf: 'flex-start', background: '#1e2640',
            borderRadius: '12px 12px 12px 4px', padding: '10px 14px',
            display: 'flex', gap: 6, alignItems: 'center'
          }}>
            {[0,1,2].map(j => (
              <div key={j} style={{
                width: 6, height: 6, borderRadius: '50%',
                background: '#6366f1',
                animation: `bounce 1s ${j*0.2}s infinite`
              }} />
            ))}
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div style={{
        padding: '12px 14px', borderTop: '1px solid #2d3748',
        display: 'flex', gap: 8
      }}>
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && !e.shiftKey && send()}
          placeholder="Ask about orders, deliveries, billing..."
          style={{
            flex: 1, background: '#0f1117', border: '1px solid #2d3748',
            borderRadius: 8, padding: '10px 12px', color: '#e2e8f0',
            fontSize: 13, outline: 'none', transition: 'border-color 0.2s'
          }}
          onFocus={e => e.target.style.borderColor = '#6366f1'}
          onBlur={e => e.target.style.borderColor = '#2d3748'}
        />
        <button
          onClick={() => send()}
          disabled={loading || !input.trim()}
          style={{
            background: loading || !input.trim() ? '#2d3748' : 'linear-gradient(135deg, #6366f1, #0ea5e9)',
            border: 'none', borderRadius: 8, padding: '10px 14px',
            cursor: loading || !input.trim() ? 'not-allowed' : 'pointer',
            color: '#fff', fontSize: 16, transition: 'all 0.2s'
          }}
        >➤</button>
      </div>

      <style>{`
        @keyframes bounce {
          0%,80%,100% { transform: translateY(0); }
          40% { transform: translateY(-6px); }
        }
      `}</style>
    </div>
  )
}

function MessageBubble({ message }) {
  const [showSQL, setShowSQL] = useState(false)
  const [showData, setShowData] = useState(false)
  const isUser = message.role === 'user'

  return (
    <div style={{ alignSelf: isUser ? 'flex-end' : 'flex-start', maxWidth: '88%' }}>
      <div style={{
        background: isUser ? 'linear-gradient(135deg, #6366f1, #4f46e5)' : '#1e2640',
        borderRadius: isUser ? '12px 12px 4px 12px' : '12px 12px 12px 4px',
        padding: '10px 14px', fontSize: 13, color: '#e2e8f0', lineHeight: 1.5
      }}>
        {message.content}
      </div>
      {message.sql && (
        <div style={{ marginTop: 4, display: 'flex', gap: 6 }}>
          <button onClick={() => setShowSQL(!showSQL)} style={{
            background: 'none', border: '1px solid #2d3748', borderRadius: 4,
            padding: '2px 8px', fontSize: 10, color: '#64748b', cursor: 'pointer'
          }}>
            {showSQL ? '▼' : '▶'} SQL
          </button>
          {message.data?.length > 0 && (
            <button onClick={() => setShowData(!showData)} style={{
              background: 'none', border: '1px solid #2d3748', borderRadius: 4,
              padding: '2px 8px', fontSize: 10, color: '#64748b', cursor: 'pointer'
            }}>
              {showData ? '▼' : '▶'} {message.data.length} rows
            </button>
          )}
        </div>
      )}
      {showSQL && message.sql && (
        <pre style={{
          marginTop: 4, background: '#0f1117', border: '1px solid #2d3748',
          borderRadius: 6, padding: '8px 10px', fontSize: 11, color: '#a78bfa',
          overflowX: 'auto', whiteSpace: 'pre-wrap'
        }}>{message.sql}</pre>
      )}
      {showData && message.data?.length > 0 && (
        <div style={{
          marginTop: 4, background: '#0f1117', border: '1px solid #2d3748',
          borderRadius: 6, overflow: 'auto', maxHeight: 200, fontSize: 11
        }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ background: '#161b2e' }}>
                {Object.keys(message.data[0]).map(k => (
                  <th key={k} style={{ padding: '4px 8px', color: '#64748b', textAlign: 'left', borderBottom: '1px solid #2d3748' }}>{k}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {message.data.slice(0,10).map((row, i) => (
                <tr key={i} style={{ borderBottom: '1px solid #1e2640' }}>
                  {Object.values(row).map((v, j) => (
                    <td key={j} style={{ padding: '4px 8px', color: '#94a3b8' }}>
                      {String(v).slice(0, 30)}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}