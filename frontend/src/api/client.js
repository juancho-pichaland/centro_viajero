const API_URL = 'http://localhost:8000'

export function saveSession(session) {
  localStorage.setItem('centro_viajero_token', session.access_token)
  localStorage.setItem('centro_viajero_user', JSON.stringify(session.user))
}

export function getToken() {
  return localStorage.getItem('centro_viajero_token')
}

export async function apiFetch(path, options = {}) {
  const headers = new Headers(options.headers || {})
  const token = getToken()
  if (token) headers.set('Authorization', `Bearer ${token}`)
  const response = await fetch(`${API_URL}${path}`, { ...options, headers })
  if (response.status === 401) {
    localStorage.removeItem('centro_viajero_token')
    localStorage.removeItem('centro_viajero_user')
  }
  return response
}