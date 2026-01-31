<script setup>
import { computed } from 'vue'

const props = defineProps({
  comment: {
    type: Object,
    required: true
  },
  isOwnComment: {
    type: Boolean,
    default: false
  },
  currentUserId: {
    type: [String, Number],
    default: null
  },
  replyingTo: {
    type: Object,
    default: null
  },
  editing: {
    type: [String, Number],
    default: null
  },
  editContent: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['reply', 'edit', 'delete', 'cancelReply', 'saveEdit', 'cancelEdit', 'update:editContent', 'update:editing'])

const isEditing = computed(() => props.editing === props.comment.id)

const displayName = computed(() => {
  return props.comment.author_display_name || props.comment.author_username || 'Anonymous'
})

const avatarUrl = computed(() => {
  return props.comment.author_avatar || '/default-avatar.png'
})

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)
  
  if (diffMins < 1) return 'just now'
  if (diffMins < 60) return `${diffMins}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  if (diffDays < 7) return `${diffDays}d ago`
  
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

const handleEditInput = (e) => {
  emit('update:editContent', e.target.value)
}

const startEdit = () => {
  emit('update:editing', props.comment.id)
  emit('update:editContent', props.comment.content)
}

const saveEdit = () => {
  emit('saveEdit', props.comment.id)
}

const cancelEdit = () => {
  emit('cancelEdit')
}

const handleKeydown = (e) => {
  if (e.key === 'Enter' && e.ctrlKey) {
    saveEdit()
  } else if (e.key === 'Escape') {
    cancelEdit()
  }
}
</script>

<template>
  <div class="comment-item">
    <div class="comment-header">
      <img 
        :src="avatarUrl" 
        :alt="displayName"
        class="comment-avatar"
      />
      <div class="comment-meta">
        <RouterLink 
          :to="`/users/${comment.author_username}`"
          class="comment-author"
        >
          {{ displayName }}
        </RouterLink>
        <span class="comment-date">
          {{ formatDate(comment.created_at) }}
          <span v-if="comment.edited" class="edited-badge">(edited)</span>
        </span>
      </div>
    </div>
    
    <div v-if="isEditing" class="edit-form">
      <textarea
        :value="editContent"
        @input="handleEditInput"
        @keydown="handleKeydown"
        class="form-textarea edit-textarea"
        rows="3"
      ></textarea>
      <div class="edit-actions">
        <button @click="cancelEdit" class="btn btn-secondary btn-sm">Cancel</button>
        <button 
          @click="saveEdit" 
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
        @click="$emit('reply', comment)" 
        class="action-link"
        :class="{ active: replyingTo?.id === comment.id }"
      >
        Reply
      </button>
      <button 
        v-if="isOwnComment && !comment.is_deleted"
        @click="startEdit" 
        class="action-link"
      >
        Edit
      </button>
      <button 
        v-if="isOwnComment"
        @click="$emit('delete', comment.id)" 
        class="action-link danger"
      >
        Delete
      </button>
    </div>
    
    <div v-if="replyingTo?.id === comment.id" class="reply-form">
      <span class="replying-label">Replying to <strong>{{ displayName }}</strong></span>
      <button @click="$emit('cancelReply')" class="cancel-reply">Cancel</button>
    </div>
  </div>
</template>

<style scoped>
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

.cancel-reply {
  background: none;
  border: none;
  color: var(--primary-color);
  cursor: pointer;
  font-size: 0.8125rem;
}
</style>
