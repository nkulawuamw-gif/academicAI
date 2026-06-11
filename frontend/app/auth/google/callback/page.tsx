'use client';

import { Suspense, useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { authApi } from '@/lib/api';
import { setTokens } from '@/lib/auth';
import { useAuthStore } from '@/store/authStore';
import { BookOpen } from 'lucide-react';

function GoogleCallbackHandler() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const code = searchParams.get('code');
    if (!code) {
      setError('No authorization code received');
      return;
    }

    authApi
      .googleAuth(code)
      .then((response) => {
        const { access_token, refresh_token, ...userData } = response.data;
        setTokens(access_token, refresh_token);
        useAuthStore.getState().setUser(userData);
        router.push('/dashboard');
      })
      .catch((err) => {
        setError(err.response?.data?.detail || 'Google authentication failed');
      });
  }, [router, searchParams]);

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 via-white to-primary-50 px-4">
        <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-8 max-w-md w-full text-center">
          <BookOpen className="h-8 w-8 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold mb-2">Authentication Failed</h2>
          <p className="text-gray-500 mb-4">{error}</p>
          <button
            onClick={() => router.push('/login')}
            className="text-primary-600 hover:underline font-medium"
          >
            Back to login
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 via-white to-primary-50 px-4">
      <div className="text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-2 border-gray-300 border-t-primary-600 mx-auto mb-4" />
        <p className="text-gray-500">Signing you in...</p>
      </div>
    </div>
  );
}

export default function GoogleCallbackPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-2 border-gray-300 border-t-primary-600" />
      </div>
    }>
      <GoogleCallbackHandler />
    </Suspense>
  );
}
