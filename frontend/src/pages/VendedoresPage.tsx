import { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer, LineChart, Line, Cell,
} from 'recharts';
import {
  Car, ArrowUp, Clock, ShoppingCart, TrendingUp,
  Download, FileText
} from 'lucide-react';
import { apiFetch } from '@/lib/api';
import { Select } from '@/components/ui/select';

import { Skeleton } from '@/components/ui/skeleton';
import { Button } from '@/components/ui/button';

import { formatAccounting } from '@/lib/utils';
import { KpiCard } from '@/components/KpiCard';
import { ChartCard } from '@/components/ChartCard';
import { FilterBar } from '@/components/FilterBar';
import type { VendedorRow } from '@/types';

const COLORS = {
  verde: '#0D7C66',
  azul: '#1B3A6B',
  azulMed: '#2E6BE6',
  naranja: '#E07B39',
  rojo: '#C0392B',
};

const MESES = [
  { value: 'todos', label: 'Todos' },
  { value: 1, label: 'Enero' }, { value: 2, label: 'Febrero' },
  { value: 3, label: 'Marzo' }, { value: 4, label: 'Abril' },
  { value: 5, label: 'Mayo' }, { value: 6, label: 'Junio' },
  { value: 7, label: 'Julio' }, { value: 8, label: 'Agosto' },
  { value: 9, label: 'Septiembre' }, { value: 10, label: 'Octubre' },
  { value: 11, label: 'Noviembre' }, { value: 12, label: 'Diciembre' },
];

export function VendedoresPage() {
  const currentYear = new Date().getFullYear();
  const currentMonth = new Date().getMonth() + 1;

  const { data: añosData } = useQuery({ queryKey: ['años'], queryFn: () => apiFetch('/api/vendedores/años') });
  const años = añosData?.años || [currentYear, currentYear - 1];

  const [anio, setAnio] = useState<string | number>(currentYear);
  const [mes, setMes] = useState<string | number>(currentMonth);

  const { data, isLoading } = useQuery({
    queryKey: ['vendedores', anio, mes],
    queryFn: () => {
      const a = anio === 'todos' ? '' : anio;
      const m = mes === 'todos' ? '' : mes;
      return apiFetch(`/api/vendedores/resumen?anio=${a}&mes=${m}`);
    },
  });

  const { data: ventasTipoData } = useQuery({
    queryKey: ['ventas-tipo', anio, mes],
    queryFn: () => {
      const a = anio === 'todos' ? '' : anio;
      const m = mes === 'todos' ? '' : mes;
      return apiFetch(`/api/vendedores/ventas-por-tipo?anio=${a}&mes=${m}`);
    },
  });

  const rows: VendedorRow[] = data?.rows || [];
  const totales = data?.totales || {};

  const topVendedores = useMemo(() =>
    [...rows].sort((a, b) => b.pedidos - a.pedidos).slice(0, 10),
  [rows]);

  const topVentas = useMemo(() =>
    [...rows].sort((a, b) => b.ventas - a.ventas).slice(0, 10),
  [rows]);

  const topBB = useMemo(() =>
    [...rows].sort((a, b) => b.media_bb3 - a.media_bb3).slice(0, 10),
  [rows]);

  const topSubidos = useMemo(() =>
    [...rows].sort((a, b) => b.subidos - a.subidos).slice(0, 10),
  [rows]);

  const kpiData = [
    { label: 'Con Placa', value: totales.con_placa || 0, color: COLORS.verde, icon: Car },
    { label: 'Subidos', value: totales.subidos || 0, color: COLORS.azulMed, icon: ArrowUp },
    { label: 'Pendientes', value: totales.pendientes || 0, color: COLORS.naranja, icon: Clock },
    { label: 'Pedidos', value: totales.pedidos || 0, color: COLORS.azul, icon: ShoppingCart },
    { label: 'Ventas', value: totales.ventas || 0, color: COLORS.rojo, icon: TrendingUp },
  ];

  return (
    <div className="space-y-6">
      {/* Filters */}
      <FilterBar>
        <div className="flex flex-wrap gap-4 max-w-lg">
          <Select
            label="Año"
            value={String(anio)}
            onChange={(e) => setAnio(e.target.value === 'todos' ? 'todos' : Number(e.target.value))}
          >
            <option value="todos">Todos</option>
            {años.map((a: number) => (
              <option key={a} value={a}>{a}</option>
            ))}
          </Select>
          <Select
            label="Mes"
            value={String(mes)}
            onChange={(e) => setMes(e.target.value === 'todos' ? 'todos' : Number(e.target.value))}
          >
            {MESES.map((m) => (
              <option key={m.value} value={m.value}>{m.label}</option>
            ))}
          </Select>
        </div>
        <p className="text-xs text-slate-400 mt-3 font-medium">
          💡 Pedidos usa fecha de pedido | Resto usa fecha aviso (FechaSimulada)
        </p>
      </FilterBar>

      {/* KPIs */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
        {isLoading
          ? Array.from({ length: 5 }).map((_, i) => (
              <Skeleton key={i} className="h-28 rounded-xl" />
            ))
          : kpiData.map((kpi, i) => (
              <KpiCard
                key={kpi.label}
                label={kpi.label}
                value={kpi.value.toLocaleString('es-ES')}
                color={kpi.color}
                icon={kpi.icon}
                index={i}
              />
            ))}
      </div>

      {/* Charts Row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartCard title="🏆 Top 10 Vendedores por Pedidos">
          <div className="h-[260px] md:h-[400px]">
            <ResponsiveContainer width="100%" height="100%">
            <BarChart data={topVendedores} layout="vertical" margin={{ left: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E8ECF2" />
              <XAxis type="number" />
              <YAxis dataKey="vendedor" type="category" width={140} tick={{ fontSize: 12 }} />
              <Tooltip
                contentStyle={{ background: '#1B3A6B', border: 'none', borderRadius: 8, color: '#fff' }}
                cursor={{ fill: '#EBF2FF' }}
              />
              <Bar dataKey="pedidos" radius={[0, 4, 4, 0]} fill={COLORS.azulMed}>
                {topVendedores.map((_, i) => (
                  <Cell key={i} fill={`rgba(46, 107, 230, ${1 - i * 0.06})`} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
          </div>
        </ChartCard>

        <ChartCard title="📊 Ventas vs Pendientes (Top 10)">
          <div className="h-[260px] md:h-[400px]">
            <ResponsiveContainer width="100%" height="100%">
            <BarChart data={topVentas} margin={{ bottom: 30 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E8ECF2" />
              <XAxis dataKey="vendedor" angle={-45} textAnchor="end" height={80} tick={{ fontSize: 11 }} />
              <YAxis />
              <Tooltip
                contentStyle={{ background: '#1B3A6B', border: 'none', borderRadius: 8, color: '#fff' }}
              />
              <Legend />
              <Bar dataKey="ventas" name="Ventas" fill={COLORS.verde} radius={[4, 4, 0, 0]} />
              <Bar dataKey="pendientes" name="Pendientes" fill={COLORS.naranja} radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
          </div>
        </ChartCard>
      </div>

      {/* Charts Row 2 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartCard title="💰 Media de BBs (Top 10)">
          <div className="h-[260px] md:h-[400px]">
            <ResponsiveContainer width="100%" height="100%">
            <LineChart data={topBB} margin={{ bottom: 30 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E8ECF2" />
              <XAxis dataKey="vendedor" angle={-45} textAnchor="end" height={80} tick={{ fontSize: 11 }} />
              <YAxis />
              <Tooltip
                contentStyle={{ background: '#1B3A6B', border: 'none', borderRadius: 8, color: '#fff' }}
              />
              <Legend />
              <Line type="monotone" dataKey="media_bb1" name="Media BB1" stroke="#93C5FD" strokeWidth={2} dot={{ r: 3 }} />
              <Line type="monotone" dataKey="media_bb2" name="Media BB2" stroke="#3B82F6" strokeWidth={2} dot={{ r: 3 }} />
              <Line type="monotone" dataKey="media_bb3" name="Media BB3" stroke="#1E3A8A" strokeWidth={2} dot={{ r: 3 }} />
            </LineChart>
          </ResponsiveContainer>
          </div>
        </ChartCard>

        <ChartCard title="📋 Subidos vs Pendientes (Top 10)">
          <div className="h-[260px] md:h-[400px]">
            <ResponsiveContainer width="100%" height="100%">
            <BarChart data={topSubidos} margin={{ bottom: 30 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E8ECF2" />
              <XAxis dataKey="vendedor" angle={-45} textAnchor="end" height={80} tick={{ fontSize: 11 }} />
              <YAxis />
              <Tooltip
                contentStyle={{ background: '#1B3A6B', border: 'none', borderRadius: 8, color: '#fff' }}
              />
              <Legend />
              <Bar dataKey="subidos" name="Subidos (Con Expediente)" stackId="a" fill={COLORS.verde} radius={[4, 4, 0, 0]} />
              <Bar dataKey="pendientes" name="Pendientes (Sin Expediente)" stackId="a" fill={COLORS.rojo} radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
          </div>
        </ChartCard>
      </div>

      {/* Tabla Detallada */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="bg-white rounded-xl shadow-sm overflow-hidden"
      >
        <div className="p-5 border-b flex items-center justify-between">
          <h3 className="text-lg font-bold text-congroup-blue flex items-center gap-2">
            <FileText className="w-5 h-5" />
            Tabla Detallada
          </h3>
          <Button variant="outline" size="sm" onClick={() => exportTable(rows, 'vendedores')}>
            <Download className="w-4 h-4 mr-2" />
            Exportar
          </Button>
        </div>
        <div className="overflow-x-auto overflow-y-auto max-h-[70vh]" style={{ WebkitOverflowScrolling: 'touch' }}>
          <table className="w-full text-sm min-w-[900px]">
            <thead className="sticky top-0 z-20">
              <tr className="bg-congroup-blue text-white">
                {['Vendedor', 'Con Placa', 'Subidos', 'Pendientes', 'Pedidos', 'Ventas', 'Suma BB1', 'Media BB1', 'Suma BB2', 'Media BB2', 'Suma BB3', 'Media BB3', 'Desc %', 'Op. Fin.'].map((h, i) => (
                  <th key={h} className={`px-2 md:px-4 py-2 md:py-3 text-left font-semibold whitespace-nowrap text-[11px] md:text-sm ${i === 0 ? 'sticky left-0 z-30' : ''}`}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                <tr><td colSpan={14}><Skeleton className="h-64 m-4" /></td></tr>
              ) : (
                rows.map((row, i) => (
                  <tr
                    key={i}
                    className={`border-b ${row.vendedor === 'TOTALES' ? 'bg-congroup-blue-light font-bold' : i % 2 === 1 ? 'bg-slate-50' : 'bg-white'}`}
                  >
                    <td className="px-2 md:px-4 py-2 md:py-3 font-medium sticky left-0 top-0 z-10 text-xs md:text-sm bg-inherit">{row.vendedor}</td>
                    <td className="px-2 md:px-4 py-2 md:py-3 text-xs md:text-sm">{row.con_placa}</td>
                    <td className="px-2 md:px-4 py-2 md:py-3 text-xs md:text-sm">{row.subidos}</td>
                    <td className="px-2 md:px-4 py-2 md:py-3 text-xs md:text-sm">{row.pendientes}</td>
                    <td className="px-2 md:px-4 py-2 md:py-3 text-xs md:text-sm">{row.pedidos}</td>
                    <td className="px-2 md:px-4 py-2 md:py-3 text-xs md:text-sm">{row.ventas}</td>
                    <td className="px-2 md:px-4 py-2 md:py-3 text-xs md:text-sm">{formatAccounting(row.suma_bb1)}</td>
                    <td className="px-2 md:px-4 py-2 md:py-3 text-xs md:text-sm">{formatAccounting(row.media_bb1)}</td>
                    <td className="px-2 md:px-4 py-2 md:py-3 text-xs md:text-sm">{formatAccounting(row.suma_bb2)}</td>
                    <td className="px-2 md:px-4 py-2 md:py-3 text-xs md:text-sm">{formatAccounting(row.media_bb2)}</td>
                    <td className="px-2 md:px-4 py-2 md:py-3 text-xs md:text-sm">{formatAccounting(row.suma_bb3)}</td>
                    <td className="px-2 md:px-4 py-2 md:py-3 text-xs md:text-sm">{formatAccounting(row.media_bb3)}</td>
                    <td className="px-2 md:px-4 py-2 md:py-3 text-xs md:text-sm">{row.media_descuento_pct?.toFixed(2)}%</td>
                    <td className="px-2 md:px-4 py-2 md:py-3 text-xs md:text-sm">{row.operaciones_financiadas}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </motion.div>

      {/* Ventas por Tipo */}
      {ventasTipoData?.rows?.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-white rounded-xl shadow-sm overflow-hidden"
        >
          <div className="p-5 border-b">
            <h3 className="text-lg font-bold text-congroup-blue flex items-center gap-2">
              <FileText className="w-5 h-5" />
              Ventas por Vendedor y Tipo de Venta
            </h3>
          </div>
          <div className="overflow-x-auto overflow-y-auto max-h-[60vh]" style={{ WebkitOverflowScrolling: 'touch' }}>
            <table className="w-full text-sm min-w-[600px]">
              <thead className="sticky top-0 z-20">
                <tr className="bg-congroup-blue text-white">
                  {Object.keys(ventasTipoData.rows[0]).map((h, i) => (
                    <th key={h} className={`px-2 md:px-4 py-2 md:py-3 text-center font-semibold whitespace-nowrap text-[11px] md:text-sm ${i === 0 ? 'sticky left-0 z-30' : ''}`}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {ventasTipoData.rows.map((row: Record<string, unknown>, i: number) => (
                  <tr
                    key={i}
                    className={`border-b ${i === ventasTipoData.rows.length - 1 ? 'bg-congroup-blue-light font-bold' : i % 2 === 1 ? 'bg-slate-50' : 'bg-white'}`}
                  >
                    {Object.entries(row).map(([_key, val], j) => (
                      <td
                        key={j}
                        className={`px-2 md:px-4 py-2 md:py-3 text-xs md:text-sm ${j === 0 ? 'text-left font-medium sticky left-0 top-0 z-10 bg-inherit' : 'text-center'}`}
                      >
                        {typeof val === 'number' ? val.toLocaleString('es-ES') : String(val)}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Stacked Bar Chart */}
          <div className="p-5 pt-0 mt-4">
            <div className="h-[280px] md:h-[350px]">
              <ResponsiveContainer width="100%" height="100%">
              <BarChart data={ventasTipoData.rows.slice(0, -1)} margin={{ bottom: 30 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E8ECF2" />
                <XAxis dataKey="Vendedor" angle={-45} textAnchor="end" height={80} tick={{ fontSize: 11 }} />
                <YAxis />
                <Tooltip contentStyle={{ background: '#1B3A6B', border: 'none', borderRadius: 8, color: '#fff' }} />
                <Legend />
                {Object.keys(ventasTipoData.rows[0])
                  .filter((k) => k !== 'Vendedor' && k !== 'TOTAL')
                  .map((tipo, i) => (
                    <Bar key={tipo} dataKey={tipo} stackId="a" fill={['#1B3A6B', '#2E6BE6', '#0D7C66', '#E07B39', '#C0392B'][i % 5]} radius={[4, 4, 0, 0]} />
                  ))}
              </BarChart>
            </ResponsiveContainer>
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
}

function exportTable(rows: VendedorRow[], filename: string) {
  const headers = Object.keys(rows[0] || {});
  const csv = [
    headers.join(';'),
    ...rows.map((row) => headers.map((h) => String(row[h as keyof VendedorRow] ?? '')).join(';')),
  ].join('\n');
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `${filename}.csv`;
  a.click();
  URL.revokeObjectURL(url);
}
