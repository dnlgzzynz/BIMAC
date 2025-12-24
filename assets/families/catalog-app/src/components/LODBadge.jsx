import React, { useState } from 'react'
import { Info } from 'lucide-react'

// LOD definitions with colors and descriptions
const lodConfig = {
  100: {
    label: 'LOD 100',
    name: 'Conceptual',
    color: 'bg-gray-200 text-gray-700 border-gray-300',
    dotColor: 'bg-gray-400',
    description: 'Representación conceptual. Símbolo o representación genérica.'
  },
  200: {
    label: 'LOD 200',
    name: 'Esquemático',
    color: 'bg-blue-100 text-blue-700 border-blue-300',
    dotColor: 'bg-blue-500',
    description: 'Elemento genérico con cantidades aproximadas, tamaño, forma y ubicación.'
  },
  300: {
    label: 'LOD 300',
    name: 'Diseño',
    color: 'bg-green-100 text-green-700 border-green-300',
    dotColor: 'bg-green-500',
    description: 'Elemento específico con cantidades, tamaño, forma y ubicación precisos.'
  },
  350: {
    label: 'LOD 350',
    name: 'Construcción',
    color: 'bg-yellow-100 text-yellow-700 border-yellow-400',
    dotColor: 'bg-yellow-500',
    description: 'Detalle para coordinación entre disciplinas e interfaces.'
  },
  400: {
    label: 'LOD 400',
    name: 'Fabricación',
    color: 'bg-orange-100 text-orange-700 border-orange-400',
    dotColor: 'bg-orange-500',
    description: 'Detalle suficiente para fabricación y ensamblaje.'
  },
  500: {
    label: 'LOD 500',
    name: 'As-Built',
    color: 'bg-red-100 text-red-700 border-red-400',
    dotColor: 'bg-red-500',
    description: 'Verificado en campo. Representación exacta de lo construido.'
  }
}

// Get LOD config with fallback
function getLodConfig(lod) {
  const lodNum = parseInt(lod)
  return lodConfig[lodNum] || {
    label: `LOD ${lod}`,
    name: 'Personalizado',
    color: 'bg-purple-100 text-purple-700 border-purple-300',
    dotColor: 'bg-purple-500',
    description: 'Nivel de desarrollo personalizado.'
  }
}

// Simple badge without tooltip
export function LODBadgeSimple({ lod, size = 'sm' }) {
  if (!lod) return null

  const config = getLodConfig(lod)
  const sizeClasses = {
    xs: 'text-xs px-1.5 py-0.5',
    sm: 'text-xs px-2 py-0.5',
    md: 'text-sm px-2.5 py-1',
    lg: 'text-base px-3 py-1.5'
  }

  return (
    <span className={`
      inline-flex items-center gap-1.5 rounded-full border font-medium
      ${config.color} ${sizeClasses[size]}
    `}>
      <span className={`w-2 h-2 rounded-full ${config.dotColor}`}></span>
      LOD {lod}
    </span>
  )
}

// Badge with tooltip showing full info
export function LODBadge({ lod, size = 'sm', showTooltip = true }) {
  const [isHovered, setIsHovered] = useState(false)

  if (!lod) return null

  const config = getLodConfig(lod)
  const sizeClasses = {
    xs: 'text-xs px-1.5 py-0.5',
    sm: 'text-xs px-2 py-0.5',
    md: 'text-sm px-2.5 py-1',
    lg: 'text-base px-3 py-1.5'
  }

  return (
    <div className="relative inline-block">
      <span
        className={`
          inline-flex items-center gap-1.5 rounded-full border font-medium cursor-help
          ${config.color} ${sizeClasses[size]}
          transition-all duration-200
        `}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
      >
        <span className={`w-2 h-2 rounded-full ${config.dotColor}`}></span>
        LOD {lod}
      </span>

      {/* Tooltip */}
      {showTooltip && isHovered && (
        <div className="absolute z-50 bottom-full left-1/2 transform -translate-x-1/2 mb-2 w-64">
          <div className="bg-gray-900 text-white text-sm rounded-lg shadow-xl p-3">
            <div className="flex items-center gap-2 mb-1">
              <span className={`w-3 h-3 rounded-full ${config.dotColor}`}></span>
              <span className="font-semibold">{config.label} - {config.name}</span>
            </div>
            <p className="text-gray-300 text-xs leading-relaxed">
              {config.description}
            </p>
            {/* Arrow */}
            <div className="absolute top-full left-1/2 transform -translate-x-1/2 -mt-px">
              <div className="border-8 border-transparent border-t-gray-900"></div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

// LOD Legend component for reference
export function LODLegend({ compact = false }) {
  const lods = [100, 200, 300, 350, 400, 500]

  if (compact) {
    return (
      <div className="flex flex-wrap gap-2">
        {lods.map(lod => {
          const config = getLodConfig(lod)
          return (
            <div
              key={lod}
              className={`inline-flex items-center gap-1 px-2 py-1 rounded text-xs ${config.color} border`}
              title={`${config.name}: ${config.description}`}
            >
              <span className={`w-2 h-2 rounded-full ${config.dotColor}`}></span>
              {lod}
            </div>
          )
        })}
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4">
      <h4 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
        <Info size={16} />
        Niveles de Desarrollo (LOD)
      </h4>
      <div className="space-y-2">
        {lods.map(lod => {
          const config = getLodConfig(lod)
          return (
            <div key={lod} className="flex items-start gap-3">
              <span className={`
                inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full border text-xs font-medium flex-shrink-0
                ${config.color}
              `}>
                <span className={`w-2 h-2 rounded-full ${config.dotColor}`}></span>
                {lod}
              </span>
              <div className="flex-1 min-w-0">
                <span className="font-medium text-gray-700 text-sm">{config.name}</span>
                <p className="text-gray-500 text-xs">{config.description}</p>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default LODBadge
