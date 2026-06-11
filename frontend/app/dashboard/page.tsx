'use client';

import { AppShell } from '@/components/layout/app-shell';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useAuthStore } from '@/store/authStore';
import { Bot, Search, FileText, Shuffle, Quote, GraduationCap, BookOpen, ArrowRight } from 'lucide-react';
import Link from 'next/link';

const features = [
  { title: 'AI Chat', description: 'Multi-turn conversations with AI', icon: Bot, href: '/chat', color: 'bg-violet-50 text-violet-600' },
  { title: 'Research', description: 'Web research & lit reviews', icon: Search, href: '/research', color: 'bg-blue-50 text-blue-600' },
  { title: 'Writing', description: 'Essays, reports & papers', icon: FileText, href: '/writing', color: 'bg-emerald-50 text-emerald-600' },
  { title: 'Paraphrase', description: 'Rewrite in any tone', icon: Shuffle, href: '/paraphrase', color: 'bg-orange-50 text-orange-600' },
  { title: 'Citations', description: 'APA, MLA, Chicago & more', icon: Quote, href: '/citation', color: 'bg-rose-50 text-rose-600' },
  { title: 'Study Tools', description: 'Quizzes, flashcards & plans', icon: GraduationCap, href: '/study', color: 'bg-cyan-50 text-cyan-600' },
];

export default function DashboardPage() {
  const { user } = useAuthStore();

  return (
    <AppShell>
      <div className="space-y-6 animate-fade-in">
        <div>
          <h1 className="text-2xl font-bold">Welcome back, {user?.full_name?.split(' ')[0] || 'Student'}!</h1>
          <p className="text-gray-500 mt-1">What would you like to work on today?</p>
        </div>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {features.map((feature) => {
            const Icon = feature.icon;
            return (
              <Link key={feature.href} href={feature.href}>
                <Card className="hover:shadow-md transition-shadow cursor-pointer group h-full">
                  <CardContent className="p-6">
                    <div className={`w-12 h-12 rounded-xl ${feature.color} flex items-center justify-center mb-4`}>
                      <Icon className="h-6 w-6" />
                    </div>
                    <h3 className="font-semibold mb-1">{feature.title}</h3>
                    <p className="text-sm text-gray-500">{feature.description}</p>
                    <div className="flex items-center gap-1 mt-3 text-sm text-primary-600 font-medium opacity-0 group-hover:opacity-100 transition-opacity">
                      Get started <ArrowRight className="h-4 w-4" />
                    </div>
                  </CardContent>
                </Card>
              </Link>
            );
          })}
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BookOpen className="h-5 w-5 text-primary-600" />
              Quick Tips
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2 text-sm text-gray-600">
              <li>💡 Use <strong>AI Chat</strong> for instant answers to academic questions</li>
              <li>📚 Upload PDFs in <strong>Research</strong> for AI-powered analysis</li>
              <li>✍️ Generate essays and outlines with the <strong>Writing</strong> tool</li>
              <li>📝 Create quizzes and flashcards in <strong>Study Tools</strong></li>
            </ul>
          </CardContent>
        </Card>
      </div>
    </AppShell>
  );
}
