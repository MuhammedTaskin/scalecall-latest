import React, { useState, useCallback } from 'react'
import { Mic, MicOff } from 'lucide-react'

interface MicButtonProps {
  isRecording: boolean
  isDisabled: boolean
  onStart: () => void
  onStop: () => void
}

const MicButton: React.FC<MicButtonProps> = ({ 
  isRecording, 
  isDisabled, 
  onStart, 
  onStop 
}) => {
  const [isPressing, setIsPressing] = useState(false)

  const handleMouseDown = useCallback(() => {
    if (isDisabled) return
    setIsPressing(true)
    onStart()
  }, [isDisabled, onStart])

  const handleMouseUp = useCallback(() => {
    if (isDisabled) return
    setIsPressing(false)
    onStop()
  }, [isDisabled, onStop])

  const handleMouseLeave = useCallback(() => {
    if (isPressing) {
      setIsPressing(false)
      onStop()
    }
  }, [isPressing, onStop])

  const handleTouchStart = useCallback((e: React.TouchEvent) => {
    e.preventDefault()
    handleMouseDown()
  }, [handleMouseDown])

  const handleTouchEnd = useCallback((e: React.TouchEvent) => {
    e.preventDefault()
    handleMouseUp()
  }, [handleMouseUp])

  return (
    <div className="flex flex-col items-center space-y-2">
      {/* Mic button */}
      <button
        onMouseDown={handleMouseDown}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseLeave}
        onTouchStart={handleTouchStart}
        onTouchEnd={handleTouchEnd}
        disabled={isDisabled}
        className={`mic-button ${isRecording ? 'recording' : ''} ${
          isDisabled ? 'opacity-50 cursor-not-allowed' : ''
        }`}
      >
        {isRecording ? (
          <Mic className="w-6 h-6" />
        ) : (
          <MicOff className="w-6 h-6 opacity-70" />
        )}
        
        {/* Recording indicator ring */}
        {isRecording && (
          <div className="absolute inset-0 rounded-full border-4 border-red-300 animate-pulse-ring" />
        )}
      </button>

      {/* Status text */}
      <div className="text-center">
        <p className={`text-sm font-medium ${
          isRecording ? 'text-red-600' : 'text-gray-600'
        }`}>
          {isRecording ? 'Kaydediliyor...' : 'Basılı Tut'}
        </p>
        
        {isDisabled && (
          <p className="text-xs text-gray-500 mt-1">
            Lütfen bekleyin
          </p>
        )}
        
        {!isDisabled && !isRecording && (
          <p className="text-xs text-gray-500 mt-1">
            Konuşmak için basılı tutun
          </p>
        )}
      </div>

      {/* Visual feedback */}
      {isRecording && (
        <div className="flex items-center space-x-1">
          <div className="w-1 h-4 bg-red-500 rounded animate-pulse" style={{ animationDelay: '0ms' }} />
          <div className="w-1 h-6 bg-red-500 rounded animate-pulse" style={{ animationDelay: '150ms' }} />
          <div className="w-1 h-8 bg-red-500 rounded animate-pulse" style={{ animationDelay: '300ms' }} />
          <div className="w-1 h-6 bg-red-500 rounded animate-pulse" style={{ animationDelay: '450ms' }} />
          <div className="w-1 h-4 bg-red-500 rounded animate-pulse" style={{ animationDelay: '600ms' }} />
        </div>
      )}
    </div>
  )
}

export default MicButton