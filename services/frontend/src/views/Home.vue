<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { usePostsStore } from '@/stores/posts'
import PostCard from '@/components/PostCard.vue'

const postsStore = usePostsStore()
const loadingMore = ref(false)

const loadPosts = async (page = 1) => {
  await postsStore.fetchPosts({ page })
}

const loadMore = async () => {
  if (loadingMore.value || !postsStore.pagination.hasMore) return
  
  loadingMore.value = true
  await postsStore.fetchPosts({ 
    page: postsStore.pagination.page + 1 
  })
  loadingMore.value = false
}

const handleScroll = () => {
  const scrollTop = window.scrollY
  const windowHeight = window.innerHeight
  const documentHeight = document.documentElement.scrollHeight
  
  if (scrollTop + windowHeight >= documentHeight - 100) {
    loadMore()
  }
}

onMounted(() => {
  loadPosts()
  window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<template>
  <div class="home">
    <div class="hero">
      <div class="container">
        <h1 class="hero-title">Discover Stories</h1>
        <p class="hero-subtitle">Read, write, and share your ideas with the world</p>
      </div>
    </div>
    
    <div class="container">
      <div class="posts-feed">
        <div v-if="postsStore.loading && postsStore.posts.length === 0" class="loading-container">
          <span class="loading-spinner large"></span>
          <p>Loading posts...</p>
        </div>
        
        <div v-else-if="postsStore.error" class="error-alert">
          {{ postsStore.error }}
          <button @click="loadPosts" class="btn btn-secondary btn-sm">Try Again</button>
        </div>
        
        <template v-else>
          <PostCard 
            v-for="post in postsStore.posts" 
            :key="post.id"
            :post="post"
          />
          
          <div v-if="loadingMore" class="loading-more">
            <span class="loading-spinner"></span>
            Loading more...
          </div>
          
          <div v-if="!postsStore.pagination.hasMore && postsStore.posts.length > 0" class="end-message">
            You've reached the end
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<style scoped>
.home {
  min-height: 100vh;
}

.hero {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 4rem 0;
  text-align: center;
  margin-bottom: 2rem;
}

.hero-title {
  font-size: 3rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.hero-subtitle {
  font-size: 1.25rem;
  opacity: 0.9;
}

.posts-feed {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  max-width: 800px;
  margin: 0 auto;
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
  padding: 1rem;
  border-radius: var(--radius);
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.loading-more {
  text-align: center;
  padding: 2rem;
  color: var(--text-muted);
}

.end-message {
  text-align: center;
  padding: 2rem;
  color: var(--text-muted);
  font-size: 0.875rem;
}

@media (max-width: 768px) {
  .hero {
    padding: 3rem 0;
  }
  
  .hero-title {
    font-size: 2rem;
  }
  
  .hero-subtitle {
    font-size: 1rem;
  }
}
</style>
