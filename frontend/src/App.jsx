import React from 'react'
import { BrowserRouter, NavLink, Routes, Route } from 'react-router-dom'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import MisViajes from './pages/MisViajes'
import Checklist from './pages/Checklist'
import CentroInformacion from './pages/CentroInformacion'
import Chatbot from './pages/Chatbot'
import Solicitudes from './pages/Solicitudes'

export default function App(){
  return (
    <BrowserRouter>
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
          <header className="topbar"><span className="breadcrumb">CENTRO DE ORIENTACIÓN</span><div className="profile"><span className="avatar">JG</span><span>Juan García</span><span className="chevron">⌄</span></div></header>
          <Routes>
            <Route path='/' element={<Login/>} />
            <Route path='/dashboard' element={<Dashboard/>} />
            <Route path='/mis-viajes' element={<MisViajes/>} />
            <Route path='/checklist' element={<Checklist/>} />
            <Route path='/centro' element={<CentroInformacion/>} />
            <Route path='/chatbot' element={<Chatbot/>} />
            <Route path='/solicitudes' element={<Solicitudes/>} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}
