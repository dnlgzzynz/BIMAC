import React from 'react'
import { Sun, Moon } from 'lucide-react'

function ThemeToggle({ isDark, onToggle, size = 'md' }) {
  const sizeClasses = {
    sm: 'w-8 h-8',
    md: 'w-10 h-10',
    lg: 'w-12 h-12'
  }

  const iconSize = {
    sm: 16,
    md: 20,
    lg: 24
  }

  return (
    <button
      onClick={onToggle}
      className={`
        ${sizeClasses[size]}
        flex items-center justify-center
        rounded-full
        transition-all duration-300 ease-in-out
        ${isDark
          ? 'bg-gray-700 text-yellow-400 hover:bg-gray-600'
          : 'bg-bimac-light text-bimac-primary hover:bg-bimac-orange-100'
        }
      `}
      title={isDark ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro'}
      aria-label={isDark ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro'}
    >
      <div className="relative">
        {/* Sun icon */}
        <Sun
          size={iconSize[size]}
          className={`
            absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2
            transition-all duration-300
            ${isDark ? 'opacity-0 rotate-90 scale-0' : 'opacity-100 rotate-0 scale-100'}
          `}
        />
        {/* Moon icon */}
        <Moon
          size={iconSize[size]}
          className={`
            transition-all duration-300
            ${isDark ? 'opacity-100 rotate-0 scale-100' : 'opacity-0 -rotate-90 scale-0'}
          `}
        />
      </div>
    </button>
  )
}

export default ThemeToggle
