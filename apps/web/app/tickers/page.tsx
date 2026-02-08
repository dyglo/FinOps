import { api } from '@/lib/api/client';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Activity, BarChart2, PieChart } from 'lucide-react';

export const dynamic = 'force-dynamic';

export default async function TickersPage() {
  let records = 0;
  try {
    const response: any = await api.get('/v1/documents/news', { params: { limit: 25 } });
    records = response.data.length;
  } catch {
    records = 0;
  }

  return (
    <div className="space-y-8">
      <header>
        <h1 className="text-3xl font-bold text-black">Ticker Lab</h1>
        <p className="text-gray-500 mt-1">Market expansion lanes and symbol analytics prototyping.</p>
      </header>

      <div className="grid gap-6 md:grid-cols-3">
        <Card className="border-none glass-card rounded-[32px] p-2">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-xs font-bold uppercase tracking-widest text-gray-400">
              News Signals
            </CardTitle>
            <Activity className="h-4 w-4 text-emerald-500" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-black">{records}</div>
            <p className="text-[10px] text-gray-400 font-bold mt-1 uppercase tracking-tighter">Canonical records loaded</p>
          </CardContent>
        </Card>

        <Card className="border-none glass-card rounded-[32px] p-2">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-xs font-bold uppercase tracking-widest text-gray-400">
              Market Stream
            </CardTitle>
            <BarChart2 className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-lg font-bold text-black">Twelve Data Lane</div>
            <p className="text-[10px] text-gray-400 font-bold mt-1 uppercase tracking-tighter">Reserved for integration</p>
          </CardContent>
        </Card>

        <Card className="border-none glass-card rounded-[32px] p-2">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-xs font-bold uppercase tracking-widest text-gray-400">
              Execution
            </CardTitle>
            <PieChart className="h-4 w-4 text-purple-500" />
          </CardHeader>
          <CardContent>
            <div className="text-lg font-bold text-black">Alpaca Telemetry</div>
            <p className="text-[10px] text-gray-400 font-bold mt-1 uppercase tracking-tighter">Future order lane</p>
          </CardContent>
        </Card>
      </div>

      <div className="h-96 rounded-[40px] bg-gray-50 border border-gray-100 flex items-center justify-center">
        <div className="text-center">
          <p className="text-sm font-bold text-gray-400">Symbol Analytics Visualization</p>
          <p className="text-xs text-gray-400 mt-1">Prototype surfaces loading...</p>
        </div>
      </div>
    </div>
  );
}