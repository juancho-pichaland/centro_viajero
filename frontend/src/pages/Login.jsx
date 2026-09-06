import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { saveSession } from '../api/client'

export default function Login() {
  const navigate = useNavigate()
  const [email, setEmail] = useState('juan@centro.viajero')
  const [password, setPassword] = useState('viajero123')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const submit = async (event) => {
    event.preventDefault()
    setLoading(true)
    setError('')
    try {
      const response = await fetch('http://localhost:8000/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      })
      if (!response.ok) throw new Error('Correo o contraseña incorrectos')
      const session = await response.json()
      saveSession(session)
      navigate('/dashboard')
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setLoading(false)
    }
  }

  return <div className="login-page"><div className="login-copy"><p className="eyebrow">CENTRO VIAJERO</p><h1>Viaja con más confianza.</h1><p>Orientación práctica para convertir la preparación en parte de la experiencia.</p></div><div className="login-box"><span className="login-mark">CV</span><h2>Bienvenido de nuevo</h2><p>Ingresa para continuar preparando tu viaje.</p><form onSubmit={submit}><label>Correo electrónico<input value={email} onChange={(event) => setEmail(event.target.value)} type="email" placeholder="tu@correo.com" /></label><label>Contraseña<input value={password} onChange={(event) => setPassword(event.target.value)} type="password" placeholder="••••••••" /></label>{error && <small className="form-error">{error}</small>}<button className="primary-button login-button" type="submit">{loading ? 'Ingresando...' : 'Ingresar'} <span>→</span></button></form><small>Demo disponible con el usuario precargado.</small></div></div>
}
