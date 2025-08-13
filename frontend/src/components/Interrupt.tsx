import React from 'react'
import { Square } from 'lucide-react'

interface InterruptProps {
  onClick: () => void
}

const Interrupt: React.FC<InterruptProps> = ({ onClick }) => {
  return (
    <div className="flex flex-col items-center space-y-2">
      {/* Interrupt button */}
      <button
        onClick={onClick}
        className="interrupt-button animate-fade-in"
        title="Konuşmayı durdur"
      >
        <Square className="w-8 h-8 fill-current" />
      </button>

      {/* Label */}
      <div className="text-center">
        <p className="text-sm font-medium text-red-600">
          DURDUR
        </p>
        <p className="text-xs text-gray-500">
          Konuşmayı durdur
        </p>
      </div>

      {/* Pulsing indicator */}
      <div className="absolute top-0 left-0 w-20 h-20 rounded-full border-4 border-red-300 animate-ping opacity-25" />
    </div>
  )
}

export default Interrupt