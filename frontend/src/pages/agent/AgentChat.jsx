import { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import Navbar from '../shared/Navbar'
import api from '../../services/api'

export default function AgentChat() {
  const { ticketId } = useParams()
  const { user, token } = useAuth()
  const navigate = useNavigate()
  const [ticket, setTicket] = useState(null)
  const [messages, setMessages] = useState([])
  const [newMessage, setNewMessage] = useState('')
  const [connected, setConnected] = useState(false)
  const wsRef = useRef(null)
  const messagesEndRef = useRef(null)

  useEffect(() => {
    fetchTicket()
    fetchMessages()
    connectWebSocket()
    return () => { if (wsRef.current) wsRef.current.close() }
  }, [ticketId])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const fetchTicket = async () => {
    try {
      const res = await api.get(`/tickets/${ticketId}`)
      setTicket(res.data)
    } catch (err) { console.error(err) }
  }

  const fetchMessages = async () => {
    try {
      const res = await api.get(`/tickets/${ticketId}/messages`)
      setMessages(res.data)
    } catch (err) { console.error(err) }
  }

  const connectWebSocket = () => {
    const WS_URL = import.meta.env.VITE_WS_URL || 'ws://127.0.0.1:8000'
    const ws = new WebSocket(`${WS_URL}/ws/${ticketId}?token=${token}`)
    ws.onopen = () => setConnected(true)
    ws.onclose = () => setConnected(false)
    ws.onmessage = (e) => {
      const data = JSON.parse(e.data)
      if (data.type === 'message') {
        setMessages(prev => [...prev, data])
      }
    }
    wsRef.current = ws
  }

  const sendMessage = () => {
    if (!newMessage.trim() || !wsRef.current) return
    wsRef.current.send(JSON.stringify({ content: newMessage }))
    setNewMessage('')
  }

  const handleStatusChange = async (newStatus) => {
    try {
      await api.patch(`/tickets/${ticketId}/status`, { status: newStatus })
      fetchTicket()
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to update status')
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Navbar />
      <div className="max-w-4xl mx-auto w-full px-4 py-6 flex flex-col flex-1">
        <button onClick={() => navigate('/agent')} className="text-blue-600 text-sm mb-4 hover:underline text-left">
          ← Back to dashboard
        </button>

        {ticket && (
          <div className="bg-white rounded-lg border p-4 mb-4">
            <div className="flex justify-between items-center">
              <div>
                <h2 className="font-bold text-gray-800">#{ticket.id} {ticket.subject}</h2>
                <p className="text-gray-500 text-sm">{ticket.description}</p>
              </div>
              <div className="flex gap-2">
                {ticket.status === 'in_progress' && (
                  <button
                    onClick={() => handleStatusChange('resolved')}
                    className="bg-green-600 text-white px-3 py-1.5 rounded-lg text-sm hover:bg-green-700"
                  >
                    Mark Resolved
                  </button>
                )}
                <div className="flex items-center gap-1">
                  <span className={`w-2 h-2 rounded-full ${connected ? 'bg-green-500' : 'bg-red-500'}`} />
                  <span className="text-xs text-gray-500">{connected ? 'Live' : 'Offline'}</span>
                </div>
              </div>
            </div>
          </div>
        )}

        <div className="bg-white rounded-lg border flex flex-col" style={{minHeight: '450px'}}>
          <div className="p-4 border-b">
            <h3 className="font-semibold text-gray-700">Customer Chat</h3>
          </div>
          <div className="flex-1 overflow-y-auto p-4 space-y-3" style={{maxHeight: '400px'}}>
            {messages.map((msg, idx) => (
              <div key={idx} className={`flex ${msg.sender_id === user?.id ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                  msg.is_auto_response ? 'bg-gray-100 text-gray-600 text-sm italic' :
                  msg.sender_id === user?.id ? 'bg-green-600 text-white' : 'bg-gray-100 text-gray-800'
                }`}>
                  {msg.sender_id !== user?.id && (
                    <p className="text-xs font-medium mb-1 opacity-70">{msg.sender_name || 'Customer'}</p>
                  )}
                  <p className="text-sm">{msg.content}</p>
                  <p className="text-xs opacity-60 mt-1">{new Date(msg.created_at).toLocaleTimeString()}</p>
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
          <div className="p-4 border-t flex gap-2">
            <input
              type="text"
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
              placeholder="Type your reply..."
              className="flex-1 border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-500"
              disabled={!connected}
            />
            <button
              onClick={sendMessage}
              disabled={!connected || !newMessage.trim()}
              className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 disabled:opacity-50"
            >
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}