/**
 * Authentication component with Supabase integration.
 */
import React, { useState, useEffect } from 'react'
import { supabase, signInWithEmail, signUpWithEmail, signInWithMagicLink, signOut } from '../lib/supabaseClient'
import type { User } from '@supabase/supabase-js'

interface AuthProps {
  onAuthChange: (user: User | null) => void
}

export const Auth: React.FC<AuthProps> = ({ onAuthChange }) => {
  const [loading, setLoading] = useState(false)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [isSignUp, setIsSignUp] = useState(false)
  const [useMagicLink, setUseMagicLink] = useState(false)
  const [user, setUser] = useState<User | null>(null)

  useEffect(() => {
    // Check initial session
    supabase.auth.getSession().then(({ data: { session } }) => {
      const currentUser = session?.user ?? null
      setUser(currentUser)
      onAuthChange(currentUser)
    })

    // Listen for auth changes
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      const currentUser = session?.user ?? null
      setUser(currentUser)
      onAuthChange(currentUser)
    })

    return () => subscription.unsubscribe()
  }, [onAuthChange])

  const handleEmailAuth = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      if (useMagicLink) {
        const { error } = await signInWithMagicLink(email)
        if (error) throw error
        alert('Magic link gönderildi! E-postanızı kontrol edin.')
      } else if (isSignUp) {
        const { error } = await signUpWithEmail(email, password)
        if (error) throw error
        alert('Kayıt başarılı! E-postanızı kontrol edin.')
      } else {
        const { error } = await signInWithEmail(email, password)
        if (error) throw error
      }
    } catch (error) {
      alert(error instanceof Error ? error.message : 'Bir hata oluştu')
    } finally {
      setLoading(false)
    }
  }

  const handleSignOut = async () => {
    setLoading(true)
    const { error } = await signOut()
    if (error) {
      alert(error.message)
    }
    setLoading(false)
  }

  if (user) {
    return (
      <div className="flex items-center justify-between p-4 bg-white rounded-lg shadow-sm border">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
            <span className="text-white text-sm font-medium">
              {user.email?.charAt(0).toUpperCase()}
            </span>
          </div>
          <div>
            <p className="text-sm font-medium text-gray-900">{user.email}</p>
            <p className="text-xs text-gray-500">Oturum açık</p>
          </div>
        </div>
        <button
          onClick={handleSignOut}
          disabled={loading}
          className="btn btn-ghost text-sm px-3 py-1"
        >
          {loading ? 'Çıkış yapılıyor...' : 'Çıkış'}
        </button>
      </div>
    )
  }

  return (
    <div className="max-w-md mx-auto p-6 bg-white rounded-lg shadow-sm border">
      <h2 className="text-xl font-semibold text-gray-900 mb-4">
        {isSignUp ? 'Hesap Oluştur' : 'Giriş Yap'}
      </h2>
      
      <form onSubmit={handleEmailAuth} className="space-y-4">
        <div>
          <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
            E-posta
          </label>
          <input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="ornek@email.com"
          />
        </div>

        {!useMagicLink && (
          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
              Şifre
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Şifrenizi girin"
            />
          </div>
        )}

        <div className="flex items-center space-x-2">
          <input
            id="magicLink"
            type="checkbox"
            checked={useMagicLink}
            onChange={(e) => setUseMagicLink(e.target.checked)}
            className="w-4 h-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
          />
          <label htmlFor="magicLink" className="text-sm text-gray-700">
            Şifresiz giriş (Magic Link)
          </label>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full btn btn-primary py-2"
        >
          {loading
            ? 'İşlem yapılıyor...'
            : useMagicLink
            ? 'Magic Link Gönder'
            : isSignUp
            ? 'Hesap Oluştur'
            : 'Giriş Yap'}
        </button>
      </form>

      {!useMagicLink && (
        <div className="mt-4 text-center">
          <button
            onClick={() => setIsSignUp(!isSignUp)}
            className="text-sm text-blue-600 hover:text-blue-700"
          >
            {isSignUp ? 'Zaten hesabınız var mı? Giriş yapın' : 'Hesabınız yok mu? Kaydolun'}
          </button>
        </div>
      )}
    </div>
  )
}
