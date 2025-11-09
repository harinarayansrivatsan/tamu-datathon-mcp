'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { MapPin, X, Loader2 } from 'lucide-react'
import { useGeolocation, reverseGeocode } from '@/hooks/useGeolocation'

interface LocationPermissionDialogProps {
  onClose: () => void
  onLocationSet: (location: string) => void
}

export function LocationPermissionDialog({ onClose, onLocationSet }: LocationPermissionDialogProps) {
  const [isDetecting, setIsDetecting] = useState(false)
  const { coordinates, loading, error, requestLocation, isSupported } = useGeolocation()

  // Handle geolocation success
  useEffect(() => {
    if (coordinates && isDetecting) {
      const getCityName = async () => {
        const cityName = await reverseGeocode(coordinates.latitude, coordinates.longitude)
        if (cityName) {
          // Save location to backend
          try {
            const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/user/profile`, {
              method: 'PATCH',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ location: cityName }),
            })
            
            if (response.ok) {
              onLocationSet(cityName)
              onClose()
            }
          } catch (error) {
            console.error('Error saving location:', error)
          }
        }
        setIsDetecting(false)
      }
      getCityName()
    }
  }, [coordinates, isDetecting, onClose, onLocationSet])

  const handleEnableLocation = () => {
    setIsDetecting(true)
    requestLocation()
  }

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <Card className="max-w-md w-full shadow-xl">
        <CardHeader>
          <div className="flex items-start justify-between">
            <div className="flex items-center space-x-2">
              <MapPin className="h-5 w-5 text-primary" />
              <CardTitle>Enable Location</CardTitle>
            </div>
            <Button variant="ghost" size="sm" className="h-6 w-6 p-0" onClick={onClose}>
              <X className="h-4 w-4" />
            </Button>
          </div>
          <CardDescription>
            Help us find local events and activities near you
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2 text-sm text-muted-foreground">
            <p>
              We'll use your location to:
            </p>
            <ul className="list-disc list-inside space-y-1 ml-2">
              <li>Recommend local social events</li>
              <li>Find nearby activities matching your interests</li>
              <li>Connect you with community resources</li>
            </ul>
            <p className="text-xs pt-2">
              Your location is stored securely and never shared without your permission.
            </p>
          </div>

          {error && (
            <div className="text-sm text-red-600 bg-red-50 p-3 rounded-md">
              {error}
            </div>
          )}

          <div className="flex space-x-2 pt-2">
            <Button
              onClick={handleEnableLocation}
              disabled={!isSupported || loading || isDetecting}
              className="flex-1"
            >
              {loading || isDetecting ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Detecting...
                </>
              ) : (
                <>
                  <MapPin className="h-4 w-4 mr-2" />
                  Enable Location
                </>
              )}
            </Button>
            <Button variant="outline" onClick={onClose} className="flex-1">
              Maybe Later
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
