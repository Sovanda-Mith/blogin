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

const emit = defineEmits(['update:commentsCount'])

const authStore = useAuthStore()
const comments = ref([])
const loading = ref(false)
const newComment = ref('')
const replyTo = ref(null)
const submitting = ref(false)
const error = ref(null)
const editingId = ref(null)
const editContent = ref('')

const commentTree = computed(() => {
  const map = {}
  const roots = []
  
  comments.value.forEach(comment => {
    map[comment.id] = { ...comment, replies: [] }
  })
  
  comments.value.forEach(comment => {
    if (comment.parent_id && map[comment.parent_id]) {
      map[comment.parent_id].replies.push(map[comment.id])
    } else {
      roots.push(map[comment.id])
    }
  })
  
  return roots.sort((a, b) => new Date(a.created_at) - new Date(b.created_at))
})

const fetchComments = async () => {
  loading.value = true
  error.value = null
  try {
    const response = await api.get(`/posts/${props.postId}/comments/all/`)
    comments.value = response.data.data?.items || []
    emit('update:commentsCount', comments.value.length)
  } catch (err) {
    console.error('Failed to fetch comments:', err)
    error.value = err.response?.data?.detail || 'Failed to load comments'
  } finally {
    loading.value = false
  }
}

const submitComment = async () => {
  if (!newComment.value.trim()) return
  
  submitting.value = true
  error.value = null
  try {
    const payload = {
      post_id: props.postId,
      content: newComment.value,
      parent_id: replyTo.value?.id || null
    }
    
    await api.post(`/comments`, payload)
    await fetchComments()
    newComment.value = ''
    replyTo.value = null
  } catch (err) {
    console.error('Failed to add comment:', err)
    error.value = err.response?.data?.detail || 'Failed to post comment'
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

const startEdit = (comment) => {
  editingId.value = comment.id
  editContent.value = comment.content
}

const cancelEdit = () => {
  editingId.value = null
  editContent.value = ''
}

const saveEdit = async (commentId) => {
  if (!editContent.value.trim()) return
  
  try {
    await api.put(`/comments/${commentId}/`, { content: editContent.value })
    await fetchComments()
    cancelEdit()
  } catch (err) {
    console.error('Failed to edit comment:', err)
    error.value = err.response?.data?.detail || 'Failed to edit comment'
  }
}

const deleteComment = async (commentId) => {
  if (!confirm('Are you sure you want to delete this comment?')) return
  
  try {
    await api.delete(`/comments/${commentId}/`)
    await fetchComments()
  } catch (err) {
    console.error('Failed to delete comment:', err)
    error.value = err.response?.data?.detail || 'Failed to delete comment'
  }
}

const isOwnComment = (comment) => {
  return authStore.currentUser?.id === comment.author_id
}

onMounted(fetchComments)
</script>

<template>
  <div class="comments-section">
    <h3 class="comments-title">
      Comments ({{ comments.length }})
    </h3>
    
    <div v-if="error" class="alert alert-error">
      {{ error }}
      <button @click="error = null" class="dismiss-btn">×</button>
    </div>
    
    <div v-if="authStore.isAuthenticated" class="comment-form">
      <div v-if="replyTo" class="reply-indicator">
        <span>Replying to <strong>{{ replyTo.author_username }}</strong></span>
        <button @click="cancelReply" class="cancel-reply">Cancel</button>
      </div>
      
      <textarea
        id="comment-input"
        v-model="newComment"
        class="form-textarea"
        placeholder="Write a comment..."
        rows="3"
        @keydown.ctrl.enter="submitComment"
      ></textarea>
      
      <div class="form-actions">
        <span class="hint">Ctrl+Enter to submit</span>
        <button 
          @click="submitComment" 
          class="btn btn-primary"
          :disabled="submitting || !newComment.trim()"
        >
          <span v-if="submitting" class="loading-spinner"></span>
          <span v-else>{{ replyTo ? 'Reply' : 'Comment' }}</span>
        </button>
      </div>
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
        v-for="comment in commentTree" 
        :key="comment.id"
        class="comment-thread"
      >
        <div class="comment-item">
          <div class="comment-header">
            <img 
              :src="comment.author_avatar || '/default-avatar.png'" 
              :alt="comment.author_display_name || comment.author_username"
              class="comment-avatar"
            />
            <div class="comment-meta">
              <RouterLink 
                :to="`/users/${comment.author_username}`"
                class="comment-author"
              >
                {{ comment.author_display_name || comment.author_username || 'Anonymous' }}
              </RouterLink>
              <span class="comment-date">
                {{ new Date(comment.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) }}
                <span v-if="comment.edited" class="edited-badge">(edited)</span>
              </span>
            </div>
          </div>
          
          <div v-if="editingId === comment.id" class="edit-form">
            <textarea
              v-model="editContent"
              class="form-textarea edit-textarea"
              rows="3"
              @keydown.ctrl.enter="saveEdit(comment.id)"
              @keydown.escape="cancelEdit"
            ></textarea>
            <div class="edit-actions">
              <button @click="cancelEdit" class="btn btn-secondary btn-sm">Cancel</button>
              <button 
                @click="saveEdit(comment.id)" 
                class="btn btn-primary btn-sm"
                :disabled="!editContent.trim()"
              >
                Save
              </button>
            </div>
          </div>
          
          <p v-else class="comment-content">{{ comment.content }}</p>
          
          <div class="comment-actions">
            <button 
              v-if="!comment.is_deleted"
              @click="startReply(comment)" 
              class="action-link"
              :class="{ active: replyTo?.id === comment.id }"
            >
              Reply
            </button>
            <button 
              v-if="isOwnComment(comment) && !comment.is_deleted"
              @click="startEdit(comment)" 
              class="action-link"
            >
              Edit
            </button>
            <button 
              v-if="isOwnComment(comment)"
              @click="deleteComment(comment.id)" 
              class="action-link danger"
            >
              Delete
            </button>
          </div>
          
          <div v-if="replyTo?.id === comment.id" class="reply-form">
            <span class="replying-label">Replying to <strong>{{ comment.author_display_name || comment.author_username }}</strong></span>
            <button @click="cancelReply" class="cancel-reply">Cancel</button>
          </div>
        </div>
        
        <div v-if="comment.replies?.length" class="replies">
          <div 
            v-for="reply in comment.replies" 
            :key="reply.id"
            class="reply-thread"
          >
            <div class="comment-item">
              <div class="comment-header">
                <img 
                  :src="reply.author_avatar || '/default-avatar.png'" 
                  :alt="reply.author_display_name || reply.author_username"
                  class="comment-avatar"
                />
                <div class="comment-meta">
                  <RouterLink 
                    :to="`/users/${reply.author_username}`"
                    class="comment-author"
                  >
                    {{ reply.author_display_name || reply.author_username || 'Anonymous' }}
                  </RouterLink>
                  <span class="comment-date">
                    {{ new Date(reply.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) }}
                    <span v-if="reply.edited" class="edited-badge">(edited)</span>
                  </span>
                </div>
              </div>
              
              <div v-if="editingId === reply.id" class="edit-form">
                <textarea
                  v-model="editContent"
                  class="form-textarea edit-textarea"
                  rows="3"
                  @keydown.ctrl.enter="saveEdit(reply.id)"
                  @keydown.escape="cancelEdit"
                ></textarea>
                <div class="edit-actions">
                  <button @click="cancelEdit" class="btn btn-secondary btn-sm">Cancel</button>
                  <button 
                    @click="saveEdit(reply.id)" 
                    class="btn btn-primary btn-sm"
                    :disabled="!editContent.trim()"
                  >
                    Save
                  </button>
                </div>
              </div>
              
              <p v-else class="comment-content">{{ reply.content }}</p>
              
              <div class="comment-actions">
                <button 
                  v-if="!reply.is_deleted"
                  @click="startReply(reply)" 
                  class="action-link"
                  :class="{ active: replyTo?.id === reply.id }"
                >
                  Reply
                </button>
                <button 
                  v-if="isOwnComment(reply) && !reply.is_deleted"
                  @click="startEdit(reply)" 
                  class="action-link"
                >
                  Edit
                </button>
                <button 
                  v-if="isOwnComment(reply)"
                  @click="deleteComment(reply.id)" 
                  class="action-link danger"
                >
                  Delete
                </button>
              </div>
              
              <div v-if="replyTo?.id === reply.id" class="reply-form">
                <span class="replying-label">Replying to <strong>{{ reply.author_display_name || reply.author_username }}</strong></span>
                <button @click="cancelReply" class="cancel-reply">Cancel</button>
              </div>
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

.form-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 0.5rem;
}

.hint {
  font-size: 0.75rem;
  color: var(--text-muted);
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

.empty-state {
  text-align: center;
  padding: 3rem 1rem;
  color: var(--text-muted);
  background-color: var(--bg-secondary);
  border-radius: var(--radius);
}

.comments-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.comment-thread {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.comment-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.comment-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.comment-avatar {
  width: 36px;
  height: 36px;
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
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.edited-badge {
  font-style: italic;
  opacity: 0.7;
}

.comment-content {
  font-size: 0.9375rem;
  line-height: 1.6;
  color: var(--text-color);
  margin-left: 48px;
}

.comment-actions {
  display: flex;
  gap: 1rem;
  margin-left: 48px;
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

.action-link.active {
  color: var(--primary-color);
}

.action-link.danger:hover {
  color: var(--danger-color);
}

.edit-form {
  margin-left: 48px;
}

.edit-textarea {
  font-size: 0.9375rem;
}

.edit-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.5rem;
  justify-content: flex-end;
}

.reply-form {
  margin-left: 48px;
  margin-top: 0.5rem;
  padding: 0.5rem;
  background-color: var(--bg-secondary);
  border-radius: var(--radius);
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.8125rem;
}

.replying-label {
  color: var(--text-muted);
}

.replies {
  margin-left: 2.5rem;
  margin-top: 0.75rem;
  padding-left: 1rem;
  border-left: 2px solid var(--border-color);
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.reply-thread {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.alert {
  padding: 0.75rem 1rem;
  border-radius: var(--radius);
  font-size: 0.875rem;
  margin-bottom: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.alert-error {
  background-color: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: var(--danger-color);
}

.dismiss-btn {
  background: none;
  border: none;
  color: inherit;
  font-size: 1.25rem;
  cursor: pointer;
  padding: 0;
  line-height: 1;
}
</style>
