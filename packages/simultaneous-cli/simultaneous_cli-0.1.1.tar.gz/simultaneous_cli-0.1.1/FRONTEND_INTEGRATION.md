# Frontend Integration for CLI Authentication

The CLI uses an OAuth-style redirect flow for authentication. When a user runs `sim auth signin --web` (or `sim auth signin` without credentials), the CLI:

1. Starts a local HTTP server on `http://localhost:8765` (or next available port)
2. Opens the browser to: `https://simultaneous.live/auth?cli=true&callback=http://localhost:8765/callback`
3. Waits for the frontend to redirect back with a token

## Frontend Implementation

Your frontend at `https://simultaneous.live/auth` should:

1. **Detect CLI request**: Check for `cli=true` in query parameters
2. **Get callback URL**: Extract `callback` parameter from query string
3. **After successful login**: Redirect to the callback URL with the token:

```
{callback_url}?token={access_token}
```

Or on error:

```
{callback_url}?error={error_message}
```

## Example Frontend Code

```typescript
// In your Next.js auth page
'use client'

import { useSearchParams, useRouter } from 'next/navigation'
import { useEffect } from 'react'
import { supabase } from '@/lib/supabase'

export default function AuthPage() {
  const searchParams = useSearchParams()
  const router = useRouter()
  
  const isCli = searchParams.get('cli') === 'true'
  const callbackUrl = searchParams.get('callback')
  
  useEffect(() => {
    // Check if user is already authenticated
    supabase.auth.getSession().then(({ data: { session } }) => {
      if (session && isCli && callbackUrl) {
        // Redirect back to CLI with token
        const redirectUrl = new URL(callbackUrl)
        redirectUrl.searchParams.set('token', session.access_token)
        window.location.href = redirectUrl.toString()
      }
    })
    
    // Listen for auth state changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange((event, session) => {
      if (event === 'SIGNED_IN' && session && isCli && callbackUrl) {
        // Redirect back to CLI with token
        const redirectUrl = new URL(callbackUrl)
        redirectUrl.searchParams.set('token', session.access_token)
        window.location.href = redirectUrl.toString()
      }
    })
    
    return () => subscription.unsubscribe()
  }, [isCli, callbackUrl, router])
  
  // ... rest of your auth UI
}
```

## Testing

1. Run `sim auth signin --web` from the CLI
2. The browser should open to your login page
3. After successful login, the browser should redirect to `http://localhost:8765/callback?token=...`
4. The CLI will automatically receive the token and complete authentication

