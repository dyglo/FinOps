'use client';

import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api/client';
import { NewsListResponseSchema } from '@/lib/api/schemas';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Newspaper, ExternalLink } from 'lucide-react';

export function NewsIntelligencePanel() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['news', 'latest'],
    queryFn: async () => {
      const response = await api.get('/v1/documents/news', { params: { limit: 5 } });
      return NewsListResponseSchema.parse(response);
    },
  });

  return (
    <Card className="h-full">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-xl font-bold flex items-center gap-2">
          <Newspaper className="h-5 w-5 text-[var(--text-muted)]" />
          News Intelligence
        </CardTitle>
        <Badge variant="outline">Live Feed</Badge>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {isLoading ? (
            Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="space-y-2">
                <Skeleton className="h-4 w-[250px]" />
                <Skeleton className="h-3 w-full" />
              </div>
            ))
          ) : error ? (
            <div className="text-sm text-red-500 py-4">Failed to load news intelligence.</div>
          ) : data?.data.length === 0 ? (
            <div className="text-sm text-[var(--text-muted)] py-4">No news found for this organization.</div>
          ) : (
            data?.data.map((doc) => (
              <div key={doc.id} className="group relative flex flex-col gap-1 border-b border-[var(--line-soft)] pb-3 last:border-0 last:pb-0">
                <div className="flex items-center justify-between gap-2">
                  <h4 className="font-medium text-sm text-[var(--text-strong)] line-clamp-1">{doc.title}</h4>
                  <a 
                    href={doc.source_url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-[var(--text-muted)] hover:text-[var(--text-strong)] transition-colors"
                  >
                    <ExternalLink className="h-3 w-3" />
                  </a>
                </div>
                <p className="text-xs text-[var(--text-muted)] line-clamp-2 leading-relaxed">
                  {doc.snippet}
                </p>
                <div className="flex items-center gap-2 mt-1">
                  <Badge variant="secondary" className="text-[10px] px-1.5 py-0 capitalize">
                    {doc.source_provider}
                  </Badge>
                  <span className="text-[10px] text-[var(--text-muted)]">
                    {doc.published_at ? new Date(doc.published_at).toLocaleDateString() : 'N/A'}
                  </span>
                </div>
              </div>
            ))
          )}
        </div>
      </CardContent>
    </Card>
  );
}
