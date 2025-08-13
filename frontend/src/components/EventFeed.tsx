import React, { useState } from 'react'
import { ChevronDown, ChevronRight, Settings, Zap, ArrowRight, Volume2 } from 'lucide-react'

interface Event {
  id: string
  type: string
  data: any
  timestamp: Date
}

interface EventFeedProps {
  events: Event[]
}

const EventFeed: React.FC<EventFeedProps> = ({ events }) => {
  const [expandedEvents, setExpandedEvents] = useState<Set<string>>(new Set())

  const toggleEvent = (eventId: string) => {
    const newExpanded = new Set(expandedEvents)
    if (newExpanded.has(eventId)) {
      newExpanded.delete(eventId)
    } else {
      newExpanded.add(eventId)
    }
    setExpandedEvents(newExpanded)
  }

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('tr-TR', { 
      hour: '2-digit', 
      minute: '2-digit',
      second: '2-digit'
    })
  }

  const getEventIcon = (type: string) => {
    switch (type) {
      case 'tool_call':
        return <Zap className="w-4 h-4" />
      case 'tool_result':
        return <Settings className="w-4 h-4" />
      case 'handoff':
        return <ArrowRight className="w-4 h-4" />
      case 'tts_chunk':
        return <Volume2 className="w-4 h-4" />
      default:
        return <div className="w-4 h-4 rounded-full bg-gray-400" />
    }
  }

  const getEventStyle = (type: string) => {
    switch (type) {
      case 'tool_call':
        return 'event-tool-call'
      case 'tool_result':
        return 'event-tool-result'
      case 'handoff':
        return 'event-handoff'
      case 'tts_chunk':
        return 'event-tts'
      default:
        return 'border-l-gray-400 bg-gray-50'
    }
  }

  const getEventTitle = (event: Event) => {
    switch (event.type) {
      case 'tool_call':
        return `Tool: ${event.data.name}`
      case 'tool_result':
        return `Result: ${event.data.name}`
      case 'handoff':
        return `Handoff: ${event.data.persona}`
      case 'tts_chunk':
        return 'TTS Chunk'
      case 'model_delta':
        return 'Response'
      case 'stt_transcript':
        return 'Speech Input'
      default:
        return event.type
    }
  }

  const getEventDescription = (event: Event) => {
    switch (event.type) {
      case 'tool_call':
        return `Calling ${event.data.name} with arguments`
      case 'tool_result':
        return event.data.result?.success ? 'Success' : 'Failed'
      case 'handoff':
        return `Switched to ${event.data.persona}`
      case 'tts_chunk':
        return 'Audio chunk generated'
      case 'model_delta':
        return event.data.text?.substring(0, 50) + (event.data.text?.length > 50 ? '...' : '')
      case 'stt_transcript':
        return event.data.text
      default:
        return 'Event occurred'
    }
  }

  const renderEventData = (event: Event) => {
    try {
      return (
        <pre className="text-xs bg-gray-100 p-2 rounded mt-2 overflow-x-auto">
          {JSON.stringify(event.data, null, 2)}
        </pre>
      )
    } catch {
      return (
        <div className="text-xs text-gray-500 mt-2">
          Unable to display event data
        </div>
      )
    }
  }

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="border-b border-gray-200 px-4 py-3 bg-gray-50">
        <h2 className="font-medium text-gray-900">Event Feed</h2>
        <p className="text-sm text-gray-600">
          System events and tool calls
        </p>
      </div>

      {/* Events list */}
      <div className="flex-1 overflow-y-auto">
        {events.length === 0 ? (
          <div className="p-4 text-center text-gray-500">
            <Settings className="w-8 h-8 mx-auto mb-2 opacity-50" />
            <p className="text-sm">No events yet</p>
          </div>
        ) : (
          <div className="space-y-2 p-4">
            {events.slice().reverse().map((event) => {
              const isExpanded = expandedEvents.has(event.id)
              
              return (
                <div
                  key={event.id}
                  className={`event-item ${getEventStyle(event.type)}`}
                >
                  {/* Event header */}
                  <div className="flex-shrink-0 mt-1">
                    {getEventIcon(event.type)}
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <button
                      onClick={() => toggleEvent(event.id)}
                      className="w-full text-left hover:bg-white/50 rounded p-1 -m-1 transition-colors"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-gray-900 truncate">
                            {getEventTitle(event)}
                          </p>
                          <p className="text-xs text-gray-600 mt-1">
                            {getEventDescription(event)}
                          </p>
                        </div>
                        
                        <div className="flex items-center space-x-2 ml-2">
                          <span className="text-xs text-gray-500">
                            {formatTime(event.timestamp)}
                          </span>
                          {isExpanded ? (
                            <ChevronDown className="w-4 h-4 text-gray-400" />
                          ) : (
                            <ChevronRight className="w-4 h-4 text-gray-400" />
                          )}
                        </div>
                      </div>
                    </button>

                    {/* Expanded content */}
                    {isExpanded && (
                      <div className="mt-2 animate-fade-in">
                        {renderEventData(event)}
                      </div>
                    )}
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>

      {/* Footer stats */}
      <div className="border-t border-gray-200 px-4 py-2 bg-gray-50">
        <div className="flex justify-between text-xs text-gray-600">
          <span>Total: {events.length}</span>
          <span>
            Tools: {events.filter(e => e.type === 'tool_call').length}
          </span>
        </div>
      </div>
    </div>
  )
}

export default EventFeed