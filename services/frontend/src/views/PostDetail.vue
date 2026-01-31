<script setup>
import { computed, onMounted } from 'vue'
import { useRoute, useRouter, RouterLink } from 'vue-router'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import { usePostsStore } from '@/stores/posts'
import { useAuthStore } from '@/stores/auth'
import CommentSection from '@/components/CommentSection.vue'
import LikeButton from '@/components/LikeButton.vue'

const route = useRoute()
const router = useRouter()
const postsStore = usePostsStore()
const authStore = useAuthStore()

const slug = computed(() => route.params.slug)
const post = computed(() => postsStore.currentPost)
const loading = computed(() => postsStore.loading)
const error = computed(() => postsStore.error)
const comments = computed(() => postsStore.comments)

const sanitizedContent = computed(() => {
  if (!post.value?.content) return ''
  const html = marked.parse(post.value.content)
  return DOMPurify.sanitize(html)
})

const formattedDate = computed(() => {
  if (!post.value?.created_at) return ''
  return new Date(post.value.created_at).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
})

const readTime = computed(() => {
  if (!post.value?.content) return '0 min read'
  const words = post.value.content.split(/\s+/).length
  const minutes = Math.ceil(words / 200)
  return `${minutes} min read`
})

const commentsCount = computed(() => {
  return comments.value.length || post.value?.comments_count || 0
})

const isAuthor = computed(() => {
  if (!authStore.currentUser || !post.value?.author_id) return false
  return authStore.currentUser.id === post.value.author_id
})

const handleDelete = async () => {
  if (!confirm('Are you sure you want to delete this post?')) return
  
  try {
    await postsStore.deletePost(slug.value)
    router.push('/')
  } catch (err) {
    console.error('Failed to delete post:', err)
  }
}

onMounted(async () => {
  console.log('Fetching post:', slug.value)
  try {
    await postsStore.fetchPost(slug.value)
    console.log('Post loaded:', post.value)
  } catch (err) {
    console.error('Error loading post:', err)
  }
})
</script>

<template>
  <div class="post-detail">
    <div class="container">
      <div v-if="loading" class="loading-container">
        <span class="loading-spinner large"></span>
        <p>Loading post...</p>
      </div>
      
      <div v-else-if="error" class="error-alert">
        {{ error }}
        <RouterLink to="/" class="btn btn-secondary btn-sm">Go Home</RouterLink>
      </div>
      
      <article v-else-if="post" class="post-article">
        <header class="post-header">
          <div class="post-meta-top">
            <RouterLink 
              :to="`/users/${post.author_username}`"
              class="author-link"
              v-if="post.author_username"
            >
              <img 
                :src="post.author_avatar || '/default-avatar.png'" 
                :alt="post.author_username"
                class="author-avatar"
              />
              <span class="author-name">{{ post.author_username }}</span>
            </RouterLink>
            <div v-else class="author-link">
              <img 
                :src="'/default-avatar.png'" 
                :alt="'Unknown'"
                class="author-avatar"
              />
              <span class="author-name">Unknown Author</span>
            </div>
            <span class="separator">•</span>
            <span class="post-date">{{ formattedDate }}</span>
            <span class="separator">•</span>
            <span class="read-time">{{ readTime }}</span>
          </div>
          
          <h1 class="post-title">{{ post.title }}</h1>
          
          <div v-if="post.tags?.length" class="post-tags">
            <span v-for="tag in post.tags" :key="tag" class="tag">
              {{ tag }}
            </span>
          </div>
          
          <div v-if="isAuthor" class="post-actions-top">
            <RouterLink 
              :to="`/posts/${post.slug}/edit`"
              class="btn btn-secondary btn-sm"
            >
              Edit
            </RouterLink>
            <button 
              @click="handleDelete"
              class="btn btn-danger btn-sm"
            >
              Delete
            </button>
          </div>
        </header>
        
        <div class="post-content" v-html="sanitizedContent"></div>
        
        <footer class="post-footer">
          <div class="post-stats">
            <LikeButton 
              :post-slug="post.slug" 
              :initial-likes="post.likes_count || 0"
              :initial-liked="post.is_liked || false"
            />
            <span class="stat">
              💬 {{ commentsCount }} comments
            </span>
          </div>
        </footer>
        
        <CommentSection :post-id="post.id" />
      </article>
    </div>
  </div>
</template>

<style scoped>
.post-detail {
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

.post-article {
  max-width: 800px;
  margin: 0 auto;
  background-color: var(--bg-color);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow);
  padding: 3rem;
}

.post-header {
  margin-bottom: 2rem;
}

.post-meta-top {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
  font-size: 0.875rem;
  color: var(--text-muted);
}

.author-link {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  text-decoration: none;
  color: var(--text-color);
  font-weight: 600;
}

.author-link:hover {
  color: var(--primary-color);
}

.author-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
}

.separator {
  opacity: 0.5;
}

.post-title {
  font-size: 2.5rem;
  font-weight: 700;
  line-height: 1.2;
  margin-bottom: 1rem;
  color: var(--text-color);
}

.post-tags {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.tag {
  background-color: var(--bg-secondary);
  color: var(--primary-color);
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.8125rem;
  font-weight: 500;
}

.post-actions-top {
  display: flex;
  gap: 0.75rem;
}

.post-content {
  font-size: 1.125rem;
  line-height: 1.8;
  color: var(--text-color);
}

.post-content :deep(h1),
.post-content :deep(h2),
.post-content :deep(h3),
.post-content :deep(h4) {
  margin-top: 2rem;
  margin-bottom: 1rem;
  font-weight: 600;
}

.post-content :deep(p) {
  margin-bottom: 1.5rem;
}

.post-content :deep(ul),
.post-content :deep(ol) {
  margin-bottom: 1.5rem;
  padding-left: 2rem;
}

.post-content :deep(li) {
  margin-bottom: 0.5rem;
}

.post-content :deep(code) {
  background-color: var(--bg-secondary);
  padding: 0.2rem 0.4rem;
  border-radius: 4px;
  font-family: monospace;
  font-size: 0.9em;
}

.post-content :deep(pre) {
  background-color: var(--bg-secondary);
  padding: 1rem;
  border-radius: var(--radius);
  overflow-x: auto;
  margin-bottom: 1.5rem;
}

.post-content :deep(pre code) {
  background: none;
  padding: 0;
}

.post-content :deep(blockquote) {
  border-left: 4px solid var(--primary-color);
  padding-left: 1rem;
  margin-left: 0;
  color: var(--text-muted);
  font-style: italic;
}

.post-footer {
  margin-top: 3rem;
  padding-top: 2rem;
  border-top: 1px solid var(--border-color);
}

.post-stats {
  display: flex;
  gap: 1.5rem;
  align-items: center;
}

.stat {
  color: var(--text-muted);
  font-size: 0.875rem;
}

@media (max-width: 768px) {
  .post-article {
    padding: 1.5rem;
  }
  
  .post-title {
    font-size: 1.75rem;
  }
  
  .post-content {
    font-size: 1rem;
  }
}
</style>
