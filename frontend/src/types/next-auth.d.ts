import NextAuth from "next-auth"

declare module "next-auth" {
  interface Session {
    user: {
      id: string
      name?: string | null
      email?: string | null
      image?: string | null
    }
    accessToken?: string
    googleAccessToken?: string
    googleRefreshToken?: string
    spotifyAccessToken?: string
  }

  interface User {
    id: string
  }
}

declare module "next-auth/jwt" {
  interface JWT {
    id: string
    accessToken?: string
    refreshToken?: string
    provider?: string
    googleAccessToken?: string
    googleRefreshToken?: string
    spotifyAccessToken?: string
    spotifyRefreshToken?: string
  }
}
