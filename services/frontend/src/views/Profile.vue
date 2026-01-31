<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const form = ref({
  username: authStore.currentUser?.username || '',
  email: authStore.currentUser?.email || '',
  full_name: authStore.currentUser?.full_name || '',
  bio: authStore.currentUser?.bio || '',
  avatar: null
})

const errors = ref({})
const successMessage = ref('')

const handleAvatarChange = (event) => {
  const file = event.target.files[0]
  if (file) {
    form.value.avatar = file
  }
}

const handleSubmit = async () => {
  errors.value = {}
  successMessage.value = ''
  
  try {
    const profileData = {
      full_name: form.value.full_name,
      bio: form.value.bio
    }
    
    await authStore.updateProfile(profileData)
    successMessage.value = 'Profile updated successfully!'
    
    setTimeout(() => {
      successMessage.value = ''
    }, 3000)
  } catch (err) {
    console.error('Failed to update profile:', err)
    if (err.response?.data?.detail) {
      errors.value.general = err.response.data.detail
    }
  }
}

const handleLogout = async () => {
  await authStore.logout()
  router.push('/')
}
</script>

<template>
  <div class="profile-page">
    <div class="container">
      <div class="profile-layout">
        <aside class="profile-sidebar">
          <div class="profile-card">
            <img 
              :src="authStore.currentUser?.avatar || '/default-avatar.png'" 
              :alt="authStore.currentUser?.username"
              class="profile-avatar"
            />
            <h2 class="profile-name">{{ authStore.currentUser?.full_name || authStore.currentUser?.username }}</h2>
            <p class="profile-username">@{{ authStore.currentUser?.username }}</p>
            <p v-if="authStore.currentUser?.bio" class="profile-bio">
              {{ authStore.currentUser.bio }}
            </p>
            
            <div class="profile-stats">
              <div class="stat">
                <span class="stat-value">0</span>
                <span class="stat-label">Posts</span>
              </div>
              <div class="stat">
                <span class="stat-value">0</span>
                <span class="stat-label">Followers</span>
              </div>
            </div>
          </div>
        </aside>
        
        <main class="profile-main">
          <div class="settings-card">
            <h1 class="page-title">Profile Settings</h1>
            
            <form @submit.prevent="handleSubmit" class="settings-form">
              <div v-if="successMessage" class="alert alert-success">
                {{ successMessage }}
              </div>
              
              <div v-if="errors.general || authStore.error" class="alert alert-error">
                {{ errors.general || authStore.error }}
              </div>
              
              <div class="form-group">
                <label class="form-label">Username</label>
                <input
                  v-model="form.username"
                  type="text"
                  class="form-input"
                  disabled
                />
                <span class="help-text">Username cannot be changed</span>
              </div>
              
              <div class="form-group">
                <label class="form-label">Email</label>
                <input
                  v-model="form.email"
                  type="email"
                  class="form-input"
                  disabled
                />
                <span class="help-text">Email cannot be changed</span>
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
                  rows="4"
                ></textarea>
              </div>
              
              <div class="form-actions">
                <button 
                  type="button"
                  @click="handleLogout"
                  class="btn btn-secondary"
                >
                  Logout
                </button>
                <button 
                  type="submit" 
                  class="btn btn-primary"
                  :disabled="authStore.loading"
                >
                  <span v-if="authStore.loading" class="loading-spinner"></span>
                  <span v-else>Save Changes</span>
                </button>
              </div>
            </form>
          </div>
        </main>
      </div>
    </div>
  </div>
</template>

<style scoped>
.profile-page {
  padding: 2rem 0;
}

.profile-layout {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 2rem;
  max-width: 1000px;
  margin: 0 auto;
}

.profile-card {
  background-color: var(--bg-color);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow);
  padding: 2rem;
  text-align: center;
  position: sticky;
  top: 100px;
}

.profile-avatar {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  object-fit: cover;
  margin-bottom: 1rem;
  border: 4px solid var(--bg-secondary);
}

.profile-name {
  font-size: 1.25rem;
  font-weight: 700;
  margin-bottom: 0.25rem;
}

.profile-username {
  color: var(--text-muted);
  font-size: 0.875rem;
  margin-bottom: 1rem;
}

.profile-bio {
  font-size: 0.9375rem;
  color: var(--text-color);
  line-height: 1.6;
  margin-bottom: 1.5rem;
}

.profile-stats {
  display: flex;
  justify-content: center;
  gap: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--border-color);
}

.stat {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.stat-value {
  font-weight: 700;
  font-size: 1.25rem;
}

.stat-label {
  font-size: 0.8125rem;
  color: var(--text-muted);
}

.settings-card {
  background-color: var(--bg-color);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow);
  padding: 2.5rem;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 2rem;
}

.settings-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.alert {
  padding: 0.75rem 1rem;
  border-radius: var(--radius);
  font-size: 0.875rem;
}

.alert-success {
  background-color: rgba(34, 197, 94, 0.1);
  border: 1px solid rgba(34, 197, 94, 0.3);
  color: var(--success-color);
}

.alert-error {
  background-color: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: var(--danger-color);
}

.help-text {
  font-size: 0.8125rem;
  color: var(--text-muted);
  margin-top: 0.25rem;
  display: block;
}

.form-actions {
  display: flex;
  justify-content: space-between;
  margin-top: 1rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--border-color);
}

@media (max-width: 768px) {
  .profile-layout {
    grid-template-columns: 1fr;
  }
  
  .profile-card {
    position: static;
  }
  
  .settings-card {
    padding: 1.5rem;
  }
}
</style>
