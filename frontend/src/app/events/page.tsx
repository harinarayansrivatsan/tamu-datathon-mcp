'use client'

import { useSession } from 'next-auth/react'
import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Separator } from '@/components/ui/separator'
import { Heart, ArrowLeft, Calendar, MapPin, Users, ExternalLink, Loader2 } from 'lucide-react'
import Link from 'next/link'
import { apiFetch } from '@/lib/api-client'

interface Event {
  id: string
  title: string
  description: string
  date: string
  location: string
  url: string
  source: string
  anxiety_match: string
  interest_match: string[]
}

export default function EventsPage() {
  const { data: session } = useSession()
  const [events, setEvents] = useState<Event[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchEvents = async () => {
      setIsLoading(true)
      setError(null)

      try {
        const response = await apiFetch('/api/v1/events/recommended')

        if (response.ok) {
          const data = await response.json()

          if (data.message) {
            setError(data.message)
          } else {
            setEvents(data.events || [])
          }
        } else {
          setError('Failed to load events')
        }
      } catch (err) {
        console.error('Error fetching events:', err)
        setError('Error loading events')
      } finally {
        setIsLoading(false)
      }
    }

    if (session) {
      fetchEvents()
    }
  }, [session])

  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-secondary/10">
      {/* Header */}
      <header className="border-b bg-background/80 backdrop-blur-sm">
        <div className="container mx-auto px-6 py-4 flex justify-between items-center">
          <Link href="/dashboard" className="flex items-center space-x-2 hover:opacity-80 transition-opacity">
            <Heart className="h-6 w-6 text-primary" />
            <span className="text-xl font-semibold">LCE</span>
          </Link>

          <div className="flex items-center space-x-4">
            <Link href="/dashboard">
              <Button variant="ghost" size="sm">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Dashboard
              </Button>
            </Link>
            <Avatar className="h-9 w-9">
              <AvatarImage src={session?.user?.image || ''} />
              <AvatarFallback className="text-xs">
                {session?.user?.name?.charAt(0) || 'U'}
              </AvatarFallback>
            </Avatar>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="container mx-auto px-6 py-8 max-w-4xl">
        <div className="mb-6">
          <h1 className="text-3xl font-bold mb-2">Recommended Events</h1>
          <p className="text-muted-foreground">
            Events matched to your interests and comfort level
          </p>
        </div>

        {isLoading ? (
          <div className="flex justify-center items-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
          </div>
        ) : error ? (
          <Card className="border-orange-200 bg-orange-50">
            <CardContent className="pt-6">
              <p className="text-sm text-orange-900">{error}</p>
              <p className="text-xs text-muted-foreground mt-2">
                Add your interests and location in{' '}
                <Link href="/settings" className="text-primary hover:underline">
                  Settings
                </Link>{' '}
                to get personalized recommendations.
              </p>
            </CardContent>
          </Card>
        ) : events.length === 0 ? (
          <Card>
            <CardContent className="pt-6 text-center">
              <p className="text-sm text-muted-foreground">
                No events found matching your preferences.
              </p>
              <p className="text-xs text-muted-foreground mt-2">
                Try updating your interests in{' '}
                <Link href="/settings" className="text-primary hover:underline">
                  Settings
                </Link>
              </p>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-4">
            {events.map((event) => (
              <Card key={event.id} className="hover:shadow-md transition-shadow">
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <CardTitle className="text-lg">{event.title}</CardTitle>
                      <CardDescription className="mt-1">
                        {event.description}
                      </CardDescription>
                    </div>
                    {event.anxiety_match && (
                      <span className="ml-4 px-2 py-1 text-xs rounded-full bg-primary/10 text-primary">
                        {event.anxiety_match} anxiety
                      </span>
                    )}
                  </div>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex items-center text-sm text-muted-foreground">
                    <Calendar className="h-4 w-4 mr-2" />
                    {new Date(event.date).toLocaleDateString('en-US', {
                      weekday: 'short',
                      month: 'short',
                      day: 'numeric',
                      hour: 'numeric',
                      minute: '2-digit',
                    })}
                  </div>

                  <div className="flex items-center text-sm text-muted-foreground">
                    <MapPin className="h-4 w-4 mr-2" />
                    {event.location}
                  </div>

                  {event.interest_match && event.interest_match.length > 0 && (
                    <div className="flex items-start text-sm text-muted-foreground">
                      <Users className="h-4 w-4 mr-2 mt-0.5" />
                      <div className="flex flex-wrap gap-1">
                        {event.interest_match.map((interest) => (
                          <span
                            key={interest}
                            className="px-2 py-0.5 text-xs rounded bg-secondary text-foreground"
                          >
                            {interest}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  <Separator className="my-3" />

                  <div className="flex items-center justify-between">
                    <span className="text-xs text-muted-foreground">
                      via {event.source}
                    </span>
                    {event.url && (
                      <Button size="sm" variant="outline" asChild>
                        <a href={event.url} target="_blank" rel="noopener noreferrer">
                          View Details
                          <ExternalLink className="h-3 w-3 ml-2" />
                        </a>
                      </Button>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
