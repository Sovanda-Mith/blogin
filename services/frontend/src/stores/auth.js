import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api/axios'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref(null)
  const token = ref(localStorage.getItem('token'))
  const refreshToken = ref(localStorage.getItem('refreshToken'))
  const loading = ref(false)
  const error = ref(null)

  // Getters
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const currentUser = computed(() => user.value)

  // Actions
  const setAuth = (authData) => {
    token.value = authData.access_token
    refreshToken.value = authData.refresh_token
    user.value = authData.user
    
    localStorage.setItem('token', authData.access_token)
    localStorage.setItem('refreshToken', authData.refresh_token)
  }

  const clearAuth = () => {
    token.value = null
    refreshToken.value = null
    user.value = null
    
    localStorage.removeItem('token')
    localStorage.removeItem('refreshToken')
  }

  const login = async (credentials) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await api.post('/auth/login', credentials)
      // API returns { success, data: { access_token, refresh_token, user }, message, errors }
      const authData = response.data.data || response.data
      setAuth(authData)
      return authData
    } catch (err) {
      error.value = err.response?.data?.detail || 'Login failed'
      throw err
    } finally {
      loading.value = false
    }
  }

  const register = async (userData) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await api.post('/auth/register', userData)
      // Registration returns user_id, not auth tokens
      // After registration, user needs to login
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Registration failed'
      throw err
    } finally {
      loading.value = false
    }
  }

  const logout = async () => {
    loading.value = true
    
    try {
      if (refreshToken.value) {
        await api.post('/auth/logout', { refresh_token: refreshToken.value })
      }
    } catch (err) {
      console.error('Logout error:', err)
    } finally {
      clearAuth()
      loading.value = false
    }
  }

  const refreshAccessToken = async () => {
    if (!refreshToken.value) return false
    
    try {
      const response = await api.post('/auth/refresh', {
        refresh_token: refreshToken.value
      })
      
      token.value = response.data.access_token
      localStorage.setItem('token', response.data.access_token)
      return true
    } catch (err) {
      clearAuth()
      return false
    }
  }

  const fetchCurrentUser = async () => {
    if (!token.value) return
    
    try {
      const response = await api.get('/auth/me')
      user.value = response.data
    } catch (err) {
      if (err.response?.status === 401) {
        const refreshed = await refreshAccessToken()
        if (refreshed) {
          const response = await api.get('/auth/me')
          user.value = response.data
        } else {
          clearAuth()
        }
      }
    }
  }

  const initializeAuth = () => {
    if (token.value) {
      fetchCurrentUser()
    }
  }

  const updateProfile = async (profileData) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await api.put('/users/profiles/me', profileData)
      user.value = { ...user.value, ...response.data.data }
      return response.data.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to update profile'
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateAvatar = async (avatarUrl) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await api.put('/users/avatars/me', { avatar_url: avatarUrl })
      if (user.value) {
        user.value.avatar = avatarUrl
      }
      return response.data.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to update avatar'
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    user,
    token,
    refreshToken,
    loading,
    error,
    isAuthenticated,
    currentUser,
    login,
    register,
    logout,
    refreshAccessToken,
    fetchCurrentUser,
    initializeAuth,
    updateProfile,
    updateAvatar,
    setAuth,
    clearAuth
  }
})
