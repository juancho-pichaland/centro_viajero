import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { apiFetch } from '../api/client'

const formatDate = (value) => {
  if (!value) return 'Sin fecha'
  return new Date(`${value}T00:00:00`).toLocaleDateString('es-CO', {
    day: 'numeric',
    month: 'short',
    year: 'numeric'
  })
}

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

  if (diffDays > 0) return `Faltan ${diffDays} días para iniciar`
  if (diffDays === 0) return 'Tu viaje empieza hoy'
  return 'Viaje en curso o ya finalizado'
}

export default function MisViajes() {
  const [viajes, setViajes] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    apiFetch('/viajes/')
      .then((response) => response.json())
      .then((data) => setViajes(data))
      .finally(() => setLoading(false))
  }, [])

  return <div className="page-wrap">
    <section className="page-intro">
      <div>
        <p className="eyebrow">RUTA EN MARCHA</p>
        <h1>Mis viajes</h1>
        <p className="intro">Todos tus planes, fechas y puntos de atención en un mismo lugar.</p>
      </div>
      <Link className="primary-button" to="/dashboard">Volver al resumen <span>→</span></Link>
    </section>

    {loading ? (
      <p className="empty-state">Cargando tus viajes...</p>
    ) : viajes.length === 0 ? (
      <div className="empty-requests">
        <span>✦</span>
        <h3>Aún no tienes viajes creados</h3>
        <p>Cuando guardes tu próximo destino, aparecerá aquí con la información de preparación.</p>
      </div>
    ) : (
      <div style={{ display: 'grid', gap: '20px' }}>
        {viajes.map((trip) => (
          <article className="trip-card" key={trip.id} style={{
            minHeight: 'auto',
            padding: '28px 30px',
            display: 'grid',
            gridTemplateColumns: '1.6fr 0.9fr',
            gap: '18px',
            alignItems: 'center'
          }}>
            <div className="trip-main" style={{ position: 'relative', zIndex: 1 }}>
              <div className="trip-kicker"><span className="trip-icon">✦</span> DESTINO ACTUAL</div>
              <h2 style={{ margin: '18px 0 10px', fontSize: '30px' }}>{trip.titulo}</h2>
              <p className="trip-meta" style={{ margin: 0 }}>
                {trip.destino} <span>·</span> {formatDate(trip.fecha_inicio)} - {formatDate(trip.fecha_fin)}
              </p>

              <div style={{ marginTop: '22px', display: 'grid', gap: '10px', color: '#c6d8d9', fontSize: '12px' }}>
                <span><strong style={{ color: '#fff', marginRight: '8px' }}>Duración:</strong> {getTripDuration(trip)}</span>
                <span><strong style={{ color: '#fff', marginRight: '8px' }}>Estado:</strong> {trip.estado}</span>
                <span><strong style={{ color: '#fff', marginRight: '8px' }}>Siguiente paso:</strong> {getCountdown(trip)}</span>
              </div>
            </div>

            <div className="trip-side" style={{ position: 'relative', zIndex: 1, alignItems: 'stretch' }}>
              <span className="state-badge" style={{ alignSelf: 'flex-end', width: 'fit-content' }}>{trip.estado}</span>
              <div style={{ display: 'grid', gap: '10px', marginTop: '12px' }}>
                <Link to="/checklist" className="primary-button" style={{ justifyContent: 'center' }}>Checklist <span>→</span></Link>
                <Link to="/centro" className="primary-button" style={{ justifyContent: 'center', background: '#2f5d79' }}>Información <span>→</span></Link>
              </div>
            </div>
          </article>
        ))}
      </div>
    )}
  </div>
}
