'use client';

import { Sidebar } from './sidebar';
import { Navbar } from './navbar';
import { useAuthStore } from '@/store/authStore';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

interface AppShellProps {
  children: React.ReactNode;
}

export function AppShell({ children }: AppShellProps) {
  const { user } = useAuthStore();
  const router = useRouter();

  useEffect(() => {
    if (!user) {
      router.push('/login');
    }
  }, [user, router]);

  if (!user) return null;

  return (
    <div className="min-h-screen bg-gray-50">
      <Sidebar />
      <Navbar />
      <main className="pl-64 pt-14">
        <div className="p-6 pb-20">{children}</div>
        <footer className="fixed bottom-0 left-64 right-0 h-8 bg-white border-t border-gray-200 flex items-center justify-center text-xs text-red-500">
          Powered by Mantchombe Technology
        </footer>
      </main>
    </div>
  );
}
