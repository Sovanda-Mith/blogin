import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/api/axios'

export const useUserStore = defineStore('user', () => {
  const profile = ref(null)
  const loading = ref(false)
  const error = ref(null)

  const createProfile = async (profileData) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await api.post('/users/profiles/', profileData)
      profile.value = response.data.data || response.data
      return profile.value
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to create profile'
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchMyProfile = async () => {
    loading.value = true
    error.value = null
    
    try {
      const response = await api.get('/users/me/')
      profile.value = response.data.data || response.data
      return profile.value
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to fetch profile'
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    profile,
    loading,
    error,
    createProfile,
    fetchMyProfile
  }
})
