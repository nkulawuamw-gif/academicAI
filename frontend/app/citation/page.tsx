'use client';

import { useState } from 'react';
import { AppShell } from '@/components/layout/app-shell';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { citationApi } from '@/lib/api';
import { toast } from 'sonner';
import { Spinner } from '@/components/ui/spinner';
import { Quote, Copy, Check } from 'lucide-react';

export default function CitationPage() {
  const [style, setStyle] = useState('apa');
  const [title, setTitle] = useState('');
  const [authors, setAuthors] = useState('');
  const [year, setYear] = useState('');
  const [sourceText, setSourceText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [copied, setCopied] = useState(false);
  const [mode, setMode] = useState<string>('auto');

  const handleGenerate = async () => {
    if (mode === 'auto' && !sourceText.trim()) return;
    if (mode === 'manual' && !title.trim()) return;

    setIsLoading(true);
    try {
      if (mode === 'auto') {
        const res = await citationApi.generate({ style, source_text: sourceText });
        setResult({ citation_text: res.data.citation_text, style: res.data.style });
      } else {
        const res = await citationApi.create({
          style, title, authors, year: year ? parseInt(year) : undefined,
        });
        setResult({ citation_text: res.data.citation_text, style: res.data.style });
      }
      toast.success('Citation generated');
    } catch {
      toast.error('Failed to generate citation');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopy = () => {
    if (result?.citation_text) {
      navigator.clipboard.writeText(result.citation_text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <AppShell>
      <div className="space-y-6 animate-fade-in">
        <div>
          <h1 className="text-2xl font-bold">Citation Generator</h1>
          <p className="text-gray-500">Generate citations in APA, MLA, Harvard, Chicago, and IEEE styles</p>
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          <div className="lg:col-span-1 space-y-4">
            <Card>
              <CardContent className="p-4 space-y-4">
                <div>
                  <label className="text-sm font-medium mb-1 block">Citation Style</label>
                  <Select value={style} onValueChange={setStyle}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="apa">APA 7th</SelectItem>
                      <SelectItem value="mla">MLA</SelectItem>
                      <SelectItem value="harvard">Harvard</SelectItem>
                      <SelectItem value="chicago">Chicago</SelectItem>
                      <SelectItem value="ieee">IEEE</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <label className="text-sm font-medium mb-1 block">Mode</label>
                  <Select value={mode} onValueChange={setMode}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="auto">Auto (from text)</SelectItem>
                      <SelectItem value="manual">Manual Entry</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </CardContent>
            </Card>

            {mode === 'manual' ? (
              <div className="space-y-3">
                <Input placeholder="Title" value={title} onChange={(e) => setTitle(e.target.value)} />
                <Input placeholder="Authors (e.g. Smith, J.)" value={authors} onChange={(e) => setAuthors(e.target.value)} />
                <Input placeholder="Year" type="number" value={year} onChange={(e) => setYear(e.target.value)} />
              </div>
            ) : (
              <div className="space-y-2">
                <label className="text-sm font-medium">Source text or URL</label>
                <textarea
                  value={sourceText}
                  onChange={(e) => setSourceText(e.target.value)}
                  className="w-full min-h-[150px] rounded-lg border border-gray-300 p-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                  placeholder="Paste source information or URL..."
                />
              </div>
            )}

            <Button onClick={handleGenerate} className="w-full" disabled={isLoading}>
              {isLoading ? <Spinner size="sm" /> : <><Quote className="h-4 w-4 mr-2" /> Generate Citation</>}
            </Button>
          </div>

          <div className="lg:col-span-2">
            {result ? (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Quote className="h-5 w-5 text-primary-600" />
                    Generated Citation ({result.style.toUpperCase()})
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="relative bg-gray-50 rounded-lg p-4 border">
                    <p className="text-sm text-gray-700 pr-8">{result.citation_text}</p>
                    <Button variant="ghost" size="icon" className="absolute top-2 right-2" onClick={handleCopy}>
                      {copied ? <Check className="h-4 w-4 text-green-500" /> : <Copy className="h-4 w-4" />}
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ) : (
              <Card>
                <CardContent className="flex flex-col items-center justify-center h-64 text-gray-400">
                  <Quote className="h-16 w-16 mb-4" />
                  <p className="text-lg font-medium">Your citation will appear here</p>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </AppShell>
  );
}
