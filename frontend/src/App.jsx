import React from 'react'
import { BrowserRouter, NavLink, Navigate, Route, Routes } from 'react-router-dom'
import { getToken } from './api/client'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import MisViajes from './pages/MisViajes'
import Checklist from './pages/Checklist'
import CentroInformacion from './pages/CentroInformacion'
import Chatbot from './pages/Chatbot'
import Solicitudes from './pages/Solicitudes'

function ProtectedRoute({ children }) {
  const token = getToken()
  return token ? children : <Navigate to='/' replace />
}

function AppShell() {
  const token = getToken()
  const user = (() => {
    try {
      const payload = JSON.parse(localStorage.getItem('centro_viajero_user') || '{}')
      return payload?.nombre || 'Juan García'
    } catch {
      return 'Juan García'
    }
  })()

  const initials = user.split(' ').filter(Boolean).slice(0, 2).map((part) => part[0]).join('').toUpperCase() || 'JG'

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand-mark"><span>CV</span><div><strong>Centro</strong><small>Viajero</small></div></div>
        <p className="nav-label">Mi experiencia</p>
        <nav className="main-nav">
          <NavLink to="/dashboard">Resumen</NavLink>
          <NavLink to="/mis-viajes">Mis viajes</NavLink>
          <NavLink to="/checklist">Checklist</NavLink>
          <NavLink to="/centro">Centro de información</NavLink>
          <NavLink to="/chatbot">Orientación</NavLink>
          <NavLink to="/solicitudes">Solicitudes</NavLink>
        </nav>
        <div className="sidebar-footer"><span className="status-dot" /> Atención disponible</div>
      </aside>
      <main className="content-area">
        <header className="topbar"><span className="breadcrumb">CENTRO DE ORIENTACIÓN</span><div className="profile"><span className="avatar">{initials}</span><span>{user}</span><span className="chevron">⌄</span></div></header>
        <Routes>
          <Route path='/' element={token ? <Navigate to='/dashboard' replace /> : <Login/>} />
          <Route path='/dashboard' element={<ProtectedRoute><Dashboard/></ProtectedRoute>} />
          <Route path='/mis-viajes' element={<ProtectedRoute><MisViajes/></ProtectedRoute>} />
          <Route path='/checklist' element={<ProtectedRoute><Checklist/></ProtectedRoute>} />
          <Route path='/centro' element={<ProtectedRoute><CentroInformacion/></ProtectedRoute>} />
          <Route path='/chatbot' element={<ProtectedRoute><Chatbot/></ProtectedRoute>} />
          <Route path='/solicitudes' element={<ProtectedRoute><Solicitudes/></ProtectedRoute>} />
        </Routes>
      </main>
    </div>
  )
}

export default function App(){
  return (
    <BrowserRouter>
      <AppShell />
    </BrowserRouter>
  )
}
