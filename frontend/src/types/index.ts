export interface User {
  username: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (username: string, password: string) => Promise<boolean>;
  logout: () => void;
}

export interface VendedorRow {
  vendedor: string;
  con_placa: number;
  subidos: number;
  pendientes: number;
  pedidos: number;
  ventas: number;
  suma_bb1: number;
  media_bb1: number;
  suma_bb2: number;
  media_bb2: number;
  suma_bb3: number;
  media_bb3: number;
  media_descuento_pct: number;
  operaciones_financiadas: number;
}

export interface BalanceRow {
  Categoria: string;
  Concepto: string;
  is_total: boolean;
  [key: string]: string | number | boolean | null;
}

export interface BalanceData {
  rows: BalanceRow[];
  meses: number[];
}
