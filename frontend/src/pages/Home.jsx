import { Link } from 'react-router-dom'
import { Sparkles, Github, Shield, Globe, ArrowRight, Code2 } from 'lucide-react'

const features = [
  {
    icon: Sparkles,
    title: 'AI-Powered Analysis',
    description: 'Advanced AI analyzes your code for bugs, code quality issues, and best practices with contextual understanding.',
    gradient: 'from-purple-500 to-primary-500',
  },
  {
    icon: Github,
    title: 'GitHub PR Integration',
    description: 'Review any GitHub pull request by URL. Get detailed analysis on every changed file automatically.',
    gradient: 'from-primary-500 to-blue-500',
  },
  {
    icon: Shield,
    title: 'Security Scanning',
    description: 'Detect hardcoded secrets, SQL injection, XSS, and other vulnerabilities before they reach production.',
    gradient: 'from-accent-400 to-emerald-500',
  },
]

export default function Home() {
  return (
    <div className="space-y-20">
      <section className="text-center py-16">
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary-500/10 border border-primary-500/20 text-primary-400 text-sm mb-8">
          <Sparkles className="w-4 h-4" />
          AI-Powered Code Review Assistant
        </div>

        <h1 className="text-4xl md:text-6xl font-bold mb-6">
          Review code with{' '}
          <span className="gradient-text">AI precision</span>
        </h1>

        <p className="text-xl text-gray-400 max-w-2xl mx-auto mb-10">
          Get instant, intelligent code reviews powered by AI. Analyze code snippets,
          review GitHub pull requests, and improve code quality with actionable feedback.
        </p>

        <div className="flex flex-wrap justify-center gap-4">
          <Link
            to="/review"
            className="inline-flex items-center gap-2 px-6 py-3 gradient-bg rounded-lg text-white font-medium hover:opacity-90 transition-opacity"
          >
            <Code2 className="w-5 h-5" />
            Start Review
            <ArrowRight className="w-4 h-4" />
          </Link>
          <Link
            to="/history"
            className="inline-flex items-center gap-2 px-6 py-3 bg-gray-800 rounded-lg text-gray-300 font-medium hover:bg-gray-700 transition-colors border border-gray-700"
          >
            <Globe className="w-5 h-5" />
            View History
          </Link>
        </div>
      </section>

      <section className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto">
        {features.map((feature) => {
          const Icon = feature.icon
          return (
            <div
              key={feature.title}
              className="bg-gray-800/50 rounded-xl p-6 border border-gray-700 card-hover"
            >
              <div className={`w-12 h-12 rounded-lg bg-gradient-to-br ${feature.gradient} flex items-center justify-center mb-4`}>
                <Icon className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-lg font-semibold text-gray-100 mb-2">{feature.title}</h3>
              <p className="text-sm text-gray-400 leading-relaxed">{feature.description}</p>
            </div>
          )
        })}
      </section>

      <section className="text-center py-12">
        <div className="inline-flex items-center gap-2 text-sm text-gray-500">
          <Globe className="w-4 h-4" />
          Supports Python, JavaScript, TypeScript, Java, Go, Rust, C++, C#, Ruby, PHP, SQL, HTML, CSS, and more
        </div>
      </section>
    </div>
  )
}
