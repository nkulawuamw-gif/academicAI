'use client';

import { useState } from 'react';
import { AppShell } from '@/components/layout/app-shell';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { writingApi } from '@/lib/api';
import { toast } from 'sonner';
import { Spinner } from '@/components/ui/spinner';
import { FileText, BookOpen } from 'lucide-react';

export default function WritingPage() {
  const [prompt, setPrompt] = useState('');
  const [type, setType] = useState('essay');
  const [length, setLength] = useState('medium');
  const [tone, setTone] = useState('academic');
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleGenerate = async () => {
    if (!prompt.trim()) return;
    setIsLoading(true);
    try {
      const res = await writingApi.generate({ prompt, type, length, tone });
      setResult(res.data);
    } catch {
      toast.error('Failed to generate writing');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AppShell>
      <div className="space-y-6 animate-fade-in">
        <div>
          <h1 className="text-2xl font-bold">Writing Assistant</h1>
          <p className="text-gray-500">Generate essays, reports, and research papers</p>
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          <div className="lg:col-span-1 space-y-4">
            <Card>
              <CardContent className="p-4 space-y-4">
                <div>
                  <label className="text-sm font-medium mb-1 block">Type</label>
                  <Select value={type} onValueChange={setType}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="essay">Essay</SelectItem>
                      <SelectItem value="report">Report</SelectItem>
                      <SelectItem value="research_paper">Research Paper</SelectItem>
                      <SelectItem value="assignment">Assignment</SelectItem>
                      <SelectItem value="outline">Outline</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <label className="text-sm font-medium mb-1 block">Length</label>
                  <Select value={length} onValueChange={setLength}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="short">Short (~500 words)</SelectItem>
                      <SelectItem value="medium">Medium (~1500 words)</SelectItem>
                      <SelectItem value="long">Long (~3000 words)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <label className="text-sm font-medium mb-1 block">Tone</label>
                  <Select value={tone} onValueChange={setTone}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="academic">Academic</SelectItem>
                      <SelectItem value="formal">Formal</SelectItem>
                      <SelectItem value="informative">Informative</SelectItem>
                      <SelectItem value="persuasive">Persuasive</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </CardContent>
            </Card>

            <div className="space-y-2">
              <label className="text-sm font-medium">Write your prompt</label>
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                className="w-full min-h-[200px] rounded-lg border border-gray-300 p-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                placeholder="Describe what you want to write..."
              />
              <Button onClick={handleGenerate} className="w-full" disabled={isLoading || !prompt.trim()}>
                {isLoading ? <Spinner size="sm" /> : <><FileText className="h-4 w-4 mr-2" /> Generate</>}
              </Button>
            </div>
          </div>

          <div className="lg:col-span-2">
            {result ? (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <BookOpen className="h-5 w-5 text-primary-600" />
                    {result.title}
                  </CardTitle>
                  <p className="text-sm text-gray-500">{result.word_count} words | {result.type}</p>
                </CardHeader>
                <CardContent>
                  <div className="prose-custom whitespace-pre-wrap text-sm text-gray-700">
                    {result.content}
                  </div>
                </CardContent>
              </Card>
            ) : (
              <Card>
                <CardContent className="flex flex-col items-center justify-center h-96 text-gray-400">
                  <FileText className="h-16 w-16 mb-4" />
                  <p className="text-lg font-medium">Your writing will appear here</p>
                  <p className="text-sm">Configure and generate to get started</p>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </AppShell>
  );
}
