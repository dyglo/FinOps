'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api/client';
import { NewsListResponseSchema } from '@/lib/api/schemas';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { ExternalLink, Search, Filter } from 'lucide-react';

export default function NewsPage() {
  const [searchQuery, setSearchQuery] = useState('');

  const { data, isLoading } = useQuery({
    queryKey: ['news', 'list', searchQuery],
    queryFn: async () => {
      const response = await api.get('/v1/documents/news', { 
        params: { 
          limit: 50,
          q: searchQuery || undefined
        } 
      });
      return NewsListResponseSchema.parse(response);
    },
  });

  return (
    <div className="space-y-6">
      <header className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-[var(--text-strong)]">News Pipeline</h1>
          <p className="text-[var(--text-muted)] mt-1">Explore and filter normalized news intelligence.</p>
        </div>
        <div className="flex items-center gap-2">
           <div className="relative w-full md:w-64">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--text-muted)]" />
            <Input 
              placeholder="Search news..." 
              className="pl-9"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          <Button variant="outline" size="icon">
            <Filter className="h-4 w-4" />
          </Button>
        </div>
      </header>

      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Title</TableHead>
                <TableHead>Provider</TableHead>
                <TableHead>Published</TableHead>
                <TableHead className="text-right">Action</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                Array.from({ length: 10 }).map((_, i) => (
                  <TableRow key={i}>
                    <TableCell><Skeleton className="h-4 w-[300px]" /></TableCell>
                    <TableCell><Skeleton className="h-4 w-[80px]" /></TableCell>
                    <TableCell><Skeleton className="h-4 w-[100px]" /></TableCell>
                    <TableCell className="text-right"><Skeleton className="h-4 w-[40px] ml-auto" /></TableCell>
                  </TableRow>
                ))
              ) : data?.data.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={4} className="h-24 text-center text-[var(--text-muted)]">
                    No news documents found.
                  </TableCell>
                </TableRow>
              ) : (
                data?.data.map((doc) => (
                  <TableRow key={doc.id}>
                    <TableCell className="font-medium max-w-md">
                      <div className="flex flex-col">
                        <span>{doc.title}</span>
                        <span className="text-xs text-[var(--text-muted)] line-clamp-1">{doc.snippet}</span>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant="secondary" className="capitalize">{doc.source_provider}</Badge>
                    </TableCell>
                    <TableCell className="text-[var(--text-muted)] text-sm">
                      {doc.published_at ? new Date(doc.published_at).toLocaleString() : 'N/A'}
                    </TableCell>
                    <TableCell className="text-right">
                      <a href={doc.source_url} target="_blank" rel="noopener noreferrer">
                        <Button variant="ghost" size="icon" className="h-8 w-8">
                          <ExternalLink className="h-4 w-4" />
                        </Button>
                      </a>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}