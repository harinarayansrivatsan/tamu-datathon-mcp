'use client'

import { useSession, signIn } from 'next-auth/react'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Heart, Shield, MessageSquare, Lightbulb } from 'lucide-react'

export default function Home() {
  const { data: session, status } = useSession()
  const router = useRouter()

  useEffect(() => {
    if (status === 'authenticated') {
      router.push('/dashboard')
    }
  }, [status, router])

  if (status === 'loading') {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-pulse text-primary text-lg">Loading...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-background via-background to-secondary/20 flex flex-col">
      {/* Header */}
      <header className="border-b bg-background/50 backdrop-blur-sm">
        <div className="container mx-auto px-6 py-4 flex items-center space-x-2">
          <Heart className="h-6 w-6 text-primary" />
          <span className="text-xl font-semibold">LCE</span>
        </div>
      </header>

      {/* Hero Section */}
      <section className="flex-1 container mx-auto px-6 py-20 flex items-center justify-center">
        <div className="max-w-2xl mx-auto text-center space-y-8">
          <div className="space-y-4">
            <h1 className="text-5xl md:text-6xl font-bold tracking-tight leading-tight">
              You're Never Alone in{' '}
              <span className="text-primary">Your Journey</span>
            </h1>
            <p className="text-lg text-muted-foreground leading-relaxed">
              An empathetic AI companion that listens and helps you build meaningful social connections.
            </p>
          </div>

          {/* Value Props - Simple 3 column */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 py-8 text-left">
            <div className="p-4 rounded-lg bg-secondary/30 space-y-2">
              <MessageSquare className="h-5 w-5 text-primary" />
              <h3 className="font-semibold text-sm">Talk Freely</h3>
              <p className="text-xs text-muted-foreground">Share how you're feeling without judgment.</p>
            </div>
            <div className="p-4 rounded-lg bg-secondary/30 space-y-2">
              <Lightbulb className="h-5 w-5 text-primary" />
              <h3 className="font-semibold text-sm">Get Support</h3>
              <p className="text-xs text-muted-foreground">Receive compassionate guidance and suggestions.</p>
            </div>
            <div className="p-4 rounded-lg bg-secondary/30 space-y-2">
              <Shield className="h-5 w-5 text-primary" />
              <h3 className="font-semibold text-sm">Privacy First</h3>
              <p className="text-xs text-muted-foreground">You control what data we access.</p>
            </div>
          </div>

          {/* CTA */}
          <div className="pt-4">
            <Button
              size="lg"
              onClick={() => signIn('google')}
              className="text-base px-10 py-6"
            >
              <svg className="mr-2 h-5 w-5" viewBox="0 0 24 24">
                <path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                <path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                <path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                <path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
              </svg>
              Sign in with Google
            </Button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t mt-auto">
        <div className="container mx-auto px-6 py-8">
          <div className="text-center space-y-2">
            <p className="text-xs text-muted-foreground">
              In crisis? Call or text <span className="font-semibold">988</span> • Available 24/7
            </p>
            <p className="text-xs text-muted-foreground">
              LCE is not a replacement for professional mental health care.
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}
