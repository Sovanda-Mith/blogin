<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/api/axios'

const props = defineProps({
  postId: {
    type: [String, Number],
    required: true
  }
})

const authStore = useAuthStore()
const comments = ref([])
const loading = ref(false)
const newComment = ref('')
const replyTo = ref(null)
const submitting = ref(false)

const rootComments = computed(() => {
  return comments.value.filter(c => !c.parent_id)
})

const getReplies = (parentId) => {
  return comments.value.filter(c => c.parent_id === parentId)
}

const fetchComments = async () => {
  loading.value = true
  try {
    const response = await api.get(`/posts/${props.postId}/comments`)
    comments.value = response.data
  } catch (err) {
    console.error('Failed to fetch comments:', err)
  } finally {
    loading.value = false
  }
}

const submitComment = async () => {
  if (!newComment.value.trim()) return
  
  submitting.value = true
  try {
    const payload = {
      content: newComment.value,
      parent_id: replyTo.value?.id || null
    }
    
    const response = await api.post(`/posts/${props.postId}/comments`, payload)
    comments.value.unshift(response.data)
    newComment.value = ''
    replyTo.value = null
  } catch (err) {
    console.error('Failed to add comment:', err)
  } finally {
    submitting.value = false
  }
}

const startReply = (comment) => {
  if (!authStore.isAuthenticated) {
    alert('Please login to reply')
    return
  }
  replyTo.value = comment
  document.getElementById('comment-input')?.focus()
}

const cancelReply = () => {
  replyTo.value = null
}

const deleteComment = async (commentId) => {
  if (!confirm('Are you sure you want to delete this comment?')) return
  
  try {
    await api.delete(`/posts/${props.postId}/comments/${commentId}`)
    comments.value = comments.value.filter(c => c.id !== commentId)
  } catch (err) {
    console.error('Failed to delete comment:', err)
  }
}

onMounted(fetchComments)
</script>

<template>
  <div class="comments-section">
    <h3 class="comments-title">
      Comments ({{ comments.length }})
    </h3>
    
    <div v-if="authStore.isAuthenticated" class="comment-form">
      <div v-if="replyTo" class="reply-indicator">
        Replying to {{ replyTo.author?.username }}
        <button @click="cancelReply" class="cancel-reply">Cancel</button>
      </div>
      
      <textarea
        id="comment-input"
        v-model="newComment"
        class="form-textarea"
        placeholder="Write a comment..."
        rows="3"
      ></textarea>
      
      <button 
        @click="submitComment" 
        class="btn btn-primary"
        :disabled="submitting || !newComment.trim()"
      >
        <span v-if="submitting" class="loading-spinner"></span>
        <span v-else>Post Comment</span>
      </button>
    </div>
    
    <div v-else class="login-prompt">
      <RouterLink to="/login">Login</RouterLink> to leave a comment
    </div>
    
    <div v-if="loading" class="loading-state">
      <span class="loading-spinner"></span>
      Loading comments...
    </div>
    
    <div v-else-if="comments.length === 0" class="empty-state">
      No comments yet. Be the first to share your thoughts!
    </div>
    
    <div v-else class="comments-list">
      <div 
        v-for="comment in rootComments" 
        :key="comment.id"
        class="comment"
      >
        <div class="comment-header">
          <img 
            :src="comment.author?.avatar || '/default-avatar.png'" 
            class="comment-avatar"
            :alt="comment.author?.username"
          />
          <div class="comment-meta">
            <RouterLink 
              :to="`/users/${comment.author?.username}`"
              class="comment-author"
            >
              {{ comment.author?.username }}
            </RouterLink>
            <span class="comment-date">
              {{ new Date(comment.created_at).toLocaleDateString() }}
            </span>
          </div>
        </div>
        
        <p class="comment-content">{{ comment.content }}</p>
        
        <div class="comment-actions">
          <button @click="startReply(comment)" class="action-link">
            Reply
          </button>
          <button 
            v-if="comment.author?.id === authStore.currentUser?.id"
            @click="deleteComment(comment.id)"
            class="action-link danger"
          >
            Delete
          </button>
        </div>
        
        <!-- Nested replies -->
        <div v-if="getReplies(comment.id).length" class="replies">
          <div 
            v-for="reply in getReplies(comment.id)" 
            :key="reply.id"
            class="comment reply"
          >
            <div class="comment-header">
              <img 
                :src="reply.author?.avatar || '/default-avatar.png'" 
                class="comment-avatar"
                :alt="reply.author?.username"
              />
              <div class="comment-meta">
                <RouterLink 
                  :to="`/users/${reply.author?.username}`"
                  class="comment-author"
                >
                  {{ reply.author?.username }}
                </RouterLink>
                <span class="comment-date">
                  {{ new Date(reply.created_at).toLocaleDateString() }}
                </span>
              </div>
            </div>
            
            <p class="comment-content">{{ reply.content }}</p>
            
            <div class="comment-actions">
              <button @click="startReply(reply)" class="action-link">
                Reply
              </button>
              <button 
                v-if="reply.author?.id === authStore.currentUser?.id"
                @click="deleteComment(reply.id)"
                class="action-link danger"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.comments-section {
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid var(--border-color);
}

.comments-title {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 1.5rem;
}

.comment-form {
  margin-bottom: 2rem;
}

.reply-indicator {
  font-size: 0.875rem;
  color: var(--text-muted);
  margin-bottom: 0.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.cancel-reply {
  background: none;
  border: none;
  color: var(--primary-color);
  cursor: pointer;
  font-size: 0.8125rem;
}

.comment-form .btn {
  margin-top: 0.75rem;
}

.login-prompt {
  padding: 1rem;
  background-color: var(--bg-secondary);
  border-radius: var(--radius);
  text-align: center;
  color: var(--text-muted);
  margin-bottom: 2rem;
}

.loading-state {
  text-align: center;
  padding: 2rem;
  color: var(--text-muted);
}

.comments-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.comment {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.comment.reply {
  margin-left: 2rem;
  margin-top: 1rem;
  padding-left: 1rem;
  border-left: 2px solid var(--border-color);
}

.comment-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.comment-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
}

.comment-meta {
  display: flex;
  flex-direction: column;
}

.comment-author {
  font-weight: 600;
  font-size: 0.875rem;
  color: var(--text-color);
  text-decoration: none;
}

.comment-author:hover {
  color: var(--primary-color);
}

.comment-date {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.comment-content {
  font-size: 0.9375rem;
  line-height: 1.6;
  color: var(--text-color);
}

.comment-actions {
  display: flex;
  gap: 1rem;
}

.action-link {
  background: none;
  border: none;
  color: var(--text-muted);
  font-size: 0.8125rem;
  cursor: pointer;
  padding: 0;
  transition: color 0.2s;
}

.action-link:hover {
  color: var(--primary-color);
}

.action-link.danger:hover {
  color: var(--danger-color);
}

.replies {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
</style>
