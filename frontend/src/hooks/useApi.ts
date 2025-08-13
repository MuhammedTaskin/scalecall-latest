/**
 * Custom hook for making authenticated API calls to the backend.
 */
import { useState, useCallback } from 'react'
import { useAuth } from '../contexts/AuthContext'

interface ApiResponse<T> {
  data: T | null
  error: string | null
  loading: boolean
}

export const useApi = () => {
  const { getAuthToken } = useAuth()

  const makeRequest = useCallback(async <T>(
    url: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> => {
    try {
      const token = await getAuthToken()
      
      const response = await fetch(`http://localhost:8000${url}`, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...(token && { Authorization: `Bearer ${token}` }),
          ...options.headers,
        },
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Request failed' }))
        throw new Error(errorData.detail || `HTTP ${response.status}`)
      }

      const data = await response.json()
      return { data, error: null, loading: false }
    } catch (error) {
      return {
        data: null,
        error: error instanceof Error ? error.message : 'Unknown error',
        loading: false,
      }
    }
  }, [getAuthToken])

  return { makeRequest }
}

// Specific hook for LLM chat
export const useLLMChat = () => {
  const { makeRequest } = useApi()
  const [loading, setLoading] = useState(false)

  const sendMessage = useCallback(async (messages: Array<{ role: string; content: string }>) => {
    setLoading(true)
    try {
      const result = await makeRequest<{ message: { role: string; content: string }; message_id: string }>('/api/llm/chat', {
        method: 'POST',
        body: JSON.stringify({ messages, stream: false }),
      })
      return result
    } finally {
      setLoading(false)
    }
  }, [makeRequest])

  const getMessages = useCallback(async (limit = 50) => {
    return await makeRequest<{ messages: Array<any> }>(`/api/llm/messages?limit=${limit}`)
  }, [makeRequest])

  const clearMessages = useCallback(async () => {
    return await makeRequest<{ deleted_count: number }>('/api/llm/messages', {
      method: 'DELETE',
    })
  }, [makeRequest])

  return {
    sendMessage,
    getMessages,
    clearMessages,
    loading,
  }
}

// Hook for streaming chat responses
export const useStreamingChat = () => {
  const { getAuthToken } = useAuth()

  const streamChat = useCallback(async function* (
    messages: Array<{ role: string; content: string }>
  ): AsyncGenerator<{ text?: string; messageId?: string; error?: string; done?: boolean }> {
    const token = await getAuthToken()
    
    const response = await fetch('http://localhost:8000/api/llm/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token && { Authorization: `Bearer ${token}` }),
      },
      body: JSON.stringify({ messages, stream: true }),
    })

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }

    const reader = response.body?.getReader()
    if (!reader) {
      throw new Error('No response body')
    }

    const decoder = new TextDecoder()
    let buffer = ''

    try {
      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6))
              if (data.type === 'delta' && data.text) {
                yield { text: data.text }
              } else if (data.type === 'complete' && data.message_id) {
                yield { messageId: data.message_id }
              } else if (data.type === 'error') {
                yield { error: data.error }
              } else if (data.type === 'done') {
                yield { done: true }
                return
              }
            } catch (e) {
              console.warn('Failed to parse SSE data:', line)
            }
          }
        }
      }
    } finally {
      reader.releaseLock()
    }
  }, [getAuthToken])

  return { streamChat }
}
