-- Esquema de referencia. La aplicación crea estas tablas al arrancar.

CREATE TABLE IF NOT EXISTS usuarios (
  id SERIAL PRIMARY KEY,
  nombre TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS destinos (
  id SERIAL PRIMARY KEY,
  nombre TEXT NOT NULL,
  pais TEXT NOT NULL DEFAULT 'Colombia',
  descripcion TEXT
);

CREATE TABLE IF NOT EXISTS articulos (
  id SERIAL PRIMARY KEY,
  titulo TEXT NOT NULL,
  resumen TEXT NOT NULL,
  contenido TEXT NOT NULL,
  categoria TEXT NOT NULL,
  destino_id INTEGER
);

CREATE TABLE IF NOT EXISTS faqs (
  id SERIAL PRIMARY KEY,
  pregunta TEXT NOT NULL,
  respuesta TEXT NOT NULL,
  categoria TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS solicitudes (
  id SERIAL PRIMARY KEY,
  asunto TEXT NOT NULL,
  descripcion TEXT NOT NULL,
  categoria TEXT NOT NULL,
  prioridad TEXT NOT NULL DEFAULT 'Normal',
  estado TEXT NOT NULL DEFAULT 'Pendiente',
  respuesta TEXT,
  creada_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  usuario_id INTEGER NOT NULL REFERENCES usuarios(id)
);

CREATE TABLE IF NOT EXISTS viajes (
  id SERIAL PRIMARY KEY,
  titulo TEXT NOT NULL,
  destino TEXT NOT NULL,
  fecha_inicio DATE NOT NULL,
  fecha_fin DATE NOT NULL,
  estado TEXT NOT NULL DEFAULT 'En preparación',
  usuario_id INTEGER NOT NULL REFERENCES usuarios(id)
);

CREATE TABLE IF NOT EXISTS tareas (
  id SERIAL PRIMARY KEY,
  titulo TEXT NOT NULL,
  categoria TEXT NOT NULL,
  completada BOOLEAN NOT NULL DEFAULT FALSE,
  viaje_id INTEGER NOT NULL REFERENCES viajes(id)
);
