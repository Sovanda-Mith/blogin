<script setup>
import { RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

const handleLogout = async () => {
  await authStore.logout()
}
</script>

<template>
  <nav class="navbar">
    <div class="container navbar-content">
      <RouterLink to="/" class="logo">
        <span class="logo-icon">📝</span>
        <span class="logo-text">Blogin</span>
      </RouterLink>

      <div class="nav-links">
        <RouterLink to="/" class="nav-link">Home</RouterLink>
        
        <template v-if="authStore.isAuthenticated">
          <RouterLink to="/posts/create" class="nav-link">Write</RouterLink>
          <RouterLink to="/profile" class="nav-link nav-user">
            <img 
              v-if="authStore.currentUser?.avatar"
              :src="authStore.currentUser.avatar" 
              :alt="authStore.currentUser.username"
              class="nav-avatar"
            />
            <span v-else class="nav-avatar-placeholder">{{ authStore.currentUser?.username?.charAt(0).toUpperCase() }}</span>
            {{ authStore.currentUser?.username }}
          </RouterLink>
          <button @click="handleLogout" class="btn btn-sm btn-secondary" :disabled="authStore.loading">
            <span v-if="authStore.loading" class="loading-spinner"></span>
            <span v-else>Logout</span>
          </button>
        </template>
        
        <template v-else>
          <RouterLink to="/login" class="nav-link">Login</RouterLink>
          <RouterLink to="/register" class="btn btn-sm btn-primary">Sign Up</RouterLink>
        </template>
      </div>
    </div>
  </nav>
</template>

<style scoped>
.navbar {
  background-color: var(--bg-color);
  border-bottom: 1px solid var(--border-color);
  padding: 1rem 0;
  position: sticky;
  top: 0;
  z-index: 100;
}

.navbar-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  text-decoration: none;
  color: var(--text-color);
  font-weight: 700;
  font-size: 1.25rem;
}

.logo-icon {
  font-size: 1.5rem;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.nav-link {
  color: var(--text-color);
  text-decoration: none;
  font-weight: 500;
  font-size: 0.875rem;
  transition: color 0.2s;
}

.nav-link:hover {
  color: var(--primary-color);
}

.nav-link.router-link-active {
  color: var(--primary-color);
}

.nav-user {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.nav-avatar {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  object-fit: cover;
}

.nav-avatar-placeholder {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background-color: var(--primary-color);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 600;
}

@media (max-width: 640px) {
  .nav-links {
    gap: 1rem;
  }
  
  .logo-text {
    display: none;
  }
}
</style>
