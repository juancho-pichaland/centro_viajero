import React, { useEffect, useMemo, useState } from 'react'
import { apiFetch } from '../api/client'

const starterMessages = [
  { role: 'bot', text: 'Hola, soy tu asistente de viaje. ¿Qué te gustaría revisar antes de salir?' },
  { role: 'bot', text: 'Puedo ayudarte con documentos, equipaje, clima, transporte o seguridad.' }
]

const quickPicks = [
  '¿Qué documentos necesito?',
  '¿Qué debo llevar en la maleta?',
  '¿Cómo me preparo para el clima?',
  '¿Qué revisar de seguridad?'
]

export default function Chatbot() {
  const [messages, setMessages] = useState(starterMessages)
  const [draft, setDraft] = useState('')
  const [isSending, setIsSending] = useState(false)
  const [travelContext, setTravelContext] = useState({ trip: null, tasks: [] })
  const [suggestions, setSuggestions] = useState(quickPicks)

  useEffect(() => {
    const loadContext = async () => {
      try {
        const [tripResponse, tasksResponse] = await Promise.all([
          apiFetch('/viajes/'),
          apiFetch('/tareas/')
        ])

        const trips = await tripResponse.json()
        const tasks = await tasksResponse.json()
        setTravelContext({ trip: trips[0] || null, tasks })
      } catch (error) {
        setTravelContext({ trip: null, tasks: [] })
      }
    }

    loadContext()
  }, [])

  const assistantName = useMemo(() => 'Centro Viajero', [])
  const travelFocus = useMemo(() => {
    if (!travelContext.trip) return ['Documentos', 'Equipaje', 'Seguridad']

    const pending = travelContext.tasks.filter((task) => !task.completada).slice(0, 3)
    return pending.length > 0 ? pending.map((task) => task.titulo) : ['Documentos', 'Alojamiento', 'Transporte']
  }, [travelContext])

  const sendMessage = async (message) => {
    const trimmed = message.trim()
    if (!trimmed || isSending) return

    setMessages((current) => [...current, { role: 'user', text: trimmed }])
    setDraft('')
    setIsSending(true)

    try {
      const response = await apiFetch('/chatbot/message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: trimmed })
      })
      const payload = await response.json()
      setMessages((current) => [...current, { role: 'bot', text: payload.reply }])
      if (payload.suggestions?.length) {
        setSuggestions(payload.suggestions)
      }
    } catch (error) {
      setMessages((current) => [...current, { role: 'bot', text: 'No pude responder en este momento. Inténtalo de nuevo en unos segundos.' }])
    } finally {
      setIsSending(false)
    }
  }

  return <div className="page-wrap chatbot-page">
    <section className="page-intro">
      <div>
        <p className="eyebrow">ASISTENTE</p>
        <h1>Orientación del viajero</h1>
        <p className="intro">Consulta recomendaciones útiles para preparar cada etapa del viaje.</p>
      </div>
    </section>

    <div className="chat-layout">
      <section className="chat-window">
        <div className="chat-header">
          <div className="chat-brand"><span>{assistantName.slice(0, 2).toUpperCase()}</span><strong>{assistantName}</strong></div>
          <small>{travelContext.trip ? `Preparando ${travelContext.trip.destino}` : 'Disponible para ayudarte'}</small>
        </div>

        <div className="chat-body">
          {messages.map((message, index) => (
            <div key={`${message.role}-${index}`} className={`chat-bubble ${message.role}`}>
              <p>{message.text}</p>
            </div>
          ))}
        </div>

        <div className="quick-picks">
          {suggestions.map((item) => (
            <button key={item} type="button" onClick={() => sendMessage(item)} disabled={isSending}>{item}</button>
          ))}
        </div>

        <form className="chat-form" onSubmit={(event) => {
          event.preventDefault()
          sendMessage(draft)
        }}>
          <input
            value={draft}
            onChange={(event) => setDraft(event.target.value)}
            placeholder="Escribe tu pregunta sobre el viaje..."
            aria-label="Mensaje para el asistente"
          />
          <button type="submit" className="primary-button" disabled={isSending || !draft.trim()}>
            {isSending ? 'Pensando...' : 'Enviar'}
          </button>
        </form>
      </section>

      <aside className="tip-panel chat-panel">
        <span className="tip-label">TUS PRIORIDADES</span>
        <h3>{travelContext.trip ? `Tu viaje a ${travelContext.trip.destino}` : 'Todo lo importante en una sola conversación.'}</h3>
        <ul className="chat-checklist">
          {travelFocus.slice(0, 4).map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </aside>
    </div>
  </div>
}
