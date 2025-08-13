import React, { useEffect, useState, useCallback } from 'react'
import { WSClient } from './lib/ws'
import type { WSMessage } from './lib/ws'
import { AudioQueue, AudioRecorder } from './lib/audio'
import Chat from './components/Chat'
import EventFeed from './components/EventFeed'
import PersonaBadge from './components/PersonaBadge'
import MicButton from './components/MicButton'
import Interrupt from './components/Interrupt'
import { Auth } from './components/Auth'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import type { User } from '@supabase/supabase-js'
import './styles/tokens.css'

interface AppState {
  isConnected: boolean
  currentPersona: string
  messages: Array<{
    id: string
    role: 'user' | 'assistant'
    content: string
    timestamp: Date
  }>
  events: Array<{
    id: string
    type: string
    data: any
    timestamp: Date
  }>
  isRecording: boolean
  isPlayingTTS: boolean
  connectionError: string | null
}

function AppContent() {
  const { user } = useAuth()
  const [state, setState] = useState<AppState>({
    isConnected: false,
    currentPersona: 'RouterAgent',
    messages: [],
    events: [],
    isRecording: false,
    isPlayingTTS: false,
    connectionError: null
  })

  // Initialize services
  const [wsClient] = useState(() => {
    const clientId = `client_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    return new WSClient('ws://localhost:8000/ws', clientId)
  })
  
  const [audioQueue] = useState(() => new AudioQueue())
  const [audioRecorder] = useState(() => new AudioRecorder())

  // WebSocket message handler
  const handleWSMessage = useCallback((message: WSMessage) => {
    console.log('Received WS message:', message)

    setState(prev => ({
      ...prev,
      events: [...prev.events, {
        id: `event_${Date.now()}_${Math.random().toString(36).substr(2, 5)}`,
        type: message.type,
        data: message,
        timestamp: new Date()
      }]
    }))

    switch (message.type) {
      case 'model_delta':
        handleModelDelta(message.text)
        break
      case 'tool_call':
        handleToolCall(message)
        break
      case 'tool_result':
        handleToolResult(message)
        break
      case 'handoff':
        handleHandoff(message.persona)
        break
      case 'tts_chunk':
        handleTTSChunk(message.url)
        break
      case 'stt_transcript':
        handleSTTTranscript(message.text)
        break
      case 'tts_stopped':
        setState(prev => ({ ...prev, isPlayingTTS: false }))
        break
      case 'error':
        console.error('Server error:', message.message)
        break
    }
  }, [])

  const handleModelDelta = useCallback((text: string) => {
    setState(prev => {
      const messages = [...prev.messages]
      const lastMessage = messages[messages.length - 1]
      
      if (lastMessage && lastMessage.role === 'assistant') {
        // Append to existing assistant message
        lastMessage.content += text
      } else {
        // Create new assistant message
        messages.push({
          id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 5)}`,
          role: 'assistant',
          content: text,
          timestamp: new Date()
        })
      }
      
      return { ...prev, messages }
    })
  }, [])

  const handleToolCall = useCallback((data: any) => {
    console.log('Tool call:', data)
  }, [])

  const handleToolResult = useCallback((data: any) => {
    console.log('Tool result:', data)
  }, [])

  const handleHandoff = useCallback((persona: string) => {
    setState(prev => ({ ...prev, currentPersona: persona }))
  }, [])

  const handleTTSChunk = useCallback((url: string) => {
    setState(prev => ({ ...prev, isPlayingTTS: true }))
    audioQueue.enqueue(`http://localhost:8000${url}`)
  }, [audioQueue])

  const handleSTTTranscript = useCallback((text: string) => {
    console.log('🎤 Received STT transcript:', text)
    setState(prev => ({
      ...prev,
      messages: [...prev.messages, {
        id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 5)}`,
        role: 'user',
        content: text,
        timestamp: new Date()
      }]
    }))
  }, [])

  // Initialize connections
  useEffect(() => {
    const initializeServices = async () => {
      try {
        // Initialize WebSocket
        wsClient.addHandler(handleWSMessage)
        await wsClient.connect()
        setState(prev => ({ ...prev, isConnected: true, connectionError: null }))

        // Initialize audio services
        await audioRecorder.initialize()
        
        // Audio queue event handlers
        audioQueue.addHandler((event, data) => {
          if (event === 'queue_complete') {
            setState(prev => ({ ...prev, isPlayingTTS: false }))
          }
        })

        // Audio recorder event handlers
        audioRecorder.addHandler((event, data) => {
          switch (event) {
            case 'start':
              setState(prev => ({ ...prev, isRecording: true }))
              wsClient.send({ type: 'user_audio_start' })
              break
            case 'chunk':
              wsClient.send({ type: 'user_audio_chunk', pcm: data })
              break
            case 'stop':
              setState(prev => ({ ...prev, isRecording: false }))
              wsClient.send({ type: 'user_audio_end' })
              break
          }
        })

      } catch (error) {
        console.error('Failed to initialize services:', error)
        setState(prev => ({ 
          ...prev, 
          connectionError: 'Bağlantı hatası. Lütfen sayfayı yenileyin.' 
        }))
      }
    }

    initializeServices()

    // Cleanup
    return () => {
      wsClient.disconnect()
      audioQueue.stop()
      audioRecorder.cleanup()
    }
  }, [wsClient, audioQueue, audioRecorder, handleWSMessage])

  // Send text message
  const sendTextMessage = useCallback((text: string) => {
    if (!wsClient.isConnected()) return

    setState(prev => ({
      ...prev,
      messages: [...prev.messages, {
        id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 5)}`,
        role: 'user',
        content: text,
        timestamp: new Date()
      }]
    }))

    wsClient.send({ type: 'user_text', text })
  }, [wsClient])

  // PTT controls
  const startRecording = useCallback(() => {
    if (!state.isRecording && !state.isPlayingTTS) {
      audioRecorder.startRecording()
    }
  }, [audioRecorder, state.isRecording, state.isPlayingTTS])

  const stopRecording = useCallback(() => {
    if (state.isRecording) {
      audioRecorder.stopRecording()
    }
  }, [audioRecorder, state.isRecording])

  // Interrupt TTS
  const interruptTTS = useCallback(() => {
    audioQueue.stop()
    wsClient.send({ type: 'interrupt' })
    setState(prev => ({ ...prev, isPlayingTTS: false }))
  }, [audioQueue, wsClient])

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <h1 className="text-xl font-semibold text-gray-900">
              Telco Agent
            </h1>
            <PersonaBadge persona={state.currentPersona} />
          </div>
          
          <div className="flex items-center space-x-4">
            {/* Connection status */}
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${
                state.isConnected ? 'bg-green-500' : 'bg-red-500'
              }`} />
              <span className="text-sm text-gray-600">
                {state.isConnected ? 'Bağlı' : 'Bağlantı Kesildi'}
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Connection error */}
      {state.connectionError && (
        <div className="bg-red-50 border-l-4 border-red-400 p-4">
          <p className="text-red-700">{state.connectionError}</p>
        </div>
      )}

      {/* Authentication check */}
      {!user ? (
        <div className="flex-1 flex items-center justify-center bg-gray-50">
          <Auth onAuthChange={() => {}} />
        </div>
      ) : (
        /* Main content */
        <div className="flex-1 flex overflow-hidden">
        {/* Chat area */}
        <div className="flex-1 flex flex-col">
          <Chat 
            messages={state.messages}
            onSendMessage={sendTextMessage}
            isConnected={state.isConnected}
          />
          
          {/* Controls */}
          <div className="bg-white border-t border-gray-200 p-4">
            <div className="flex items-center justify-center space-x-6">
              {/* Mic button */}
              <MicButton
                isRecording={state.isRecording}
                isDisabled={state.isPlayingTTS || !state.isConnected}
                onStart={startRecording}
                onStop={stopRecording}
              />
              
              {/* Interrupt button */}
              {state.isPlayingTTS && (
                <Interrupt onClick={interruptTTS} />
              )}
            </div>
          </div>
        </div>

        {/* Event feed sidebar */}
        <div className="w-96 border-l border-gray-200 bg-white">
          <EventFeed events={state.events} />
        </div>
      </div>
      )}
    </div>
  )
}

// Main App component with authentication provider
function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  )
}

export default App