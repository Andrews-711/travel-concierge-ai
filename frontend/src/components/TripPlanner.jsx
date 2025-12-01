import { useState } from 'react'
import axios from 'axios'

const API_URL = 'http://127.0.0.1:8001'

export default function TripPlanner() {
  const [formData, setFormData] = useState({
    destination: '',
    duration_days: 3,
    budget: 50000,
    currency: 'INR',
    interests: [],
    dietary_preferences: []
  })
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const interests = ['museums', 'beaches', 'mountains', 'nightlife', 'shopping', 'food', 'adventure', 'culture']
  const dietary = ['vegetarian', 'vegan', 'halal', 'kosher', 'gluten-free']

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setResult(null)
    setError(null)

    try {
      const response = await axios.post(`${API_URL}/plan`, formData, { timeout: 90000 })
      setResult(response.data)
    } catch (error) {
      const errorMsg = error.response?.data?.detail || error.message
      setError(errorMsg)
      alert('Error planning trip: ' + errorMsg)
    } finally {
      setLoading(false)
    }
  }

  const toggleArray = (arr, item) => {
    return arr.includes(item) ? arr.filter(i => i !== item) : [...arr, item]
  }

  return (
    <div className="animate-fadeIn">
      <div className="card max-w-4xl mx-auto">
        <h2 className="text-3xl font-bold text-gray-800 mb-6">Plan Your Perfect Trip</h2>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                🌍 Destination
              </label>
              <input
                type="text"
                value={formData.destination}
                onChange={(e) => setFormData({ ...formData, destination: e.target.value })}
                placeholder="e.g., Tokyo, Paris, Bali"
                className="input-field"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                📅 Duration (days)
              </label>
              <input
                type="number"
                min="1"
                max="30"
                value={formData.duration_days}
                onChange={(e) => setFormData({ ...formData, duration_days: parseInt(e.target.value) })}
                className="input-field"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                💰 Budget
              </label>
              <input
                type="number"
                min="1000"
                value={formData.budget}
                onChange={(e) => setFormData({ ...formData, budget: parseFloat(e.target.value) })}
                className="input-field"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                💱 Currency
              </label>
              <select
                value={formData.currency}
                onChange={(e) => setFormData({ ...formData, currency: e.target.value })}
                className="input-field"
              >
                <option value="INR">INR (₹)</option>
                <option value="USD">USD ($)</option>
                <option value="EUR">EUR (€)</option>
                <option value="GBP">GBP (£)</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-3">
              🎯 Interests (Click to select)
            </label>
            <div className="flex flex-wrap gap-2">
              {interests.map(interest => (
                <button
                  key={interest}
                  type="button"
                  onClick={() => setFormData({
                    ...formData,
                    interests: toggleArray(formData.interests, interest)
                  })}
                  className={`px-4 py-2 rounded-full font-medium transition-all transform hover:scale-105 ${
                    formData.interests.includes(interest)
                      ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg ring-2 ring-blue-300'
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300 hover:shadow-md'
                  }`}
                >
                  {formData.interests.includes(interest) && '✓ '}
                  {interest}
                </button>
              ))}
            </div>
            {formData.interests.length === 0 && (
              <p className="text-sm text-gray-500 mt-2">Select at least one interest to personalize your trip</p>
            )}
            {formData.interests.length > 0 && (
              <p className="text-sm text-blue-600 mt-2">✓ Selected: {formData.interests.join(', ')}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-3">
              🍽️ Dietary Preferences (Click to select)
            </label>
            <div className="flex flex-wrap gap-2">
              {dietary.map(diet => (
                <button
                  key={diet}
                  type="button"
                  onClick={() => setFormData({
                    ...formData,
                    dietary_preferences: toggleArray(formData.dietary_preferences, diet)
                  })}
                  className={`px-4 py-2 rounded-full font-medium transition-all transform hover:scale-105 ${
                    formData.dietary_preferences.includes(diet)
                      ? 'bg-gradient-to-r from-green-500 to-teal-600 text-white shadow-lg ring-2 ring-green-300'
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300 hover:shadow-md'
                  }`}
                >
                  {formData.dietary_preferences.includes(diet) && '✓ '}
                  {diet}
                </button>
              ))}
            </div>
            {formData.dietary_preferences.length > 0 && (
              <p className="text-sm text-green-600 mt-2">✓ Selected: {formData.dietary_preferences.join(', ')}</p>
            )}
          </div>

          <button
            type="submit"
            disabled={loading}
            className="btn-primary w-full text-lg py-4"
          >
            {loading ? '✨ Generating Your Perfect Trip...' : '🚀 Plan My Trip'}
          </button>
        </form>
      </div>

      {loading && (
        <div className="card max-w-4xl mx-auto mt-8 text-center py-12">
          <div className="inline-block animate-spin text-6xl mb-4">🌍</div>
          <p className="text-xl text-gray-700">Searching the web for the best options...</p>
          <p className="text-gray-500 mt-2">This may take 10-15 seconds</p>
        </div>
      )}

      {result && (
        <div className="mt-8 space-y-6 animate-slideUp">
          <div className="card max-w-4xl mx-auto">
            <h3 className="text-2xl font-bold text-gray-800 mb-4">
              🗺️ Trip to {result.destination} ({result.duration} days)
            </h3>
            {result.map_link && (
              <a
                href={result.map_link}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-block btn-secondary text-sm mb-4"
              >
                🗺️ View on Maps
              </a>
            )}
          </div>

          {result.options.map((option, idx) => (
            <div key={idx} className="card max-w-4xl mx-auto">
              <div className="flex items-center justify-between mb-4">
                <h4 className="text-2xl font-bold text-gray-800">
                  {option.budget_type === 'budget' && '💰'}
                  {option.budget_type === 'balanced' && '⚖️'}
                  {option.budget_type === 'luxury' && '✨'}
                  {' '}{option.title}
                </h4>
                <span className="text-xl font-bold text-purple-600">
                  {option.currency} {option.total_cost.toLocaleString()}
                </span>
              </div>

              <div className="space-y-4">
                {option.days.map((day, dayIdx) => (
                  <div key={dayIdx} className="bg-gradient-to-r from-blue-50 to-purple-50 p-4 rounded-lg">
                    <h5 className="font-bold text-lg text-gray-800 mb-3">Day {day.day}</h5>
                    <div className="space-y-2 text-gray-700">
                      <p><span className="font-semibold">🌅 Morning:</span> {day.morning}</p>
                      <p><span className="font-semibold">☀️ Afternoon:</span> {day.afternoon}</p>
                      <p><span className="font-semibold">🌙 Evening:</span> {day.evening}</p>
                      <div className="mt-3 pt-3 border-t border-blue-200">
                        <p className="font-semibold mb-1">🍽️ Meals:</p>
                        <div className="grid grid-cols-3 gap-2 text-sm">
                          <span>🥐 {day.meals.breakfast}</span>
                          <span>🍱 {day.meals.lunch}</span>
                          <span>🍜 {day.meals.dinner}</span>
                        </div>
                      </div>
                      <p className="text-right font-semibold text-purple-600 mt-2">
                        ~{option.currency} {day.estimated_cost.toLocaleString()}/day
                      </p>
                    </div>
                  </div>
                ))}
              </div>

              <div className="mt-6 grid md:grid-cols-2 gap-6">
                <div>
                  <h5 className="font-bold text-gray-800 mb-2">🏨 Accommodations</h5>
                  <ul className="space-y-1 text-gray-700">
                    {option.accommodation_suggestions.map((hotel, i) => (
                      <li key={i}>• {hotel}</li>
                    ))}
                  </ul>
                </div>

                <div>
                  <h5 className="font-bold text-gray-800 mb-2">🎒 Packing List</h5>
                  <ul className="space-y-1 text-gray-700 text-sm">
                    {option.packing_list.slice(0, 5).map((item, i) => (
                      <li key={i}>• {item}</li>
                    ))}
                  </ul>
                </div>
              </div>

              <div className="mt-6">
                <h5 className="font-bold text-gray-800 mb-2">💡 Travel Tips</h5>
                <ul className="space-y-1 text-gray-700">
                  {option.tips.map((tip, i) => (
                    <li key={i}>• {tip}</li>
                  ))}
                </ul>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
