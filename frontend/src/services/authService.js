import api from './api'

export const registerUser = (name, email, password) =>
  api.post('/api/auth/register', { name, email, password }).then((res) => res.data)

export const loginUser = (email, password) =>
  api.post('/api/auth/login', { email, password }).then((res) => res.data)

export const logoutUser = () => api.post('/api/auth/logout').then((res) => res.data)

export const fetchProfile = () => api.get('/api/auth/profile').then((res) => res.data)
