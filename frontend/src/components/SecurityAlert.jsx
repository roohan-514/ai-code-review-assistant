import { useState } from 'react'
import { Shield, ShieldAlert, ShieldX, AlertTriangle } from 'lucide-react'

const severityStyles = {
  critical: {
    container: 'bg-red-900/20 border-red-800',
    badge: 'bg-red-800 text-red-200',
    icon: ShieldX,
    iconColor: 'text-red-400',
    header: 'text-red-300',
    accent: 'text-red-400',
  },
  high: {
    container: 'bg-orange-900/20 border-orange-800',
    badge: 'bg-orange-800 text-orange-200',
    icon: ShieldAlert,
    iconColor: 'text-orange-400',
    header: 'text-orange-300',
    accent: 'text-orange-400',
  },
  medium: {
    container: 'bg-yellow-900/20 border-yellow-800',
    badge: 'bg-yellow-800 text-yellow-200',
    icon: AlertTriangle,
    iconColor: 'text-yellow-400',
    header: 'text-yellow-300',
    accent: 'text-yellow-400',
  },
  low: {
    container: 'bg-blue-900/20 border-blue-800',
    badge: 'bg-blue-800 text-blue-200',
    icon: Shield,
    iconColor: 'text-blue-400',
    header: 'text-blue-300',
    accent: 'text-blue-400',
  },
}

export default function SecurityAlert({ alert }) {
  const [expanded, setExpanded] = useState(false)
  const styles = severityStyles[alert.severity] || severityStyles.low
  const Icon = styles.icon

  return (
    <div
      className={`rounded-lg border ${styles.container} card-hover cursor-pointer`}
      onClick={() => setExpanded(!expanded)}
    >
      <div className="p-4">
        <div className="flex items-start gap-3">
          <div className={`mt-0.5 ${styles.iconColor}`}>
            <Icon className="w-5 h-5" />
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 flex-wrap mb-1">
              <span className={`text-xs font-semibold uppercase px-2 py-0.5 rounded ${styles.badge}`}>
                {alert.severity}
              </span>
              <span className="text-xs font-mono text-gray-400">
                {alert.vulnerability_type.replace(/_/g, ' ')}
              </span>
              {alert.line && (
                <span className="text-xs text-gray-500">Line {alert.line}</span>
              )}
            </div>
            <p className={`text-sm font-medium ${styles.header}`}>{alert.description}</p>

            {expanded && (
              <div className="mt-3 space-y-3">
                <div>
                  <p className="text-xs text-gray-500 mb-1">Impact:</p>
                  <p className="text-sm text-gray-300">{alert.impact}</p>
                </div>
                {alert.code_context && (
                  <div>
                    <p className="text-xs text-gray-500 mb-1">Code:</p>
                    <pre className="bg-gray-900/80 rounded p-2 text-xs text-gray-300 overflow-x-auto">
                      <code>{alert.code_context}</code>
                    </pre>
                  </div>
                )}
                <div>
                  <p className="text-xs text-gray-500 mb-1">Recommendation:</p>
                  <p className={`text-sm ${styles.accent}`}>{alert.recommendation}</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
