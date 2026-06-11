'use client';

import { useState, useEffect } from 'react';
import { AppShell } from '@/components/layout/app-shell';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { adminApi } from '@/lib/api';
import { toast } from 'sonner';
import { Spinner } from '@/components/ui/spinner';
import { Users, Activity, FileText, MessageSquare, ToggleLeft, ToggleRight } from 'lucide-react';

export default function AdminPage() {
  const [users, setUsers] = useState<any[]>([]);
  const [analytics, setAnalytics] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const [usersRes, analyticsRes] = await Promise.all([
        adminApi.getUsers(1, 100),
        adminApi.getAnalytics(),
      ]);
      setUsers(usersRes.data.users);
      setAnalytics(analyticsRes.data);
    } catch {
      toast.error('Failed to load admin data');
    } finally {
      setIsLoading(false);
    }
  };

  const toggleActive = async (userId: string) => {
    try {
      await adminApi.toggleUserActive(userId);
      setUsers(users.map((u) => (u.id === userId ? { ...u, is_active: !u.is_active } : u)));
      toast.success('User status updated');
    } catch {
      toast.error('Failed to update user');
    }
  };

  if (isLoading) {
    return (
      <AppShell>
        <div className="flex justify-center py-20"><Spinner size="lg" /></div>
      </AppShell>
    );
  }

  return (
    <AppShell>
      <div className="space-y-6 animate-fade-in">
        <div>
          <h1 className="text-2xl font-bold">Admin Dashboard</h1>
          <p className="text-gray-500">Manage users and monitor platform usage</p>
        </div>

        {analytics && (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <Card>
              <CardContent className="p-4 flex items-center gap-4">
                <div className="bg-primary-50 p-3 rounded-lg"><Users className="h-5 w-5 text-primary-600" /></div>
                <div>
                  <p className="text-sm text-gray-500">Total Users</p>
                  <p className="text-2xl font-bold">{analytics.total_users}</p>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4 flex items-center gap-4">
                <div className="bg-blue-50 p-3 rounded-lg"><MessageSquare className="h-5 w-5 text-blue-600" /></div>
                <div>
                  <p className="text-sm text-gray-500">Conversations</p>
                  <p className="text-2xl font-bold">{analytics.total_conversations}</p>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4 flex items-center gap-4">
                <div className="bg-emerald-50 p-3 rounded-lg"><FileText className="h-5 w-5 text-emerald-600" /></div>
                <div>
                  <p className="text-sm text-gray-500">Documents</p>
                  <p className="text-2xl font-bold">{analytics.total_documents}</p>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4 flex items-center gap-4">
                <div className="bg-amber-50 p-3 rounded-lg"><Activity className="h-5 w-5 text-amber-600" /></div>
                <div>
                  <p className="text-sm text-gray-500">Active Today</p>
                  <p className="text-2xl font-bold">{analytics.active_users_today}</p>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="h-5 w-5 text-primary-600" />
              User Management ({users.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b text-left">
                    <th className="pb-3 font-medium">Name</th>
                    <th className="pb-3 font-medium">Email</th>
                    <th className="pb-3 font-medium">Role</th>
                    <th className="pb-3 font-medium">Provider</th>
                    <th className="pb-3 font-medium">Status</th>
                    <th className="pb-3 font-medium">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((user) => (
                    <tr key={user.id} className="border-b last:border-0">
                      <td className="py-3">{user.full_name}</td>
                      <td className="py-3 text-gray-500">{user.email}</td>
                      <td className="py-3">
                        <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${user.role === 'admin' ? 'bg-purple-100 text-purple-700' : 'bg-gray-100 text-gray-700'}`}>
                          {user.role}
                        </span>
                      </td>
                      <td className="py-3 text-gray-500">{user.auth_provider}</td>
                      <td className="py-3">
                        <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${user.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                          {user.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      <td className="py-3">
                        <Button variant="ghost" size="sm" onClick={() => toggleActive(user.id)}>
                          {user.is_active ? <ToggleRight className="h-4 w-4 text-green-600" /> : <ToggleLeft className="h-4 w-4 text-red-600" />}
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      </div>
    </AppShell>
  );
}
