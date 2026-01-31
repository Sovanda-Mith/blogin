<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { usePostsStore } from '@/stores/posts'

const route = useRoute()
const router = useRouter()
const postsStore = usePostsStore()

const slug = computed(() => route.params.slug)
const originalPost = ref(null)

const form = ref({
  title: '',
  content: '',
  tags: [],
  tagInput: ''
})

const errors = ref({})

onMounted(async () => {
  try {
    await postsStore.fetchPost(slug.value)
    originalPost.value = postsStore.currentPost
    
    form.value = {
      title: originalPost.value.title,
      content: originalPost.value.content,
      tags: [...(originalPost.value.tags || [])],
      tagInput: ''
    }
  } catch (err) {
    console.error('Failed to load post:', err)
  }
})

const addTag = () => {
  const tag = form.value.tagInput.trim().toLowerCase()
  if (tag && !form.value.tags.includes(tag) && form.value.tags.length < 5) {
    form.value.tags.push(tag)
    form.value.tagInput = ''
  }
}

const removeTag = (index) => {
  form.value.tags.splice(index, 1)
}

const validateForm = () => {
  errors.value = {}
  
  if (!form.value.title.trim()) {
    errors.value.title = 'Title is required'
  }
  
  if (!form.value.content.trim()) {
    errors.value.content = 'Content is required'
  }
  
  return Object.keys(errors.value).length === 0
}

const handleSubmit = async () => {
  if (!validateForm()) return
  
  try {
    const postData = {
      title: form.value.title,
      content: form.value.content,
      tags: form.value.tags
    }
    
    await postsStore.updatePost(slug.value, postData)
    router.push(`/posts/${slug.value}`)
  } catch (err) {
    console.error('Failed to update post:', err)
    if (err.response?.data?.detail) {
      errors.value.general = err.response.data.detail
    }
  }
}
</script>

<template>
  <div class="edit-post">
    <div class="container">
      <div v-if="postsStore.loading && !originalPost" class="loading-container">
        <span class="loading-spinner large"></span>
        <p>Loading post...</p>
      </div>
      
      <div v-else-if="postsStore.error" class="error-alert">
        {{ postsStore.error }}
        <RouterLink to="/" class="btn btn-secondary btn-sm">Go Home</RouterLink>
      </div>
      
      <div v-else class="post-form-card">
        <h1 class="page-title">Edit Post</h1>
        
        <form @submit.prevent="handleSubmit" class="post-form">
          <div v-if="errors.general" class="alert alert-error">
            {{ errors.general }}
          </div>
          
          <div class="form-group">
            <label class="form-label">Title *</label>
            <input
              v-model="form.title"
              type="text"
              class="form-input"
              placeholder="Enter a catchy title"
              required
            />
            <span v-if="errors.title" class="error-message">{{ errors.title }}</span>
          </div>
          
          <div class="form-group">
            <label class="form-label">Tags (up to 5)</label>
            <div class="tags-input-wrapper">
              <div v-if="form.tags.length" class="selected-tags">
                <span v-for="(tag, index) in form.tags" :key="tag" class="selected-tag">
                  {{ tag }}
                  <button @click="removeTag(index)" type="button" class="remove-tag">×</button>
                </span>
              </div>
              <input
                v-model="form.tagInput"
                type="text"
                class="form-input tag-input"
                placeholder="Add a tag and press Enter"
                @keydown.enter.prevent="addTag"
              />
            </div>
          </div>
          
          <div class="form-group">
            <label class="form-label">Content *</label>
            <textarea
              v-model="form.content"
              class="form-textarea content-editor"
              placeholder="Write your story... (Markdown supported)"
              rows="15"
              required
            ></textarea>
            <span v-if="errors.content" class="error-message">{{ errors.content }}</span>
          </div>
          
          <div class="form-actions">
            <RouterLink 
              :to="`/posts/${slug}`"
              class="btn btn-secondary"
            >
              Cancel
            </RouterLink>
            <button 
              type="submit" 
              class="btn btn-primary btn-lg"
              :disabled="postsStore.loading"
            >
              <span v-if="postsStore.loading" class="loading-spinner"></span>
              <span v-else>Update Post</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
.edit-post {
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

.post-form-card {
  max-width: 800px;
  margin: 0 auto;
  background-color: var(--bg-color);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow);
  padding: 2.5rem;
}

.page-title {
  font-size: 1.75rem;
  font-weight: 700;
  margin-bottom: 2rem;
}

.post-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
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

.tags-input-wrapper {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.selected-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.selected-tag {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  background-color: var(--primary-color);
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.8125rem;
}

.remove-tag {
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  font-size: 1rem;
  line-height: 1;
  padding: 0;
  margin-left: 0.25rem;
}

.tag-input {
  margin-top: 0.5rem;
}

.content-editor {
  font-family: 'Inter', monospace;
  font-size: 1rem;
  line-height: 1.7;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1rem;
}

@media (max-width: 768px) {
  .post-form-card {
    padding: 1.5rem;
  }
  
  .form-actions {
    flex-direction: column-reverse;
  }
  
  .form-actions .btn {
    width: 100%;
  }
}
</style>
