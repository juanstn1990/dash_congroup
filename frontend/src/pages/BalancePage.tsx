import * as React from 'react';
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer, LineChart, Line, ComposedChart, Cell,
} from 'recharts';
import { Download, TrendingUp, TrendingDown, DollarSign, Users, Calendar, BarChart3, GitCompare, Target, History, ChevronDown, ChevronUp } from 'lucide-react';
import { apiFetch } from '@/lib/api';
import { useAuth } from '@/hooks/useAuth';
import { Select } from '@/components/ui/select';

import { Skeleton } from '@/components/ui/skeleton';
import { Button } from '@/components/ui/button';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { formatAccounting, formatPercent } from '@/lib/utils';
import { KpiCard } from '@/components/KpiCard';
import { ChartCard } from '@/components/ChartCard';
import { FilterBar } from '@/components/FilterBar';
import { EmptyState } from '@/components/EmptyState';

const MESES_LABELS: Record<number, string> = {
  1: 'enero', 2: 'febrero', 3: 'marzo', 4: 'abril',
  5: 'mayo', 6: 'junio', 7: 'julio', 8: 'agosto',
  9: 'septiembre', 10: 'octubre', 11: 'noviembre', 12: 'diciembre',
};

const AZUL = '#1B3A6B';
const AZUL_ALT = '#254E9A';
const ROJO = '#C0392B';
const VERDE = '#0D7C66';
const GRIS_TOTAL = '#2D3748';
const COL_ODD = '#EEF3FB';
const COL_ODD_STRIPE = '#E4EDF8';
const COL_TOT = '#E0EAF8';
const COL_TOT_STRIPE = '#D6E4F5';
const ROW_STRIPE = '#F7F9FC';

// ── helpers de color (igual que Dash original) ─────────────────────────────
function hdrBg(i: number, totalMeses: number) {
  if (i >= totalMeses) return '#163266';
  return i % 2 === 1 ? AZUL_ALT : AZUL;
}

function dataBg(mesIdx: number, rowIdx: number, isTotalRow: boolean, totalMeses: number) {
  if (isTotalRow) return GRIS_TOTAL;
  const stripe = rowIdx % 2 === 1;
  if (mesIdx >= totalMeses) {
    return stripe ? COL_TOT_STRIPE : COL_TOT;
  }
  if (mesIdx % 2 === 1) {
    return stripe ? COL_ODD_STRIPE : COL_ODD;
  }
  return stripe ? ROW_STRIPE : 'white';
}

export function BalancePage() {
  const { data: filters } = useQuery({
    queryKey: ['balance-filters'],
    queryFn: () => apiFetch('/api/balance/filters'),
  });

  const empresas = filters?.empresas || [];
  const años = filters?.años || [2026];

  const [empresa, setEmpresa] = useState('CANTON MOTOR');
  const [año, setAño] = useState(String(años[0] || 2026));
  const [tab, setTab] = useState('resultado');

  const { data: resultado, isLoading: loadingR } = useQuery({
    queryKey: ['balance-resultado', empresa, año],
    queryFn: () => apiFetch(`/api/balance/resultado?empresa=${encodeURIComponent(empresa)}&año=${año}`),
  });

  const { data: vsPpto, isLoading: loadingVs } = useQuery({
    queryKey: ['balance-vs-ppto', empresa, año],
    queryFn: () => apiFetch(`/api/balance/vs-presupuesto?empresa=${encodeURIComponent(empresa)}&año=${año}`),
    enabled: tab === 'vs-presupuesto',
  });

  const { data: ppto, isLoading: loadingP } = useQuery({
    queryKey: ['balance-ppto', empresa, año],
    queryFn: () => apiFetch(`/api/balance/presupuesto?empresa=${encodeURIComponent(empresa)}&año=${año}`),
    enabled: tab === 'presupuesto',
  });

  const handleExport = async () => {
    const token = useAuth.getState().token;
    const url = `/api/balance/export-excel?empresa=${encodeURIComponent(empresa)}&año=${año}`;
    const res = await fetch(url, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });
    if (!res.ok) return;
    const blob = await res.blob();
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'balance_pyg.xlsx';
    a.click();
    URL.revokeObjectURL(a.href);
  };

  return (
    <div className="space-y-5">
      {/* Filters */}
      <FilterBar>
        <Select
          label="Empresa"
          value={empresa}
          onChange={(e) => setEmpresa(e.target.value)}
        >
          <option value="Todas">Todas</option>
          {empresas.map((e: string) => (
            <option key={e} value={e}>{e}</option>
          ))}
        </Select>
        <Select
          label="Año"
          value={año}
          onChange={(e) => setAño(e.target.value)}
        >
          <option value="Todos">Todos</option>
          {años.map((a: number) => (
            <option key={a} value={a}>{a}</option>
          ))}
        </Select>
      </FilterBar>

      {/* Tabs */}
      <Tabs value={tab} onValueChange={setTab}>
        <TabsList>
          <TabsTrigger value="resultado" icon={BarChart3} color="#1B3A6B">Resultado</TabsTrigger>
          <TabsTrigger value="vs-presupuesto" icon={GitCompare} color="#2E6BE6">Vs Presupuesto</TabsTrigger>
          <TabsTrigger value="presupuesto" icon={Target} color="#0D7C66">Presupuesto</TabsTrigger>
          <TabsTrigger value="vs-anterior" icon={History} color="#E07B39">Vs Ejercicio Anterior</TabsTrigger>
        </TabsList>

        <TabsContent value="resultado">
          {loadingR ? <BalanceSkeleton /> : resultado?.rows?.length > 0 ? (
            <ResultadoTab data={resultado} onExport={handleExport} empresa={empresa} año={año} />
          ) : (
            <EmptyState message="No hay datos de resultado para los filtros seleccionados." />
          )}
        </TabsContent>

        <TabsContent value="vs-presupuesto">
          {loadingVs ? <BalanceSkeleton /> : vsPpto?.rows?.length > 0 ? (
            <VsPresupuestoTab data={vsPpto} />
          ) : (
            <EmptyState message="No hay datos de presupuesto vs real para los filtros seleccionados." />
          )}
        </TabsContent>

        <TabsContent value="presupuesto">
          {loadingP ? <BalanceSkeleton /> : ppto?.rows?.length > 0 ? (
            <PresupuestoTab data={ppto} />
          ) : (
            <EmptyState message="No hay datos de presupuesto para la empresa y año seleccionados." />
          )}
        </TabsContent>

        <TabsContent value="vs-anterior">
          <VsAnteriorTab empresa={empresa} año={año} />
        </TabsContent>
      </Tabs>
    </div>
  );
}

function ExpandableRow({ row, ri, cols, meses, empresa, año }: { row: any; ri: number; cols: (number | string)[]; meses: number[]; empresa: string; año: string }) {
  const [expanded, setExpanded] = useState(false);
  const isTotal = row.is_total;
  const fg = isTotal ? 'white' : '#1C2B3A';
  const sBg = isTotal ? GRIS_TOTAL : (ri % 2 === 1 ? ROW_STRIPE : 'white');

  const { data: cuentasData, isLoading: loadingCuentas } = useQuery({
    queryKey: ['balance-cuentas', empresa, año, row.Categoria],
    queryFn: () => apiFetch(`/api/balance/cuentas?empresa=${encodeURIComponent(empresa)}&año=${año}&categoria=${encodeURIComponent(row.Categoria)}`),
    enabled: expanded,
  });

  const toggle = () => setExpanded((e) => !e);

  return (
    <React.Fragment>
      <tr
        onClick={toggle}
        className="cursor-pointer hover:opacity-80 transition-opacity"
      >
        <td className="px-2 md:px-3 py-1 md:py-1.5 font-bold sticky left-0 top-0 z-10 text-xs md:text-[13px]" style={{ background: sBg, color: fg }}>
          <div className="flex items-center gap-1">
            {!isTotal && (expanded ? <ChevronUp className="w-3 h-3 opacity-60" /> : <ChevronDown className="w-3 h-3 opacity-60" />)}
            {row.Categoria}
          </div>
        </td>
        <td className="px-2 md:px-3 py-1 md:py-1.5 sticky left-[80px] top-0 z-10 text-xs md:text-[13px]" style={{ background: sBg, color: fg, fontWeight: isTotal ? 'bold' : 'normal', paddingLeft: isTotal ? '8px' : '16px' }}>{row.Concepto}</td>
        {cols.map((c, ci) => {
          const bg = dataBg(ci, ri, isTotal, meses.length);
          const val = row[`res_${c}`] || 0;
          const valFg = isTotal ? fg : (val < 0 ? ROJO : '#1C2B3A');
          const pct = row[`pct_${c}`];
          const pctFg = isTotal ? fg : (pct > 0 ? VERDE : pct < 0 ? ROJO : '#888');
          return (
            <React.Fragment key={c}>
              <td className="px-1.5 md:px-2 py-1 md:py-1.5 text-right tabular-nums text-[11px] md:text-[13px]" style={{ background: bg, color: valFg, fontWeight: isTotal ? 'bold' : 'normal' }}>{formatAccounting(val)}</td>
              <td className="px-1.5 md:px-2 py-1 md:py-1.5 text-right tabular-nums text-[11px] md:text-[13px]" style={{ background: bg, color: pctFg, fontWeight: isTotal ? 'bold' : 'normal' }}>{formatPercent(pct)}</td>
            </React.Fragment>
          );
        })}
      </tr>
      {expanded && (
        <tr>
          <td colSpan={2 + cols.length * 2} className="p-0">
            <div className="bg-[#F0F4FA] border-y border-[#D6E4F5]">
              <div className="p-3 overflow-x-auto">
                {loadingCuentas ? (
                  <div className="space-y-2">
                    <Skeleton className="h-6 w-full" />
                    <Skeleton className="h-6 w-full" />
                    <Skeleton className="h-6 w-full" />
                  </div>
                ) : !cuentasData?.cuentas?.length ? (
                  <div className="text-sm text-gray-500 py-2">No hay cuentas asociadas para esta categoría.</div>
                ) : (
                  <table className="w-full text-[12px] min-w-max">
                    <thead>
                      <tr className="bg-congroup-blue text-white">
                        <th className="px-2 py-1 text-left font-semibold rounded-tl whitespace-nowrap">Cuenta</th>
                        <th className="px-2 py-1 text-left font-semibold whitespace-nowrap">Nombre Cuenta</th>
                        {cuentasData.meses.map((m: number) => (
                          <th key={m} className="px-2 py-1 text-right font-semibold whitespace-nowrap">{MESES_LABELS[m]}</th>
                        ))}
                        <th className="px-2 py-1 text-right font-semibold rounded-tr whitespace-nowrap">Total</th>
                      </tr>
                    </thead>
                    <tbody>
                      {cuentasData.cuentas.map((c: any, ci: number) => (
                        <tr key={ci} className={ci % 2 === 1 ? 'bg-white/60' : 'bg-white'}>
                          <td className="px-2 py-1 font-mono text-[11px] whitespace-nowrap">{c.cuenta}</td>
                          <td className="px-2 py-1 whitespace-nowrap">{c.nombre_cuenta}</td>
                          {cuentasData.meses.map((m: number) => (
                            <td key={m} className="px-2 py-1 text-right tabular-nums whitespace-nowrap" style={{ color: (c[`saldo_${m}`] || 0) < 0 ? ROJO : '#1C2B3A' }}>
                              {formatAccounting(c[`saldo_${m}`] || 0)}
                            </td>
                          ))}
                          <td className="px-2 py-1 text-right tabular-nums font-bold whitespace-nowrap" style={{ color: c.total < 0 ? ROJO : '#1C2B3A' }}>
                            {formatAccounting(c.total)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
            </div>
          </td>
        </tr>
      )}
    </React.Fragment>
  );
}

function ResultadoTab({ data, onExport, empresa, año }: { data: { rows: any[]; meses: number[] }; onExport: () => void; empresa: string; año: string }) {
  const { rows, meses } = data;
  const cols = [...meses, 'Total'];

  // KPIs
  const tRows = rows.filter((r: any) => r.is_total);
  const tLookup = Object.fromEntries(tRows.map((r: any) => [r.Categoria, r]));
  const tv = (cat: string, col: string | number = 'Total') => tLookup[cat]?.[`res_${col}`] || 0;

  const pygTotal = tv('T18');
  const bnTotal = tv('T13');
  const gastosG = tv('T14');
  const gastosP = tv('T15');
  const pygByMes = Object.fromEntries(meses.map((m) => [m, tv('T18', m)]));
  const mejorM = meses.reduce((a, b) => (pygByMes[a] > pygByMes[b] ? a : b), meses[0]);
  const peorM = meses.reduce((a, b) => (pygByMes[a] < pygByMes[b] ? a : b), meses[0]);

  const kpis = [
    { label: 'PyG Total', value: pygTotal, color: pygTotal >= 0 ? VERDE : ROJO, icon: DollarSign },
    { label: 'BN Total', value: bnTotal, color: AZUL, icon: TrendingUp },
    { label: 'Gastos Generales', value: Math.abs(gastosG), color: ROJO, icon: TrendingDown },
    { label: 'Gastos Personal', value: Math.abs(gastosP), color: ROJO, icon: Users },
    { label: 'Mejor Mes', value: pygByMes[mejorM], color: VERDE, icon: Calendar, sub: MESES_LABELS[mejorM] },
    { label: 'Peor Mes', value: pygByMes[peorM], color: ROJO, icon: Calendar, sub: MESES_LABELS[peorM] },
  ];

  // Chart data
  const chartData = meses.map((m) => ({
    mes: MESES_LABELS[m],
    pyg: tv('T18', m),
    bn: tv('T13', m),
    bn_vn: tv('T2', m),
    bn_vo: tv('T4', m),
    bn_pos: tv('T12', m),
    bb_vn_pct: tLookup['T1']?.[`pct_${m}`],
    bn_vn_pct: tLookup['T2']?.[`pct_${m}`],
    bn_total_pct: tLookup['T13']?.[`pct_${m}`],
    pyg_pct: tLookup['T18']?.[`pct_${m}`],
  }));

  // Waterfall data
  const wf = [
    { name: 'BN Total', value: tv('T13') },
    { name: 'G.Generales', value: tv('T14') },
    { name: 'G.Personal', value: tv('T15') },
    { name: 'Res. I+A', value: tv('T16') },
    { name: 'I+Amort.', value: tv('T17') - tv('T16') },
    { name: 'Res. Op.', value: tv('T17') },
    { name: 'Otros', value: tv('T18') - tv('T17') },
    { name: 'PyG', value: tv('T18') },
  ];

  return (
    <div className="space-y-5">
      {/* KPIs */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {kpis.map((kpi, i) => (
          <KpiCard
            key={kpi.label}
            label={kpi.label}
            value={formatAccounting(kpi.value)}
            color={kpi.color}
            icon={kpi.icon}
            subtitle={'sub' in kpi ? (kpi as any).sub : undefined}
            index={i}
          />
        ))}
      </div>

      {/* Table */}
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="bg-white rounded-xl shadow-sm overflow-hidden">
        <div className="p-4 border-b flex items-center justify-between">
          <h3 className="text-base font-bold text-congroup-blue">Balance P&G</h3>
          <Button variant="outline" size="sm" onClick={onExport}>
            <Download className="w-4 h-4 mr-2" />
            Descargar Excel
          </Button>
        </div>
        <div className="overflow-auto max-h-[70vh] md:max-h-[calc(100vh-300px)]" style={{ WebkitOverflowScrolling: 'touch' }}>
          <table className="w-full text-[13px] min-w-[800px]">
            <thead className="sticky top-0 z-20">
              <tr>
                <th className="px-2 md:px-3 py-1.5 md:py-2 bg-congroup-blue text-white font-semibold text-left sticky left-0 z-30" rowSpan={2}>Categoría</th>
                <th className="px-2 md:px-3 py-1.5 md:py-2 bg-congroup-blue text-white font-semibold text-left sticky left-[80px] z-30" rowSpan={2}>Concepto</th>
                {cols.map((c, i) => (
                  <th key={c} colSpan={2} className="px-1.5 md:px-2 py-1 md:py-1.5 text-white font-semibold text-center text-[11px] md:text-[13px]" style={{ background: hdrBg(i, meses.length) }}>
                    {typeof c === 'number' ? MESES_LABELS[c] : c}
                  </th>
                ))}
              </tr>
              <tr>
                {cols.map((c, i) => (
                  <React.Fragment key={c}>
                    <th className="px-1.5 md:px-2 py-0.5 md:py-1 text-white font-semibold text-center text-[10px] md:text-xs" style={{ background: hdrBg(i, meses.length) }}>Resultado</th>
                    <th className="px-1.5 md:px-2 py-0.5 md:py-1 text-white font-semibold text-center text-[10px] md:text-xs" style={{ background: hdrBg(i, meses.length) }}>%</th>
                  </React.Fragment>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((row, ri) => (
                <ExpandableRow
                  key={ri}
                  row={row}
                  ri={ri}
                  cols={cols}
                  meses={meses}
                  empresa={empresa}
                  año={año}
                />
              ))}
            </tbody>
          </table>
        </div>
      </motion.div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <ChartCard title="Evolución mensual: PyG vs BN Total">
          <div className="h-[200px] md:h-[320px]">
            <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E8ECF2" />
              <XAxis dataKey="mes" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip contentStyle={{ background: '#1B3A6B', border: 'none', borderRadius: 8, color: '#fff' }} />
              <Legend />
              <Bar dataKey="pyg" name="PyG" radius={[4, 4, 0, 0]}>
                {chartData.map((d, i) => <Cell key={i} fill={d.pyg >= 0 ? VERDE : ROJO} />)}
              </Bar>
              <Line type="monotone" dataKey="bn" name="BN Total" stroke={AZUL} strokeWidth={2} dot={{ r: 3 }} strokeDasharray="4 4" />
            </ComposedChart>
          </ResponsiveContainer>
          </div>
        </ChartCard>

        <ChartCard title="Evolución de Márgenes (%)">
          <div className="h-[200px] md:h-[320px]">
            <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E8ECF2" />
              <XAxis dataKey="mes" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} tickFormatter={(v) => `${v?.toFixed?.(0) ?? v}%`} />
              <Tooltip contentStyle={{ background: '#1B3A6B', border: 'none', borderRadius: 8, color: '#fff' }} formatter={(v: any) => `${Number(v).toFixed(2)}%`} />
              <Legend />
              <Line type="monotone" dataKey="bb_vn_pct" name="BB VN %" stroke="#1B3A6B" strokeWidth={2} dot={{ r: 3 }} />
              <Line type="monotone" dataKey="bn_vn_pct" name="BN VN %" stroke="#2E6BE6" strokeWidth={2} dot={{ r: 3 }} />
              <Line type="monotone" dataKey="bn_total_pct" name="BN Total %" stroke="#0D7C66" strokeWidth={2} dot={{ r: 3 }} />
              <Line type="monotone" dataKey="pyg_pct" name="PyG %" stroke="#E07B39" strokeWidth={2} dot={{ r: 3 }} />
            </LineChart>
          </ResponsiveContainer>
          </div>
        </ChartCard>

        <ChartCard title="BN por Área de Negocio">
          <div className="h-[200px] md:h-[320px]">
            <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E8ECF2" />
              <XAxis dataKey="mes" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip contentStyle={{ background: '#1B3A6B', border: 'none', borderRadius: 8, color: '#fff' }} />
              <Legend />
              <Bar dataKey="bn_vn" name="BN VN" fill="#1B3A6B" radius={[4, 4, 0, 0]} />
              <Bar dataKey="bn_vo" name="BN VO" fill="#2E6BE6" radius={[4, 4, 0, 0]} />
              <Bar dataKey="bn_pos" name="BN Posventa" fill="#0D7C66" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
          </div>
        </ChartCard>

        <ChartCard title="Cascada del Resultado (PyG)">
          <div className="h-[200px] md:h-[320px]">
            <ResponsiveContainer width="100%" height="100%">
            <BarChart data={wf}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E8ECF2" />
              <XAxis dataKey="name" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip contentStyle={{ background: '#1B3A6B', border: 'none', borderRadius: 8, color: '#fff' }} formatter={(v: any) => formatAccounting(Number(v))} />
              <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                {wf.map((d, i) => {
                  const isTotal = [0, 3, 5, 7].includes(i);
                  const isPositive = d.value >= 0;
                  return <Cell key={i} fill={isTotal ? AZUL : isPositive ? VERDE : ROJO} />;
                })}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
          </div>
        </ChartCard>
      </div>
    </div>
  );
}

function VsPresupuestoTab({ data }: { data: { rows: any[]; meses: number[] } }) {
  const { rows, meses } = data;
  const cols = [...meses, 'Total'];

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="bg-white rounded-xl shadow-sm overflow-hidden">
      <div className="p-4 border-b">
        <h3 className="text-base font-bold text-congroup-blue">Resultado vs Presupuesto</h3>
      </div>
      <div className="overflow-auto" style={{ maxHeight: 'calc(100vh - 280px)', WebkitOverflowScrolling: 'touch' }}>
        <table className="w-full text-[13px]">
          <thead className="sticky top-0 z-20">
            <tr>
              <th className="px-2 md:px-3 py-1.5 md:py-2 bg-congroup-blue text-white font-semibold text-left sticky left-0 z-30" rowSpan={2}>Categoría</th>
              <th className="px-2 md:px-3 py-1.5 md:py-2 bg-congroup-blue text-white font-semibold text-left sticky left-[80px] z-30" rowSpan={2}>Concepto</th>
              {cols.map((c, i) => (
                <th key={c} colSpan={4} className="px-1.5 md:px-2 py-1 md:py-1.5 text-white font-semibold text-center text-[11px] md:text-[13px]" style={{ background: hdrBg(i, meses.length) }}>
                  {typeof c === 'number' ? MESES_LABELS[c] : c}
                </th>
              ))}
            </tr>
            <tr>
              {cols.map((c, i) => (
                <React.Fragment key={c}>
                  <th className="px-1.5 md:px-2 py-0.5 md:py-1 text-white font-semibold text-center text-[10px] md:text-[11px]" style={{ background: hdrBg(i, meses.length) }}>Real</th>
                  <th className="px-1.5 md:px-2 py-0.5 md:py-1 text-white font-semibold text-center text-[10px] md:text-[11px]" style={{ background: hdrBg(i, meses.length) }}>Ppto</th>
                  <th className="px-1.5 md:px-2 py-0.5 md:py-1 text-white font-semibold text-center text-[10px] md:text-[11px]" style={{ background: hdrBg(i, meses.length) }}>Dif</th>
                  <th className="px-1.5 md:px-2 py-0.5 md:py-1 text-white font-semibold text-center text-[10px] md:text-[11px]" style={{ background: hdrBg(i, meses.length) }}>Var %</th>
                </React.Fragment>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, ri) => {
              const isTotal = row.is_total;
              const fg = isTotal ? 'white' : '#1C2B3A';
              const sBg = isTotal ? GRIS_TOTAL : (ri % 2 === 1 ? ROW_STRIPE : 'white');
              return (
                <tr key={ri}>
                  <td className="px-2 md:px-3 py-1 md:py-1.5 font-bold sticky left-0 top-0 z-10 text-xs md:text-[13px]" style={{ background: sBg, color: fg }}>{row.Categoria}</td>
                  <td className="px-2 md:px-3 py-1 md:py-1.5 sticky left-[80px] top-0 z-10 text-xs md:text-[13px]" style={{ background: sBg, color: fg, fontWeight: isTotal ? 'bold' : 'normal', paddingLeft: isTotal ? '8px' : '16px' }}>{row.Concepto}</td>
                  {cols.map((c, ci) => {
                    const bg = dataBg(ci, ri, isTotal, meses.length);
                    const real = row[`real_${c}`] || 0;
                    const ppto = row[`ppto_${c}`] || 0;
                    const diff = row[`diff_${c}`] || 0;
                    const varPct = row[`var_${c}`];
                    return (
                      <React.Fragment key={c}>
                        <td className="px-1.5 md:px-2 py-1 md:py-1.5 text-right tabular-nums text-[11px] md:text-[13px]" style={{ background: bg, color: isTotal ? fg : (real < 0 ? ROJO : '#1C2B3A'), fontWeight: isTotal ? 'bold' : 'normal' }}>{formatAccounting(real)}</td>
                        <td className="px-1.5 md:px-2 py-1 md:py-1.5 text-right tabular-nums text-[11px] md:text-[13px]" style={{ background: bg, color: isTotal ? fg : (ppto < 0 ? ROJO : '#1C2B3A'), fontWeight: isTotal ? 'bold' : 'normal' }}>{formatAccounting(ppto)}</td>
                        <td className="px-1.5 md:px-2 py-1 md:py-1.5 text-right tabular-nums text-[11px] md:text-[13px]" style={{ background: bg, color: isTotal ? fg : (diff > 0 ? VERDE : diff < 0 ? ROJO : '#1C2B3A'), fontWeight: isTotal ? 'bold' : 'normal' }}>{formatAccounting(diff)}</td>
                        <td className="px-1.5 md:px-2 py-1 md:py-1.5 text-right tabular-nums text-[11px] md:text-[13px]" style={{ background: bg, color: isTotal ? fg : (varPct > 0 ? VERDE : varPct < 0 ? ROJO : '#888'), fontWeight: isTotal ? 'bold' : 'normal' }}>{formatPercent(varPct)}</td>
                      </React.Fragment>
                    );
                  })}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </motion.div>
  );
}

function PresupuestoTab({ data }: { data: { rows: any[]; meses: number[] } }) {
  const { rows, meses } = data;
  const cols = [...meses, 'Total'];

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="bg-white rounded-xl shadow-sm overflow-hidden">
      <div className="p-4 border-b">
        <h3 className="text-base font-bold text-congroup-blue">Presupuesto</h3>
      </div>
      <div className="overflow-auto" style={{ maxHeight: 'calc(100vh - 280px)', WebkitOverflowScrolling: 'touch' }}>
        <table className="w-full text-[13px]">
          <thead className="sticky top-0 z-20">
            <tr>
              <th className="px-2 md:px-3 py-1.5 md:py-2 bg-congroup-blue text-white font-semibold text-left sticky left-0 z-30" rowSpan={2}>Categoría</th>
              <th className="px-2 md:px-3 py-1.5 md:py-2 bg-congroup-blue text-white font-semibold text-left sticky left-[80px] z-30" rowSpan={2}>Concepto</th>
              {cols.map((c, i) => (
                <th key={c} colSpan={2} className="px-1.5 md:px-2 py-1 md:py-1.5 text-white font-semibold text-center text-[11px] md:text-[13px]" style={{ background: hdrBg(i, meses.length) }}>
                  {typeof c === 'number' ? MESES_LABELS[c] : c}
                </th>
              ))}
            </tr>
            <tr>
              {cols.map((c, i) => (
                <React.Fragment key={c}>
                  <th className="px-1.5 md:px-2 py-0.5 md:py-1 text-white font-semibold text-center text-[10px] md:text-xs" style={{ background: hdrBg(i, meses.length) }}>Presupuesto</th>
                  <th className="px-1.5 md:px-2 py-0.5 md:py-1 text-white font-semibold text-center text-[10px] md:text-xs" style={{ background: hdrBg(i, meses.length) }}>%</th>
                </React.Fragment>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, ri) => {
              const isTotal = row.is_total;
              const fg = isTotal ? 'white' : '#1C2B3A';
              const sBg = isTotal ? GRIS_TOTAL : (ri % 2 === 1 ? ROW_STRIPE : 'white');
              return (
                <tr key={ri}>
                  <td className="px-2 md:px-3 py-1 md:py-1.5 font-bold sticky left-0 top-0 z-10 text-xs md:text-[13px]" style={{ background: sBg, color: fg }}>{row.Categoria}</td>
                  <td className="px-2 md:px-3 py-1 md:py-1.5 sticky left-[80px] top-0 z-10 text-xs md:text-[13px]" style={{ background: sBg, color: fg, fontWeight: isTotal ? 'bold' : 'normal', paddingLeft: isTotal ? '8px' : '16px' }}>{row.Concepto}</td>
                  {cols.map((c, ci) => {
                    const bg = dataBg(ci, ri, isTotal, meses.length);
                    const val = row[`ppto_${c}`] || 0;
                    const pct = row[`pct_${c}`];
                    return (
                      <React.Fragment key={c}>
                        <td className="px-1.5 md:px-2 py-1 md:py-1.5 text-right tabular-nums text-[11px] md:text-[13px]" style={{ background: bg, color: isTotal ? fg : (val < 0 ? ROJO : '#1C2B3A'), fontWeight: isTotal ? 'bold' : 'normal' }}>{formatAccounting(val)}</td>
                        <td className="px-1.5 md:px-2 py-1 md:py-1.5 text-right tabular-nums text-[11px] md:text-[13px]" style={{ background: bg, color: isTotal ? fg : (pct > 0 ? VERDE : pct < 0 ? ROJO : '#888'), fontWeight: isTotal ? 'bold' : 'normal' }}>{formatPercent(pct)}</td>
                      </React.Fragment>
                    );
                  })}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </motion.div>
  );
}

function VsAnteriorTab({ empresa, año }: { empresa: string; año: string }) {
  const [mes, setMes] = useState(1);

  const { data, isLoading } = useQuery({
    queryKey: ['balance-vs-anterior', empresa, año, mes],
    queryFn: () => apiFetch(`/api/balance/vs-anterior?empresa=${encodeURIComponent(empresa)}&año=${año}&mes=${mes}`),
    enabled: año !== 'Todos',
  });

  if (año === 'Todos') {
    return (
      <EmptyState message="Seleccione un año específico para comparar con el ejercicio anterior." />
    );
  }

  const rows = data?.rows || [];
  const añoAnterior = String(parseInt(año) - 1);

  return (
    <div className="space-y-4">
      <Select
        label="Mes a comparar"
        value={String(mes)}
        onChange={(e) => setMes(Number(e.target.value))}
        className="max-w-xs"
      >
        {Object.entries(MESES_LABELS).map(([num, label]) => (
          <option key={num} value={num}>{label}</option>
        ))}
      </Select>

      {isLoading ? <BalanceSkeleton /> : rows.length > 0 ? (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="bg-white rounded-xl shadow-sm overflow-hidden">
          <div className="overflow-auto" style={{ maxHeight: 'calc(100vh - 280px)', WebkitOverflowScrolling: 'touch' }}>
            <table className="w-full text-[13px]">
              <thead className="sticky top-0 z-20">
                <tr className="bg-congroup-blue text-white">
                  <th className="px-2 md:px-3 py-1.5 md:py-2 text-left font-semibold sticky left-0 z-30">Concepto</th>
                  <th className="px-2 md:px-3 py-1.5 md:py-2 text-center font-semibold text-[11px] md:text-[13px]">Resultado {año}</th>
                  <th className="px-2 md:px-3 py-1.5 md:py-2 text-center font-semibold text-[11px] md:text-[13px]">Resultado {añoAnterior}</th>
                  <th className="px-2 md:px-3 py-1.5 md:py-2 text-center font-semibold text-[11px] md:text-[13px]">Diferencia</th>
                  <th className="px-2 md:px-3 py-1.5 md:py-2 text-center font-semibold text-[11px] md:text-[13px]">Variación %</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((row: any, ri: number) => {
                  const isTotal = row.is_total;
                  const bg = isTotal ? GRIS_TOTAL : (ri % 2 === 1 ? ROW_STRIPE : 'white');
                  const fg = isTotal ? 'white' : '#1C2B3A';
                  return (
                    <tr key={ri}>
                      <td className="px-2 md:px-3 py-1 md:py-1.5 sticky left-0 top-0 z-10 text-xs md:text-[13px]" style={{ background: bg, color: fg, fontWeight: isTotal ? 'bold' : 'normal', paddingLeft: isTotal ? '8px' : '16px' }}>{row.Concepto}</td>
                      <td className="px-2 md:px-3 py-1 md:py-1.5 text-right tabular-nums text-[11px] md:text-[13px]" style={{ background: bg, color: isTotal ? fg : (row.actual < 0 ? ROJO : '#1C2B3A'), fontWeight: isTotal ? 'bold' : 'normal' }}>{formatAccounting(row.actual)}</td>
                      <td className="px-2 md:px-3 py-1 md:py-1.5 text-right tabular-nums text-[11px] md:text-[13px]" style={{ background: bg, color: isTotal ? fg : (row.anterior < 0 ? ROJO : '#1C2B3A'), fontWeight: isTotal ? 'bold' : 'normal' }}>{formatAccounting(row.anterior)}</td>
                      <td className="px-2 md:px-3 py-1 md:py-1.5 text-right tabular-nums text-[11px] md:text-[13px]" style={{ background: bg, color: isTotal ? fg : (row.diferencia > 0 ? VERDE : row.diferencia < 0 ? ROJO : '#1C2B3A'), fontWeight: isTotal ? 'bold' : 'normal' }}>{formatAccounting(row.diferencia)}</td>
                      <td className="px-2 md:px-3 py-1 md:py-1.5 text-right tabular-nums text-[11px] md:text-[13px]" style={{ background: bg, color: isTotal ? fg : (row.variacion > 0 ? VERDE : row.variacion < 0 ? ROJO : '#888'), fontWeight: isTotal ? 'bold' : 'normal' }}>{formatPercent(row.variacion)}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </motion.div>
      ) : (
        <EmptyState message="No hay datos para comparar con el ejercicio anterior." />
      )}
    </div>
  );
}

function BalanceSkeleton() {
  return (
    <div className="space-y-4">
      <Skeleton className="h-8 w-48" />
      <Skeleton className="h-96 w-full" />
    </div>
  );
}
