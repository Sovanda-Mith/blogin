<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import api from '@/api/axios'
import PostCard from '@/components/PostCard.vue'

const route = useRoute()

const username = computed(() => route.params.username)
const user = ref(null)
const posts = ref([])
const loading = ref(false)
const error = ref(null)

const sanitizedBio = computed(() => {
  if (!user.value?.bio) return ''
  const html = marked.parse(user.value.bio)
  return DOMPurify.sanitize(html)
})

const fetchUserProfile = async () => {
  loading.value = true
  error.value = null
  
  try {
    const [userResponse, postsResponse] = await Promise.all([
      api.get(`/users/${username.value}`),
      api.get(`/users/${username.value}/posts`)
    ])
    
    user.value = userResponse.data
    posts.value = postsResponse.data.items || []
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to load user profile'
    console.error('Failed to fetch user:', err)
  } finally {
    loading.value = false
  }
}

onMounted(fetchUserProfile)
</script>

<template>
  <div class="user-profile">
    <div class="container">
      <div v-if="loading" class="loading-container">
        <span class="loading-spinner large"></span>
        <p>Loading profile...</p>
      </div>
      
      <div v-else-if="error" class="error-alert">
        {{ error }}
        <RouterLink to="/" class="btn btn-secondary btn-sm">Go Home</RouterLink>
      </div>
      
      <template v-else-if="user">
        <div class="profile-header">
          <div class="profile-info">
            <img 
              :src="user.avatar || '/default-avatar.png'" 
              :alt="user.username"
              class="profile-avatar"
            />
            <div class="profile-details">
              <h1 class="profile-name">
                {{ user.full_name || user.username }}
              </h1>
              <p class="profile-username">@{{ user.username }}</p>
              <div v-if="user.bio" class="profile-bio" v-html="sanitizedBio"></div>
              
              <div class="profile-meta">
                <span class="join-date">
                  Joined {{ new Date(user.created_at).toLocaleDateString('en-US', { month: 'long', year: 'numeric' }) }}
                </span>
              </div>
            </div>
          </div>
          
          <div class="profile-stats">
            <div class="stat-card">
              <span class="stat-number">{{ posts.length }}</span>
              <span class="stat-label">Posts</span>
            </div>
            <div class="stat-card">
              <span class="stat-number">0</span>
              <span class="stat-label">Followers</span>
            </div>
            <div class="stat-card">
              <span class="stat-number">0</span>
              <span class="stat-label">Following</span>
            </div>
          </div>
        </div>
        
        <div class="profile-content">
          <h2 class="section-title">Posts</h2>
          
          <div v-if="posts.length === 0" class="empty-state">
            <p>This user hasn't published any posts yet.</p>
          </div>
          
          <div v-else class="posts-grid">
            <PostCard 
              v-for="post in posts" 
              :key="post.id"
              :post="post"
              :show-actions="false"
            />
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<style scoped>
.user-profile {
  padding: 2rem 0;
}

.loading-container {
  text-align: center;
  padding: 4rem 1rem;
  color: var(--text-muted);
}

.loading-spinner.large {
  width: 40px;
  height: 40px;
  display: block;
  margin: 0 auto 1rem;
}

.error-alert {
  background-color: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: var(--danger-color);
  padding: 2rem;
  border-radius: var(--radius-lg);
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  max-width: 400px;
  margin: 0 auto;
}

.profile-header {
  background-color: var(--bg-color);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow);
  padding: 2.5rem;
  margin-bottom: 2rem;
}

.profile-info {
  display: flex;
  gap: 2rem;
  margin-bottom: 2rem;
}

.profile-avatar {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  object-fit: cover;
  border: 4px solid var(--bg-secondary);
}

.profile-details {
  flex: 1;
}

.profile-name {
  font-size: 1.75rem;
  font-weight: 700;
  margin-bottom: 0.25rem;
}

.profile-username {
  color: var(--text-muted);
  font-size: 1rem;
  margin-bottom: 1rem;
}

.profile-bio {
  font-size: 1rem;
  line-height: 1.6;
  color: var(--text-color);
  margin-bottom: 1rem;
}

.profile-bio :deep(p) {
  margin: 0;
}

.profile-meta {
  font-size: 0.875rem;
  color: var(--text-muted);
}

.join-date {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.profile-stats {
  display: flex;
  gap: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--border-color);
}

.stat-card {
  text-align: center;
}

.stat-number {
  display: block;
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-color);
}

.stat-label {
  font-size: 0.8125rem;
  color: var(--text-muted);
}

.profile-content {
  max-width: 800px;
  margin: 0 auto;
}

.section-title {
  font-size: 1.25rem;
  font-weight: 700;
  margin-bottom: 1.5rem;
}

.posts-grid {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.empty-state {
  text-align: center;
  padding: 3rem;
  background-color: var(--bg-color);
  border-radius: var(--radius-lg);
  color: var(--text-muted);
}

@media (max-width: 768px) {
  .profile-header {
    padding: 1.5rem;
  }
  
  .profile-info {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }
  
  .profile-stats {
    justify-content: center;
    gap: 1.5rem;
  }
}
</style>
