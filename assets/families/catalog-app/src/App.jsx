import React, { useState, useMemo } from 'react'
import { Search, Grid, List, Filter, Download, ExternalLink } from 'lucide-react'
import FamilyCard from './components/FamilyCard'
import FamilyTable from './components/FamilyTable'
import SearchBar from './components/SearchBar'
import FilterPanel from './components/FilterPanel'
import familiesData from './data/families.json'

function App() {
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [selectedCollection, setSelectedCollection] = useState('all')
  const [viewMode, setViewMode] = useState('grid') // 'grid' or 'table'
  const [showFilters, setShowFilters] = useState(false)

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

      return matchesSearch && matchesCategory && matchesCollection
    })
  }, [searchTerm, selectedCategory, selectedCollection])

  // Stats
  const stats = useMemo(() => ({
    total: familiesData.length,
    filtered: filteredFamilies.length,
    categories: categories.length - 1,
    collections: collections.length - 1
  }), [filteredFamilies, categories, collections])

  // Export filtered list
  const handleExport = () => {
    const csv = [
      ['Nombre', 'Categoría', 'Colección', 'Descripción', 'Tags'].join(','),
      ...filteredFamilies.map(f =>
        [f.name, f.category, f.collection, `"${f.description}"`, `"${f.tags.join(', ')}"`].join(',')
      )
    ].join('\n')

    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'bimac-familias.csv'
    a.click()
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-bimac-primary text-white py-6 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl md:text-3xl font-bold">Catálogo de Familias Revit</h1>
              <p className="text-bimac-light mt-1">BIMAC Studio - Biblioteca BIM</p>
            </div>
            <div className="hidden md:flex items-center gap-4 text-sm">
              <span className="bg-bimac-secondary px-3 py-1 rounded-full">
                {stats.total} familias
              </span>
              <span className="bg-bimac-secondary px-3 py-1 rounded-full">
                {stats.categories} categorías
              </span>
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
              onClick={handleExport}
              className="filter-button flex items-center gap-2"
              title="Exportar lista"
            >
              <Download size={18} />
            </button>
          </div>
        </div>

        {/* Filters */}
        {showFilters && (
          <FilterPanel
            categories={categories}
            collections={collections}
            selectedCategory={selectedCategory}
            selectedCollection={selectedCollection}
            onCategoryChange={setSelectedCategory}
            onCollectionChange={setSelectedCollection}
          />
        )}

        {/* Results count */}
        <div className="mb-4 text-gray-600">
          Mostrando <span className="font-semibold text-bimac-primary">{stats.filtered}</span> de {stats.total} familias
          {(selectedCategory !== 'all' || selectedCollection !== 'all' || searchTerm) && (
            <button
              onClick={() => {
                setSearchTerm('')
                setSelectedCategory('all')
                setSelectedCollection('all')
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
              <FamilyCard key={family.id} family={family} />
            ))}
          </div>
        ) : (
          <FamilyTable families={filteredFamilies} />
        )}

        {/* No results */}
        {filteredFamilies.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500 text-lg">No se encontraron familias con los filtros seleccionados.</p>
            <button
              onClick={() => {
                setSearchTerm('')
                setSelectedCategory('all')
                setSelectedCollection('all')
              }}
              className="mt-4 text-bimac-accent hover:underline"
            >
              Limpiar filtros
            </button>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-bimac-dark text-gray-400 py-6 px-4 mt-12">
        <div className="max-w-7xl mx-auto text-center">
          <p>
            <a href="https://bimacstudio.com" className="text-white hover:text-bimac-accent" target="_blank" rel="noopener noreferrer">
              BIMAC Studio
            </a>
            {' '}&copy; {new Date().getFullYear()} - Catálogo de Familias Revit
          </p>
          <p className="text-sm mt-2">
            <a href="mailto:arq.dnlgzz@bimacstudio.com" className="hover:text-white">
              arq.dnlgzz@bimacstudio.com
            </a>
          </p>
        </div>
      </footer>
    </div>
  )
}

export default App
