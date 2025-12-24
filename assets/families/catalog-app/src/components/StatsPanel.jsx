import React, { useMemo } from 'react'
import {
  BarChart3,
  PieChart,
  Layers,
  FolderOpen,
  Star,
  TrendingUp,
  Box
} from 'lucide-react'

// Category colors matching the app theme
const categoryConfig = {
  'Arquitectura': { color: 'bg-blue-500', lightColor: 'bg-blue-100' },
  'Estructura': { color: 'bg-gray-500', lightColor: 'bg-gray-100' },
  'MEP': { color: 'bg-green-500', lightColor: 'bg-green-100' },
  'Mobiliario': { color: 'bg-yellow-500', lightColor: 'bg-yellow-100' },
  'Anotacion': { color: 'bg-purple-500', lightColor: 'bg-purple-100' },
  'Muros Cortina': { color: 'bg-cyan-500', lightColor: 'bg-cyan-100' },
  'Membretes': { color: 'bg-pink-500', lightColor: 'bg-pink-100' }
}

// LOD colors
const lodConfig = {
  100: { color: 'bg-gray-400', name: 'Conceptual' },
  200: { color: 'bg-blue-500', name: 'Esquemático' },
  300: { color: 'bg-green-500', name: 'Diseño' },
  350: { color: 'bg-yellow-500', name: 'Construcción' },
  400: { color: 'bg-orange-500', name: 'Fabricación' },
  500: { color: 'bg-red-500', name: 'As-Built' }
}

// Progress bar component
function ProgressBar({ value, max, color = 'bg-bimac-primary', label, count }) {
  const percentage = max > 0 ? (value / max) * 100 : 0

  return (
    <div className="mb-3">
      <div className="flex justify-between items-center mb-1">
        <span className="text-sm text-gray-700">{label}</span>
        <span className="text-sm font-medium text-gray-900">{count}</span>
      </div>
      <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
        <div
          className={`h-full ${color} rounded-full transition-all duration-500`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  )
}

// Stat card component
function StatCard({ icon: Icon, title, value, subtitle, color = 'text-bimac-primary' }) {
  return (
    <div className="bg-white rounded-lg shadow p-4">
      <div className="flex items-center gap-3">
        <div className={`p-2 rounded-lg bg-bimac-light ${color}`}>
          <Icon size={20} />
        </div>
        <div>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
          <p className="text-sm text-gray-500">{title}</p>
          {subtitle && (
            <p className="text-xs text-gray-400">{subtitle}</p>
          )}
        </div>
      </div>
    </div>
  )
}

// Mini donut chart (CSS-based)
function MiniDonut({ segments, size = 80 }) {
  const total = segments.reduce((sum, s) => sum + s.value, 0)
  let cumulativePercent = 0

  const gradientStops = segments.map(segment => {
    const start = cumulativePercent
    const percent = total > 0 ? (segment.value / total) * 100 : 0
    cumulativePercent += percent
    return `${segment.color} ${start}% ${cumulativePercent}%`
  }).join(', ')

  return (
    <div
      className="rounded-full relative"
      style={{
        width: size,
        height: size,
        background: `conic-gradient(${gradientStops})`,
      }}
    >
      <div
        className="absolute bg-white rounded-full"
        style={{
          width: size * 0.6,
          height: size * 0.6,
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)'
        }}
      />
    </div>
  )
}

function StatsPanel({ families, allFamilies, favoritesCount }) {
  // Calculate statistics
  const stats = useMemo(() => {
    // By category
    const byCategory = {}
    families.forEach(f => {
      byCategory[f.category] = (byCategory[f.category] || 0) + 1
    })

    // By collection
    const byCollection = {}
    families.forEach(f => {
      byCollection[f.collection] = (byCollection[f.collection] || 0) + 1
    })

    // By LOD
    const byLOD = {}
    families.forEach(f => {
      if (f.lod) {
        byLOD[f.lod] = (byLOD[f.lod] || 0) + 1
      }
    })

    // With/without LOD
    const withLOD = families.filter(f => f.lod).length
    const withoutLOD = families.length - withLOD

    // Sort by count
    const sortedCategories = Object.entries(byCategory)
      .sort((a, b) => b[1] - a[1])
    const sortedCollections = Object.entries(byCollection)
      .sort((a, b) => b[1] - a[1])
    const sortedLOD = Object.entries(byLOD)
      .sort((a, b) => parseInt(a[0]) - parseInt(b[0]))

    return {
      total: families.length,
      allTotal: allFamilies.length,
      categories: sortedCategories,
      collections: sortedCollections,
      lod: sortedLOD,
      withLOD,
      withoutLOD,
      categoryCount: Object.keys(byCategory).length,
      collectionCount: Object.keys(byCollection).length
    }
  }, [families, allFamilies])

  // Max value for progress bars
  const maxCategoryCount = stats.categories[0]?.[1] || 1
  const maxCollectionCount = stats.collections[0]?.[1] || 1
  const maxLODCount = Math.max(...stats.lod.map(l => l[1]), 1)

  // Donut chart data for categories
  const categoryDonutData = stats.categories.map(([cat, count]) => ({
    value: count,
    color: categoryConfig[cat]?.color.replace('bg-', '') || 'gray-500'
  }))

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
      <div className="flex items-center gap-2 mb-6">
        <BarChart3 size={24} className="text-bimac-primary" />
        <h3 className="text-lg font-semibold text-gray-800">Estadísticas del Catálogo</h3>
        {stats.total < stats.allTotal && (
          <span className="text-sm text-gray-500 ml-2">
            (mostrando {stats.total} de {stats.allTotal} familias)
          </span>
        )}
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <StatCard
          icon={Box}
          title="Total Familias"
          value={stats.total}
          subtitle={stats.total !== stats.allTotal ? `de ${stats.allTotal}` : null}
        />
        <StatCard
          icon={FolderOpen}
          title="Categorías"
          value={stats.categoryCount}
          color="text-blue-600"
        />
        <StatCard
          icon={Layers}
          title="Colecciones"
          value={stats.collectionCount}
          color="text-green-600"
        />
        <StatCard
          icon={Star}
          title="Favoritos"
          value={favoritesCount}
          color="text-yellow-600"
        />
      </div>

      {/* Detailed Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* By Category */}
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-4">
            <PieChart size={18} className="text-bimac-primary" />
            <h4 className="font-medium text-gray-800">Por Categoría</h4>
          </div>
          <div className="space-y-1">
            {stats.categories.map(([category, count]) => {
              const config = categoryConfig[category] || { color: 'bg-gray-500' }
              return (
                <ProgressBar
                  key={category}
                  label={category}
                  count={count}
                  value={count}
                  max={maxCategoryCount}
                  color={config.color}
                />
              )
            })}
            {stats.categories.length === 0 && (
              <p className="text-sm text-gray-500 text-center py-4">Sin datos</p>
            )}
          </div>
        </div>

        {/* By LOD */}
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-4">
            <TrendingUp size={18} className="text-bimac-primary" />
            <h4 className="font-medium text-gray-800">Por LOD</h4>
          </div>
          <div className="space-y-1">
            {stats.lod.map(([lod, count]) => {
              const config = lodConfig[lod] || { color: 'bg-purple-500', name: `LOD ${lod}` }
              return (
                <ProgressBar
                  key={lod}
                  label={`LOD ${lod} - ${config.name}`}
                  count={count}
                  value={count}
                  max={maxLODCount}
                  color={config.color}
                />
              )
            })}
            {stats.lod.length === 0 && (
              <p className="text-sm text-gray-500 text-center py-4">Sin datos de LOD</p>
            )}
          </div>
          {/* LOD Coverage */}
          {stats.total > 0 && (
            <div className="mt-4 pt-4 border-t border-gray-200">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Cobertura LOD:</span>
                <span className="font-medium text-gray-800">
                  {Math.round((stats.withLOD / stats.total) * 100)}%
                </span>
              </div>
              <div className="mt-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className="h-full bg-bimac-primary rounded-full"
                  style={{ width: `${(stats.withLOD / stats.total) * 100}%` }}
                />
              </div>
              <p className="text-xs text-gray-500 mt-1">
                {stats.withLOD} con LOD / {stats.withoutLOD} sin LOD
              </p>
            </div>
          )}
        </div>

        {/* By Collection */}
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-4">
            <FolderOpen size={18} className="text-bimac-primary" />
            <h4 className="font-medium text-gray-800">Por Colección</h4>
          </div>
          <div className="space-y-1 max-h-64 overflow-y-auto">
            {stats.collections.slice(0, 8).map(([collection, count]) => (
              <ProgressBar
                key={collection}
                label={collection}
                count={count}
                value={count}
                max={maxCollectionCount}
                color="bg-bimac-secondary"
              />
            ))}
            {stats.collections.length > 8 && (
              <p className="text-xs text-gray-500 text-center pt-2">
                +{stats.collections.length - 8} más colecciones
              </p>
            )}
            {stats.collections.length === 0 && (
              <p className="text-sm text-gray-500 text-center py-4">Sin datos</p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default StatsPanel
