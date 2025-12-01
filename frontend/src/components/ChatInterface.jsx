import { useState, useRef, useEffect } from 'react'
import axios from 'axios'

const API_URL = 'http://127.0.0.1:8001'

export default function ChatInterface({ sessionId, setSessionId }) {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [uploadingDoc, setUploadingDoc] = useState(false)
  const [error, setError] = useState(null)
  const messagesEndRef = useRef(null)
  const fileInputRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    // Add welcome message
    setMessages([{
      role: 'assistant',
      content: '👋 Welcome to your AI Travel Assistant!\n\nI\'m powered by Google Gemini 2.0 and can help you with:\n\n✈️ **Travel Planning**\n• Real-time weather forecasts for destinations\n• Hotel recommendations with pricing\n• Local attractions and must-visit places\n• Restaurant suggestions and local cuisine\n\n📚 **Document Analysis**\n• Upload travel documents (PDF, DOCX, TXT)\n• Ask questions about your uploaded files\n• Extract important information from documents\n\n💬 **Smart Conversations**\n• Answer travel-related questions\n• Provide travel tips and guides\n• Help with itinerary planning\n• Cultural insights and local customs\n\n🎯 **How to use:**\n1. Simply type your travel question below\n2. Or upload a document using the "Upload Document" button\n3. Ask me anything about your destination!\n\n**Try asking:**\n• "What\'s the weather like in Paris next week?"\n• "Recommend hotels in Tokyo under $100/night"\n• "What are the top attractions in Bali?"\n• "Best restaurants for vegetarian food in Rome"\n\nWhat would you like to know?'
    }])
  }, [])

  const sendMessage = async () => {
    if (!input.trim() || loading) return

    const userMessage = input.trim()
    setInput('')
    setError(null)
    setMessages(prev => [...prev, { role: 'user', content: userMessage }])
    setLoading(true)

    try {
      const response = await axios.post(`${API_URL}/chat`, {
        message: userMessage,
        session_id: sessionId
      }, {
        timeout: 60000 // 60 second timeout
      })

      setMessages(prev => [...prev, {
        role: 'assistant',
        content: response.data.message,
        sources: response.data.sources,
        tools: response.data.tool_calls
      }])

      if (response.data.session_id && !sessionId) {
        setSessionId(response.data.session_id)
      }
    } catch (error) {
      console.error('Chat error:', error)
      const errorMsg = error.response?.data?.detail || error.message || 'Unknown error'
      setError(errorMsg)
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `❌ Sorry, I encountered an error: ${errorMsg}\n\nPlease try again or rephrase your question.`
      }])
    } finally {
      setLoading(false)
    }
  }

  const uploadDocument = async (file) => {
    if (!file) return

    setUploadingDoc(true)
    const formData = new FormData()
    formData.append('file', file)
    if (sessionId) formData.append('session_id', sessionId)

    try {
      const response = await axios.post(`${API_URL}/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })

      if (response.data.status === 'success') {
        setMessages(prev => [...prev, {
          role: 'system',
          content: `✅ Document uploaded: ${response.data.filename} (${response.data.chunks} chunks processed)`
        }])

        const newSessionId = response.data.message.split('Session ID: ')[1]
        if (newSessionId && !sessionId) {
          setSessionId(newSessionId)
        }
      }
    } catch (error) {
      setMessages(prev => [...prev, {
        role: 'system',
        content: `❌ Failed to upload document: ${error.response?.data?.detail || error.message}`
      }])
    } finally {
      setUploadingDoc(false)
    }
  }

  return (
    <div className="card max-w-5xl mx-auto animate-fadeIn">
      <div className="mb-6 flex items-center justify-between border-b pb-4">
        <div>
          <h2 className="text-3xl font-bold text-gray-800 mb-1">💬 AI Travel Chat</h2>
          <p className="text-sm text-gray-600">Powered by Google Gemini 2.0 • Real-time assistance</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={uploadingDoc}
            className="btn-secondary text-sm flex items-center gap-2"
          >
            {uploadingDoc ? (
              <>
                <span className="animate-spin">⏳</span>
                Uploading...
              </>
            ) : (
              <>
                📎 Upload Document
              </>
            )}
          </button>
          <button
            onClick={() => {
              setMessages([{
                role: 'assistant',
                content: '👋 Welcome to your AI Travel Assistant!\n\nI\'m powered by Google Gemini 2.0 and can help you with:\n\n✈️ **Travel Planning**\n• Real-time weather forecasts for destinations\n• Hotel recommendations with pricing\n• Local attractions and must-visit places\n• Restaurant suggestions and local cuisine\n\n📚 **Document Analysis**\n• Upload travel documents (PDF, DOCX, TXT)\n• Ask questions about your uploaded files\n• Extract important information from documents\n\n💬 **Smart Conversations**\n• Answer travel-related questions\n• Provide travel tips and guides\n• Help with itinerary planning\n• Cultural insights and local customs\n\n🎯 **How to use:**\n1. Simply type your travel question below\n2. Or upload a document using the "Upload Document" button\n3. Ask me anything about your destination!\n\n**Try asking:**\n• "What\'s the weather like in Paris next week?"\n• "Recommend hotels in Tokyo under $100/night"\n• "What are the top attractions in Bali?"\n• "Best restaurants for vegetarian food in Rome"\n\nWhat would you like to know?'
              }])
              setSessionId(null)
            }}
            className="btn-secondary text-sm"
            title="Start new conversation"
          >
            🔄 Reset
          </button>
        </div>
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.docx,.txt"
          onChange={(e) => e.target.files[0] && uploadDocument(e.target.files[0])}
          className="hidden"
        />
      </div>

      <div className="bg-gradient-to-br from-gray-50 to-blue-50 rounded-xl p-6 h-[550px] overflow-y-auto mb-4 space-y-4 shadow-inner border border-gray-200">
        {messages.length === 0 && (
          <div className="text-center text-gray-400 mt-32 animate-fadeIn">
            <div className="text-6xl mb-4">🌍</div>
            <p className="text-xl font-semibold text-gray-600">Start Your Journey</p>
            <p className="mt-2 text-sm">Ask me anything about travel destinations, hotels, weather, or attractions!</p>
          </div>
        )}

        {messages.map((msg, idx) => (
          <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-slideUp`}>
            <div
              className={`max-w-[80%] p-5 rounded-2xl shadow-lg transform transition-all hover:scale-[1.01] ${
                msg.role === 'user'
                  ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white'
                  : msg.role === 'system'
                  ? 'bg-gradient-to-r from-yellow-100 to-orange-100 text-gray-800 border-2 border-yellow-400'
                  : 'bg-white text-gray-800 border-2 border-gray-200'
              }`}
            >
              <div className="flex items-start gap-3">
                <div className={`text-3xl ${msg.role === 'user' ? 'mt-1' : ''}`}>
                  {msg.role === 'user' ? '👤' : msg.role === 'system' ? '📋' : '🤖'}
                </div>
                <div className="flex-1">
                  <p className="whitespace-pre-wrap leading-relaxed text-[15px]">{msg.content}</p>
                  
                  {msg.tools && msg.tools.length > 0 && (
                    <div className="mt-4 pt-3 border-t border-gray-300">
                      <p className="text-xs opacity-75 flex items-center gap-2">
                        <span>🔧</span>
                        <span className="font-semibold">Tools Used:</span>
                        <span>{msg.tools.join(', ')}</span>
                      </p>
                    </div>
                  )}

                  {msg.sources && msg.sources.length > 0 && (
                    <div className="mt-3 pt-3 border-t border-gray-300">
                      <p className="text-xs opacity-75 flex items-center gap-2">
                        <span>📚</span>
                        <span className="font-semibold">Sources:</span>
                        <span>{msg.sources.length} references found</span>
                      </p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-white p-5 rounded-2xl shadow-lg border-2 border-blue-200">
              <div className="flex items-center gap-3">
                <div className="flex space-x-2">
                  <div className="w-3 h-3 bg-blue-500 rounded-full animate-bounce"></div>
                  <div className="w-3 h-3 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-3 h-3 bg-pink-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
                <span className="text-sm text-gray-600 font-medium">AI is thinking...</span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="space-y-3">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
            placeholder="💬 Ask me anything about travel destinations, hotels, weather, attractions..."
            className="input-field flex-1 text-base py-4"
            disabled={loading}
          />
          <button
            onClick={sendMessage}
            disabled={loading || !input.trim()}
            className="btn-primary px-8 text-lg"
          >
            {loading ? '⏳' : '📤'} Send
          </button>
        </div>

        <div className="flex items-center justify-between text-xs text-gray-500">
          <div className="flex items-center gap-4">
            {sessionId && (
              <span className="bg-gray-100 px-3 py-1 rounded-full">
                🔗 Session: {sessionId.substring(0, 8)}...
              </span>
            )}
            <span className="bg-green-100 text-green-700 px-3 py-1 rounded-full font-medium">
              ✓ AI Online
            </span>
          </div>
          <span className="text-gray-400">
            Press Enter to send • Powered by Gemini 2.0
          </span>
        </div>
      </div>
    </div>
  )
}
