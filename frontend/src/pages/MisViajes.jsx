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

const formatCurrency = (value) => {
  const numeric = Number(value || 0)
  return new Intl.NumberFormat('es-CO', {
    style: 'currency',
    currency: 'COP',
    maximumFractionDigits: 0,
  }).format(numeric)
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

  const loadViajes = async () => {
    const response = await apiFetch('/viajes/')
    const data = await response.json()
    setViajes(data)
    setLoading(false)
  }

  useEffect(() => {
    loadViajes()
  }, [])

  const handleUpdate = async (tripId, updates) => {
    await apiFetch(`/viajes/${tripId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updates)
    })
    await loadViajes()
  }

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
                <span><strong style={{ color: '#fff', marginRight: '8px' }}>Presupuesto:</strong> {formatCurrency(trip.presupuesto_total || 0)}</span>
                <span><strong style={{ color: '#fff', marginRight: '8px' }}>Clima:</strong> {trip.clima_recomendado || 'Temporada variable'}</span>
              </div>

              <div className="trip-plan-block" style={{ marginTop: '22px' }}>
                <div className="trip-plan-header" style={{ color: '#f5d39d', fontWeight: 700, fontSize: '11px', letterSpacing: '.12em', textTransform: 'uppercase', marginBottom: '12px' }}>Itinerario</div>
                <ul style={{ margin: 0, paddingLeft: '18px', display: 'grid', gap: '8px', color: '#dfe8ea', fontSize: '12px' }}>
                  {(trip.plan || []).slice(0, 3).map((step, index) => (
                    <li key={`${trip.id}-${step.title || index}`}><strong style={{ color: '#fff' }}>{step.title || `Etapa ${index + 1}`}</strong> — {step.summary || step.detail || 'Sin resumen aún'}</li>
                  ))}
                </ul>
              </div>
            </div>

            <div className="trip-side" style={{ position: 'relative', zIndex: 1, alignItems: 'stretch' }}>
              <span className="state-badge" style={{ alignSelf: 'flex-end', width: 'fit-content' }}>{trip.estado}</span>
              <div className="trip-badges" style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginTop: '14px' }}>
                {(trip.dias_recomendados || ['Clima', 'Movilidad', trip.destino]).slice(0, 3).map((item) => (
                  <span className="mini-badge" key={`${trip.id}-${item}`}>{item}</span>
                ))}
              </div>
              <div style={{ display: 'grid', gap: '10px', marginTop: '12px' }}>
                <Link to="/checklist" className="primary-button" style={{ justifyContent: 'center' }}>Checklist <span>→</span></Link>
                <Link to="/centro" className="primary-button" style={{ justifyContent: 'center', background: '#2f5d79' }}>Información <span>→</span></Link>
              </div>

              <div className="trip-edit-panel" style={{ marginTop: '18px', background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.08)', padding: '14px', borderRadius: '12px' }}>
                <div style={{ fontSize: '11px', letterSpacing: '.12em', color: '#dfb67f', textTransform: 'uppercase', marginBottom: '10px' }}>Editar</div>
                <form onSubmit={(event) => {
                  event.preventDefault()
                  const form = event.currentTarget

                  let planValue = trip.plan || []
                  let budgetValue = trip.presupuesto_detallado || {}

                  try {
                    if (form.plan.value.trim()) planValue = JSON.parse(form.plan.value)
                  } catch (error) {
                    planValue = trip.plan || []
                  }

                  try {
                    if (form.presupuesto_detallado.value.trim()) budgetValue = JSON.parse(form.presupuesto_detallado.value)
                  } catch (error) {
                    budgetValue = trip.presupuesto_detallado || {}
                  }

                  const values = {
                    descripcion: form.descripcion.value,
                    estado: form.estado.value,
                    clima_recomendado: form.clima_recomendado.value,
                    transporte_recomendado: form.transporte_recomendado.value,
                    presupuesto_total: Number(form.presupuesto_total.value || 0),
                    presupuesto_detallado: budgetValue,
                    plan: planValue
                  }
                  handleUpdate(trip.id, values)
                }} style={{ display: 'grid', gap: '8px' }}>
                  <input name="descripcion" defaultValue={trip.descripcion || ''} placeholder="Descripcion del viaje" style={{ padding: '8px 10px', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.12)', background: '#1c334b', color: '#f4f0e9' }} />
                  <input name="clima_recomendado" defaultValue={trip.clima_recomendado || ''} placeholder="Clima recomendado" style={{ padding: '8px 10px', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.12)', background: '#1c334b', color: '#f4f0e9' }} />
                  <input name="transporte_recomendado" defaultValue={trip.transporte_recomendado || ''} placeholder="Transporte" style={{ padding: '8px 10px', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.12)', background: '#1c334b', color: '#f4f0e9' }} />
                  <input name="presupuesto_total" defaultValue={trip.presupuesto_total || 0} type="number" placeholder="Presupuesto" style={{ padding: '8px 10px', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.12)', background: '#1c334b', color: '#f4f0e9' }} />
                  <textarea name="presupuesto_detallado" defaultValue={JSON.stringify(trip.presupuesto_detallado || {}, null, 2)} rows="4" placeholder={'{"hospedaje": 700000}'} style={{ padding: '8px 10px', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.12)', background: '#1c334b', color: '#f4f0e9', resize: 'vertical' }} />
                  <textarea name="plan" defaultValue={JSON.stringify(trip.plan || [], null, 2)} rows="4" placeholder={'[{"day": 1, "title": "Llegada"}]'} style={{ padding: '8px 10px', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.12)', background: '#1c334b', color: '#f4f0e9', resize: 'vertical' }} />
                  <input name="estado" defaultValue={trip.estado || 'En preparación'} placeholder="Estado" style={{ padding: '8px 10px', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.12)', background: '#1c334b', color: '#f4f0e9' }} />
                  <button className="primary-button" type="submit" style={{ justifyContent: 'center', width: '100%' }}>Guardar <span>→</span></button>
                </form>
              </div>
            </div>
          </article>
        ))}
      </div>
    )}
  </div>
}
