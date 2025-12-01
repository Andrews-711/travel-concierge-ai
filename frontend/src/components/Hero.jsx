export default function Hero({ activeTab, setActiveTab }) {
  return (
    <header className="relative overflow-hidden bg-gradient-to-br from-blue-600 via-indigo-700 to-purple-800 text-white py-24 animate-fadeIn shadow-2xl">
      {/* Decorative elements */}
      <div className="absolute top-0 left-0 w-full h-full opacity-10">
        <div className="absolute top-10 left-10 w-72 h-72 bg-white rounded-full blur-3xl animate-pulse-slow"></div>
        <div className="absolute bottom-10 right-10 w-96 h-96 bg-blue-300 rounded-full blur-3xl animate-pulse-slow" style={{animationDelay: '1s'}}></div>
      </div>
      
      <div className="container mx-auto px-4 max-w-7xl relative z-10">
        <div className="text-center mb-12 animate-slideUp">
          <div className="flex items-center justify-center mb-8">
            <div className="bg-white/10 backdrop-blur-md rounded-3xl p-6 animate-float">
              <span className="text-8xl">✈️</span>
            </div>
          </div>
          
          <h1 className="text-7xl md:text-8xl font-extrabold mb-6 tracking-tight">
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-white via-blue-100 to-indigo-200 drop-shadow-2xl">
              Travel Concierge
            </span>
          </h1>
          
          <p className="text-2xl md:text-3xl text-blue-100 font-medium mb-4 max-w-3xl mx-auto">
            Your AI-Powered Travel Planning Assistant
          </p>
          
          <div className="flex items-center justify-center gap-6 flex-wrap text-sm md:text-base text-blue-200/90 mt-6">
            <div className="flex items-center gap-2 bg-white/10 backdrop-blur-sm px-4 py-2 rounded-full">
              <span className="text-lg">🤖</span>
              <span>Google Gemini 2.0</span>
            </div>
            <div className="flex items-center gap-2 bg-white/10 backdrop-blur-sm px-4 py-2 rounded-full">
              <span className="text-lg">⚡</span>
              <span>Real-time Search</span>
            </div>
            <div className="flex items-center gap-2 bg-white/10 backdrop-blur-sm px-4 py-2 rounded-full">
              <span className="text-lg">🌍</span>
              <span>Global Coverage</span>
            </div>
          </div>
        </div>

        <div className="flex justify-center gap-6 mt-12 flex-wrap">
          <button
            onClick={() => setActiveTab('chat')}
            className={`group px-12 py-5 rounded-2xl font-bold text-lg transition-all duration-300 transform hover:scale-105 ${
              activeTab === 'chat'
                ? 'bg-white text-blue-700 shadow-2xl shadow-blue-900/30 scale-105'
                : 'bg-white/15 backdrop-blur-md text-white hover:bg-white/25 border-2 border-white/20'
            }`}
          >
            <div className="flex items-center gap-3">
              <span className="text-3xl group-hover:scale-110 transition-transform">💬</span>
              <div className="text-left">
                <div>Chat Assistant</div>
                <div className="text-xs opacity-75 font-normal">Ask anything about travel</div>
              </div>
            </div>
          </button>
          
          <button
            onClick={() => setActiveTab('plan')}
            className={`group px-12 py-5 rounded-2xl font-bold text-lg transition-all duration-300 transform hover:scale-105 ${
              activeTab === 'plan'
                ? 'bg-white text-indigo-700 shadow-2xl shadow-purple-900/30 scale-105'
                : 'bg-white/15 backdrop-blur-md text-white hover:bg-white/25 border-2 border-white/20'
            }`}
          >
            <div className="flex items-center gap-3">
              <span className="text-3xl group-hover:scale-110 transition-transform">🗺️</span>
              <div className="text-left">
                <div>Plan Your Trip</div>
                <div className="text-xs opacity-75 font-normal">Complete itinerary generation</div>
              </div>
            </div>
          </button>
        </div>

        {/* Feature highlights */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-16 max-w-5xl mx-auto">
          <div className="bg-white/10 backdrop-blur-md rounded-2xl p-6 text-center border border-white/20">
            <div className="text-4xl mb-3">🎯</div>
            <h3 className="font-bold text-lg mb-2">Smart Recommendations</h3>
            <p className="text-sm text-blue-100">Get personalized suggestions based on your preferences</p>
          </div>
          <div className="bg-white/10 backdrop-blur-md rounded-2xl p-6 text-center border border-white/20">
            <div className="text-4xl mb-3">💰</div>
            <h3 className="font-bold text-lg mb-2">Budget Planning</h3>
            <p className="text-sm text-blue-100">Plan trips that match your budget perfectly</p>
          </div>
          <div className="bg-white/10 backdrop-blur-md rounded-2xl p-6 text-center border border-white/20">
            <div className="text-4xl mb-3">📍</div>
            <h3 className="font-bold text-lg mb-2">Real Places</h3>
            <p className="text-sm text-blue-100">Actual restaurants, hotels, and attractions</p>
          </div>
        </div>
      </div>
    </header>
  )
}
