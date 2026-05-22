import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import api from '../services/api'

export default function Register() {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    full_name: '',
    role: 'customer',
    organization_name: '',
    organization_id: ''
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const payload = {
        email: formData.email,
        password: formData.password,
        full_name: formData.full_name,
        role: formData.role,
      }

      // Add org info based on selection
      if (formData.organization_name) {
        payload.organization_name = formData.organization_name
      } else if (formData.organization_id) {
        payload.organization_id = parseInt(formData.organization_id)
      }

      await api.post('/auth/register', payload)
      navigate('/login')

    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center py-8">
      <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-md">

        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-blue-600">SupportDesk</h1>
          <p className="text-gray-500 mt-2">Create your account</p>
        </div>

        {/* Error */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-medium mb-2">
              Full Name
            </label>
            <input
              type="text"
              name="full_name"
              value={formData.full_name}
              onChange={handleChange}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter your full name"
              required
            />
          </div>

          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-medium mb-2">
              Email
            </label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter your email"
              required
            />
          </div>

          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-medium mb-2">
              Password
            </label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter your password"
              required
            />
          </div>

          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-medium mb-2">
              Role
            </label>
            <select
              name="role"
              value={formData.role}
              onChange={handleChange}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="customer">Customer</option>
              <option value="admin">Admin</option>
            </select>
          </div>

          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-medium mb-2">
              Organization Name (Create New)
            </label>
            <input
              type="text"
              name="organization_name"
              value={formData.organization_name}
              onChange={handleChange}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Create new organization"
            />
          </div>

          <div className="mb-6">
            <label className="block text-gray-700 text-sm font-medium mb-2">
              Organization ID (Join Existing)
            </label>
            <input
              type="number"
              name="organization_id"
              value={formData.organization_id}
              onChange={handleChange}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter existing org ID"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 font-medium disabled:opacity-50"
          >
            {loading ? 'Creating account...' : 'Create Account'}
          </button>
        </form>

        <p className="text-center text-gray-500 mt-6">
          Already have an account?{' '}
          <Link to="/login" className="text-blue-600 hover:underline font-medium">
            Sign In
          </Link>
        </p>

      </div>
    </div>
  )
}