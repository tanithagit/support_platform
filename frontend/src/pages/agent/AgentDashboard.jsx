import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import Navbar from '../shared/Navbar'
import api from '../../services/api'

export default function AgentDashboard() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [tickets, setTickets] = useState([])
  const [stats, setStats] = useState({})
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchTickets()
    fetchStats()
  }, [])

  const fetchTickets = async () => {
    try {
      const res = await api.get('/tickets/')
      setTickets(res.data)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const fetchStats = async () => {
    try {
      const res = await api.get('/tickets/dashboard')
      setStats(res.data)
    } catch (err) {
      console.error(err)
    }
  }

  const handleStatusChange = async (ticketId, newStatus) => {
    try {
      await api.patch(`/tickets/${ticketId}/status`, { status: newStatus })
      fetchTickets()
      fetchStats()
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to update status')
    }
  }

  const getStatusColor = (status) => {
    const colors = {
      open: 'bg-blue-100 text-blue-800',
      in_progress: 'bg-yellow-100 text-yellow-800',
      resolved: 'bg-green-100 text-green-800',
      closed: 'bg-gray-100 text-gray-800',
    }
    return colors[status] || 'bg-gray-100 text-gray-800'
  }

  const getNextStatus = (status) => {
    const next = { open: 'in_progress', in_progress: 'resolved', resolved: 'closed' }
    return next[status] || null
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-800">Agent Dashboard</h1>
          <p className="text-gray-500">Manage your assigned tickets</p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-4 gap-4 mb-6">
          {[
            { label: 'Total', value: stats.total || 0, color: 'text-gray-800' },
            { label: 'Open', value: stats.open || 0, color: 'text-blue-600' },
            { label: 'In Progress', value: stats.in_progress || 0, color: 'text-yellow-600' },
            { label: 'Resolved', value: stats.resolved || 0, color: 'text-green-600' },
          ].map(stat => (
            <div key={stat.label} className="bg-white rounded-lg p-4 shadow-sm border">
              <p className="text-gray-500 text-sm">{stat.label}</p>
              <p className={`text-2xl font-bold ${stat.color}`}>{stat.value}</p>
            </div>
          ))}
        </div>

        {/* Tickets */}
        {loading ? (
          <div className="text-center py-8 text-gray-500">Loading...</div>
        ) : tickets.length === 0 ? (
          <div className="text-center py-12 bg-white rounded-lg border">
            <p className="text-gray-500">No tickets assigned to you</p>
          </div>
        ) : (
          <div className="space-y-3">
            {tickets.map(ticket => (
              <div key={ticket.id} className="bg-white rounded-lg border p-5">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-gray-400 text-sm">#{ticket.id}</span>
                      <h3 className="font-semibold text-gray-800">{ticket.subject}</h3>
                      <span className={`text-xs px-2 py-0.5 rounded-full ${getStatusColor(ticket.status)}`}>
                        {ticket.status.replace('_', ' ')}
                      </span>
                    </div>
                    <p className="text-gray-500 text-sm">{ticket.description}</p>
                  </div>
                </div>

                <div className="mt-4 flex gap-2">
                  <button
                    onClick={() => navigate(`/agent/chat/${ticket.id}`)}
                    className="bg-blue-600 text-white px-4 py-1.5 rounded-lg text-sm hover:bg-blue-700"
                  >
                    Open Chat
                  </button>
                  {getNextStatus(ticket.status) && (
                    <button
                      onClick={() => handleStatusChange(ticket.id, getNextStatus(ticket.status))}
                      className="bg-green-50 text-green-700 px-4 py-1.5 rounded-lg text-sm hover:bg-green-100 border border-green-200"
                    >
                      Mark as {getNextStatus(ticket.status).replace('_', ' ')}
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}