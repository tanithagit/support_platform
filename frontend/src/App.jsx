import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './context/AuthContext'
import { AuthProvider } from './context/AuthContext'
import Login from './pages/Login'
import Register from './pages/Register'

function AppRoutes() {
  const { user, loading } = useAuth()

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-gray-500 text-lg">Loading...</p>
      </div>
    )
  }

  return (
    <Routes>
      <Route path="/login" element={
        user ? <Navigate to="/dashboard" replace /> : <Login />
      } />
      <Route path="/register" element={
        user ? <Navigate to="/dashboard" replace /> : <Register />
      } />
      <Route path="/dashboard" element={
        user ? (
          <div className="p-8">
            <h1 className="text-2xl font-bold text-blue-600">
              Welcome {user.full_name}!
            </h1>
            <p className="text-gray-500">Role: {user.role}</p>
          </div>
        ) : <Navigate to="/login" replace />
      } />
      <Route path="/" element={<Navigate to="/login" replace />} />
      <Route path="*" element={<Navigate to="/login" replace />} />
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