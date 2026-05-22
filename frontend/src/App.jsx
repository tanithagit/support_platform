import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import Login from './pages/Login'
import Register from './pages/Register'
import CustomerDashboard from './pages/customer/CustomerDashboard'
import CustomerChat from './pages/customer/CustomerChat'
import AgentDashboard from './pages/agent/AgentDashboard'
import AgentChat from './pages/agent/AgentChat'
import AdminDashboard from './pages/admin/AdminDashboard'

function ProtectedRoute({ children, allowedRoles }) {
  const { user, loading } = useAuth()

  if (loading) return (
    <div className="min-h-screen flex items-center justify-center">
      <p className="text-gray-500">Loading...</p>
    </div>
  )

  if (!user) return <Navigate to="/login" replace />
  if (allowedRoles && !allowedRoles.includes(user.role)) {
    return <Navigate to="/login" replace />
  }
  return children
}

function AppRoutes() {
  const { user, loading } = useAuth()

  if (loading) return (
    <div className="min-h-screen flex items-center justify-center">
      <p className="text-gray-500">Loading...</p>
    </div>
  )

  const getDashboard = () => {
    if (!user) return '/login'
    if (user.role === 'admin') return '/admin'
    if (user.role === 'agent') return '/agent'
    return '/customer'
  }

  return (
    <Routes>
      {/* Public */}
      <Route path="/login" element={
        user ? <Navigate to={getDashboard()} replace /> : <Login />
      } />
      <Route path="/register" element={
        user ? <Navigate to={getDashboard()} replace /> : <Register />
      } />

      {/* Customer */}
      <Route path="/customer" element={
        <ProtectedRoute allowedRoles={['customer']}>
          <CustomerDashboard />
        </ProtectedRoute>
      } />
      <Route path="/customer/chat/:ticketId" element={
        <ProtectedRoute allowedRoles={['customer']}>
          <CustomerChat />
        </ProtectedRoute>
      } />

      {/* Agent */}
      <Route path="/agent" element={
        <ProtectedRoute allowedRoles={['agent']}>
          <AgentDashboard />
        </ProtectedRoute>
      } />
      <Route path="/agent/chat/:ticketId" element={
        <ProtectedRoute allowedRoles={['agent']}>
          <AgentChat />
        </ProtectedRoute>
      } />

      {/* Admin */}
      <Route path="/admin" element={
        <ProtectedRoute allowedRoles={['admin']}>
          <AdminDashboard />
        </ProtectedRoute>
      } />

      {/* Default */}
      <Route path="/dashboard" element={<Navigate to={getDashboard()} replace />} />
      <Route path="/" element={<Navigate to={getDashboard()} replace />} />
      <Route path="*" element={<Navigate to={getDashboard()} replace />} />
    </Routes>
  )
}

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  )
}

export default App