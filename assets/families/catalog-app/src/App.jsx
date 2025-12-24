import React, { useState, useMemo } from 'react'
import { Search, Grid, List, Filter, Download, ExternalLink, Star, Info, BarChart3 } from 'lucide-react'
import FamilyCard from './components/FamilyCard'
import FamilyTable from './components/FamilyTable'
import FamilyModal from './components/FamilyModal'
import ExportModal from './components/ExportModal'
import StatsPanel from './components/StatsPanel'
import ThemeToggle from './components/ThemeToggle'
import SearchBar from './components/SearchBar'
import FilterPanel from './components/FilterPanel'
import { LODLegend } from './components/LODBadge'
import { useFavorites } from './hooks/useFavorites'
import { useTheme } from './hooks/useTheme'
import familiesData from './data/families.json'

function App() {
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [selectedCollection, setSelectedCollection] = useState('all')
  const [viewMode, setViewMode] = useState('grid') // 'grid' or 'table'
  const [showFilters, setShowFilters] = useState(false)
  const [selectedFamily, setSelectedFamily] = useState(null)
  const [showFavoritesOnly, setShowFavoritesOnly] = useState(false)
  const [showLODLegend, setShowLODLegend] = useState(false)
  const [showExportModal, setShowExportModal] = useState(false)
  const [showStats, setShowStats] = useState(false)

  // Favorites hook
  const { favorites, toggleFavorite, isFavorite, count: favoritesCount } = useFavorites()

  // Theme hook
  const { isDark, toggleTheme } = useTheme()

  // Get unique categories and collections
  const categories = useMemo(() => {
    const cats = [...new Set(familiesData.map(f => f.category))]
    return ['all', ...cats.sort()]
  }, [])

  const collections = useMemo(() => {
    const cols = [...new Set(familiesData.map(f => f.collection))]
    return ['all', ...cols.sort()]
  }, [])

  // Filter families
  const filteredFamilies = useMemo(() => {
    return familiesData.filter(family => {
      const matchesSearch =
        family.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        family.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
        family.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()))

      const matchesCategory = selectedCategory === 'all' || family.category === selectedCategory
      const matchesCollection = selectedCollection === 'all' || family.collection === selectedCollection
      const matchesFavorites = !showFavoritesOnly || isFavorite(family.id)

      return matchesSearch && matchesCategory && matchesCollection && matchesFavorites
    })
  }, [searchTerm, selectedCategory, selectedCollection, showFavoritesOnly, favorites])

  // Stats
  const stats = useMemo(() => ({
    total: familiesData.length,
    filtered: filteredFamilies.length,
    categories: categories.length - 1,
    collections: collections.length - 1
  }), [filteredFamilies, categories, collections])

  return (
    <div className={`min-h-screen transition-colors duration-300 ${isDark ? 'dark bg-gray-900' : 'bg-gray-50'}`}>
      {/* Header */}
      <header className={`py-6 px-4 transition-colors duration-300 ${isDark ? 'bg-gray-800' : 'bg-bimac-primary'} text-white`}>
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              {/* Logo */}
              <img
                src="/images/bimac-logo.svg"
                alt="BIMAC Logo"
                className="w-12 h-12 md:w-14 md:h-14"
              />
              <div>
                <h1 className="text-2xl md:text-3xl font-bold">Catálogo de Familias Revit</h1>
                <p className={`mt-1 ${isDark ? 'text-gray-400' : 'text-bimac-light'}`}>BIMAC Studio - Biblioteca BIM</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              {/* Theme Toggle */}
              <ThemeToggle isDark={isDark} onToggle={toggleTheme} size="sm" />
              {/* Stats badges - hidden on mobile */}
              <div className="hidden md:flex items-center gap-4 text-sm">
                <span className={`px-3 py-1 rounded-full ${isDark ? 'bg-gray-700' : 'bg-bimac-secondary'}`}>
                  {stats.total} familias
                </span>
                <span className={`px-3 py-1 rounded-full ${isDark ? 'bg-gray-700' : 'bg-bimac-secondary'}`}>
                  {stats.categories} categorías
                </span>
                {favoritesCount > 0 && (
                  <span className="bg-yellow-400 text-yellow-900 px-3 py-1 rounded-full flex items-center gap-1">
                    <Star size={14} fill="currentColor" />
                    {favoritesCount} favoritos
                  </span>
                )}
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-6">
        {/* Search and Controls */}
        <div className="flex flex-col md:flex-row gap-4 mb-6">
          <div className="flex-1">
            <SearchBar
              value={searchTerm}
              onChange={setSearchTerm}
              placeholder="Buscar familias por nombre, descripción o tags..."
            />
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setShowFilters(!showFilters)}
              className={`filter-button flex items-center gap-2 ${showFilters ? 'active' : ''}`}
            >
              <Filter size={18} />
              Filtros
            </button>
            <button
              onClick={() => setViewMode('grid')}
              className={`filter-button ${viewMode === 'grid' ? 'active' : ''}`}
              title="Vista de tarjetas"
            >
              <Grid size={18} />
            </button>
            <button
              onClick={() => setViewMode('table')}
              className={`filter-button ${viewMode === 'table' ? 'active' : ''}`}
              title="Vista de tabla"
            >
              <List size={18} />
            </button>
            <button
              onClick={() => setShowExportModal(true)}
              className="filter-button flex items-center gap-2"
              title="Exportar lista"
            >
              <Download size={18} />
              <span className="hidden sm:inline">Exportar</span>
            </button>
            <button
              onClick={() => setShowLODLegend(!showLODLegend)}
              className={`filter-button flex items-center gap-2 ${showLODLegend ? 'active' : ''}`}
              title="Leyenda LOD"
            >
              <Info size={18} />
              <span className="hidden sm:inline">LOD</span>
            </button>
            <button
              onClick={() => setShowStats(!showStats)}
              className={`filter-button flex items-center gap-2 ${showStats ? 'active' : ''}`}
              title="Estadísticas"
            >
              <BarChart3 size={18} />
              <span className="hidden sm:inline">Stats</span>
            </button>
          </div>
        </div>

        {/* Stats Panel */}
        {showStats && (
          <StatsPanel
            families={filteredFamilies}
            allFamilies={familiesData}
            favoritesCount={favoritesCount}
          />
        )}

        {/* LOD Legend */}
        {showLODLegend && (
          <div className="mb-6">
            <LODLegend />
          </div>
        )}

        {/* Filters */}
        {showFilters && (
          <FilterPanel
            categories={categories}
            collections={collections}
            selectedCategory={selectedCategory}
            selectedCollection={selectedCollection}
            onCategoryChange={setSelectedCategory}
            onCollectionChange={setSelectedCollection}
            showFavoritesOnly={showFavoritesOnly}
            onToggleFavoritesOnly={() => setShowFavoritesOnly(!showFavoritesOnly)}
            favoritesCount={favoritesCount}
          />
        )}

        {/* Results count */}
        <div className="mb-4 text-gray-600">
          Mostrando <span className="font-semibold text-bimac-primary">{stats.filtered}</span> de {stats.total} familias
          {showFavoritesOnly && (
            <span className="ml-2 inline-flex items-center gap-1 text-yellow-600">
              <Star size={14} fill="currentColor" />
              Solo favoritos
            </span>
          )}
          {(selectedCategory !== 'all' || selectedCollection !== 'all' || searchTerm || showFavoritesOnly) && (
            <button
              onClick={() => {
                setSearchTerm('')
                setSelectedCategory('all')
                setSelectedCollection('all')
                setShowFavoritesOnly(false)
              }}
              className="ml-2 text-bimac-accent hover:underline"
            >
              Limpiar filtros
            </button>
          )}
        </div>

        {/* Results */}
        {viewMode === 'grid' ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {filteredFamilies.map(family => (
              <FamilyCard
                key={family.id}
                family={family}
                onClick={() => setSelectedFamily(family)}
                isFavorite={isFavorite(family.id)}
                onToggleFavorite={toggleFavorite}
              />
            ))}
          </div>
        ) : (
          <FamilyTable
            families={filteredFamilies}
            onFamilyClick={setSelectedFamily}
            isFavorite={isFavorite}
            onToggleFavorite={toggleFavorite}
          />
        )}

        {/* No results */}
        {filteredFamilies.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500 text-lg">
              {showFavoritesOnly && favoritesCount === 0
                ? 'No tienes familias en favoritos aún.'
                : 'No se encontraron familias con los filtros seleccionados.'}
            </p>
            <button
              onClick={() => {
                setSearchTerm('')
                setSelectedCategory('all')
                setSelectedCollection('all')
                setShowFavoritesOnly(false)
              }}
              className="mt-4 text-bimac-accent hover:underline"
            >
              Limpiar filtros
            </button>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className={`py-6 px-4 mt-12 transition-colors duration-300 ${isDark ? 'bg-gray-950' : 'bg-bimac-dark'} text-gray-400`}>
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col md:flex-row items-center justify-center gap-4">
            <img
              src="/images/bimac-logo.svg"
              alt="BIMAC Logo"
              className="w-10 h-10 opacity-80"
            />
            <div className="text-center">
              <p>
                <a href="https://bimacstudio.com" className={`hover:text-bimac-accent ${isDark ? 'text-gray-200' : 'text-white'}`} target="_blank" rel="noopener noreferrer">
                  BIMAC Studio
                </a>
                {' '}&copy; {new Date().getFullYear()} - Catálogo de Familias Revit
              </p>
              <p className="text-sm mt-1">
                <a href="mailto:arq.dnlgzz@bimacstudio.com" className={`hover:${isDark ? 'text-gray-200' : 'text-white'}`}>
                  arq.dnlgzz@bimacstudio.com
                </a>
              </p>
            </div>
          </div>
        </div>
      </footer>

      {/* Family Detail Modal */}
      {selectedFamily && (
        <FamilyModal
          family={selectedFamily}
          onClose={() => setSelectedFamily(null)}
          isFavorite={isFavorite(selectedFamily.id)}
          onToggleFavorite={toggleFavorite}
        />
      )}

      {/* Export Modal */}
      <ExportModal
        isOpen={showExportModal}
        onClose={() => setShowExportModal(false)}
        families={filteredFamilies}
        favoritesCount={favoritesCount}
        totalCount={stats.total}
      />
    </div>
  )
}

export default App
