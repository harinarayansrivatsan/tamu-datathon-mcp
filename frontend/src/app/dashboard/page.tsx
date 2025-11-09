'use client'

import { useSession, signOut } from 'next-auth/react'
import { useState, useRef, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Separator } from '@/components/ui/separator'
import { Heart, Settings, LogOut, Send, User, Bot, Loader2, TrendingUp, MessageCircle, X, Minimize2, Calendar, MessageSquare } from 'lucide-react'
import Link from 'next/link'
import { LocationPermissionDialog } from '@/components/LocationPermissionDialog'
import { apiFetch, syncAuthWithBackend } from '@/lib/api-client'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  suggestions?: string[]
  activities?: any[]
}

export default function Dashboard() {
  const { data: session } = useSession()
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: "Hey! I'm here to listen and support you. How are you feeling today?",
      timestamp: new Date(),
    },
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [wellnessScore, setWellnessScore] = useState<number | null>(null)
  const [isLoadingScore, setIsLoadingScore] = useState(true)
  const [showLocationDialog, setShowLocationDialog] = useState(false)
  const [userLocation, setUserLocation] = useState<string | null>(null)
  const [isChatOpen, setIsChatOpen] = useState(false)
  const [baselineStatus, setBaselineStatus] = useState<{
    established: boolean
    message?: string
  } | null>(null)
  const [calendarConnected, setCalendarConnected] = useState(false)
  const scrollAreaRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (scrollAreaRef.current && isChatOpen) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight
    }
  }, [messages, isChatOpen])

  useEffect(() => {
    // Sync NextAuth session with backend
    const syncAuth = async () => {
      if (session) {
        await syncAuthWithBackend(session)
      }
    }
    syncAuth()
  }, [session])

  useEffect(() => {
    // Fetch user profile and check if location is set
    const fetchUserProfile = async () => {
      if (!session) return
      
      try {
        const response = await apiFetch('/api/v1/user/me')
        if (response.ok) {
          const data = await response.json()
          setUserLocation(data.location)
          
          // Show location dialog if user doesn't have location set
          // Only show once per session using sessionStorage
          const hasSeenLocationPrompt = sessionStorage.getItem('hasSeenLocationPrompt')
          if (!data.location && !hasSeenLocationPrompt) {
            // Delay showing the dialog slightly so it doesn't appear immediately
            setTimeout(() => {
              setShowLocationDialog(true)
              sessionStorage.setItem('hasSeenLocationPrompt', 'true')
            }, 2000)
          }
        }
      } catch (error) {
        console.error('Error fetching user profile:', error)
      }
    }

    fetchUserProfile()
  }, [session])

  useEffect(() => {
    // Fetch real wellness score from backend
    const fetchWellnessScore = async () => {
      if (!session) return

      try {
        const response = await apiFetch('/api/v1/user/wellness-score')
        if (response.ok) {
          const data = await response.json()
          if (data.score !== null) {
            setWellnessScore(data.score)
          }
        }
      } catch (error) {
        console.error('Error fetching wellness score:', error)
      } finally {
        setIsLoadingScore(false)
      }
    }

    fetchWellnessScore()
  }, [session])

  useEffect(() => {
    const fetchBaseline = async () => {
      if (!session) return

      try {
        const response = await apiFetch('/api/v1/user/baseline')
        if (response.ok) {
          const data = await response.json()
          setBaselineStatus(data)
        }
      } catch (error) {
        console.error('Error fetching baseline:', error)
      }
    }

    fetchBaseline()
  }, [session])

  useEffect(() => {
    const checkCalendarConnection = async () => {
      if (!session) return

      try {
        const response = await apiFetch('/api/v1/user/permissions')
        if (response.ok) {
          const data = await response.json()
          setCalendarConnected(data.calendar_enabled === true || data.calendar_enabled === 'true')
        }
      } catch (error) {
        console.error('Error checking calendar connection:', error)
      }
    }

    checkCalendarConnection()
  }, [session])

  const handleSend = async () => {
    if (!input.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date(),
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      const response = await apiFetch('/api/v1/chat', {
        method: 'POST',
        body: JSON.stringify({
          message: input,
          userId: session?.user?.id,
        }),
      })

      const data = await response.json()

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.response || "I appreciate you sharing. Tell me more if you'd like.",
        timestamp: new Date(),
        suggestions: data.suggestions || [],
        activities: data.activities || [],
      }

      setMessages(prev => [...prev, assistantMessage])
      
      // Update wellness score if provided
      if (data.risk_score !== undefined && data.risk_score !== null) {
        const wellness = 100 - data.risk_score
        setWellnessScore(wellness)
      }
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: "I'm having trouble connecting right now. Please try again in a moment.",
        timestamp: new Date(),
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const getWellnessInterpretation = (score: number) => {
    if (score >= 71) return "You're maintaining strong social connections!"
    if (score >= 50) return "Your social wellness is moderate. Consider reaching out to friends."
    return "Your social connections could use more attention right now."
  }

  return (
    <div className="h-screen flex flex-col bg-gradient-to-b from-background to-secondary/10">
      {/* Header */}
      <header className="border-b bg-background/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4 flex justify-between items-center">
          <Link href="/dashboard" className="flex items-center space-x-2 hover:opacity-80 transition-opacity">
            <Heart className="h-6 w-6 text-primary" />
            <span className="text-xl font-semibold">LCE</span>
          </Link>

          <div className="flex items-center space-x-4">
            <Link href="/calendar">
              <Button variant="ghost" size="sm">
                <Calendar className="h-4 w-4 mr-2" />
                Calendar
              </Button>
            </Link>
            <Link href="/events">
              <Button variant="ghost" size="sm">
                <Calendar className="h-4 w-4 mr-2" />
                Events
              </Button>
            </Link>
            <Link href="/history">
              <Button variant="ghost" size="sm">
                <MessageSquare className="h-4 w-4 mr-2" />
                History
              </Button>
            </Link>
            <Link href="/settings">
              <Button variant="ghost" size="sm">
                <Settings className="h-4 w-4 mr-2" />
                Settings
              </Button>
            </Link>
            <Avatar className="h-9 w-9">
              <AvatarImage src={session?.user?.image || ''} />
              <AvatarFallback className="text-xs">
                {session?.user?.name?.charAt(0) || 'U'}
              </AvatarFallback>
            </Avatar>
            <Button variant="ghost" size="sm" onClick={() => signOut()}>
              <LogOut className="h-4 w-4 mr-2" />
              Sign Out
            </Button>
          </div>
        </div>
      </header>

      {/* Main Dashboard Content */}
      <div className="flex-1 container mx-auto px-6 py-8 max-w-6xl">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          
          {/* Wellness Score Card */}
          <Card className="col-span-1">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-lg">Social Wellness</CardTitle>
                  <CardDescription className="text-xs">How you're doing socially</CardDescription>
                </div>
                <TrendingUp className="h-5 w-5 text-primary opacity-50" />
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-center">
                {isLoadingScore ? (
                  <div className="flex flex-col items-center justify-center space-y-2">
                    <Loader2 className="h-12 w-12 animate-spin text-primary" />
                    <p className="text-xs text-muted-foreground">Calculating your wellness...</p>
                  </div>
                ) : wellnessScore === null ? (
                  <div className="text-center space-y-2">
                    <p className="text-sm text-muted-foreground">No data yet</p>
                    <p className="text-xs text-muted-foreground">Connect your calendar to see your score</p>
                  </div>
                ) : (
                  <div className="relative w-28 h-28">
                    <svg className="w-full h-full transform -rotate-90">
                      <circle
                        cx="56"
                        cy="56"
                        r="50"
                        stroke="currentColor"
                        strokeWidth="6"
                        fill="none"
                        className="text-secondary"
                      />
                      <circle
                        cx="56"
                        cy="56"
                        r="50"
                        stroke="currentColor"
                        strokeWidth="6"
                        fill="none"
                        strokeDasharray={`${2 * Math.PI * 50}`}
                        strokeDashoffset={`${2 * Math.PI * 50 * (1 - wellnessScore / 100)}`}
                        className="text-primary transition-all duration-500"
                      />
                    </svg>
                    <div className="absolute inset-0 flex items-center justify-center">
                      <span className="text-2xl font-bold">{wellnessScore}</span>
                    </div>
                  </div>
                )}
              </div>
              {!isLoadingScore && wellnessScore !== null && (
                <div className="text-center space-y-2">
                  <p className="text-sm font-medium text-foreground">
                    {getWellnessInterpretation(wellnessScore)}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    Updated from your calendar activity
                  </p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* How It Works Card */}
          <Card className="col-span-1">
            <CardHeader>
              <CardTitle className="text-sm">How It Works</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-xs text-muted-foreground">
              <p>
                LCE analyzes your calendar to detect social connection patterns.
              </p>

              {baselineStatus && !baselineStatus.established && (
                <div className="p-2 bg-blue-50 border border-blue-200 rounded text-blue-900">
                  <p className="font-medium">Learning your patterns...</p>
                  <p className="mt-1">{baselineStatus.message}</p>
                </div>
              )}

              {baselineStatus && baselineStatus.established && (
                <div className="p-2 bg-green-50 border border-green-200 rounded text-green-900">
                  <p className="font-medium">✓ Baseline established</p>
                  <p className="mt-1">Monitoring your social patterns</p>
                </div>
              )}

              <p>
                Go to <Link href="/settings" className="text-primary hover:underline">Settings</Link> to manage data access.
              </p>
            </CardContent>
          </Card>

          {/* Quick Stats Card */}
          <Card className="col-span-1">
            <CardHeader>
              <CardTitle className="text-sm">Quick Stats</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-xs text-muted-foreground">Calendar Connected</span>
                <span className="text-xs font-medium">{calendarConnected ? 'Yes' : 'No'}</span>
              </div>
              <Separator />
              <div className="flex justify-between items-center">
                <span className="text-xs text-muted-foreground">Location Set</span>
                <span className="text-xs font-medium">{userLocation ? 'Yes' : 'No'}</span>
              </div>
              <Separator />
              {calendarConnected && (
                <>
                  <Link href="/calendar">
                    <Button variant="outline" size="sm" className="w-full text-xs">
                      <Calendar className="h-3 w-3 mr-2" />
                      View Calendar
                    </Button>
                  </Link>
                </>
              )}
            </CardContent>
          </Card>

        </div>
      </div>

      {/* Floating Chat Widget */}
      {isChatOpen ? (
        <div className="fixed bottom-6 right-6 w-96 h-[500px] shadow-2xl rounded-lg border bg-background flex flex-col z-50">
          {/* Chat Header */}
          <div className="border-b p-4 flex items-center justify-between bg-primary/5 rounded-t-lg">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                <Bot className="h-4 w-4 text-primary" />
              </div>
              <div>
                <h3 className="text-sm font-semibold">LCE Support</h3>
                <p className="text-xs text-muted-foreground">Always here to listen</p>
              </div>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsChatOpen(false)}
              className="h-8 w-8 p-0"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>

          {/* Chat Messages */}
          <ScrollArea className="flex-1 p-4" ref={scrollAreaRef}>
            <div className="space-y-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex gap-2 ${
                    message.role === 'user' ? 'flex-row-reverse' : 'flex-row'
                  }`}
                >
                  <Avatar className="h-6 w-6 flex-shrink-0">
                    {message.role === 'user' ? (
                      <>
                        <AvatarImage src={session?.user?.image || ''} />
                        <AvatarFallback className="text-xs">
                          <User className="h-3 w-3" />
                        </AvatarFallback>
                      </>
                    ) : (
                      <AvatarFallback className="bg-primary/10 text-xs">
                        <Bot className="h-3 w-3 text-primary" />
                      </AvatarFallback>
                    )}
                  </Avatar>

                  <div
                    className={`flex-1 max-w-[80%] ${
                      message.role === 'user' ? 'items-end' : 'items-start'
                    } flex flex-col`}
                  >
                    <div
                      className={`rounded-lg p-2 ${
                        message.role === 'user'
                          ? 'bg-primary text-primary-foreground'
                          : 'bg-muted text-foreground'
                      }`}
                    >
                      <p className="text-xs leading-relaxed break-words">{message.content}</p>

                      {/* Suggestions Display */}
                      {message.role === 'assistant' && message.suggestions && message.suggestions.length > 0 && (
                        <div className="mt-3 pt-3 border-t border-border/50">
                          <p className="text-xs font-semibold mb-2">Suggestions:</p>
                          <ul className="space-y-1">
                            {message.suggestions.map((suggestion, idx) => (
                              <li key={idx} className="text-xs flex items-start">
                                <span className="mr-2">•</span>
                                <span>{suggestion}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Activities Link */}
                      {message.role === 'assistant' && message.activities && message.activities.length > 0 && (
                        <div className="mt-2">
                          <Link href="/events">
                            <Button size="sm" variant="outline" className="text-xs h-7">
                              View {message.activities.length} recommended events
                            </Button>
                          </Link>
                        </div>
                      )}
                    </div>
                    <span className="text-xs text-muted-foreground mt-1">
                      {message.timestamp.toLocaleTimeString([], {
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </span>
                  </div>
                </div>
              ))}

              {isLoading && (
                <div className="flex gap-2">
                  <Avatar className="h-6 w-6 flex-shrink-0">
                    <AvatarFallback className="bg-primary/10 text-xs">
                      <Bot className="h-3 w-3 text-primary" />
                    </AvatarFallback>
                  </Avatar>
                  <div className="bg-muted rounded-lg p-2">
                    <Loader2 className="h-3 w-3 animate-spin text-primary" />
                  </div>
                </div>
              )}
            </div>
          </ScrollArea>

          <Separator />

          {/* Input Area */}
          <div className="p-3">
            <div className="flex gap-2">
              <Input
                placeholder="How are you feeling?"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                disabled={isLoading}
                className="flex-1 text-sm"
              />
              <Button
                onClick={handleSend}
                disabled={!input.trim() || isLoading}
                size="sm"
                className="flex-shrink-0"
              >
                <Send className="h-3 w-3" />
              </Button>
            </div>
          </div>
        </div>
      ) : (
        <button
          onClick={() => setIsChatOpen(true)}
          className="fixed bottom-6 right-6 w-14 h-14 rounded-full bg-primary text-primary-foreground shadow-lg hover:shadow-xl transition-all hover:scale-110 flex items-center justify-center z-50"
        >
          <MessageCircle className="h-6 w-6" />
        </button>
      )}

      {/* Location Permission Dialog */}
      {showLocationDialog && (
        <LocationPermissionDialog
          onClose={() => setShowLocationDialog(false)}
          onLocationSet={(location) => setUserLocation(location)}
        />
      )}
    </div>
  )
}
