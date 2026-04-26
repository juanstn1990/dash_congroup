import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatAccounting(value: number): string {
  const rounded = Math.round(value)
  if (rounded < 0) {
    return `(${Math.abs(rounded).toLocaleString('es-ES')})`
  }
  return rounded.toLocaleString('es-ES')
}

export function formatPercent(value: number | null | undefined): string {
  if (value === null || value === undefined || Number.isNaN(value)) return ''
  return `${value.toFixed(2)} %`
}
