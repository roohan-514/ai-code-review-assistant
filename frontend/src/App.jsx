import { Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import ReviewPR from './pages/ReviewPR'
import History from './pages/History'

export default function App() {
  return (
    <div className="min-h-screen bg-gray-900">
      <Navbar />
      <main className="container mx-auto px-4 py-8">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/review" element={<ReviewPR />} />
          <Route path="/history" element={<History />} />
        </Routes>
      </main>
    </div>
  )
}
