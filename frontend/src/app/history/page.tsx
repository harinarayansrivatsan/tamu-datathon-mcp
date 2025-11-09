'use client'

import { useSession } from 'next-auth/react'
import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Heart, ArrowLeft, MessageSquare, Loader2, TrendingDown, TrendingUp } from 'lucide-react'
import Link from 'next/link'
import { apiFetch } from '@/lib/api-client'

interface Intervention {
  id: string
  risk_score: number
  risk_level: string
  suggestion: string
  created_at: string
  event_id?: string
}

export default function HistoryPage() {
  const { data: session } = useSession()
  const [interventions, setInterventions] = useState<Intervention[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchHistory = async () => {
      setIsLoading(true)

      try {
        const response = await apiFetch('/api/v1/interventions/history?limit=20')

        if (response.ok) {
          const data = await response.json()
          setInterventions(data.interventions || [])
        }
      } catch (error) {
        console.error('Error fetching history:', error)
      } finally {
        setIsLoading(false)
      }
    }

    if (session) {
      fetchHistory()
    }
  }, [session])

  const getWellnessColor = (riskScore: number) => {
    const wellness = 100 - riskScore
    if (wellness >= 75) return 'text-green-600 bg-green-50'
    if (wellness >= 50) return 'text-blue-600 bg-blue-50'
    if (wellness >= 25) return 'text-yellow-600 bg-yellow-50'
    return 'text-red-600 bg-red-50'
  }

  const getWellnessLabel = (riskScore: number) => {
    const wellness = 100 - riskScore
    if (wellness >= 75) return 'Excellent'
    if (wellness >= 50) return 'Good'
    if (wellness >= 25) return 'Needs Attention'
    return 'Critical'
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
          <h1 className="text-3xl font-bold mb-2">Intervention History</h1>
          <p className="text-muted-foreground">
            Your past assessments and suggestions
          </p>
        </div>

        {isLoading ? (
          <div className="flex justify-center items-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
          </div>
        ) : interventions.length === 0 ? (
          <Card>
            <CardContent className="pt-6 text-center">
              <MessageSquare className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
              <p className="text-sm text-muted-foreground">
                No interventions yet. Start a conversation to get personalized support.
              </p>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-4">
            {interventions.map((intervention) => (
              <Card key={intervention.id}>
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <div>
                      <CardTitle className="text-base">
                        {new Date(intervention.created_at).toLocaleDateString('en-US', {
                          weekday: 'long',
                          month: 'long',
                          day: 'numeric',
                          year: 'numeric',
                        })}
                      </CardTitle>
                      <CardDescription>
                        {new Date(intervention.created_at).toLocaleTimeString('en-US', {
                          hour: 'numeric',
                          minute: '2-digit',
                        })}
                      </CardDescription>
                    </div>
                    <div className={`px-3 py-1 rounded-full text-xs font-medium ${getWellnessColor(intervention.risk_score)}`}>
                      {getWellnessLabel(intervention.risk_score)} ({100 - intervention.risk_score})
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    {intervention.suggestion}
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
