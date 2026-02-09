/**
 * Utility functions for NeuroDegenRx frontend.
 */
import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

/**
 * Merge Tailwind CSS classes with conflict resolution.
 */
export function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs))
}

/**
 * Format a number as a score indicator.
 */
export function formatScore(value: number | null | undefined, decimals = 2): string {
    if (value == null) return 'N/A'
    return value.toFixed(decimals)
}

/**
 * Get CSS class for score color.
 */
export function getScoreClass(value: number | null, threshold = 4): string {
    if (value == null) return 'text-muted-foreground'
    if (value >= threshold + 1) return 'score-high'
    if (value >= threshold) return 'score-medium'
    return 'score-low'
}

/**
 * Format affinity value.
 */
export function formatAffinity(nM: number | null): string {
    if (nM == null) return '—'
    if (nM < 1) return '<1 nM'
    if (nM >= 10000) return '>10 µM'
    if (nM >= 1000) return `${(nM / 1000).toFixed(1)} µM`
    return `${nM.toFixed(0)} nM`
}

/**
 * Get a human-readable label for parameter names.
 */
export function formatParameterName(param: string): string {
    return param
        .replace(/_/g, ' ')
        .replace(/\b\w/g, (c) => c.toUpperCase())
}
