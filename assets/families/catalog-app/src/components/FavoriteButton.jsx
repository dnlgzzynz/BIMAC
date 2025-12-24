import React from 'react'

export default function FavoriteButton({
  isFavorite,
  onToggle,
  size = 'md',
  showLabel = false,
  className = ''
}) {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-5 h-5',
    lg: 'w-6 h-6'
  }

  const handleClick = (e) => {
    e.stopPropagation() // Prevent triggering parent click events
    onToggle()
  }

  return (
    <button
      onClick={handleClick}
      className={`
        inline-flex items-center gap-1.5 transition-all duration-200
        ${isFavorite
          ? 'text-yellow-500 hover:text-yellow-600'
          : 'text-gray-400 hover:text-yellow-500'
        }
        ${className}
      `}
      title={isFavorite ? 'Quitar de favoritos' : 'Agregar a favoritos'}
      aria-label={isFavorite ? 'Quitar de favoritos' : 'Agregar a favoritos'}
    >
      <svg
        className={`${sizeClasses[size]} transition-transform duration-200 ${isFavorite ? 'scale-110' : 'hover:scale-110'}`}
        fill={isFavorite ? 'currentColor' : 'none'}
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"
        />
      </svg>
      {showLabel && (
        <span className="text-sm font-medium">
          {isFavorite ? 'Favorito' : 'Agregar'}
        </span>
      )}
    </button>
  )
}
