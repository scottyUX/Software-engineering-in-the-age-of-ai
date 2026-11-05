# Contract: Saved Favorites

- **Location**: browser localStorage
- **Key**: `quote-of-the-day:favorites`
- **Value**: a JSON array of quote id strings, for example `["knuth-optimization","lao-tzu-journey"]`

| Saved state | Behavior on load |
|-------------|------------------|
| Key missing | No favorites |
| Not valid JSON, or not an array | No favorites |
| Array with unknown or non-string entries | Those entries are ignored |
| Reading throws | No favorites |

If a write throws, the favorite still applies for the current visit.
