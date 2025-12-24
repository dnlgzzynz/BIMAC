import React from 'react'
import { Star } from 'lucide-react'

function FilterPanel({
  categories,
  collections,
  selectedCategory,
  selectedCollection,
  onCategoryChange,
  onCollectionChange,
  showFavoritesOnly,
  onToggleFavoritesOnly,
  favoritesCount
}) {
  return (
    <div className="bg-white rounded-lg shadow p-4 mb-6">
      {/* Favorites Filter */}
      <div className="mb-4 pb-4 border-b border-gray-200">
        <button
          onClick={onToggleFavoritesOnly}
          className={`
            flex items-center gap-2 px-4 py-2 rounded-lg transition-all duration-200
            ${showFavoritesOnly
              ? 'bg-yellow-100 text-yellow-700 border-2 border-yellow-400'
              : 'bg-gray-100 text-gray-600 border-2 border-transparent hover:bg-yellow-50 hover:text-yellow-600'
            }
          `}
        >
          <Star
            size={18}
            fill={showFavoritesOnly ? 'currentColor' : 'none'}
            className="transition-all"
          />
          <span className="font-medium">
            Mostrar solo favoritos
          </span>
          {favoritesCount > 0 && (
            <span className={`
              px-2 py-0.5 rounded-full text-xs font-bold
              ${showFavoritesOnly ? 'bg-yellow-400 text-yellow-800' : 'bg-gray-200 text-gray-600'}
            `}>
              {favoritesCount}
            </span>
          )}
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Category Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Categoría
          </label>
          <div className="flex flex-wrap gap-2">
            {categories.map(category => (
              <button
                key={category}
                onClick={() => onCategoryChange(category)}
                className={`filter-button text-sm ${selectedCategory === category ? 'active' : ''}`}
              >
                {category === 'all' ? 'Todas' : category}
              </button>
            ))}
          </div>
        </div>

        {/* Collection Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Colección
          </label>
          <div className="flex flex-wrap gap-2">
            {collections.map(collection => (
              <button
                key={collection}
                onClick={() => onCollectionChange(collection)}
                className={`filter-button text-sm ${selectedCollection === collection ? 'active' : ''}`}
              >
                {collection === 'all' ? 'Todas' : collection}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default FilterPanel
