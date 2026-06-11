'use client';

import { useState } from 'react';
import { AppShell } from '@/components/layout/app-shell';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { researchApi } from '@/lib/api';
import { toast } from 'sonner';
import { Spinner } from '@/components/ui/spinner';
import { Search, ExternalLink, BookOpen, FileText, ChevronDown, ChevronUp } from 'lucide-react';

export default function ResearchPage() {
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [expandedSource, setExpandedSource] = useState<number | null>(null);

  const handleSearch = async () => {
    if (!query.trim()) return;
    setIsLoading(true);
    try {
      const res = await researchApi.search({ query, max_sources: 10, include_summary: true, include_citations: true });
      setResult(res.data);
    } catch {
      toast.error('Research search failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AppShell>
      <div className="space-y-6 animate-fade-in">
        <div>
          <h1 className="text-2xl font-bold">Research Assistant</h1>
          <p className="text-gray-500">Search the web and generate research summaries</p>
        </div>

        <div className="flex gap-2">
          <Input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Enter your research topic..."
            className="flex-1"
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
          />
          <Button onClick={handleSearch} disabled={isLoading || !query.trim()}>
            {isLoading ? <Spinner size="sm" /> : <><Search className="h-4 w-4 mr-2" /> Search</>}
          </Button>
        </div>

        {result && (
          <div className="space-y-6">
            {result.summary && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <BookOpen className="h-5 w-5 text-primary-600" />
                    Research Summary
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-700 whitespace-pre-wrap">{result.summary}</p>
                </CardContent>
              </Card>
            )}

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileText className="h-5 w-5 text-primary-600" />
                  Sources ({result.sources?.length || 0})
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {result.sources?.map((source: any, i: number) => (
                  <div key={i} className="border rounded-lg p-4">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h3 className="font-medium text-sm">{source.title}</h3>
                        <p className="text-xs text-gray-500 mt-1">{source.url}</p>
                      </div>
                      <div className="flex gap-2">
                        <a href={source.url} target="_blank" rel="noopener noreferrer">
                          <Button variant="ghost" size="icon"><ExternalLink className="h-4 w-4" /></Button>
                        </a>
                        <Button variant="ghost" size="icon" onClick={() => setExpandedSource(expandedSource === i ? null : i)}>
                          {expandedSource === i ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                        </Button>
                      </div>
                    </div>
                    {expandedSource === i && source.snippet && (
                      <p className="text-sm text-gray-600 mt-2">{source.snippet}</p>
                    )}
                  </div>
                ))}
              </CardContent>
            </Card>

            {result.citations && result.citations.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <BookOpen className="h-5 w-5 text-primary-600" />
                    Citations
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2 text-sm">
                    {result.citations.map((c: any, i: number) => (
                      <li key={i} className="text-gray-700">{c.text}</li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            )}
          </div>
        )}
      </div>
    </AppShell>
  );
}
