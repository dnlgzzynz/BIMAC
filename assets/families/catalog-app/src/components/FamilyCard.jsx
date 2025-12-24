import React from 'react'
import { FileBox, Tag, FolderOpen } from 'lucide-react'
import FavoriteButton from './FavoriteButton'
import { LODBadge } from './LODBadge'

const categoryColors = {
  'Arquitectura': 'category-arquitectura',
  'Estructura': 'category-estructura',
  'MEP': 'category-mep',
  'Mobiliario': 'category-mobiliario',
  'Anotacion': 'category-anotacion',
  'Muros Cortina': 'category-muros-cortina',
  'Membretes': 'category-anotacion',
}

function FamilyCard({ family, onClick, isFavorite, onToggleFavorite }) {
  const categoryClass = categoryColors[family.category] || 'bg-gray-100 text-gray-800'

  return (
    <div
      className="family-card p-4 flex flex-col h-full cursor-pointer relative"
      onClick={onClick}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => e.key === 'Enter' && onClick()}
    >
      {/* Favorite Button */}
      <div className="absolute top-2 right-2 z-10">
        <FavoriteButton
          isFavorite={isFavorite}
          onToggle={() => onToggleFavorite(family.id)}
          size="md"
        />
      </div>

      {/* Thumbnail */}
      <div className="bg-gray-100 rounded-lg h-32 flex items-center justify-center mb-3 overflow-hidden">
        {family.thumbnail ? (
          <img
            src={family.thumbnail}
            alt={family.name}
            className="w-full h-full object-cover"
          />
        ) : (
          <FileBox size={48} className="text-gray-400" />
        )}
      </div>

      {/* Content */}
      <div className="flex-1">
        <div className="flex items-start justify-between gap-2 mb-2">
          <h3 className="font-semibold text-gray-800 text-sm leading-tight">
            {family.name}
          </h3>
          <span className={`category-badge ${categoryClass} flex-shrink-0`}>
            {family.category}
          </span>
        </div>

        <p className="text-gray-600 text-xs mb-3 line-clamp-2">
          {family.description}
        </p>

        {/* Collection */}
        <div className="flex items-center gap-1 text-xs text-gray-500 mb-2">
          <FolderOpen size={12} />
          <span>{family.collection}</span>
        </div>

        {/* Tags */}
        {family.tags && family.tags.length > 0 && (
          <div className="flex flex-wrap gap-1 mt-auto">
            {family.tags.slice(0, 3).map(tag => (
              <span
                key={tag}
                className="inline-flex items-center gap-1 px-2 py-0.5 bg-gray-100 text-gray-600 rounded text-xs"
              >
                <Tag size={10} />
                {tag}
              </span>
            ))}
            {family.tags.length > 3 && (
              <span className="text-xs text-gray-400">+{family.tags.length - 3}</span>
            )}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="mt-3 pt-3 border-t border-gray-100 flex items-center justify-between text-xs">
        <span className="text-gray-500 truncate max-w-[60%]">{family.file}</span>
        {family.lod && (
          <LODBadge lod={family.lod} size="xs" />
        )}
      </div>
    </div>
  )
}

export default FamilyCard
