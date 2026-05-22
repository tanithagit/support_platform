import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'

export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const getRoleColor = (role) => {
    if (role === 'admin') return 'bg-purple-600'
    if (role === 'agent') return 'bg-green-600'
    return 'bg-blue-600'
  }

  return (
    <nav className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 py-3 flex justify-between items-center">
        
        {/* Logo */}
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-sm">SD</span>
          </div>
          <span className="font-bold text-gray-800 text-lg">SupportDesk</span>
        </div>

        {/* User Info */}
        <div className="flex items-center gap-4">
          <div className="text-right">
            <p className="text-sm font-medium text-gray-800">{user?.full_name}</p>
            <span className={`text-xs text-white px-2 py-0.5 rounded-full ${getRoleColor(user?.role)}`}>
              {user?.role}
            </span>
          </div>
          <button
            onClick={handleLogout}
            className="bg-red-50 text-red-600 px-4 py-2 rounded-lg text-sm hover:bg-red-100 font-medium"
          >
            Logout
          </button>
        </div>

      </div>
    </nav>
  )
}