import React from 'react'
import { User, Settings, CreditCard, HelpCircle, Router } from 'lucide-react'

interface PersonaBadgeProps {
  persona: string
}

const PersonaBadge: React.FC<PersonaBadgeProps> = ({ persona }) => {
  const getPersonaConfig = (persona: string) => {
    switch (persona) {
      case 'RouterAgent':
        return {
          label: 'Router',
          icon: <Router className="w-4 h-4" />,
          className: 'persona-router',
          description: 'Genel yönlendirme'
        }
      case 'TechAgent':
        return {
          label: 'Teknik',
          icon: <Settings className="w-4 h-4" />,
          className: 'persona-tech',
          description: 'Teknik destek'
        }
      case 'PlanAgent':
        return {
          label: 'Paket',
          icon: <User className="w-4 h-4" />,
          className: 'persona-plan',
          description: 'Paket yönetimi'
        }
      case 'BillingAgent':
        return {
          label: 'Fatura',
          icon: <CreditCard className="w-4 h-4" />,
          className: 'persona-billing',
          description: 'Fatura ve ödeme'
        }
      case 'FAQAgent':
        return {
          label: 'Bilgi',
          icon: <HelpCircle className="w-4 h-4" />,
          className: 'persona-faq',
          description: 'Genel bilgi'
        }
      default:
        return {
          label: persona,
          icon: <User className="w-4 h-4" />,
          className: 'persona-router',
          description: 'Bilinmiyor'
        }
    }
  }

  const config = getPersonaConfig(persona)

  return (
    <div className="relative group">
      <div className={`persona-badge ${config.className} animate-fade-in`}>
        {config.icon}
        <span className="ml-1 font-medium">{config.label}</span>
      </div>
      
      {/* Tooltip */}
      <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-2 py-1 bg-gray-900 text-white text-xs rounded whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none">
        {config.description}
        <div className="absolute top-full left-1/2 transform -translate-x-1/2 border-4 border-transparent border-t-gray-900"></div>
      </div>
    </div>
  )
}

export default PersonaBadge