<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const authStore = useAuthStore()
const userStore = useUserStore()

const form = ref({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  full_name: '',
  bio: ''
})

const errors = ref({})

const validateForm = () => {
  errors.value = {}
  
  // Check email
  if (!form.value.email || form.value.email.trim() === '') {
    errors.value.email = 'Email is required'
  } else if (!form.value.email.includes('@')) {
    errors.value.email = 'Please enter a valid email address'
  }
  
  // Check username
  if (!form.value.username || form.value.username.trim() === '') {
    errors.value.username = 'Username is required'
  }
  
  if (form.value.password !== form.value.confirmPassword) {
    errors.value.confirmPassword = 'Passwords do not match'
  }
  
  if (form.value.password.length < 8) {
    errors.value.password = 'Password must be at least 8 characters'
  }
  
  return Object.keys(errors.value).length === 0
}

const handleSubmit = async () => {
  if (!validateForm()) {
    console.log('Validation failed:', errors.value)
    return
  }
  
  try {
    const userData = {
      email: form.value.email,
      password: form.value.password
    }
    
    console.log('Sending registration data:', userData)
    
    // Step 1: Register user
    await authStore.register(userData)
    
    // Step 2: Auto-login after registration
    await authStore.login({
      email: form.value.email,
      password: form.value.password
    })
    
    // Step 3: Create profile automatically
    try {
      await userStore.createProfile({
        username: form.value.username,
        display_name: form.value.full_name || form.value.username,
        bio: form.value.bio || ''
      })
    } catch (profileErr) {
      console.warn('Profile creation failed:', profileErr)
      // Don't fail registration if profile creation fails
    }
    
    // Success! Redirect to home
    router.push('/')
  } catch (err) {
    console.error('Registration failed:', err)
    console.error('Error response:', err.response?.data)
    if (err.response?.data?.detail) {
      if (Array.isArray(err.response.data.detail)) {
        errors.value.general = err.response.data.detail.map(d => d.msg).join(', ')
      } else {
        errors.value.general = err.response.data.detail
      }
    }
  }
}
</script>

<template>
  <div class="auth-page">
    <div class="container">
      <div class="auth-card">
        <div class="auth-header">
          <h1>Create Account</h1>
          <p>Join our community of writers and readers</p>
        </div>
        
        <form @submit.prevent="handleSubmit" class="auth-form">
          <div v-if="errors.general || authStore.error" class="alert alert-error">
            {{ errors.general || authStore.error }}
          </div>
          
          <div class="form-group">
            <label class="form-label">Username *</label>
            <input
              v-model="form.username"
              type="text"
              class="form-input"
              placeholder="Choose a username"
              required
            />
            <span v-if="errors.username" class="error-message">{{ errors.username }}</span>
          </div>
          
          <div class="form-group">
            <label class="form-label">Email *</label>
            <input
              v-model="form.email"
              type="email"
              class="form-input"
              placeholder="your@email.com"
              required
            />
            <span v-if="errors.email" class="error-message">{{ errors.email }}</span>
          </div>
          
          <div class="form-group">
            <label class="form-label">Full Name</label>
            <input
              v-model="form.full_name"
              type="text"
              class="form-input"
              placeholder="Your full name"
            />
          </div>
          
          <div class="form-group">
            <label class="form-label">Bio</label>
            <textarea
              v-model="form.bio"
              class="form-textarea"
              placeholder="Tell us about yourself"
              rows="3"
            ></textarea>
          </div>
          
          <div class="form-group">
            <label class="form-label">Password *</label>
            <input
              v-model="form.password"
              type="password"
              class="form-input"
              placeholder="Create a password"
              required
            />
            <span v-if="errors.password" class="error-message">{{ errors.password }}</span>
          </div>
          
          <div class="form-group">
            <label class="form-label">Confirm Password *</label>
            <input
              v-model="form.confirmPassword"
              type="password"
              class="form-input"
              placeholder="Confirm your password"
              required
            />
            <span v-if="errors.confirmPassword" class="error-message">{{ errors.confirmPassword }}</span>
          </div>
          
          <button 
            type="submit" 
            class="btn btn-primary btn-lg btn-full"
            :disabled="authStore.loading"
          >
            <span v-if="authStore.loading" class="loading-spinner"></span>
            <span v-else>Create Account</span>
          </button>
        </form>
        
        <div class="auth-footer">
          <p>Already have an account? <RouterLink to="/login">Sign in</RouterLink></p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.auth-page {
  min-height: calc(100vh - 200px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem 0;
}

.auth-card {
  background-color: var(--bg-color);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  padding: 2.5rem;
  width: 100%;
  max-width: 480px;
}

.auth-header {
  text-align: center;
  margin-bottom: 2rem;
}

.auth-header h1 {
  font-size: 1.75rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.auth-header p {
  color: var(--text-muted);
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.alert {
  padding: 0.75rem 1rem;
  border-radius: var(--radius);
  font-size: 0.875rem;
}

.alert-error {
  background-color: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: var(--danger-color);
}

.btn-full {
  width: 100%;
}

.auth-footer {
  text-align: center;
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--border-color);
  font-size: 0.875rem;
  color: var(--text-muted);
}

.auth-footer a {
  color: var(--primary-color);
  text-decoration: none;
  font-weight: 500;
}

.auth-footer a:hover {
  text-decoration: underline;
}
</style>
