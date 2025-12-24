import React from 'react'

function FilterPanel({
  categories,
  collections,
  selectedCategory,
  selectedCollection,
  onCategoryChange,
  onCollectionChange
}) {
  return (
    <div className="bg-white rounded-lg shadow p-4 mb-6">
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
