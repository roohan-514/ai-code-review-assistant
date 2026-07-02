import { useState } from 'react'
import { AlertTriangle, Bug, Lightbulb, Shield, CheckCircle, FileCode, Download } from 'lucide-react'
import IssueCard from './IssueCard'
import SecurityAlert from './SecurityAlert'

export default function ReviewResult({ result }) {
  const [activeTab, setActiveTab] = useState('issues')

  if (!result) return null

  const tabs = [
    { id: 'issues', label: 'Issues', count: result.issues?.length || 0, icon: Bug },
    { id: 'security', label: 'Security', count: result.security_alerts?.length || 0, icon: Shield },
    { id: 'suggestions', label: 'Suggestions', count: result.suggestions?.length || 0, icon: Lightbulb },
  ]

  const statCards = [
    { label: 'Total Issues', value: result.total_issues, color: 'text-gray-300', bg: 'bg-gray-800' },
    { label: 'Critical', value: result.critical_count, color: 'text-red-400', bg: 'bg-red-900/20' },
    { label: 'High', value: result.high_count, color: 'text-orange-400', bg: 'bg-orange-900/20' },
    { label: 'Medium', value: result.medium_count, color: 'text-yellow-400', bg: 'bg-yellow-900/20' },
    { label: 'Low', value: result.low_count, color: 'text-blue-400', bg: 'bg-blue-900/20' },
  ]

  return (
    <div className="space-y-6">
      <div className="bg-gray-800/50 rounded-xl p-6 border border-gray-700">
        <div className="flex items-start gap-3 mb-4">
          <CheckCircle className="w-6 h-6 text-accent-400 mt-1" />
          <div>
            <h3 className="text-lg font-semibold text-gray-100">Review Complete</h3>
            <p className="text-sm text-gray-400 mt-1">{result.summary}</p>
            <div className="flex items-center gap-4 mt-2">
              <span className="text-xs text-gray-500">
                <FileCode className="w-3 h-3 inline mr-1" />
                {result.language}
              </span>
              {result.analyzed_files && (
                <span className="text-xs text-gray-500">
                  {result.analyzed_files.length} file(s) analyzed
                </span>
              )}
            </div>
          </div>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3">
          {statCards.map((stat) => (
            <div key={stat.label} className={`${stat.bg} rounded-lg p-3 text-center`}>
              <div className={`text-2xl font-bold ${stat.color}`}>{stat.value}</div>
              <div className="text-xs text-gray-500 mt-1">{stat.label}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-gray-800/30 rounded-xl border border-gray-700 overflow-hidden">
        <div className="flex border-b border-gray-700">
          {tabs.map((tab) => {
            const TabIcon = tab.icon
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-5 py-3 text-sm font-medium transition-colors ${
                  activeTab === tab.id
                    ? 'text-primary-400 border-b-2 border-primary-500 bg-primary-500/10'
                    : 'text-gray-400 hover:text-gray-300 hover:bg-gray-800/50'
                }`}
              >
                <TabIcon className="w-4 h-4" />
                {tab.label}
                <span className="text-xs bg-gray-700 px-2 py-0.5 rounded-full">{tab.count}</span>
              </button>
            )
          })}
        </div>

        <div className="p-4 space-y-3 max-h-[600px] overflow-y-auto scrollbar-thin">
          {activeTab === 'issues' && (
            result.issues?.length > 0
              ? result.issues.map((issue, i) => <IssueCard key={i} issue={issue} />)
              : <p className="text-gray-500 text-center py-8">No issues found. Great code!</p>
          )}

          {activeTab === 'security' && (
            result.security_alerts?.length > 0
              ? result.security_alerts.map((alert, i) => <SecurityAlert key={i} alert={alert} />)
              : (
                <div className="text-center py-8">
                  <Shield className="w-12 h-12 mx-auto text-accent-400 mb-2" />
                  <p className="text-gray-500">No security vulnerabilities detected.</p>
                </div>
              )
          )}

          {activeTab === 'suggestions' && (
            result.suggestions?.length > 0
              ? (
                <ul className="space-y-2">
                  {result.suggestions.map((s, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-gray-300">
                      <Lightbulb className="w-4 h-4 text-yellow-400 mt-0.5 shrink-0" />
                      <span>{s}</span>
                    </li>
                  ))}
                </ul>
              )
              : <p className="text-gray-500 text-center py-8">No suggestions available.</p>
          )}
        </div>
      </div>
    </div>
  )
}
