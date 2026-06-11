'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import {
  Bot,
  Search,
  FileText,
  Shuffle,
  Quote,
  GraduationCap,
  BookOpen,
  LayoutDashboard,
  Users,
  ChevronLeft,
} from 'lucide-react';
import { useState } from 'react';
import { isAdmin } from '@/lib/auth';

const navItems = [
  { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/chat', label: 'AI Chat', icon: Bot },
  { href: '/research', label: 'Research', icon: Search },
  { href: '/writing', label: 'Writing', icon: FileText },
  { href: '/paraphrase', label: 'Paraphrase', icon: Shuffle },
  { href: '/citation', label: 'Citations', icon: Quote },
  { href: '/study', label: 'Study Tools', icon: GraduationCap },
];

const adminItems = [
  { href: '/admin', label: 'Admin Dashboard', icon: Users },
];

export function Sidebar() {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);

  return (
    <aside
      className={cn(
        'fixed left-0 top-0 z-40 flex h-screen flex-col border-r border-primary-800 bg-primary-900 text-white transition-all duration-300',
        collapsed ? 'w-16' : 'w-64',
      )}
    >
      <div className="flex h-14 items-center border-b border-primary-800 px-4">
        {!collapsed && (
          <Link href="/dashboard" className="flex items-center gap-2">
            <BookOpen className="h-6 w-6 text-primary-200" />
            <span className="text-lg font-bold text-white">AcademAI</span>
          </Link>
        )}
        <Button
          variant="ghost"
          size="icon"
          className={cn('ml-auto text-primary-200 hover:text-white hover:bg-primary-800', collapsed && 'mx-auto')}
          onClick={() => setCollapsed(!collapsed)}
        >
          <ChevronLeft className={cn('h-4 w-4 transition-transform', collapsed && 'rotate-180')} />
        </Button>
      </div>

      <nav className="flex-1 overflow-y-auto p-3 space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname.startsWith(item.href);
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors relative',
                isActive
                  ? 'bg-primary-800 text-white'
                  : 'text-primary-100 hover:bg-primary-800 hover:text-white',
              )}
            >
              {isActive && <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-5 bg-primary-300 rounded-r-full" />}
              <Icon className={cn('h-5 w-5 shrink-0', isActive && 'text-primary-200')} />
              {!collapsed && <span>{item.label}</span>}
            </Link>
          );
        })}

        {isAdmin() && (
          <>
            <div className={cn('border-t border-primary-800 my-2', collapsed && 'mx-2')} />
            {adminItems.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors relative',
                    isActive
                      ? 'bg-primary-800 text-white'
                      : 'text-primary-100 hover:bg-primary-800 hover:text-white',
                  )}
                >
                  {isActive && <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-5 bg-primary-300 rounded-r-full" />}
                  <Icon className={cn('h-5 w-5 shrink-0', isActive && 'text-primary-200')} />
                  {!collapsed && <span>{item.label}</span>}
                </Link>
              );
            })}
          </>
        )}
      </nav>
    </aside>
  );
}
