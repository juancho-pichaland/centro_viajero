import React, { useEffect, useState } from 'react'
import { apiFetch } from '../api/client'

const initialForm = { asunto: '', descripcion: '', categoria: 'Orientación de viaje', prioridad: 'Normal' }

export default function Solicitudes() {
  const [requests, setRequests] = useState([])
  const [form, setForm] = useState(initialForm)
  const [showForm, setShowForm] = useState(false)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  const loadRequests = () => apiFetch('/solicitudes/').then((response) => response.json()).then(setRequests).finally(() => setLoading(false))

  useEffect(() => { loadRequests() }, [])

  const updateField = (event) => setForm({ ...form, [event.target.name]: event.target.value })

  const submit = async (event) => {
    event.preventDefault()
    setSaving(true)
    setError('')
    const response = await apiFetch('/solicitudes/', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(form) })
    if (!response.ok) {
      const payload = await response.json()
      setError(payload.detail?.[0]?.msg || payload.detail || 'No fue posible crear la solicitud')
    } else {
      setForm(initialForm)
      setShowForm(false)
      await loadRequests()
    }
    setSaving(false)
  }

  return <div className="page-wrap requests-page">
    <section className="requests-header"><div><p className="eyebrow">ACOMPAÑAMIENTO</p><h1>Solicitudes</h1><p className="intro">Cuéntanos qué necesitas y daremos seguimiento a tu caso.</p></div><button className="primary-button request-action" onClick={() => setShowForm(!showForm)}>{showForm ? 'Cerrar formulario' : 'Nueva solicitud'} <span>{showForm ? '×' : '+'}</span></button></section>
    {showForm && <form className="request-form" onSubmit={submit}><div className="form-title"><div><p className="eyebrow">NUEVO CASO</p><h2>¿En qué podemos orientarte?</h2></div><span>Respuesta habitual en menos de 24 horas</span></div><div className="request-fields"><label>Asunto<input name="asunto" value={form.asunto} onChange={updateField} placeholder="Ej. Requisitos para ingresar al destino" required minLength="5" /></label><label>Categoría<select name="categoria" value={form.categoria} onChange={updateField}><option>Orientación de viaje</option><option>Documentos</option><option>Reservas</option><option>Seguridad</option><option>Otro</option></select></label><label className="full-field">Describe tu solicitud<textarea name="descripcion" value={form.descripcion} onChange={updateField} placeholder="Incluye los detalles que nos ayuden a entender tu situación." required minLength="10" rows="5" /></label><label>Prioridad<select name="prioridad" value={form.prioridad} onChange={updateField}><option>Normal</option><option>Alta</option><option>Urgente</option></select></label></div>{error && <p className="request-error">{error}</p>}<button className="primary-button" disabled={saving}>{saving ? 'Enviando...' : 'Enviar solicitud'} <span>→</span></button></form>}
    <section className="request-history"><div className="section-heading"><div><p className="eyebrow">HISTORIAL</p><h2>Mis solicitudes</h2></div><span className="article-count">{requests.length} casos</span></div>{loading ? <p className="empty-state">Cargando historial...</p> : requests.length === 0 ? <div className="empty-requests"><span>○</span><h3>Aún no tienes solicitudes</h3><p>Cuando necesites orientación personalizada, crea tu primer caso.</p></div> : <div className="request-list">{requests.map((request) => <article className="request-item" key={request.id}><div className="request-status"><span className={`status-pill status-${request.estado.toLowerCase()}`}>{request.estado}</span><small>{new Date(request.creada_en).toLocaleDateString('es-CO')}</small></div><div className="request-content"><h3>{request.asunto}</h3><p>{request.descripcion}</p><small>{request.categoria} · Prioridad {request.prioridad}</small>{request.respuesta && <div className="request-response"><strong>Respuesta del equipo</strong><p>{request.respuesta}</p></div>}</div><span className="request-id">#{String(request.id).padStart(3, '0')}</span></article>)}</div>}</section>
  </div>
}
