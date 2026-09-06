import React from 'react'
import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { apiFetch } from '../api/client'

export default function Checklist(){
  const [tasks, setTasks] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    apiFetch('/tareas/').then((response) => response.json()).then((data) => setTasks(data)).finally(() => setLoading(false))
  }, [])

  const toggleTask = async (id) => {
    const response = await apiFetch(`/tareas/${id}`, { method: 'PATCH' })
    const updated = await response.json()
    setTasks((current) => current.map((task) => task.id === updated.id ? updated : task))
  }

  const completed = tasks.filter((task) => task.completada).length

  return <div className="page-wrap checklist-page"><section className="page-intro"><p className="eyebrow">RUTA POR EL EJE CAFETERO</p><h1>Checklist de viaje</h1><p className="intro">Pequeños pasos que hacen que el viaje empiece mucho antes de llegar.</p></section><div className="checklist-layout"><section className="task-panel"><div className="panel-header"><div><h2>Antes de viajar</h2><p>{completed} de {tasks.length || 4} tareas completadas</p></div><div className="completion-ring"><strong>{tasks.length ? Math.round((completed / tasks.length) * 100) : 0}%</strong></div></div>{loading ? <p className="empty-state">Cargando tus tareas...</p> : <div className="task-list">{tasks.map((task) => <button className={`task-row ${task.completada ? 'is-done' : ''}`} key={task.id} onClick={() => toggleTask(task.id)}><span className="check-box">{task.completada ? '✓' : ''}</span><span className="task-copy"><strong>{task.titulo}</strong><small>{task.categoria}</small></span><span className="task-arrow">→</span></button>)}</div>}</section><aside className="tip-panel"><span className="tip-label">UNA IDEA ÚTIL</span><h3>La tranquilidad también se prepara.</h3><p>Guarda una copia digital de tus documentos y compártela con alguien de confianza.</p><Link to="/centro">Más recomendaciones <span>→</span></Link></aside></div></div>
}
