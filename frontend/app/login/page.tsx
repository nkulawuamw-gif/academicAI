'use client';

import Link from 'next/link';
import { LoginForm } from '@/components/auth/login-form';
import { BookOpen } from 'lucide-react';

export default function LoginPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 via-white to-primary-50 px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-2 mb-2">
            <BookOpen className="h-8 w-8 text-primary-600" />
            <h1 className="text-2xl font-bold">AcademAI</h1>
          </div>
          <p className="text-gray-500">Your AI Academic Assistant</p>
        </div>

        <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-8">
          <h2 className="text-xl font-semibold mb-1">Welcome back</h2>
          <p className="text-sm text-gray-500 mb-6">Sign in to your account</p>
          <LoginForm />
          <p className="text-center text-sm text-gray-500 mt-4">
            Don&apos;t have an account?{' '}
            <Link href="/register" className="text-primary-600 hover:underline font-medium">
              Sign up
            </Link>
          </p>
          <p className="text-center text-sm mt-2">
            <Link href="/forgot-password" className="text-gray-400 hover:text-gray-600">
              Forgot password?
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
