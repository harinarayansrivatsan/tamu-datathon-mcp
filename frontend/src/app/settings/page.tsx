'use client'

import { useSession, signOut } from 'next-auth/react'
import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Input } from '@/components/ui/input'
import { Separator } from '@/components/ui/separator'
import { Heart, ArrowLeft, Calendar, Shield, AlertCircle, Loader2, MapPin, Sparkles, Navigation } from 'lucide-react'
import Link from 'next/link'
import { useGeolocation, reverseGeocode } from '@/hooks/useGeolocation'
import { apiFetch, syncAuthWithBackend } from '@/lib/api-client'

interface DataSource {
  id: string
  name: string
  description: string
  icon: React.ReactNode
  connected: boolean
  dataCollected: string[]
}

// Profile Preferences Component
function ProfilePreferences() {
  const { data: session } = useSession()
  const [interests, setInterests] = useState('')
  const [location, setLocation] = useState('')
  const [isSaving, setIsSaving] = useState(false)
  const [message, setMessage] = useState('')
  const [isDetectingLocation, setIsDetectingLocation] = useState(false)
  const { coordinates, loading: geoLoading, error: geoError, requestLocation, isSupported } = useGeolocation()

  useEffect(() => {
    // Sync auth with backend first
    const initAuth = async () => {
      if (session) {
        await syncAuthWithBackend(session)
        // Then fetch profile
        fetchProfile()
      }
    }
    initAuth()
  }, [session])

  const fetchProfile = async () => {
    try {
      const response = await apiFetch('/api/v1/user/me')
      if (response.ok) {
        const data = await response.json()
        setInterests(data.interests || '')
        setLocation(data.location || '')
      }
    } catch (error) {
      console.error('Error fetching profile:', error)
    }
  }

  // Handle geolocation result
  useEffect(() => {
    if (coordinates && isDetectingLocation) {
      const getCityName = async () => {
        const cityName = await reverseGeocode(coordinates.latitude, coordinates.longitude)
        if (cityName) {
          setLocation(cityName)
          setMessage('Location detected! Remember to save.')
        } else {
          setMessage('Could not determine city name. Please enter manually.')
        }
        setIsDetectingLocation(false)
      }
      getCityName()
    }
  }, [coordinates, isDetectingLocation])

  // Handle geolocation error
  useEffect(() => {
    if (geoError && isDetectingLocation) {
      setMessage(geoError)
      setIsDetectingLocation(false)
    }
  }, [geoError, isDetectingLocation])

  const handleDetectLocation = () => {
    setIsDetectingLocation(true)
    setMessage('')
    requestLocation()
  }

  const handleSave = async () => {
    setIsSaving(true)
    setMessage('')

    try {
      const response = await apiFetch('/api/v1/user/profile', {
        method: 'PATCH',
        body: JSON.stringify({ interests, location }),
      })

      if (response.ok) {
        setMessage('✓ Profile updated successfully!')
        setTimeout(() => setMessage(''), 3000)
      } else {
        const error = await response.json()
        setMessage(`Failed: ${error.detail || 'Unknown error'}`)
      }
    } catch (error) {
      console.error('Error updating profile:', error)
      setMessage('Network error - please check your connection')
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Your Preferences</CardTitle>
        <CardDescription>Help us personalize your experience</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <label className="text-sm font-medium flex items-center space-x-2">
            <Sparkles className="h-4 w-4 text-primary" />
            <span>Interests</span>
          </label>
          <Input
            placeholder="e.g., tech, music, sports, coffee, hiking"
            value={interests}
            onChange={(e) => setInterests(e.target.value)}
          />
          <p className="text-xs text-muted-foreground">
            Comma-separated interests help us recommend better events
          </p>
        </div>

        <div className="space-y-2">
          <label className="text-sm font-medium flex items-center space-x-2">
            <MapPin className="h-4 w-4 text-primary" />
            <span>Location</span>
          </label>
          <div className="flex space-x-2">
            <Input
              placeholder="e.g., College Station, TX"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              className="flex-1"
            />
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={handleDetectLocation}
              disabled={geoLoading || isDetectingLocation}
              className="px-3"
            >
              {geoLoading || isDetectingLocation ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Navigation className="h-4 w-4" />
              )}
            </Button>
          </div>
          <p className="text-xs text-muted-foreground">
            Your city helps us find local events and activities. Click the location icon to auto-detect.
          </p>
        </div>

        <div className="flex items-center justify-between pt-2">
          <span className="text-sm text-green-600">{message}</span>
          <Button
            onClick={handleSave}
            disabled={isSaving}
            size="sm"
          >
            {isSaving ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Saving...
              </>
            ) : (
              'Save Preferences'
            )}
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}

export default function Settings() {
  const { data: session } = useSession()
  const [calendarConnected, setCalendarConnected] = useState(false)
  const [spotifyConnected, setSpotifyConnected] = useState(false)
  const [isConnectingCalendar, setIsConnectingCalendar] = useState(false)
  const [isConnectingSpotify, setIsConnectingSpotify] = useState(false)
  const [successMessage, setSuccessMessage] = useState('')
  const [refetchTrigger, setRefetchTrigger] = useState(0)

  useEffect(() => {
    // Check for OAuth callback success
    const params = new URLSearchParams(window.location.search)
    if (params.get('calendar') === 'connected') {
      setSuccessMessage('Google Calendar connected successfully!')
      // Clean up URL
      window.history.replaceState({}, '', '/settings')
      // Trigger permission refetch
      setRefetchTrigger(prev => prev + 1)
      // Clear message after 3 seconds
      setTimeout(() => setSuccessMessage(''), 3000)
    }
    if (params.get('spotify') === 'connected') {
      setSuccessMessage('Spotify connected successfully!')
      window.history.replaceState({}, '', '/settings')
      // Trigger permission refetch
      setRefetchTrigger(prev => prev + 1)
      setTimeout(() => setSuccessMessage(''), 3000)
    }
  }, [])

  useEffect(() => {
    // Sync auth with backend first
    const initAuth = async () => {
      if (session) {
        await syncAuthWithBackend(session)
        // Then check connections
        checkConnections()
      }
    }
    initAuth()
  }, [session, refetchTrigger])

  const checkConnections = async () => {
    try {
      const response = await apiFetch('/api/v1/user/permissions')
      if (response.ok) {
        const data = await response.json()
        // Calendar is connected if it's enabled AND has a valid token
        setCalendarConnected(data.calendar_enabled === true && data.has_google_token === true)
        setSpotifyConnected(data.spotify_enabled === true && data.has_spotify_token === true)
      }
    } catch (error) {
      console.error('Error checking connections:', error)
    }
  }

  const handleCalendarToggle = async () => {
    setIsConnectingCalendar(true)

    try {
      const response = await apiFetch('/api/v1/user/permissions/calendar', {
        method: 'POST',
        body: JSON.stringify({
          enabled: !calendarConnected
        }),
      })

      const data = await response.json()

      if (data.needs_oauth && data.oauth_url) {
        // Redirect to Google OAuth for Calendar
        window.location.href = data.oauth_url
        return
      }

      if (response.ok && data.success) {
        setCalendarConnected(data.enabled)
      } else {
        alert('Failed to toggle calendar access')
      }
    } catch (error) {
      console.error('Error toggling calendar:', error)
      alert('Error toggling calendar access')
    } finally {
      setIsConnectingCalendar(false)
    }
  }

  const handleSpotifyToggle = async () => {
    setIsConnectingSpotify(true)

    try {
      const response = await apiFetch('/api/v1/user/permissions/spotify', {
        method: 'POST',
        body: JSON.stringify({
          enabled: !spotifyConnected
        }),
      })

      const data = await response.json()

      if (data.needs_oauth && data.oauth_url) {
        // Redirect to Spotify OAuth
        window.location.href = data.oauth_url
        return
      }

      if (response.ok && data.success) {
        setSpotifyConnected(data.enabled)
      } else {
        alert('Failed to toggle Spotify access')
      }
    } catch (error) {
      console.error('Error toggling Spotify:', error)
      alert('Error toggling Spotify access')
    } finally {
      setIsConnectingSpotify(false)
    }
  }

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
                Back to Chat
              </Button>
            </Link>
            <Avatar className="h-9 w-9">
              <AvatarImage src={session?.user?.image || ''} />
              <AvatarFallback className="text-xs">
                {session?.user?.name?.charAt(0) || 'U'}
              </AvatarFallback>
            </Avatar>
            <Button variant="ghost" size="sm" onClick={() => signOut()}>
              Sign Out
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="container mx-auto px-6 py-8 max-w-2xl space-y-6">

        {/* Success Message */}
        {successMessage && (
          <Card className="border-green-500 bg-green-50">
            <CardContent className="pt-6">
              <p className="text-sm font-medium text-green-700">{successMessage}</p>
            </CardContent>
          </Card>
        )}

        {/* Profile Section */}
        <Card>
          <CardHeader>
            <CardTitle>Account</CardTitle>
            <CardDescription>Your profile information</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center space-x-4">
              <Avatar className="h-16 w-16">
                <AvatarImage src={session?.user?.image || ''} />
                <AvatarFallback className="text-lg">
                  {session?.user?.name?.charAt(0) || 'U'}
                </AvatarFallback>
              </Avatar>
              <div className="flex-1">
                <h3 className="text-lg font-semibold">{session?.user?.name || 'User'}</h3>
                <p className="text-sm text-muted-foreground">{session?.user?.email}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Profile Preferences */}
        <ProfilePreferences />

        {/* Privacy Notice */}
        <Card className="border-primary/20 bg-primary/5">
          <CardHeader>
            <div className="flex items-center space-x-2">
              <Shield className="h-5 w-5 text-primary" />
              <CardTitle>Privacy & Data</CardTitle>
            </div>
          </CardHeader>
          <CardContent className="space-y-3 text-sm text-muted-foreground">
            <p>
              Your privacy is our top priority. LCE only accesses data you explicitly authorize.
            </p>
            <p>
              All data is encrypted and never shared with third parties.
            </p>
          </CardContent>
        </Card>

        {/* Google Calendar Integration */}
        <Card>
          <CardHeader>
            <CardTitle>Data Source</CardTitle>
            <CardDescription>Manage what LCE can analyze</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-start justify-between">
              <div className="flex items-start space-x-4 flex-1">
                <div className="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center text-blue-600 flex-shrink-0">
                  <Calendar className="h-5 w-5" />
                </div>
                <div className="flex-1 space-y-1">
                  <h4 className="font-semibold text-sm">Google Calendar</h4>
                  <p className="text-xs text-muted-foreground">
                    LCE analyzes your calendar to detect social connection patterns and calculate your wellness score.
                  </p>
                  <details className="text-xs mt-2">
                    <summary className="cursor-pointer text-primary hover:underline">
                      What data is collected?
                    </summary>
                    <ul className="mt-2 ml-4 list-disc text-muted-foreground space-y-1">
                      <li>Event titles</li>
                      <li>Event times and duration</li>
                      <li>Number of attendees</li>
                      <li>Whether it's a social event</li>
                    </ul>
                  </details>
                </div>
              </div>
              <Button
                variant={calendarConnected ? 'default' : 'outline'}
                size="sm"
                onClick={handleCalendarToggle}
                disabled={isConnectingCalendar}
                className="flex-shrink-0 ml-4"
              >
                {isConnectingCalendar ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    {calendarConnected ? 'Disconnecting...' : 'Connecting...'}
                  </>
                ) : (
                  calendarConnected ? 'Connected' : 'Connect'
                )}
              </Button>
            </div>

            <Separator className="my-4" />

            {/* Spotify Integration */}
            <div className="flex items-start justify-between">
              <div className="flex items-start space-x-4 flex-1">
                <div className="w-10 h-10 rounded-lg bg-green-100 flex items-center justify-center text-green-600 flex-shrink-0">
                  <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 0C5.4 0 0 5.4 0 12s5.4 12 12 12 12-5.4 12-12S18.66 0 12 0zm5.521 17.34c-.24.359-.66.48-1.021.24-2.82-1.74-6.36-2.101-10.561-1.141-.418.122-.779-.179-.899-.539-.12-.421.18-.78.54-.9 4.56-1.021 8.52-.6 11.64 1.32.42.18.479.659.301 1.02zm1.44-3.3c-.301.42-.841.6-1.262.3-3.239-1.98-8.159-2.58-11.939-1.38-.479.12-1.02-.12-1.14-.6-.12-.48.12-1.021.6-1.141C9.6 9.9 15 10.561 18.72 12.84c.361.181.54.78.241 1.2zm.12-3.36C15.24 8.4 8.82 8.16 5.16 9.301c-.6.179-1.2-.181-1.38-.721-.18-.601.18-1.2.72-1.381 4.26-1.26 11.28-1.02 15.721 1.621.539.3.719 1.02.419 1.56-.299.421-1.02.599-1.559.3z"/>
                  </svg>
                </div>
                <div className="flex-1 space-y-1">
                  <h4 className="font-semibold text-sm">Spotify</h4>
                  <p className="text-xs text-muted-foreground">
                    Analyze your music listening patterns to detect mood shifts and emotional well-being.
                  </p>
                  <details className="text-xs mt-2">
                    <summary className="cursor-pointer text-primary hover:underline">
                      What data is collected?
                    </summary>
                    <ul className="mt-2 ml-4 list-disc text-muted-foreground space-y-1">
                      <li>Recently played tracks</li>
                      <li>Audio features (valence, energy)</li>
                      <li>Listening time patterns</li>
                      <li>Music mood indicators</li>
                    </ul>
                  </details>
                </div>
              </div>
              <Button
                variant={spotifyConnected ? 'default' : 'outline'}
                size="sm"
                onClick={handleSpotifyToggle}
                disabled={isConnectingSpotify}
                className="flex-shrink-0 ml-4"
              >
                {isConnectingSpotify ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    {spotifyConnected ? 'Disconnecting...' : 'Connecting...'}
                  </>
                ) : (
                  spotifyConnected ? 'Connected' : 'Connect'
                )}
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Crisis Resources */}
        <Card className="border-orange-200 bg-orange-50">
          <CardHeader>
            <div className="flex items-center space-x-2">
              <AlertCircle className="h-5 w-5 text-orange-600" />
              <CardTitle className="text-orange-900">Crisis Resources</CardTitle>
            </div>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <p className="text-muted-foreground">
              LCE is not a replacement for professional mental health support. If you're in crisis:
            </p>
            <div className="space-y-2">
              <div className="p-3 bg-white rounded-lg border">
                <p className="font-semibold text-sm">988 Suicide & Crisis Lifeline</p>
                <p className="text-xs text-muted-foreground">Call or text 988 • Available 24/7</p>
              </div>
              <div className="p-3 bg-white rounded-lg border">
                <p className="font-semibold text-sm">TAMU Counseling Services</p>
                <p className="text-xs text-muted-foreground">(979) 845-4427</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Sign Out */}
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Session</CardTitle>
          </CardHeader>
          <CardContent>
            <Button variant="outline" className="w-full" onClick={() => signOut()}>
              Sign Out
            </Button>
          </CardContent>
        </Card>

      </div>
    </div>
  )
}
