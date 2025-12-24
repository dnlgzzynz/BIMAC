import React from 'react'
import { FileBox, Tag } from 'lucide-react'
import FavoriteButton from './FavoriteButton'

const categoryColors = {
  'Arquitectura': 'category-arquitectura',
  'Estructura': 'category-estructura',
  'MEP': 'category-mep',
  'Mobiliario': 'category-mobiliario',
  'Anotacion': 'category-anotacion',
  'Muros Cortina': 'category-muros-cortina',
  'Membretes': 'category-anotacion',
}

function FamilyTable({ families, onFamilyClick, isFavorite, onToggleFavorite }) {
  return (
    <div className="bg-white rounded-lg shadow overflow-hidden">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-2 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider w-12">
                Fav
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Familia
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Categoría
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Colección
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider hidden md:table-cell">
                Tags
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider hidden lg:table-cell">
                LOD
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {families.map(family => {
              const categoryClass = categoryColors[family.category] || 'bg-gray-100 text-gray-800'

              return (
                <tr
                  key={family.id}
                  className="hover:bg-gray-50 cursor-pointer"
                  onClick={() => onFamilyClick(family)}
                >
                  <td className="px-2 py-3 text-center" onClick={e => e.stopPropagation()}>
                    <FavoriteButton
                      isFavorite={isFavorite(family.id)}
                      onToggle={() => onToggleFavorite(family.id)}
                      size="sm"
                    />
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-3">
                      <div className="flex-shrink-0 w-10 h-10 bg-gray-100 rounded flex items-center justify-center">
                        {family.thumbnail ? (
                          <img
                            src={family.thumbnail}
                            alt={family.name}
                            className="w-full h-full object-cover rounded"
                          />
                        ) : (
                          <FileBox size={20} className="text-gray-400" />
                        )}
                      </div>
                      <div>
                        <div className="font-medium text-gray-900 text-sm">
                          {family.name}
                        </div>
                        <div className="text-gray-500 text-xs">
                          {family.file}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`category-badge ${categoryClass}`}>
                      {family.category}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-600">
                    {family.collection}
                  </td>
                  <td className="px-4 py-3 hidden md:table-cell">
                    <div className="flex flex-wrap gap-1">
                      {family.tags.slice(0, 2).map(tag => (
                        <span
                          key={tag}
                          className="inline-flex items-center gap-1 px-2 py-0.5 bg-gray-100 text-gray-600 rounded text-xs"
                        >
                          {tag}
                        </span>
                      ))}
                      {family.tags.length > 2 && (
                        <span className="text-xs text-gray-400">+{family.tags.length - 2}</span>
                      )}
                    </div>
                  </td>
                  <td className="px-4 py-3 hidden lg:table-cell">
                    {family.lod && (
                      <span className="bg-bimac-light text-bimac-primary px-2 py-0.5 rounded text-xs font-medium">
                        {family.lod}
                      </span>
                    )}
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default FamilyTable
