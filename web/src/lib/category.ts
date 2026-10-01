/** Which category to show selected: the user's own pick always wins; otherwise follow the top AI suggestion. */
export function chooseCategory(current: string | null, userChose: boolean, suggestions: string[]): string | null {
  if (userChose) return current
  return suggestions[0] ?? current
}
