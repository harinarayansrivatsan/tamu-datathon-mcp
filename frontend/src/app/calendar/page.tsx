'use client'

import { useSession, signOut } from 'next-auth/react'
import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Separator } from '@/components/ui/separator'
import { Heart, Settings, LogOut, Calendar as CalendarIcon, Users, TrendingDown, TrendingUp, Loader2, ArrowLeft, Clock, ChevronRight } from 'lucide-react'
import Link from 'next/link'
import { apiFetch, syncAuthWithBackend } from '@/lib/api-client'
import { formatDistanceToNow, format } from 'date-fns'

interface CalendarEvent {
  id: string
  summary: string
  start: string
  end?: string
  attendees_count: number
  description?: string
}

interface CalendarData {
  past_events: CalendarEvent[]
  upcoming_events: CalendarEvent[]
  analysis: {
    total_events: number
    social_events: number
    social_frequency: number
    period_days: number
    declined_analysis?: {
      total_invitations: number
      declined_count: number
      decline_rate: number
    }
    friend_graph?: {
      total_unique_contacts: number
      top_contacts: Array<{
        name: string
        email: string
        count: number
      }>
    }
  }
  period: {
    days_back: number
    days_ahead: number
  }
}

export default function CalendarPage() {
  const { data: session } = useSession()
  const [calendarData, setCalendarData] = useState<CalendarData | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchCalendarData = async () => {
      if (!session) return

      setIsLoading(true)
      setError(null)

      try {
        // Sync auth first
        await syncAuthWithBackend(session)

        // Fetch calendar events
        const response = await apiFetch('/api/v1/user/calendar/events?days_back=30&days_ahead=14')

        if (response.ok) {
          const data = await response.json()
          setCalendarData(data)
        } else {
          const errorData = await response.json()
          setError(errorData.detail || 'Failed to load calendar events')
        }
      } catch (err) {
        console.error('Error fetching calendar:', err)
        setError('Network error. Please try again.')
      } finally {
        setIsLoading(false)
      }
    }

    fetchCalendarData()
  }, [session])

  const formatEventDate = (dateString: string) => {
    try {
      const date = new Date(dateString)
      return format(date, 'MMM d, yyyy h:mm a')
    } catch {
      return dateString
    }
  }

  const formatEventTime = (dateString: string) => {
    try {
      const date = new Date(dateString)
      return format(date, 'h:mm a')
    } catch {
      return dateString
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-secondary/10">
      {/* Header */}
      <header className="border-b bg-background/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4 flex justify-between items-center">
          <Link href="/dashboard" className="flex items-center space-x-2 hover:opacity-80 transition-opacity">
            <Heart className="h-6 w-6 text-primary" />
            <span className="text-xl font-semibold">LCE</span>
          </Link>

          <div className="flex items-center space-x-4">
            <Link href="/dashboard">
              <Button variant="ghost" size="sm">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Dashboard
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

      {/* Main Content */}
      <div className="container mx-auto px-6 py-8 max-w-6xl">
        <div className="mb-6">
          <h1 className="text-3xl font-bold flex items-center space-x-3">
            <CalendarIcon className="h-8 w-8 text-primary" />
            <span>Your Calendar</span>
          </h1>
          <p className="text-muted-foreground mt-2">
            View your social events and connection patterns
          </p>
        </div>

        {isLoading ? (
          <div className="flex items-center justify-center py-20">
            <div className="text-center space-y-4">
              <Loader2 className="h-12 w-12 animate-spin text-primary mx-auto" />
              <p className="text-muted-foreground">Loading your calendar...</p>
            </div>
          </div>
        ) : error ? (
          <Card className="border-primary/30 bg-primary/5">
            <CardContent className="pt-6">
              <div className="text-center space-y-4">
                <CalendarIcon className="h-16 w-16 text-primary/60 mx-auto" />
                <div>
                  <h3 className="font-semibold text-xl">Connect Your Calendar</h3>
                  <p className="text-sm text-muted-foreground mt-2 max-w-md mx-auto">
                    {error.includes('not enabled')
                      ? 'To help you stay connected, please grant access to your Google Calendar in Settings.'
                      : error}
                  </p>
                </div>
                <Link href="/settings">
                  <Button className="mt-2">
                    <Settings className="h-4 w-4 mr-2" />
                    Go to Settings to Connect
                  </Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        ) : calendarData ? (
          <div className="space-y-6">
            {/* Analytics Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <Card>
                <CardHeader className="pb-3">
                  <CardDescription className="text-xs">Social Events</CardDescription>
                  <CardTitle className="text-2xl">{calendarData.analysis.social_events}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-xs text-muted-foreground">
                    Last {calendarData.period.days_back} days
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-3">
                  <CardDescription className="text-xs">Events/Week</CardDescription>
                  <CardTitle className="text-2xl">{calendarData.analysis.social_frequency}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-xs text-muted-foreground">
                    Social frequency
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-3">
                  <CardDescription className="text-xs">Unique Contacts</CardDescription>
                  <CardTitle className="text-2xl">
                    {calendarData.analysis.friend_graph?.total_unique_contacts || 0}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-xs text-muted-foreground">
                    People you meet with
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-3">
                  <CardDescription className="text-xs">Decline Rate</CardDescription>
                  <CardTitle className="text-2xl">
                    {calendarData.analysis.declined_analysis?.decline_rate || 0}%
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-xs text-muted-foreground">
                    Declined invitations
                  </p>
                </CardContent>
              </Card>
            </div>

            {/* Upcoming Events */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Clock className="h-5 w-5 text-primary" />
                  <span>Upcoming Events</span>
                  <span className="text-sm font-normal text-muted-foreground">
                    (Next {calendarData.period.days_ahead} days)
                  </span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                {calendarData.upcoming_events.length === 0 ? (
                  <div className="text-center py-8">
                    <CalendarIcon className="h-12 w-12 text-muted-foreground/30 mx-auto mb-3" />
                    <p className="text-sm text-muted-foreground">
                      No upcoming social events found
                    </p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {calendarData.upcoming_events.map((event, index) => (
                      <div key={index} className="p-4 rounded-lg border bg-card hover:bg-accent/5 transition-colors">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <h4 className="font-semibold text-sm">{event.summary}</h4>
                            <div className="flex items-center space-x-4 mt-2 text-xs text-muted-foreground">
                              <span className="flex items-center">
                                <CalendarIcon className="h-3 w-3 mr-1" />
                                {formatEventDate(event.start)}
                              </span>
                              <span className="flex items-center">
                                <Users className="h-3 w-3 mr-1" />
                                {event.attendees_count} attendees
                              </span>
                            </div>
                          </div>
                          <ChevronRight className="h-4 w-4 text-muted-foreground" />
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Past Social Events */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <CalendarIcon className="h-5 w-5 text-primary" />
                  <span>Recent Social Events</span>
                  <span className="text-sm font-normal text-muted-foreground">
                    (Last {calendarData.period.days_back} days)
                  </span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                {calendarData.past_events.length === 0 ? (
                  <div className="text-center py-8">
                    <CalendarIcon className="h-12 w-12 text-muted-foreground/30 mx-auto mb-3" />
                    <p className="text-sm text-muted-foreground">
                      No past social events found
                    </p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {calendarData.past_events.slice(0, 10).map((event) => (
                      <div key={event.id} className="p-4 rounded-lg border bg-card hover:bg-accent/5 transition-colors">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <h4 className="font-semibold text-sm">{event.summary}</h4>
                            <div className="flex items-center space-x-4 mt-2 text-xs text-muted-foreground">
                              <span className="flex items-center">
                                <CalendarIcon className="h-3 w-3 mr-1" />
                                {formatEventDate(event.start)}
                              </span>
                              <span className="flex items-center">
                                <Users className="h-3 w-3 mr-1" />
                                {event.attendees_count} attendees
                              </span>
                            </div>
                            {event.description && (
                              <p className="text-xs text-muted-foreground mt-2 line-clamp-2">
                                {event.description}
                              </p>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Top Contacts */}
            {calendarData.analysis.friend_graph && calendarData.analysis.friend_graph.top_contacts.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Users className="h-5 w-5 text-primary" />
                    <span>Your Top Connections</span>
                  </CardTitle>
                  <CardDescription>People you meet with most often</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {calendarData.analysis.friend_graph.top_contacts.slice(0, 5).map((contact, index) => (
                      <div key={index} className="flex items-center justify-between p-3 rounded-lg border">
                        <div className="flex items-center space-x-3">
                          <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                            <span className="text-xs font-semibold text-primary">
                              {contact.name.charAt(0).toUpperCase()}
                            </span>
                          </div>
                          <div>
                            <p className="text-sm font-medium">{contact.name}</p>
                            <p className="text-xs text-muted-foreground">{contact.email}</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="text-sm font-semibold">{contact.count}</p>
                          <p className="text-xs text-muted-foreground">events</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        ) : null}
      </div>
    </div>
  )
}
