import { AlertTriangle, Bug, Zap, Lightbulb, Shield } from 'lucide-react'
import { useState } from 'react'

const severityConfig = {
  critical: { class: 'severity-critical', icon: Shield },
  high: { class: 'severity-high', icon: AlertTriangle },
  medium: { class: 'severity-medium', icon: Bug },
  low: { class: 'severity-low', icon: Zap },
}

const categoryIcons = {
  code_quality: Lightbulb,
  bug: Bug,
  security: Shield,
  performance: Zap,
  best_practice: Lightbulb,
}

export default function IssueCard({ issue }) {
  const [expanded, setExpanded] = useState(false)
  const sevConfig = severityConfig[issue.severity] || severityConfig.low
  const SevIcon = sevConfig.icon
  const CatIcon = categoryIcons[issue.category] || Lightbulb

  return (
    <div
      className={`rounded-lg border ${sevConfig.class} card-hover cursor-pointer`}
      onClick={() => setExpanded(!expanded)}
    >
      <div className="p-4">
        <div className="flex items-start gap-3">
          <div className={`mt-0.5 p-1.5 rounded-md ${sevConfig.class}`}>
            <SevIcon className="w-4 h-4" />
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 flex-wrap mb-1">
              <span className={`text-xs font-semibold uppercase px-2 py-0.5 rounded ${sevConfig.class}`}>
                {issue.severity}
              </span>
              <span className="flex items-center gap-1 text-xs text-gray-400">
                <CatIcon className="w-3 h-3" />
                {issue.category.replace('_', ' ')}
              </span>
              {issue.line && (
                <span className="text-xs text-gray-500">Line {issue.line}</span>
              )}
            </div>
            <p className="text-sm text-gray-200">{issue.description}</p>

            {expanded && (
              <div className="mt-3 space-y-3">
                {issue.code_context && (
                  <div>
                    <p className="text-xs text-gray-500 mb-1">Code:</p>
                    <pre className="bg-gray-900/80 rounded p-2 text-xs text-gray-300 overflow-x-auto">
                      <code>{issue.code_context}</code>
                    </pre>
                  </div>
                )}
                <div>
                  <p className="text-xs text-gray-500 mb-1">Suggestion:</p>
                  <p className="text-sm text-accent-400">{issue.suggestion}</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
