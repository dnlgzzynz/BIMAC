import React, { useState, useEffect } from 'react'
import {
  X,
  Download,
  FileText,
  Table,
  Check,
  FileSpreadsheet,
  Filter,
  Star
} from 'lucide-react'

// Export formats available
const exportFormats = [
  {
    id: 'csv',
    name: 'CSV',
    description: 'Archivo de valores separados por comas',
    icon: FileText,
    extension: '.csv'
  },
  {
    id: 'excel',
    name: 'Excel',
    description: 'Hoja de cálculo Microsoft Excel',
    icon: FileSpreadsheet,
    extension: '.xlsx'
  },
  {
    id: 'json',
    name: 'JSON',
    description: 'Formato de datos JavaScript',
    icon: Table,
    extension: '.json'
  }
]

// Fields that can be exported
const exportFields = [
  { id: 'name', label: 'Nombre', default: true },
  { id: 'category', label: 'Categoría', default: true },
  { id: 'collection', label: 'Colección', default: true },
  { id: 'description', label: 'Descripción', default: true },
  { id: 'file', label: 'Archivo', default: true },
  { id: 'lod', label: 'LOD', default: true },
  { id: 'tags', label: 'Tags', default: true },
  { id: 'revitVersion', label: 'Versión Revit', default: false },
  { id: 'author', label: 'Autor', default: false },
  { id: 'dateAdded', label: 'Fecha', default: false }
]

function ExportModal({ isOpen, onClose, families, favoritesCount, totalCount }) {
  const [selectedFormat, setSelectedFormat] = useState('csv')
  const [selectedFields, setSelectedFields] = useState(
    exportFields.filter(f => f.default).map(f => f.id)
  )
  const [isExporting, setIsExporting] = useState(false)
  const [exportSuccess, setExportSuccess] = useState(false)

  // Reset state when modal opens
  useEffect(() => {
    if (isOpen) {
      setExportSuccess(false)
    }
  }, [isOpen])

  // Close on ESC
  useEffect(() => {
    const handleEsc = (e) => {
      if (e.key === 'Escape') onClose()
    }
    if (isOpen) {
      window.addEventListener('keydown', handleEsc)
      document.body.style.overflow = 'hidden'
    }
    return () => {
      window.removeEventListener('keydown', handleEsc)
      document.body.style.overflow = 'unset'
    }
  }, [isOpen, onClose])

  const toggleField = (fieldId) => {
    setSelectedFields(prev => {
      if (prev.includes(fieldId)) {
        return prev.filter(f => f !== fieldId)
      }
      return [...prev, fieldId]
    })
  }

  const selectAllFields = () => {
    setSelectedFields(exportFields.map(f => f.id))
  }

  const selectDefaultFields = () => {
    setSelectedFields(exportFields.filter(f => f.default).map(f => f.id))
  }

  // Generate CSV content
  const generateCSV = () => {
    const headers = selectedFields.map(fieldId => {
      const field = exportFields.find(f => f.id === fieldId)
      return field?.label || fieldId
    })

    const rows = families.map(family => {
      return selectedFields.map(fieldId => {
        const value = family[fieldId]
        if (Array.isArray(value)) {
          return `"${value.join(', ')}"`
        }
        if (typeof value === 'string' && (value.includes(',') || value.includes('"'))) {
          return `"${value.replace(/"/g, '""')}"`
        }
        return value || ''
      })
    })

    return [headers.join(','), ...rows.map(r => r.join(','))].join('\n')
  }

  // Generate JSON content
  const generateJSON = () => {
    const filtered = families.map(family => {
      const obj = {}
      selectedFields.forEach(fieldId => {
        if (family[fieldId] !== undefined) {
          obj[fieldId] = family[fieldId]
        }
      })
      return obj
    })
    return JSON.stringify(filtered, null, 2)
  }

  // Generate Excel-compatible XML (simple XLSX simulation)
  const generateExcelXML = () => {
    const headers = selectedFields.map(fieldId => {
      const field = exportFields.find(f => f.id === fieldId)
      return field?.label || fieldId
    })

    let xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<?mso-application progid="Excel.Sheet"?>\n'
    xml += '<Workbook xmlns="urn:schemas-microsoft-com:office:spreadsheet"\n'
    xml += ' xmlns:ss="urn:schemas-microsoft-com:office:spreadsheet">\n'
    xml += '<Worksheet ss:Name="Familias BIMAC">\n<Table>\n'

    // Header row
    xml += '<Row>\n'
    headers.forEach(h => {
      xml += `<Cell><Data ss:Type="String">${h}</Data></Cell>\n`
    })
    xml += '</Row>\n'

    // Data rows
    families.forEach(family => {
      xml += '<Row>\n'
      selectedFields.forEach(fieldId => {
        const value = family[fieldId]
        const cellValue = Array.isArray(value) ? value.join(', ') : (value || '')
        const type = typeof value === 'number' ? 'Number' : 'String'
        xml += `<Cell><Data ss:Type="${type}">${cellValue}</Data></Cell>\n`
      })
      xml += '</Row>\n'
    })

    xml += '</Table>\n</Worksheet>\n</Workbook>'
    return xml
  }

  const handleExport = async () => {
    if (selectedFields.length === 0) return

    setIsExporting(true)

    try {
      let content, mimeType, extension

      switch (selectedFormat) {
        case 'csv':
          content = generateCSV()
          mimeType = 'text/csv;charset=utf-8'
          extension = '.csv'
          break
        case 'json':
          content = generateJSON()
          mimeType = 'application/json'
          extension = '.json'
          break
        case 'excel':
          content = generateExcelXML()
          mimeType = 'application/vnd.ms-excel'
          extension = '.xls'
          break
        default:
          throw new Error('Formato no soportado')
      }

      // Create and download file
      const blob = new Blob([content], { type: mimeType })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `bimac-familias-${new Date().toISOString().split('T')[0]}${extension}`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)

      setExportSuccess(true)
      setTimeout(() => {
        onClose()
      }, 1500)
    } catch (error) {
      console.error('Export error:', error)
    } finally {
      setIsExporting(false)
    }
  }

  if (!isOpen) return null

  return (
    <div
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <div className="bg-white rounded-xl shadow-2xl max-w-lg w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="bg-bimac-primary text-white px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Download size={24} />
            <h2 className="text-xl font-semibold">Exportar Familias</h2>
          </div>
          <button
            onClick={onClose}
            className="p-1 hover:bg-white hover:bg-opacity-20 rounded-full transition-colors"
          >
            <X size={24} />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* Export summary */}
          <div className="bg-bimac-light rounded-lg p-4">
            <div className="flex items-center gap-2 text-bimac-primary font-medium mb-2">
              <Filter size={18} />
              Resumen de exportación
            </div>
            <div className="text-sm text-gray-600 space-y-1">
              <p>Se exportarán <span className="font-semibold text-bimac-primary">{families.length}</span> familias</p>
              {families.length < totalCount && (
                <p className="text-xs text-gray-500">
                  (filtrado de {totalCount} totales)
                </p>
              )}
            </div>
          </div>

          {/* Format selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Formato de exportación
            </label>
            <div className="grid grid-cols-3 gap-3">
              {exportFormats.map(format => {
                const Icon = format.icon
                const isSelected = selectedFormat === format.id
                return (
                  <button
                    key={format.id}
                    onClick={() => setSelectedFormat(format.id)}
                    className={`
                      p-4 rounded-lg border-2 transition-all duration-200 text-center
                      ${isSelected
                        ? 'border-bimac-primary bg-bimac-light'
                        : 'border-gray-200 hover:border-bimac-secondary'
                      }
                    `}
                  >
                    <Icon
                      size={24}
                      className={`mx-auto mb-2 ${isSelected ? 'text-bimac-primary' : 'text-gray-400'}`}
                    />
                    <span className={`font-medium ${isSelected ? 'text-bimac-primary' : 'text-gray-700'}`}>
                      {format.name}
                    </span>
                    <p className="text-xs text-gray-500 mt-1">{format.extension}</p>
                  </button>
                )
              })}
            </div>
          </div>

          {/* Field selection */}
          <div>
            <div className="flex items-center justify-between mb-3">
              <label className="block text-sm font-medium text-gray-700">
                Campos a incluir
              </label>
              <div className="flex gap-2 text-xs">
                <button
                  onClick={selectAllFields}
                  className="text-bimac-primary hover:underline"
                >
                  Todos
                </button>
                <span className="text-gray-300">|</span>
                <button
                  onClick={selectDefaultFields}
                  className="text-bimac-primary hover:underline"
                >
                  Por defecto
                </button>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-2">
              {exportFields.map(field => {
                const isSelected = selectedFields.includes(field.id)
                return (
                  <button
                    key={field.id}
                    onClick={() => toggleField(field.id)}
                    className={`
                      flex items-center gap-2 px-3 py-2 rounded-lg border transition-all duration-200 text-sm
                      ${isSelected
                        ? 'border-bimac-primary bg-bimac-light text-bimac-primary'
                        : 'border-gray-200 text-gray-600 hover:border-gray-300'
                      }
                    `}
                  >
                    <div className={`
                      w-4 h-4 rounded border flex items-center justify-center flex-shrink-0
                      ${isSelected ? 'bg-bimac-primary border-bimac-primary' : 'border-gray-300'}
                    `}>
                      {isSelected && <Check size={12} className="text-white" />}
                    </div>
                    <span>{field.label}</span>
                  </button>
                )
              })}
            </div>
            {selectedFields.length === 0 && (
              <p className="text-red-500 text-sm mt-2">
                Selecciona al menos un campo para exportar
              </p>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="border-t border-gray-200 px-6 py-4 bg-gray-50 flex justify-between items-center">
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
          >
            Cancelar
          </button>
          <button
            onClick={handleExport}
            disabled={selectedFields.length === 0 || isExporting}
            className={`
              flex items-center gap-2 px-6 py-2 rounded-lg font-medium transition-all duration-200
              ${selectedFields.length === 0 || isExporting
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : exportSuccess
                  ? 'bg-green-500 text-white'
                  : 'bg-bimac-primary text-white hover:bg-bimac-accent'
              }
            `}
          >
            {exportSuccess ? (
              <>
                <Check size={18} />
                Exportado
              </>
            ) : isExporting ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Exportando...
              </>
            ) : (
              <>
                <Download size={18} />
                Exportar {selectedFormat.toUpperCase()}
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  )
}

export default ExportModal
