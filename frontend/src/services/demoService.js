import api from './api'

export async function getDemoSchema(slug) {
  const { data } = await api.get(`/api/demos/${slug}`)
  return data
}

export async function runDemoPredict(slug, inputs) {
  const { data } = await api.post(`/api/demos/${slug}/predict`, { inputs })
  return data
}
