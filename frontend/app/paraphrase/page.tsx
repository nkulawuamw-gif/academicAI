'use client';

import { useState } from 'react';
import { AppShell } from '@/components/layout/app-shell';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { paraphraseApi } from '@/lib/api';
import { toast } from 'sonner';
import { Spinner } from '@/components/ui/spinner';
import { Shuffle, Copy, Check } from 'lucide-react';

export default function ParaphrasePage() {
  const [text, setText] = useState('');
  const [mode, setMode] = useState('academic');
  const [intensity, setIntensity] = useState('moderate');
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [copied, setCopied] = useState(false);

  const handleParaphrase = async () => {
    if (!text.trim()) return;
    setIsLoading(true);
    try {
      const res = await paraphraseApi.paraphrase({ text, mode, intensity });
      setResult(res.data);
    } catch {
      toast.error('Failed to paraphrase text');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopy = () => {
    if (result?.paraphrased_text) {
      navigator.clipboard.writeText(result.paraphrased_text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
      toast.success('Copied to clipboard');
    }
  };

  return (
    <AppShell>
      <div className="space-y-6 animate-fade-in">
        <div>
          <h1 className="text-2xl font-bold">Paraphrasing Tool</h1>
          <p className="text-gray-500">Rewrite text in any tone or make AI text sound more human</p>
        </div>

        <div className="grid gap-4 md:grid-cols-3">
          <div>
            <label className="text-sm font-medium mb-1 block">Mode</label>
            <Select value={mode} onValueChange={setMode}>
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="academic">Academic</SelectItem>
                <SelectItem value="professional">Professional</SelectItem>
                <SelectItem value="simplification">Simplification</SelectItem>
                <SelectItem value="creative">Creative</SelectItem>
                <SelectItem value="humanize">Humanize</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div>
            <label className="text-sm font-medium mb-1 block">Intensity</label>
            <Select value={intensity} onValueChange={setIntensity}>
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="light">Light</SelectItem>
                <SelectItem value="moderate">Moderate</SelectItem>
                <SelectItem value="heavy">Heavy</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="flex items-end">
            <Button onClick={handleParaphrase} className="w-full" disabled={isLoading || !text.trim()}>
              {isLoading ? <Spinner size="sm" /> : <><Shuffle className="h-4 w-4 mr-2" /> Paraphrase</>}
            </Button>
          </div>
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          <div>
            <label className="text-sm font-medium mb-2 block">Original Text</label>
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              className="w-full min-h-[300px] rounded-lg border border-gray-300 p-4 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
              placeholder="Paste your text here..."
            />
            <p className="text-xs text-gray-400 mt-1">{text.split(/\s+/).filter(Boolean).length} words</p>
          </div>

          <div>
            <label className="text-sm font-medium mb-2 block">Paraphrased Result</label>
            <div className="relative">
              <textarea
                readOnly
                value={result?.paraphrased_text || ''}
                className="w-full min-h-[300px] rounded-lg border border-gray-300 p-4 text-sm bg-gray-50 focus:outline-none"
                placeholder="Your paraphrased text will appear here..."
              />
              {result && (
                <Button variant="ghost" size="icon" className="absolute top-2 right-2" onClick={handleCopy}>
                  {copied ? <Check className="h-4 w-4 text-green-500" /> : <Copy className="h-4 w-4" />}
                </Button>
              )}
            </div>
            {result && (
              <p className="text-xs text-gray-400 mt-1">
                {result.word_count_paraphrased} words | {result.changes_made} changes made
              </p>
            )}
          </div>
        </div>
      </div>
    </AppShell>
  );
}
