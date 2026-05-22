import { useState, useEffect } from 'react'
import { useAuth } from '../../context/AuthContext'
import Navbar from '../shared/Navbar'
import api from '../../services/api'

export default function AdminDashboard() {
  const { user } = useAuth()
  const [tickets, setTickets] = useState([])
  const [agents, setAgents] = useState([])
  const [stats, setStats] = useState({})
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('all')

  useEffect(() => {
    fetchAll()
  }, [])

  const fetchAll = async () => {
    try {
      const [ticketsRes, agentsRes, statsRes] = await Promise.all([
        api.get('/tickets/'),
        api.get('/users/agents'),
        api.get('/tickets/dashboard')
      ])
      setTickets(ticketsRes.data)
      setAgents(agentsRes.data)
      setStats(statsRes.data)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleAssign = async (ticketId, agentId) => {
    try {
      await api.post(`/tickets/${ticketId}/assign`, { agent_id: parseInt(agentId) })
      fetchAll()
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to assign')
    }
  }

  const handleStatusChange = async (ticketId, newStatus) => {
    try {
      await api.patch(`/tickets/${ticketId}/status`, { status: newStatus })
      fetchAll()
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

  const getPriorityColor = (priority) => {
    const colors = {
      low: 'bg-green-100 text-green-800',
      medium: 'bg-yellow-100 text-yellow-800',
      high: 'bg-orange-100 text-orange-800',
      urgent: 'bg-red-100 text-red-800',
    }
    return colors[priority] || 'bg-gray-100 text-gray-800'
  }

  const filteredTickets = filter === 'all'
    ? tickets
    : tickets.filter(t => t.status === filter)

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="max-w-7xl mx-auto px-4 py-8">

        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-800">Admin Dashboard</h1>
          <p className="text-gray-500">Manage all tickets and agents</p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-5 gap-4 mb-6">
          {[
            { label: 'Total', value: stats.total || 0, color: 'text-gray-800' },
            { label: 'Open', value: stats.open || 0, color: 'text-blue-600' },
            { label: 'In Progress', value: stats.in_progress || 0, color: 'text-yellow-600' },
            { label: 'Resolved', value: stats.resolved || 0, color: 'text-green-600' },
            { label: 'Closed', value: stats.closed || 0, color: 'text-gray-500' },
          ].map(stat => (
            <div key={stat.label} className="bg-white rounded-lg p-4 shadow-sm border text-center">
              <p className="text-gray-500 text-sm">{stat.label}</p>
              <p className={`text-3xl font-bold ${stat.color}`}>{stat.value}</p>
            </div>
          ))}
        </div>

        {/* Agents Summary */}
        <div className="bg-white rounded-lg border p-4 mb-6">
          <h2 className="font-semibold text-gray-700 mb-3">
            Agents ({agents.length})
          </h2>
          <div className="flex gap-3 flex-wrap">
            {agents.map(agent => (
              <div key={agent.id} className="flex items-center gap-2 bg-gray-50 px-3 py-2 rounded-lg border">
                <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                  <span className="text-green-700 font-medium text-sm">
                    {agent.full_name.charAt(0)}
                  </span>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-800">{agent.full_name}</p>
                  <p className="text-xs text-gray-500">
                    {tickets.filter(t => t.assigned_to === agent.id && t.status !== 'closed').length} active tickets
                  </p>
                </div>
              </div>
            ))}
            {agents.length === 0 && (
              <p className="text-gray-400 text-sm">No agents yet</p>
            )}
          </div>
        </div>

        {/* Filter */}
        <div className="flex gap-2 mb-4">
          {['all', 'open', 'in_progress', 'resolved', 'closed'].map(f => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium ${
                filter === f
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-600 border hover:bg-gray-50'
              }`}
            >
              {f.replace('_', ' ')}
            </button>
          ))}
        </div>

        {/* Tickets Table */}
        {loading ? (
          <div className="text-center py-8 text-gray-500">Loading...</div>
        ) : (
          <div className="bg-white rounded-lg border overflow-hidden">
            <table className="w-full">
              <thead className="bg-gray-50 border-b">
                <tr>
                  <th className="text-left px-4 py-3 text-sm font-medium text-gray-600">#</th>
                  <th className="text-left px-4 py-3 text-sm font-medium text-gray-600">Subject</th>
                  <th className="text-left px-4 py-3 text-sm font-medium text-gray-600">Status</th>
                  <th className="text-left px-4 py-3 text-sm font-medium text-gray-600">Priority</th>
                  <th className="text-left px-4 py-3 text-sm font-medium text-gray-600">Assign Agent</th>
                  <th className="text-left px-4 py-3 text-sm font-medium text-gray-600">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {filteredTickets.map(ticket => (
                  <tr key={ticket.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm text-gray-500">#{ticket.id}</td>
                    <td className="px-4 py-3">
                      <p className="font-medium text-gray-800 text-sm">{ticket.subject}</p>
                      <p className="text-xs text-gray-400 mt-0.5 line-clamp-1">{ticket.description}</p>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`text-xs px-2 py-1 rounded-full ${getStatusColor(ticket.status)}`}>
                        {ticket.status.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`text-xs px-2 py-1 rounded-full ${getPriorityColor(ticket.priority)}`}>
                        {ticket.priority}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <select
                        onChange={(e) => e.target.value && handleAssign(ticket.id, e.target.value)}
                        value={ticket.assigned_to || ''}
                        className="text-sm border rounded px-2 py-1 focus:outline-none focus:ring-1 focus:ring-blue-500"
                      >
                        <option value="">Unassigned</option>
                        {agents.map(agent => (
                          <option key={agent.id} value={agent.id}>
                            {agent.full_name}
                          </option>
                        ))}
                      </select>
                    </td>
                    <td className="px-4 py-3">
                      {ticket.status === 'resolved' && (
                        <button
                          onClick={() => handleStatusChange(ticket.id, 'closed')}
                          className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded hover:bg-gray-200"
                        >
                          Close
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
                {filteredTickets.length === 0 && (
                  <tr>
                    <td colSpan={6} className="text-center py-8 text-gray-400">
                      No tickets found
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}