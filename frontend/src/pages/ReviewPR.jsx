import { useState } from 'react'
import { Github, Code2, ArrowRight, Loader2, Link as LinkIcon } from 'lucide-react'
import CodeInput from '../components/CodeInput'
import ReviewResult from '../components/ReviewResult'
import { reviewCode, reviewPR } from '../services/api'

export default function ReviewPR() {
  const [reviewMode, setReviewMode] = useState('code')
  const [code, setCode] = useState('')
  const [language, setLanguage] = useState('python')
  const [fileName, setFileName] = useState('')
  const [prUrl, setPrUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)

  const handleSubmit = async () => {
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      let data
      if (reviewMode === 'code') {
        if (!code.trim()) {
          throw new Error('Please enter code to review.')
        }
        data = await reviewCode(code, language, fileName || null)
      } else {
        if (!prUrl.trim()) {
          throw new Error('Please enter a GitHub PR URL.')
        }
        data = await reviewPR(prUrl)
      }
      setResult(data)
    } catch (err) {
      const msg = err.response?.data?.detail || err.message || 'An error occurred during review.'
      setError(msg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div className="flex items-center gap-4 mb-2">
        <button
          onClick={() => { setReviewMode('code'); setResult(null); setError(null) }}
          className={`flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-medium transition-all ${
            reviewMode === 'code'
              ? 'gradient-bg text-white shadow-lg shadow-primary-600/30'
              : 'bg-gray-800 text-gray-400 hover:text-gray-200 border border-gray-700'
          }`}
        >
          <Code2 className="w-4 h-4" />
          Paste Code
        </button>
        <button
          onClick={() => { setReviewMode('pr'); setResult(null); setError(null) }}
          className={`flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-medium transition-all ${
            reviewMode === 'pr'
              ? 'gradient-bg text-white shadow-lg shadow-primary-600/30'
              : 'bg-gray-800 text-gray-400 hover:text-gray-200 border border-gray-700'
          }`}
        >
          <Github className="w-4 h-4" />
          Review PR
        </button>
      </div>

      <div className="bg-gray-800/30 rounded-xl p-6 border border-gray-700">
        {reviewMode === 'code' ? (
          <CodeInput
            value={code}
            onChange={setCode}
            language={language}
            onLanguageChange={setLanguage}
            fileName={fileName}
            onFileNameChange={setFileName}
          />
        ) : (
          <div className="space-y-4">
            <label className="block text-sm font-medium text-gray-300">
              GitHub Pull Request URL
            </label>
            <div className="relative">
              <LinkIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
              <input
                type="url"
                value={prUrl}
                onChange={(e) => setPrUrl(e.target.value)}
                placeholder="https://github.com/owner/repo/pull/123"
                className="w-full bg-gray-800 border border-gray-700 rounded-lg pl-10 pr-4 py-3 text-sm text-gray-200 placeholder-gray-500 focus:outline-none focus:border-primary-500"
              />
            </div>
            <p className="text-xs text-gray-500">
              Enter the full URL of a GitHub pull request to review all changed files.
            </p>
          </div>
        )}

        <button
          onClick={handleSubmit}
          disabled={loading}
          className="mt-6 inline-flex items-center gap-2 px-6 py-3 gradient-bg rounded-lg text-white font-medium hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Analyzing...
            </>
          ) : (
            <>
              {reviewMode === 'code' ? 'Review Code' : 'Review PR'}
              <ArrowRight className="w-4 h-4" />
            </>
          )}
        </button>
      </div>

      {loading && (
        <div className="flex flex-col items-center justify-center py-12">
          <div className="loading-spinner mb-4" />
          <p className="text-gray-400 text-sm">Analyzing code with AI...</p>
          <p className="text-gray-600 text-xs mt-1">This may take a moment</p>
        </div>
      )}

      {error && (
        <div className="bg-red-900/30 border border-red-800 rounded-lg p-4 text-red-300 text-sm">
          {error}
        </div>
      )}

      {result && <ReviewResult result={result} />}
    </div>
  )
}
