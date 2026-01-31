<script setup>
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import LikeButton from './LikeButton.vue'

const props = defineProps({
  post: {
    type: Object,
    required: true
  },
  showActions: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['delete'])

const sanitizedExcerpt = computed(() => {
  // Use summary if available, otherwise use content, or empty string
  const excerptText = props.post.summary || props.post.content?.substring(0, 200) || ''
  const excerpt = excerptText + (excerptText.length >= 200 ? '...' : '')
  const html = marked.parse(excerpt || 'No summary available')
  return DOMPurify.sanitize(html)
})

const formattedDate = computed(() => {
  return new Date(props.post.created_at).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
})

const readTime = computed(() => {
  const content = props.post.content || props.post.summary || ''
  const words = content.split(/\s+/).length || 0
  const minutes = Math.ceil(words / 200)
  return `${minutes} min read`
})
</script>

<template>
  <article class="post-card">
    <RouterLink :to="`/posts/${post.slug}`" class="post-link">
      <div class="post-header">
        <div class="post-author">
          <img 
            :src="post.author_avatar || '/default-avatar.png'" 
            :alt="post.author_username || 'Author'"
            class="author-avatar"
          />
          <div class="author-info">
            <RouterLink 
              v-if="post.author_username"
              :to="`/users/${post.author_username}`"
              class="author-name"
              @click.stop
            >
              {{ post.author_username }}
            </RouterLink>
            <span v-else class="author-name">Unknown Author</span>
            <span class="post-meta">{{ formattedDate }} • {{ readTime }}</span>
          </div>
        </div>
      </div>
      
      <h2 class="post-title">{{ post.title }}</h2>
      
      <div class="post-tags" v-if="post.tags?.length">
        <span v-for="tag in post.tags.slice(0, 3)" :key="tag.id || tag" class="tag">
          #{{ tag.name || tag }}
        </span>
      </div>
      
      <div class="post-excerpt" v-html="sanitizedExcerpt"></div>
    </RouterLink>
    
    <div class="post-footer" v-if="showActions">
      <div class="post-actions">
        <LikeButton 
          :post-slug="post.slug" 
          :initial-likes="post.likes_count"
          :initial-liked="post.is_liked"
        />
        
        <RouterLink :to="`/posts/${post.slug}`" class="action-btn">
          <span>💬</span>
          <span>{{ post.comments_count || 0 }}</span>
        </RouterLink>
      </div>
    </div>
  </article>
</template>

<style scoped>
.post-card {
  background-color: var(--bg-color);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow);
  padding: 1.5rem;
  transition: box-shadow 0.2s;
}

.post-card:hover {
  box-shadow: var(--shadow-lg);
}

.post-link {
  text-decoration: none;
  color: inherit;
  display: block;
}

.post-header {
  margin-bottom: 1rem;
}

.post-author {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.author-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid var(--border-color);
}

.author-info {
  display: flex;
  flex-direction: column;
}

.author-name {
  font-weight: 600;
  color: var(--text-color);
  text-decoration: none;
  font-size: 0.875rem;
}

.author-name:hover {
  color: var(--primary-color);
}

.post-meta {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.post-title {
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 0.75rem;
  color: var(--text-color);
  line-height: 1.3;
}

.post-tags {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
  flex-wrap: wrap;
}

.tag {
  font-size: 0.75rem;
  color: var(--primary-color);
  background-color: rgba(59, 130, 246, 0.1);
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}

.post-excerpt {
  color: var(--text-muted);
  font-size: 0.9375rem;
  line-height: 1.6;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
}

.post-excerpt :deep(p) {
  margin: 0;
}

.post-footer {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border-color);
}

.post-actions {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.375rem 0.75rem;
  background-color: var(--bg-secondary);
  border-radius: var(--radius);
  text-decoration: none;
  color: var(--text-muted);
  font-size: 0.875rem;
  transition: all 0.2s;
}

.action-btn:hover {
  background-color: var(--border-color);
  color: var(--text-color);
}
</style>
