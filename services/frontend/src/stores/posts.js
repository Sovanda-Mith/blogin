import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api/axios'
import { useAuthStore } from '@/stores/auth'

export const usePostsStore = defineStore('posts', () => {
  // State
  const posts = ref([])
  const currentPost = ref(null)
  const comments = ref([])
  const loading = ref(false)
  const error = ref(null)
  const pagination = ref({
    page: 1,
    limit: 10,
    total: 0,
    hasMore: true
  })

  // Getters
  const allPosts = computed(() => posts.value)
  const postCount = computed(() => pagination.value.total)

  // Actions
  const fetchPosts = async (params = {}) => {
    loading.value = true
    error.value = null
    
    try {
      const queryParams = new URLSearchParams({
        page: params.page || pagination.value.page,
        limit: params.limit || pagination.value.limit,
        ...params
      })
      
      const response = await api.get(`/posts/?${queryParams}`)
      // API returns { success, data: { items, pagination }, message, errors }
      const responseData = response.data.data || response.data
      
      if (params.page === 1 || !params.page) {
        posts.value = responseData.items || []
      } else {
        posts.value = [...posts.value, ...(responseData.items || [])]
      }
      
      pagination.value = {
        page: responseData.pagination?.page || 1,
        limit: responseData.pagination?.limit || 10,
        total: responseData.pagination?.total || 0,
        hasMore: (responseData.pagination?.page || 1) < (responseData.pagination?.total_pages || 1)
      }
      
      return responseData
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to fetch posts'
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchPost = async (slug) => {
    loading.value = true
    error.value = null
    currentPost.value = null
    
    try {
      const response = await api.get(`/posts/${slug}/`)
      const postData = response.data.data || response.data
      currentPost.value = postData
      
      const authStore = useAuthStore()
      if (authStore.isAuthenticated) {
        try {
          const likeStatus = await getLikeStatus(slug)
          currentPost.value.is_liked = likeStatus.liked
          currentPost.value.likes_count = likeStatus.count
        } catch (e) {
          console.error('Failed to fetch like status:', e)
        }
      }
      
      return postData
    } catch (err) {
      if (err.response) {
        error.value = err.response.data?.detail || err.response.data?.message || err.message || 'Failed to fetch post'
      } else if (err.request) {
        error.value = 'No response from server'
      } else {
        error.value = err.message || 'Failed to fetch post'
      }
      throw err
    } finally {
      loading.value = false
    }
  }

  const getLikeStatus = async (slug) => {
    try {
      const response = await api.get(`/likes/status?post_slug=${slug}`)
      const countResponse = await api.get(`/likes/count?post_slug=${slug}`)
      return {
        liked: response.data.data?.liked || false,
        count: countResponse.data.data?.count || 0
      }
    } catch (err) {
      console.error('Failed to get like status:', err)
      return { liked: false, count: 0 }
    }
  }

  const createPost = async (postData) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await api.post('/posts/', postData)
      // API returns { success, data: {...}, message, errors }
      const newPost = response.data.data || response.data
      posts.value.unshift(newPost)
      return newPost
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to create post'
      throw err
    } finally {
      loading.value = false
    }
  }

  const updatePost = async (slug, postData) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await api.put(`/posts/${slug}/`, postData)
      
      const index = posts.value.findIndex(p => p.slug === slug)
      if (index !== -1) {
        posts.value[index] = response.data
      }
      
      if (currentPost.value?.slug === slug) {
        currentPost.value = response.data
      }
      
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to update post'
      throw err
    } finally {
      loading.value = false
    }
  }

  const deletePost = async (slug) => {
    loading.value = true
    error.value = null
    
    try {
      await api.delete(`/posts/${slug}/`)
      posts.value = posts.value.filter(p => p.slug !== slug)
      
      if (currentPost.value?.slug === slug) {
        currentPost.value = null
      }
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to delete post'
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchComments = async (postId) => {
    try {
      const response = await api.get(`/posts/${postId}/comments/all/`)
      comments.value = response.data.data?.items || []
      return comments.value
    } catch (err) {
      console.error('Failed to fetch comments:', err)
      throw err
    }
  }

  const addComment = async (postId, content, parentId = null) => {
    try {
      const response = await api.post(`/comments`, {
        post_id: postId,
        content: content,
        parent_id: parentId
      })
      await fetchComments(postId)
      return response.data.data
    } catch (err) {
      throw err
    }
  }

  const editComment = async (commentId, content) => {
    try {
      const response = await api.put(`/comments/${commentId}/`, { content })
      return response.data.data
    } catch (err) {
      throw err
    }
  }

  const deleteComment = async (commentId) => {
    try {
      await api.delete(`/comments/${commentId}/`)
      return true
    } catch (err) {
      throw err
    }
  }

  const likePost = async (slug) => {
    try {
      const response = await api.post(`/likes/`, { post_slug: slug })
      
      if (currentPost.value?.slug === slug) {
        currentPost.value.likes_count = response.data.data?.count || response.data.data?.likes_count
        currentPost.value.is_liked = response.data.data?.liked || true
      }
      
      const post = posts.value.find(p => p.slug === slug)
      if (post) {
        post.likes_count = response.data.data?.count || post.likes_count
        post.is_liked = response.data.data?.liked || post.is_liked
      }
      
      return response.data.data || response.data
    } catch (err) {
      throw err
    }
  }

  const unlikePost = async (slug) => {
    try {
      const response = await api.delete(`/likes/${slug}`)
      
      if (currentPost.value?.slug === slug) {
        currentPost.value.likes_count = Math.max(0, (currentPost.value.likes_count || 1) - 1)
        currentPost.value.is_liked = false
      }
      
      const post = posts.value.find(p => p.slug === slug)
      if (post) {
        post.likes_count = Math.max(0, (post.likes_count || 1) - 1)
        post.is_liked = false
      }
      
      return response.data
    } catch (err) {
      throw err
    }
  }

  const resetPosts = () => {
    posts.value = []
    pagination.value = {
      page: 1,
      limit: 10,
      total: 0,
      hasMore: true
    }
  }

  return {
    posts,
    currentPost,
    comments,
    loading,
    error,
    pagination,
    allPosts,
    postCount,
    fetchPosts,
    fetchPost,
    createPost,
    updatePost,
    deletePost,
    fetchComments,
    addComment,
    editComment,
    deleteComment,
    likePost,
    unlikePost,
    getLikeStatus,
    resetPosts
  }
})
