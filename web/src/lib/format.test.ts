import { describe, expect, it } from 'vitest'
import { fmtTaka, parseAmount, toBnDigits } from './format'

describe('parseAmount', () => {
  it('parses Bangla digits and separators', () => {
    expect(parseAmount('৫০০')).toBe(500)
    expect(parseAmount('১,৫০০.৫০')).toBe(1500.5)
    expect(parseAmount(' 2,000 ')).toBe(2000)
  })
  it('rejects invalid input', () => {
    expect(parseAmount('abc')).toBeNull()
    expect(parseAmount('-5')).toBeNull()
    expect(parseAmount('0')).toBeNull()
    expect(parseAmount('')).toBeNull()
    expect(parseAmount('1.2.3')).toBeNull()
  })
})

describe('fmtTaka', () => {
  it('uses Indian grouping and Bangla digits in bn', () => {
    expect(fmtTaka(1800, 'bn')).toBe('৳১,৮০০')
    expect(fmtTaka(150000, 'en')).toBe('৳1,50,000')
    expect(fmtTaka(-2500.4, 'en')).toBe('-৳2,500')
  })
  it('keeps paisa when asked', () => {
    expect(fmtTaka(0.35, 'bn', { paisa: true })).toBe('৳০.৩৫')
  })
})

describe('toBnDigits', () => {
  it('converts digits only', () => {
    expect(toBnDigits('2026-09')).toBe('২০২৬-০৯')
  })
})
