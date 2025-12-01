import { useState } from 'react'
import ChatInterface from './components/ChatInterface'
import TripPlanner from './components/TripPlanner'
import './App.css'

function App() {
  const [activeTab, setActiveTab] = useState('chat') // 'chat' or 'plan'
  const [sessionId, setSessionId] = useState(null)
  const [sidebarOpen, setSidebarOpen] = useState(true)

  return (
    <div className="min-h-screen flex bg-gray-50">
      {/* Sidebar Navigation */}
      <aside className={`fixed left-0 top-0 h-full bg-white border-r border-gray-200 transition-all duration-300 z-50 shadow-xl ${
        sidebarOpen ? 'w-72' : 'w-20'
      }`}>
        <div className="flex flex-col h-full">
          {/* Logo/Brand */}
          <div className="p-6 border-b border-gray-200">
            <div className="flex items-center justify-between">
              {sidebarOpen ? (
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg">
                    <span className="text-2xl">✈️</span>
                  </div>
                  <div>
                    <h1 className="text-xl font-bold gradient-text">TravelAI</h1>
                    <p className="text-xs text-gray-500">Smart Concierge</p>
                  </div>
                </div>
              ) : (
                <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg mx-auto">
                  <span className="text-2xl">✈️</span>
                </div>
              )}
            </div>
          </div>

          {/* Navigation Items */}
          <nav className="flex-1 p-4 space-y-2">
            <button
              onClick={() => setActiveTab('chat')}
              className={`w-full flex items-center gap-4 px-4 py-3.5 rounded-xl transition-all duration-200 ${
                activeTab === 'chat'
                  ? 'bg-gradient-to-r from-blue-500 to-indigo-600 text-white shadow-lg shadow-blue-500/30'
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              <span className="text-2xl">💬</span>
              {sidebarOpen && (
                <div className="text-left">
                  <div className="font-semibold">Chat Assistant</div>
                  <div className="text-xs opacity-75">Ask travel questions</div>
                </div>
              )}
            </button>

            <button
              onClick={() => setActiveTab('plan')}
              className={`w-full flex items-center gap-4 px-4 py-3.5 rounded-xl transition-all duration-200 ${
                activeTab === 'plan'
                  ? 'bg-gradient-to-r from-blue-500 to-indigo-600 text-white shadow-lg shadow-blue-500/30'
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              <span className="text-2xl">🗺️</span>
              {sidebarOpen && (
                <div className="text-left">
                  <div className="font-semibold">Trip Planner</div>
                  <div className="text-xs opacity-75">Create itineraries</div>
                </div>
              )}
            </button>
          </nav>

          {/* Features & Toggle */}
          <div className="p-4 border-t border-gray-200">
            {sidebarOpen && (
              <div className="mb-4 p-4 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl border border-blue-100">
                <div className="text-xs font-semibold text-gray-700 mb-3">Powered by:</div>
                <div className="space-y-2 text-xs text-gray-600">
                  <div className="flex items-center gap-2">
                    <span>🤖</span>
                    <span>Gemini 2.0</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span>⚡</span>
                    <span>Real-time Search</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span>🌍</span>
                    <span>Global Coverage</span>
                  </div>
                </div>
              </div>
            )}
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg text-gray-600 hover:bg-gray-100 transition-colors"
            >
              <span className="text-lg">{sidebarOpen ? '◀' : '▶'}</span>
              {sidebarOpen && <span className="text-sm font-medium">Collapse</span>}
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className={`flex-1 transition-all duration-300 ${
        sidebarOpen ? 'ml-72' : 'ml-20'
      }`}>
        {/* Top Bar */}
        <div className="bg-white border-b border-gray-200 px-8 py-4 shadow-sm sticky top-0 z-40">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold text-gray-800">
                {activeTab === 'chat' ? '💬 AI Chat Assistant' : '🗺️ Trip Planner'}
              </h2>
              <p className="text-sm text-gray-500 mt-1">
                {activeTab === 'chat' 
                  ? 'Ask me anything about your travel plans' 
                  : 'Create your perfect itinerary with AI'}
              </p>
            </div>
            <div className="flex items-center gap-3">
              <div className="px-4 py-2 bg-green-100 text-green-700 rounded-full text-sm font-medium flex items-center gap-2">
                <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                AI Online
              </div>
            </div>
          </div>
        </div>

        {/* Content Area */}
        <div className="p-8 max-w-7xl mx-auto">
          {activeTab === 'chat' ? (
            <ChatInterface sessionId={sessionId} setSessionId={setSessionId} />
          ) : (
            <TripPlanner />
          )}
        </div>
      </main>
    </div>
  )
}

export default App
