import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { apiFetch } from '../api/client'

export default function Dashboard() {
  const [trip, setTrip] = useState(null)

  useEffect(() => {
    apiFetch('/viajes/')
      .then((response) => response.json())
      .then((data) => setTrip(data[0]))
  }, [])

  const formatDate = (date) => date
    ? new Date(`${date}T00:00:00`).toLocaleDateString('es-CO', { day: 'numeric', month: 'short' })
    : 'Cargando...'

  return <div className="page-wrap">
    <section className="welcome-row"><div><p className="eyebrow">LUNES, 05 DE SEPTIEMBRE DE 2026</p><h1>Tu próximo viaje, más claro.</h1><p className="intro">Tienes todo lo necesario para prepararte sin improvisar.</p></div><Link className="primary-button" to="/checklist">Abrir checklist <span>→</span></Link></section>
    <section className="trip-card"><div className="trip-main"><div className="trip-kicker"><span className="trip-icon">✦</span> PRÓXIMO VIAJE</div><h2>{trip?.titulo || 'Cargando tu viaje...'}</h2><p className="trip-meta">{trip?.destino || ' '} <span>·</span> {formatDate(trip?.fecha_inicio)} - {formatDate(trip?.fecha_fin)}</p><div className="progress-line"><span style={{ width: '25%' }} /></div><p className="progress-label"><strong>1 de 4 tareas</strong> completadas</p></div><div className="trip-side"><span className="state-badge">{trip?.estado || 'En preparación'}</span><Link to="/mis-viajes">Ver detalles <span>→</span></Link></div></section>
    <section className="section-heading"><div><p className="eyebrow">PREPARACIÓN</p><h2>Lo importante para hoy</h2></div><Link to="/checklist">Ver todo <span>→</span></Link></section>
    <div className="insight-grid"><article className="insight-card warm"><span className="card-number">01</span><div><h3>Completa tu checklist</h3><p>Hay 3 tareas pendientes antes de viajar.</p><Link to="/checklist">Continuar <span>→</span></Link></div></article><article className="insight-card blue"><span className="card-number">02</span><div><h3>Conoce tu destino</h3><p>Descubre recomendaciones para Colombia.</p><Link to="/centro">Explorar información <span>→</span></Link></div></article></div>
  </div>
}
