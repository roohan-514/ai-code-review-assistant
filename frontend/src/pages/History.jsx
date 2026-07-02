import { useState, useEffect } from 'react'
import { Clock, FileCode, AlertTriangle, Trash2, ChevronRight } from 'lucide-react'

const STORAGE_KEY = 'code-review-history'

function loadHistory() {
  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    return stored ? JSON.parse(stored) : []
  } catch {
    return []
  }
}

function saveHistory(items) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(items))
}

export default function History() {
  const [reviews, setReviews] = useState([])
  const [selectedReview, setSelectedReview] = useState(null)

  useEffect(() => {
    setReviews(loadHistory())
  }, [])

  const handleClear = () => {
    localStorage.removeItem(STORAGE_KEY)
    setReviews([])
    setSelectedReview(null)
  }

  const handleDelete = (index) => {
    const updated = reviews.filter((_, i) => i !== index)
    setReviews(updated)
    saveHistory(updated)
    if (selectedReview && reviews[index] === selectedReview) {
      setSelectedReview(null)
    }
  }

  if (reviews.length === 0) {
    return (
      <div className="text-center py-20">
        <Clock className="w-16 h-16 mx-auto text-gray-700 mb-4" />
        <h2 className="text-xl font-semibold text-gray-400 mb-2">No review history yet</h2>
        <p className="text-gray-600">Submit your first code review to see it here.</p>
      </div>
    )
  }

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-gray-100">Review History</h2>
        <button
          onClick={handleClear}
          className="flex items-center gap-2 px-3 py-1.5 text-sm text-red-400 hover:text-red-300 hover:bg-red-900/20 rounded-lg transition-colors"
        >
          <Trash2 className="w-4 h-4" />
          Clear All
        </button>
      </div>

      <div className="grid md:grid-cols-3 gap-4">
        <div className="md:col-span-1 space-y-2">
          {reviews.map((review, index) => (
            <button
              key={index}
              onClick={() => setSelectedReview(review)}
              className={`w-full text-left p-4 rounded-lg border transition-colors ${
                selectedReview === review
                  ? 'bg-primary-600/20 border-primary-600'
                  : 'bg-gray-800/30 border-gray-700 hover:bg-gray-800/50'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs text-gray-500">
                  {new Date(review.date || Date.now()).toLocaleDateString()}
                </span>
                <button
                  onClick={(e) => { e.stopPropagation(); handleDelete(index) }}
                  className="text-gray-600 hover:text-red-400"
                >
                  <Trash2 className="w-3 h-3" />
                </button>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <FileCode className="w-4 h-4 text-gray-500" />
                <span className="text-gray-300 capitalize">{review.language || 'unknown'}</span>
              </div>
              <div className="flex items-center gap-2 mt-2 text-xs text-gray-500">
                <AlertTriangle className="w-3 h-3" />
                <span>{review.total_issues || 0} issues</span>
                <ChevronRight className="w-3 h-3 ml-auto" />
              </div>
            </button>
          ))}
        </div>

        <div className="md:col-span-2">
          {selectedReview ? (
            <div className="bg-gray-800/30 rounded-xl border border-gray-700 p-6 space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-gray-100">
                  Review Details
                </h3>
                <span className="text-xs text-gray-500">
                  {new Date(selectedReview.date || Date.now()).toLocaleString()}
                </span>
              </div>

              <div className="grid grid-cols-5 gap-2">
                {[
                  { label: 'Total', value: selectedReview.total_issues, cls: 'text-gray-300' },
                  { label: 'Critical', value: selectedReview.critical_count, cls: 'text-red-400' },
                  { label: 'High', value: selectedReview.high_count, cls: 'text-orange-400' },
                  { label: 'Medium', value: selectedReview.medium_count, cls: 'text-yellow-400' },
                  { label: 'Low', value: selectedReview.low_count, cls: 'text-blue-400' },
                ].map((s) => (
                  <div key={s.label} className="bg-gray-900/50 rounded-lg p-3 text-center">
                    <div className={`text-lg font-bold ${s.cls}`}>{s.value}</div>
                    <div className="text-xs text-gray-600">{s.label}</div>
                  </div>
                ))}
              </div>

              {selectedReview.summary && (
                <div>
                  <p className="text-sm text-gray-500 mb-1">Summary:</p>
                  <p className="text-sm text-gray-300">{selectedReview.summary}</p>
                </div>
              )}

              {selectedReview.analyzed_files?.length > 0 && (
                <div>
                  <p className="text-sm text-gray-500 mb-2">Analyzed Files:</p>
                  <ul className="space-y-1">
                    {selectedReview.analyzed_files.map((f, i) => (
                      <li key={i} className="text-sm text-gray-400 font-mono">- {f}</li>
                    ))}
                  </ul>
                </div>
              )}

              {selectedReview.issues?.length > 0 && (
                <div>
                  <p className="text-sm text-gray-500 mb-2">Issues:</p>
                  <div className="space-y-2">
                    {selectedReview.issues.slice(0, 5).map((issue, i) => (
                      <div key={i} className="text-sm text-gray-400 bg-gray-900/30 rounded p-2">
                        <span className="text-xs uppercase font-bold text-red-400">{issue.severity}</span>
                        {' '}{issue.description}
                      </div>
                    ))}
                    {selectedReview.issues.length > 5 && (
                      <p className="text-xs text-gray-600">...and {selectedReview.issues.length - 5} more</p>
                    )}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="flex items-center justify-center h-64 bg-gray-800/20 rounded-xl border border-gray-700/50">
              <p className="text-gray-600">Select a review to view details</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
