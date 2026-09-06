import React, { useEffect, useState } from 'react'
import { apiFetch } from '../api/client'

const categories = ['Todos', 'Preparación', 'Equipaje', 'Destino', 'Seguridad']

export default function CentroInformacion() {
  const [articles, setArticles] = useState([])
  const [destinations, setDestinations] = useState([])
  const [faqs, setFaqs] = useState([])
  const [query, setQuery] = useState('')
  const [category, setCategory] = useState('Todos')
  const [openFaq, setOpenFaq] = useState(null)
  const [selectedArticle, setSelectedArticle] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      apiFetch('/articulos/').then((response) => response.json()),
      apiFetch('/destinos/').then((response) => response.json()),
      apiFetch('/faqs/').then((response) => response.json()),
    ]).then(([articleData, destinationData, faqData]) => {
      setArticles(articleData)
      setDestinations(destinationData)
      setFaqs(faqData)
    }).finally(() => setLoading(false))
  }, [])

  const filteredArticles = articles.filter((article) => {
    const matchesCategory = category === 'Todos' || article.categoria === category
    const normalizedQuery = query.toLowerCase()
    const matchesQuery = !normalizedQuery || `${article.titulo} ${article.resumen}`.toLowerCase().includes(normalizedQuery)
    return matchesCategory && matchesQuery
  })

  return <div className="page-wrap information-page">
    <section className="info-hero"><div><p className="eyebrow">GUÍA DEL VIAJERO</p><h1>Información para viajar mejor.</h1><p className="intro">Encuentra orientación clara para cada momento de tu viaje.</p></div><div className="search-box"><span>⌕</span><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Buscar una recomendación" /></div></section>
    <section className="destination-strip"><div><p className="eyebrow">DESTINOS</p><h2>Explora antes de llegar</h2></div><div className="destination-list">{destinations.map((destination) => <article key={destination.id} className="destination-chip"><span className="destination-symbol">◌</span><div><strong>{destination.nombre}</strong><small>{destination.pais}</small></div></article>)}</div></section>
    <section className="article-section"><div className="section-heading"><div><p className="eyebrow">RECOMENDACIONES</p><h2>Prepara tu viaje</h2></div><span className="article-count">{filteredArticles.length} artículos</span></div><div className="category-tabs">{categories.map((item) => <button className={category === item ? 'selected' : ''} key={item} onClick={() => setCategory(item)}>{item}</button>)}</div>{loading ? <p className="empty-state">Cargando recomendaciones...</p> : <div className="article-grid">{filteredArticles.map((article, index) => <article className={`article-card article-tone-${index % 3}`} key={article.id}><span className="article-index">0{index + 1}</span><span className="article-category">{article.categoria}</span><h3>{article.titulo}</h3><p>{article.resumen}</p><button onClick={() => setSelectedArticle(article)}>Leer artículo <span>→</span></button></article>)}</div>}</section>
    {selectedArticle && <section className="article-reader"><div><p className="eyebrow">{selectedArticle.categoria}</p><h2>{selectedArticle.titulo}</h2><p>{selectedArticle.contenido}</p></div><button onClick={() => setSelectedArticle(null)}>Cerrar <span>×</span></button></section>}
    <section className="faq-section"><div><p className="eyebrow">PREGUNTAS FRECUENTES</p><h2>Respuestas rápidas</h2><p className="intro">Lo esencial, explicado sin rodeos.</p></div><div className="faq-list">{faqs.map((faq, index) => <button className={`faq-row ${openFaq === index ? 'open' : ''}`} key={faq.id} onClick={() => setOpenFaq(openFaq === index ? null : index)}><span><strong>{faq.pregunta}</strong>{openFaq === index && <small>{faq.respuesta}</small>}</span><b>{openFaq === index ? '−' : '+'}</b></button>)}</div></section>
  </div>
}
