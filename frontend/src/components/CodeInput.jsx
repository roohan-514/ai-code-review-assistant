import { useState } from 'react'
import { Code2, FileCode } from 'lucide-react'

const LANGUAGES = [
  { value: 'python', label: 'Python' },
  { value: 'javascript', label: 'JavaScript' },
  { value: 'typescript', label: 'TypeScript' },
  { value: 'java', label: 'Java' },
  { value: 'go', label: 'Go' },
  { value: 'rust', label: 'Rust' },
  { value: 'cpp', label: 'C++' },
  { value: 'csharp', label: 'C#' },
  { value: 'ruby', label: 'Ruby' },
  { value: 'php', label: 'PHP' },
  { value: 'sql', label: 'SQL' },
  { value: 'html', label: 'HTML' },
  { value: 'css', label: 'CSS' },
  { value: 'bash', label: 'Bash' },
  { value: 'yaml', label: 'YAML' },
  { value: 'json', label: 'JSON' },
]

export default function CodeInput({ value, onChange, language, onLanguageChange, fileName, onFileNameChange }) {
  const lineCount = (value || '').split('\n').length

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-4 items-center">
        <div className="flex items-center gap-2">
          <FileCode className="w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="File name (optional)"
            value={fileName || ''}
            onChange={(e) => onFileNameChange?.(e.target.value)}
            className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-300 placeholder-gray-500 focus:outline-none focus:border-primary-500 w-48"
          />
        </div>
        <div className="flex items-center gap-2">
          <Code2 className="w-4 h-4 text-gray-400" />
          <select
            value={language}
            onChange={(e) => onLanguageChange(e.target.value)}
            className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-300 focus:outline-none focus:border-primary-500"
          >
            {LANGUAGES.map((l) => (
              <option key={l.value} value={l.value}>{l.label}</option>
            ))}
          </select>
        </div>
      </div>

      <div className="relative">
        <div className="absolute left-0 top-0 bottom-0 w-12 bg-gray-800/50 border-r border-gray-700 flex flex-col items-center pt-3 text-xs text-gray-600 font-mono select-none overflow-hidden">
          {Array.from({ length: lineCount }, (_, i) => (
            <span key={i + 1} className="leading-6">{i + 1}</span>
          ))}
        </div>
        <textarea
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder="Paste your code here..."
          className="w-full min-h-[300px] bg-gray-800 border border-gray-700 rounded-lg pl-14 pr-4 py-3 font-mono text-sm text-gray-200 placeholder-gray-500 focus:outline-none focus:border-primary-500 resize-y leading-6"
          spellCheck={false}
        />
      </div>
    </div>
  )
}
