import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api/axios'

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
    
    try {
      const response = await api.get(`/posts/${slug}/`)
      // API returns { success, data: {...}, message, errors }
      const postData = response.data.data || response.data
      currentPost.value = postData
      return postData
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to fetch post'
      throw err
    } finally {
      loading.value = false
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
      const response = await api.get(`/comments/post/${postId}/`)
      comments.value = response.data
      return response.data
    } catch (err) {
      console.error('Failed to fetch comments:', err)
      throw err
    }
  }

  const addComment = async (postId, commentData) => {
    try {
      const response = await api.post(`/comments/`, {post_id: postId, ...commentData})
      comments.value.unshift(response.data)
      
      if (currentPost.value) {
        currentPost.value.comments_count++
      }
      
      return response.data
    } catch (err) {
      throw err
    }
  }

  const likePost = async (slug) => {
    try {
      const response = await api.post(`/likes/`, {post_id: slug})
      
      if (currentPost.value?.slug === slug) {
        currentPost.value.likes_count = response.data.likes_count
        currentPost.value.is_liked = response.data.is_liked
      }
      
      const post = posts.value.find(p => p.slug === slug)
      if (post) {
        post.likes_count = response.data.likes_count
        post.is_liked = response.data.is_liked
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
    likePost,
    resetPosts
  }
})
