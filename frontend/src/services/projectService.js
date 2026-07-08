import api from './api'

export const getProjects = (params = {}) =>
  api.get('/api/projects', { params }).then((res) => res.data)

export const getProjectBySlug = (slug) =>
  api.get(`/api/projects/${slug}`).then((res) => res.data)

export const getProjectsByCategory = (categorySlug) =>
  api.get(`/api/projects/category/${categorySlug}`).then((res) => res.data)

export const getProjectsByMethod = (method) =>
  api.get(`/api/projects/method/${encodeURIComponent(method)}`).then((res) => res.data)

export const createProject = (payload) =>
  api.post('/api/projects', payload).then((res) => res.data)

export const updateProject = (id, payload) =>
  api.put(`/api/projects/${id}`, payload).then((res) => res.data)

export const deleteProject = (id) => api.delete(`/api/projects/${id}`)

export const getCategories = () => api.get('/api/categories').then((res) => res.data)

export const submitContactMessage = (payload) =>
  api.post('/api/contact', payload).then((res) => res.data)

export const getContactMessages = () =>
  api.get('/api/contact/messages').then((res) => res.data)
