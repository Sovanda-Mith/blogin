<script setup>
import { ref, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { usePostsStore } from '@/stores/posts'
import { useRouter } from 'vue-router'

const props = defineProps({
  postSlug: {
    type: String,
    required: true
  },
  initialLikes: {
    type: Number,
    default: 0
  },
  initialLiked: {
    type: Boolean,
    default: false
  }
})

const authStore = useAuthStore()
const postsStore = usePostsStore()
const router = useRouter()

const likesCount = ref(props.initialLikes)
const isLiked = ref(props.initialLiked)
const loading = ref(false)

const buttonText = computed(() => {
  if (isLiked.value) return 'Liked'
  return 'Like'
})

const handleLike = async () => {
  if (!authStore.isAuthenticated) {
    router.push({ name: 'Login', query: { redirect: router.currentRoute.value.fullPath } })
    return
  }
  
  loading.value = true
  try {
    const result = await postsStore.likePost(props.postSlug)
    likesCount.value = result.likes_count
    isLiked.value = result.is_liked
  } catch (err) {
    console.error('Failed to like post:', err)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <button 
    @click="handleLike"
    class="like-btn"
    :class="{ 'liked': isLiked }"
    :disabled="loading"
  >
    <span v-if="loading" class="loading-spinner"></span>
    <template v-else>
      <span class="like-icon">{{ isLiked ? '❤️' : '🤍' }}</span>
      <span class="like-count">{{ likesCount }}</span>
    </template>
  </button>
</template>

<style scoped>
.like-btn {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.375rem 0.75rem;
  background-color: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  cursor: pointer;
  font-size: 0.875rem;
  color: var(--text-muted);
  transition: all 0.2s;
}

.like-btn:hover:not(:disabled) {
  background-color: rgba(239, 68, 68, 0.1);
  border-color: rgba(239, 68, 68, 0.3);
}

.like-btn.liked {
  background-color: rgba(239, 68, 68, 0.1);
  border-color: rgba(239, 68, 68, 0.3);
  color: var(--danger-color);
}

.like-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.like-icon {
  font-size: 1rem;
}

.like-count {
  font-weight: 500;
}
</style>
