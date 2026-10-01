import { describe, expect, it } from 'vitest'
import { chooseCategory } from './category'

describe('chooseCategory', () => {
  it('pre-selects the top AI suggestion when the user has not chosen', () => {
    expect(chooseCategory(null, false, ['food_grocery', 'shopping'])).toBe('food_grocery')
  })
  it('never overrides a category the user picked', () => {
    expect(chooseCategory('shopping', true, ['food_grocery', 'shopping'])).toBe('shopping')
  })
  it('follows new suggestions while the user has not chosen', () => {
    expect(chooseCategory('food_grocery', false, ['family_support'])).toBe('family_support')
  })
  it('keeps the current value when there are no suggestions', () => {
    expect(chooseCategory('other', false, [])).toBe('other')
    expect(chooseCategory(null, false, [])).toBeNull()
  })
})
