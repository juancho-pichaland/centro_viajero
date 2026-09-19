import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { apiFetch } from '../api/client'

const getTripDuration = (trip) => {
  if (!trip?.fecha_inicio || !trip?.fecha_fin) return 'Fechas por confirmar'

  const start = new Date(`${trip.fecha_inicio}T00:00:00`)
  const end = new Date(`${trip.fecha_fin}T00:00:00`)
  const diffDays = Math.ceil((end - start) / (1000 * 60 * 60 * 24)) + 1
  return `${diffDays} días`
}

const getCountdown = (trip) => {
  if (!trip?.fecha_inicio) return 'Próximo viaje'

  const today = new Date()
  const start = new Date(`${trip.fecha_inicio}T00:00:00`)
  const diffDays = Math.ceil((start - today) / (1000 * 60 * 60 * 24))

  if (diffDays > 0) return `Faltan ${diffDays} días`
  if (diffDays === 0) return 'Empieza hoy'
  return 'En curso'
}

const formatCurrency = (value) => {
  const numeric = Number(value || 0)
  return new Intl.NumberFormat('es-CO', {
    style: 'currency',
    currency: 'COP',
    maximumFractionDigits: 0,
  }).format(numeric)
}

export default function Dashboard() {
  const [trip, setTrip] = useState(null)
  const [tasks, setTasks] = useState([])

  useEffect(() => {
    apiFetch('/viajes/')
      .then((response) => response.json())
      .then((data) => setTrip(data[0] || null))

    apiFetch('/tareas/')
      .then((response) => response.json())
      .then((data) => setTasks(data))
  }, [])

  const formatDate = (date) => date
    ? new Date(`${date}T00:00:00`).toLocaleDateString('es-CO', { day: 'numeric', month: 'short' })
    : 'Cargando...'

  const completed = tasks.filter((task) => task.completada).length
  const tripPlan = trip?.plan || []
  const budgetData = trip?.presupuesto_detallado || {}
  const budgetFocus = Object.keys(budgetData).slice(0, 3)
  const budgetTotal = trip?.presupuesto_total || 0

  const stats = [
    { label: 'Checklist', value: `${completed}/${tasks.length || 0}`, detail: tasks.length ? 'tareas completadas' : 'sin tareas aún' },
    { label: 'Destino', value: trip?.destino || 'Colombia', detail: trip?.clima_recomendado || 'temporada variable' },
    { label: 'Presupuesto', value: formatCurrency(budgetTotal), detail: getCountdown(trip) }
  ]

  return <div className="page-wrap">
    <section className="welcome-row"><div><p className="eyebrow">LUNES, 05 DE SEPTIEMBRE DE 2026</p><h1>Tu próximo viaje, más claro.</h1><p className="intro">Tienes todo lo necesario para prepararte sin improvisar.</p></div><Link className="primary-button" to="/checklist">Abrir checklist <span>→</span></Link></section>

    <section className="trip-card"><div className="trip-main"><div className="trip-kicker"><span className="trip-icon">✦</span> PRÓXIMO VIAJE</div><h2>{trip?.titulo || 'Cargando tu viaje...'}</h2><p className="trip-meta">{trip?.destino || ' '} <span>·</span> {formatDate(trip?.fecha_inicio)} - {formatDate(trip?.fecha_fin)}</p><div className="progress-line"><span style={{ width: `${tasks.length ? (completed / tasks.length) * 100 : 18}%` }} /></div><p className="progress-label"><strong>{completed} de {tasks.length || 4}</strong> tareas completadas</p></div><div className="trip-side"><span className="state-badge">{trip?.estado || 'En preparación'}</span><Link to="/mis-viajes">Ver detalles <span>→</span></Link></div></section>

    <div className="dashboard-grid">
      <div className="stats-strip">
        {stats.map((item, index) => (
          <article className="metric-card" key={`${item.label}-${index}`}>
            <span>{item.label}</span>
            <strong>{item.value}</strong>
            <small>{item.detail}</small>
          </article>
        ))}
      </div>

      <div className="planning-grid">
        <article className="plan-panel">
          <div className="section-heading compact-heading">
            <div>
              <p className="eyebrow">PLAN DE VIAJE</p>
              <h2>Ruta práctica</h2>
            </div>
            <Link to="/mis-viajes">Ver detalle <span>→</span></Link>
          </div>
          <div className="plan-list">
            {(tripPlan.length ? tripPlan : [{ title: 'Preparación', summary: 'Revisa documentos, alojamiento y clima del destino.' }]).map((step, index) => (
              <div className="plan-item" key={`${step.title || 'plan'}-${index}`}>
                <span className="plan-index">0{index + 1}</span>
                <div>
                  <strong>{step.title || `Etapa ${index + 1}`}</strong>
                  <p>{step.summary || step.detail || 'Sin detalle aún.'}</p>
                </div>
              </div>
            ))}
          </div>
        </article>

        <article className="budget-panel">
          <span className="tip-label">PRESUPUESTO</span>
          <h3>{formatCurrency(budgetTotal)}</h3>
          <p>{trip?.clima_recomendado || 'Clima según temporada'}</p>
          <div className="budget-tags">
            {budgetFocus.map((tag) => (
              <span key={tag}>{tag}</span>
            ))}
          </div>
        </article>
      </div>
    </div>

    <section className="section-heading"><div><p className="eyebrow">PREPARACIÓN</p><h2>Lo importante para hoy</h2></div><Link to="/checklist">Ver todo <span>→</span></Link></section>
    <div className="insight-grid">
      <article className="insight-card warm"><span className="card-number">01</span><div><h3>Completa tu checklist</h3><p>{tasks.length ? `${Math.max(tasks.length - completed, 0)} tareas pendientes antes de viajar.` : 'Todavía puedes preparar la ruta con calma.'}</p><Link to="/checklist">Continuar <span>→</span></Link></div></article>
      <article className="insight-card blue"><span className="card-number">02</span><div><h3>Conoce tu destino</h3><p>{trip?.destino ? `Revisa recomendaciones, clima y logística para ${trip.destino}.` : 'Descubre recomendaciones del lugar de llegada.'}</p><Link to="/centro">Explorar información <span>→</span></Link></div></article>
    </div>
  </div>
}

