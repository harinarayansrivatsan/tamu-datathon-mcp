'use client'

import { useState, useEffect, useCallback } from 'react'

interface GeolocationCoordinates {
  latitude: number
  longitude: number
  accuracy: number
}

interface GeolocationState {
  coordinates: GeolocationCoordinates | null
  loading: boolean
  error: string | null
  isSupported: boolean
}

export function useGeolocation() {
  const [state, setState] = useState<GeolocationState>({
    coordinates: null,
    loading: false,
    error: null,
    isSupported: typeof window !== 'undefined' && 'geolocation' in navigator,
  })

  const requestLocation = useCallback(() => {
    if (!state.isSupported) {
      setState(prev => ({
        ...prev,
        error: 'Geolocation is not supported by your browser',
      }))
      return
    }

    setState(prev => ({ ...prev, loading: true, error: null }))

    navigator.geolocation.getCurrentPosition(
      (position) => {
        setState({
          coordinates: {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
            accuracy: position.coords.accuracy,
          },
          loading: false,
          error: null,
          isSupported: true,
        })
      },
      (error) => {
        let errorMessage = 'Failed to get location'
        
        switch (error.code) {
          case error.PERMISSION_DENIED:
            errorMessage = 'Location permission denied. Please enable location access in your browser settings.'
            break
          case error.POSITION_UNAVAILABLE:
            errorMessage = 'Location information is unavailable.'
            break
          case error.TIMEOUT:
            errorMessage = 'Location request timed out.'
            break
        }

        setState(prev => ({
          ...prev,
          loading: false,
          error: errorMessage,
        }))
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0,
      }
    )
  }, [state.isSupported])

  return {
    ...state,
    requestLocation,
  }
}

// Utility function to reverse geocode coordinates to city name
export async function reverseGeocode(lat: number, lng: number): Promise<string | null> {
  try {
    // Using Nominatim OpenStreetMap API (free, no API key required)
    const response = await fetch(
      `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&zoom=10&addressdetails=1`,
      {
        headers: {
          'User-Agent': 'LonelinessCombabtEngine/1.0',
        },
      }
    )

    if (!response.ok) {
      throw new Error('Geocoding failed')
    }

    const data = await response.json()
    
    // Extract city/town and state
    const address = data.address
    const city = address.city || address.town || address.village || address.county
    const state = address.state
    
    if (city && state) {
      return `${city}, ${state}`
    } else if (city) {
      return city
    }
    
    return null
  } catch (error) {
    console.error('Reverse geocoding error:', error)
    return null
  }
}
