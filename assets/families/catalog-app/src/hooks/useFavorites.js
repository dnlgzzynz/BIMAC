import { useState, useEffect, useCallback } from 'react'

const STORAGE_KEY = 'bimac-family-favorites'

export function useFavorites() {
  const [favorites, setFavorites] = useState(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY)
      return stored ? JSON.parse(stored) : []
    } catch {
      return []
    }
  })

  // Persist to localStorage whenever favorites change
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(favorites))
    } catch (error) {
      console.error('Error saving favorites:', error)
    }
  }, [favorites])

  const addFavorite = useCallback((familyId) => {
    setFavorites(prev => {
      if (prev.includes(familyId)) return prev
      return [...prev, familyId]
    })
  }, [])

  const removeFavorite = useCallback((familyId) => {
    setFavorites(prev => prev.filter(id => id !== familyId))
  }, [])

  const toggleFavorite = useCallback((familyId) => {
    setFavorites(prev => {
      if (prev.includes(familyId)) {
        return prev.filter(id => id !== familyId)
      }
      return [...prev, familyId]
    })
  }, [])

  const isFavorite = useCallback((familyId) => {
    return favorites.includes(familyId)
  }, [favorites])

  const clearFavorites = useCallback(() => {
    setFavorites([])
  }, [])

  return {
    favorites,
    addFavorite,
    removeFavorite,
    toggleFavorite,
    isFavorite,
    clearFavorites,
    count: favorites.length
  }
}
