import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { apiFetch } from '../api/client'

const budgetLabels = {
  within_budget: 'Dentro del presupuesto',
  watching_budget: 'Revisión del presupuesto',
  over_budget: 'Presupuesto ajustado',
}

export default function Operaciones() {
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(true)

  const handleReportDownload = async () => {
    try {
      const response = await apiFetch('/usuarios/admin/report')
      const report = await response.json()
      const blob = new Blob([report.csv_content || ''], { type: 'text/csv;charset=utf-8;' })
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = 'centro-viajero-reporte.csv'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(url)
    } catch (error) {
      console.error('No se pudo exportar el reporte', error)
    }
  }

  useEffect(() => {
    const loadDashboard = async () => {
      const userResponse = await apiFetch('/usuarios/me/dashboard')
      const userData = await userResponse.json()
      const metricsData = await apiFetch('/usuarios/operaciones/summary').then((response) => response.json())
      const merged = { ...userData, ...metricsData }

      if (userData.rol === 'admin') {
        try {
          const adminResponse = await apiFetch('/usuarios/admin/overview')
          const adminData = await adminResponse.json()
          Object.assign(merged, adminData)
        } catch (error) {
          console.warn('No se pudo cargar el overview administrativo', error)
        }
      }

      setSummary(merged)
      setLoading(false)
    }

    loadDashboard().catch(() => setLoading(false))
  }, [])

  if (loading) {
    return <div className="page-wrap"><p className="empty-state">Cargando panel operativo...</p></div>
  }

  const readiness = summary?.travel_readiness_score ?? summary?.promedio_preparacion ?? 0
  const nextFocus = summary?.next_focus || summary?.foco_principal || 'Sin foco activo todavía'
  const budgetStatus = budgetLabels[summary?.budget_status] || (summary?.alertas_presupuesto ? 'Revisión del presupuesto' : 'Sin plan presupuestario')
  const permissions = summary?.permissions || {
    manage_travelers: true,
    review_reports: true,
    edit_budget: true,
    approve_changes: true,
  }
  const role = summary?.rol || 'traveler'
  const chartData = summary?.chart_data || [
    { label: 'Preparación', value: readiness, color: '#7ad7b1' },
    { label: 'Viajes', value: 60, color: '#7fa7ff' },
    { label: 'Alertas', value: 35, color: '#f0c574' },
  ]

  return (
    <>
      <style>{`
        .chart-report { background: rgba(15, 25, 38, 0.92); border: 1px solid rgba(255,255,255,0.08); border-radius: 20px; padding: 24px; }
        .chart-report-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 18px; }
        .chart-report-header h3 { margin: 0; font-size: 18px; }
        .chart-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 16px; align-items: end; min-height: 210px; }
        .chart-column { display: flex; flex-direction: column; align-items: center; gap: 10px; }
        .chart-bar-shell { width: 72px; height: 140px; background: rgba(255,255,255,0.05); border-radius: 16px; display: flex; align-items: end; justify-content: center; padding: 8px; }
        .chart-bar { width: 100%; border-radius: 12px; min-height: 12px; box-shadow: inset 0 0 12px rgba(255,255,255,0.12); }
        .chart-column small { color: #c9d7dc; text-transform: uppercase; letter-spacing: 0.08em; font-size: 10px; }
        .chart-label { color: white; font-size: 12px; font-weight: 700; }
      `}</style>
      <div className="page-wrap">
      <section className="page-intro">
        <div>
          <p className="eyebrow">OPERACIÓN</p>
          <h1>Panel ejecutivo del viajero</h1>
          <p className="intro">Una vista de control para medir preparación, costos y prioridad del próximo viaje.</p>
        </div>
        <Link className="primary-button" to="/dashboard">Volver al resumen <span>→</span></Link>
      </section>

      <section className="trip-card" style={{ padding: '28px 30px' }}>
        <div className="trip-main">
          <div className="trip-kicker"><span className="trip-icon">✦</span> ESTADO OPERATIVO</div>
          <h2 style={{ margin: '18px 0 8px' }}>{summary?.nombre || 'Usuario'}</h2>
          <p className="trip-meta" style={{ margin: 0 }}>
            {summary?.active_trip_exists ? (summary.trip_titulo || 'Viaje activo') : 'Sin viaje activo definido'}
            {summary?.trip_destino ? ` · ${summary.trip_destino}` : ''}
            {role === 'admin' ? ' · Acceso administrativo' : ' · Perfil viajero'}
          </p>
          <div className="progress-line" style={{ marginTop: '22px' }}>
            <span style={{ width: `${readiness}%` }} />
          </div>
          <p className="progress-label"><strong>{readiness}%</strong> de preparación del viaje</p>
        </div>

        <div className="trip-side">
          <span className="state-badge">{budgetStatus}</span>
          <div className="trip-badges" style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginTop: '14px' }}>
            <span className="mini-badge">{summary?.completed_tasks ?? 0} tareas hechas</span>
            <span className="mini-badge">{summary?.total_tasks ?? 0} en total</span>
          </div>
        </div>
      </section>

      <div className="dashboard-grid" style={{ marginTop: '22px' }}>
        <div className="stats-strip">
          <article className="metric-card">
            <span>Preparación</span>
            <strong>{readiness}%</strong>
            <small>{readiness >= 80 ? 'Listo para cerrar' : 'Queda trabajo clave'}</small>
          </article>

          <article className="metric-card">
            <span>Presupuesto</span>
            <strong>{budgetStatus}</strong>
            <small>{summary?.budget_status === 'over_budget' || summary?.alertas_presupuesto ? 'Revisa gastos' : 'Control estable'}</small>
          </article>

          <article className="metric-card">
            <span>Foco ahora</span>
            <strong>{summary?.next_focus ? String(summary.next_focus).slice(0, 18) : 'Sin foco'}</strong>
            <small>{summary?.trip_estado || 'Sin viaje activo'}</small>
          </article>
        </div>
      </div>

      {role === 'admin' && (
        <section className="section-heading" style={{ marginTop: '20px' }}>
          <div>
            <p className="eyebrow">ADMINISTRACIÓN</p>
            <h2>Permisos del negocio</h2>
          </div>
        </section>
      )}

      {role === 'admin' && (
        <div className="insight-grid">
          <article className="insight-card blue">
            <span className="card-number">A1</span>
            <div>
              <h3>Permisos activos</h3>
              <p>{permissions.manage_travelers ? 'Gestionar viajeros y actividades del servicio.' : 'Sin permisos de gestión'}</p>
            </div>
          </article>
          <article className="insight-card warm">
            <span className="card-number">A2</span>
            <div>
              <h3>Reporte operativo</h3>
              <p>{summary?.report_status || 'monitoring'} · {summary?.travelers_with_trip ?? 0} viajeros con plan activo</p>
              <button className="primary-button" type="button" onClick={handleReportDownload} style={{ marginTop: '12px' }}>
                Exportar CSV <span>→</span>
              </button>
            </div>
          </article>
        </div>
      )}

      <section className="chart-report" style={{ marginTop: '22px' }}>
        <div className="chart-report-header">
          <h3>Reporte visual operativo</h3>
          <span className="state-badge">{summary?.estado_general || 'revisión'}</span>
        </div>
        <div className="chart-grid">
          {chartData.map((item) => (
            <div key={item.label} className="chart-column">
              <span className="chart-label">{item.value}%</span>
              <div className="chart-bar-shell">
                <div className="chart-bar" style={{ height: `${Math.max(12, Number(item.value) || 0)}%`, background: item.color || '#7ad7b1' }} />
              </div>
              <small>{item.label}</small>
            </div>
          ))}
        </div>
      </section>

      <section className="section-heading" style={{ marginTop: '22px' }}>
        <div>
          <p className="eyebrow">Siguiente acción</p>
          <h2>Prioridad del equipo de viaje</h2>
        </div>
      </section>

      <div className="insight-grid">
        <article className="insight-card warm">
          <span className="card-number">01</span>
          <div>
            <h3>Qué hacer ahora</h3>
            <p>{nextFocus}</p>
            <Link to="/checklist">Revisar checklist <span>→</span></Link>
          </div>
        </article>

        <article className="insight-card blue">
          <span className="card-number">02</span>
          <div>
            <h3>Alcance de la preparación</h3>
            <p>{summary?.active_trip_exists ? 'El viaje tiene contexto y planificación base activa.' : 'Aún no hay un viaje activo con indicadores completos.'}</p>
            <Link to="/mis-viajes">Ver viajes <span>→</span></Link>
          </div>
        </article>
      </div>
    </div>
    </>
  )
}
