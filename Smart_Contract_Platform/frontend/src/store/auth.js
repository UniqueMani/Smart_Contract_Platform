import { defineStore } from 'pinia'
import http from '../api/http'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    me: JSON.parse(localStorage.getItem('me') || 'null'),
  }),
  getters: {
    role: (s) => s.me?.role || '',
    username: (s) => s.me?.username || '',
    level: (s) => s.me?.level || null,
    isAuthed: (s) => !!s.token,
  },
  actions: {
    async login(username, password) {
      const form = new URLSearchParams()
      form.append('username', username)
      form.append('password', password)
      const { data } = await http.post('/auth/login', form, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      })
      this.token = data.access_token
      localStorage.setItem('token', this.token)
      await this.fetchMe()
    },
    async fetchMe() {
      const { data } = await http.get('/auth/me')
      this.me = data
      localStorage.setItem('me', JSON.stringify(data))
    },
    logout() {
      this.token = ''
      this.me = null
      localStorage.removeItem('token')
      localStorage.removeItem('me')
    }
  }
})
