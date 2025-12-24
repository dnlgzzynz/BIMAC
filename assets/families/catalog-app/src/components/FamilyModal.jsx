import React, { useEffect } from 'react'
import {
  X,
  FileBox,
  Tag,
  FolderOpen,
  Layers,
  Download,
  Copy,
  Check,
  Box,
  FileType,
  Calendar,
  User
} from 'lucide-react'

const categoryColors = {
  'Arquitectura': 'category-arquitectura',
  'Estructura': 'category-estructura',
  'MEP': 'category-mep',
  'Mobiliario': 'category-mobiliario',
  'Anotacion': 'category-anotacion',
  'Muros Cortina': 'category-muros-cortina',
  'Membretes': 'category-anotacion',
}

function FamilyModal({ family, onClose }) {
  const [copied, setCopied] = React.useState(false)
  const categoryClass = categoryColors[family.category] || 'bg-gray-100 text-gray-800'

  // Close on ESC key
  useEffect(() => {
    const handleEsc = (e) => {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', handleEsc)
    return () => window.removeEventListener('keydown', handleEsc)
  }, [onClose])

  // Prevent body scroll when modal is open
  useEffect(() => {
    document.body.style.overflow = 'hidden'
    return () => {
      document.body.style.overflow = 'unset'
    }
  }, [])

  const copyFileName = () => {
    navigator.clipboard.writeText(family.file)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const handleBackdropClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose()
    }
  }

  return (
    <div
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      onClick={handleBackdropClick}
    >
      <div className="bg-white rounded-xl shadow-2xl max-w-3xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="bg-bimac-primary text-white px-6 py-4 flex items-center justify-between">
          <h2 className="text-xl font-semibold truncate pr-4">{family.name}</h2>
          <button
            onClick={onClose}
            className="p-1 hover:bg-white hover:bg-opacity-20 rounded-full transition-colors"
          >
            <X size={24} />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Left Column - Image and Actions */}
            <div>
              {/* Thumbnail */}
              <div className="bg-gray-100 rounded-lg h-64 flex items-center justify-center mb-4 overflow-hidden">
                {family.thumbnail ? (
                  <img
                    src={family.thumbnail}
                    alt={family.name}
                    className="w-full h-full object-contain"
                  />
                ) : (
                  <div className="text-center">
                    <FileBox size={64} className="text-gray-400 mx-auto mb-2" />
                    <span className="text-gray-400 text-sm">Sin preview</span>
                  </div>
                )}
              </div>

              {/* Actions */}
              <div className="space-y-2">
                <button
                  onClick={copyFileName}
                  className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
                >
                  {copied ? (
                    <>
                      <Check size={18} className="text-green-600" />
                      <span className="text-green-600">Copiado</span>
                    </>
                  ) : (
                    <>
                      <Copy size={18} />
                      <span>Copiar nombre de archivo</span>
                    </>
                  )}
                </button>

                {family.downloadUrl && (
                  <a
                    href={family.downloadUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-bimac-accent text-white hover:bg-opacity-90 rounded-lg transition-colors"
                  >
                    <Download size={18} />
                    <span>Descargar familia</span>
                  </a>
                )}
              </div>
            </div>

            {/* Right Column - Details */}
            <div className="space-y-4">
              {/* Category & Collection */}
              <div className="flex flex-wrap gap-2">
                <span className={`category-badge ${categoryClass} text-sm px-3 py-1`}>
                  {family.category}
                </span>
                <span className="inline-flex items-center gap-1 px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm">
                  <FolderOpen size={14} />
                  {family.collection}
                </span>
              </div>

              {/* Description */}
              <div>
                <h3 className="text-sm font-medium text-gray-500 mb-1">Descripción</h3>
                <p className="text-gray-800">{family.description || 'Sin descripción'}</p>
              </div>

              {/* File Info */}
              <div className="bg-gray-50 rounded-lg p-4 space-y-3">
                <div className="flex items-center gap-3">
                  <FileType size={18} className="text-gray-400" />
                  <div>
                    <span className="text-sm text-gray-500">Archivo</span>
                    <p className="font-mono text-sm">{family.file}</p>
                  </div>
                </div>

                {family.lod && (
                  <div className="flex items-center gap-3">
                    <Layers size={18} className="text-gray-400" />
                    <div>
                      <span className="text-sm text-gray-500">Level of Development</span>
                      <p className="font-semibold">LOD {family.lod}</p>
                    </div>
                  </div>
                )}

                {family.revitVersion && (
                  <div className="flex items-center gap-3">
                    <Box size={18} className="text-gray-400" />
                    <div>
                      <span className="text-sm text-gray-500">Versión Revit</span>
                      <p>{family.revitVersion}</p>
                    </div>
                  </div>
                )}

                {family.author && (
                  <div className="flex items-center gap-3">
                    <User size={18} className="text-gray-400" />
                    <div>
                      <span className="text-sm text-gray-500">Autor</span>
                      <p>{family.author}</p>
                    </div>
                  </div>
                )}

                {family.dateAdded && (
                  <div className="flex items-center gap-3">
                    <Calendar size={18} className="text-gray-400" />
                    <div>
                      <span className="text-sm text-gray-500">Fecha de creación</span>
                      <p>{family.dateAdded}</p>
                    </div>
                  </div>
                )}
              </div>

              {/* Parameters */}
              {family.parameters && family.parameters.length > 0 && (
                <div>
                  <h3 className="text-sm font-medium text-gray-500 mb-2">Parámetros</h3>
                  <div className="bg-gray-50 rounded-lg p-3">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="text-left text-gray-500">
                          <th className="pb-2">Nombre</th>
                          <th className="pb-2">Tipo</th>
                        </tr>
                      </thead>
                      <tbody>
                        {family.parameters.map((param, idx) => (
                          <tr key={idx} className="border-t border-gray-200">
                            <td className="py-1.5 font-mono text-xs">{param.name}</td>
                            <td className="py-1.5 text-gray-600">{param.type}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* Tags */}
              {family.tags && family.tags.length > 0 && (
                <div>
                  <h3 className="text-sm font-medium text-gray-500 mb-2">Tags</h3>
                  <div className="flex flex-wrap gap-2">
                    {family.tags.map(tag => (
                      <span
                        key={tag}
                        className="inline-flex items-center gap-1 px-3 py-1 bg-bimac-light text-bimac-primary rounded-full text-sm"
                      >
                        <Tag size={12} />
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="border-t border-gray-200 px-6 py-4 bg-gray-50 flex justify-between items-center">
          <span className="text-sm text-gray-500">
            ID: {family.id}
          </span>
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-200 hover:bg-gray-300 rounded-lg transition-colors"
          >
            Cerrar
          </button>
        </div>
      </div>
    </div>
  )
}

export default FamilyModal
