<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { usePostsStore } from '@/stores/posts'

const router = useRouter()
const postsStore = usePostsStore()

const form = ref({
  title: '',
  content: '',
  tags: [],
  tagInput: ''
})

const errors = ref({})

const charCount = computed(() => form.value.content.length)

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
    
    const newPost = await postsStore.createPost(postData)
    router.push(`/posts/${newPost.slug}`)
  } catch (err) {
    console.error('Failed to create post:', err)
    if (err.response?.data?.detail) {
      errors.value.general = err.response.data.detail
    }
  }
}
</script>

<template>
  <div class="create-post">
    <div class="container">
      <div class="post-form-card">
        <h1 class="page-title">Create New Post</h1>
        
        <form @submit.prevent="handleSubmit" class="post-form">
          <div v-if="errors.general || postsStore.error" class="alert alert-error">
            {{ errors.general || postsStore.error }}
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
            <div class="editor-meta">
              <span v-if="errors.content" class="error-message">{{ errors.content }}</span>
              <span class="char-count">{{ charCount }} characters</span>
            </div>
          </div>
          
          <div class="form-actions">
            <button 
              type="button"
              @click="$router.back()"
              class="btn btn-secondary"
            >
              Cancel
            </button>
            <button 
              type="submit" 
              class="btn btn-primary btn-lg"
              :disabled="postsStore.loading"
            >
              <span v-if="postsStore.loading" class="loading-spinner"></span>
              <span v-else>Publish Post</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
.create-post {
  padding: 2rem 0;
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

.editor-meta {
  display: flex;
  justify-content: space-between;
  margin-top: 0.5rem;
}

.char-count {
  font-size: 0.8125rem;
  color: var(--text-muted);
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
