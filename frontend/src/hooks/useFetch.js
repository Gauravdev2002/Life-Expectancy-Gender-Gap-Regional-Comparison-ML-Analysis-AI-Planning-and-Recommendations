// src/hooks/useFetch.js
// High-performance custom hook with client-side memory caching.
// Prevents flickering and ensures instant UI rendering across navigation.

import { useState, useEffect } from 'react'

const _clientCache = new Map()

/**
 * @param {Function} fetchFn – An async function that returns data (from api.js)
 * @param {string} key – Optional custom cache key
 */
export default function useFetch(fetchFn, key = null) {
  const cacheKey = key || fetchFn.name || 'default_fetch_key'
  const cachedData = _clientCache.get(cacheKey)

  const [data,    setData]    = useState(cachedData || null)
  const [loading, setLoading] = useState(!cachedData)
  const [error,   setError]   = useState(null)

  useEffect(() => {
    let cancelled = false

    if (!cachedData) {
      setLoading(true)
    }

    fetchFn()
      .then((result) => {
        if (!cancelled) {
          _clientCache.set(cacheKey, result)
          setData(result)
          setError(null)
        }
      })
      .catch((err) => {
        if (!cancelled && !cachedData) {
          setError(err.message)
        }
      })
      .finally(() => {
        if (!cancelled) {
          setLoading(false)
        }
      })

    return () => { cancelled = true }
  }, [cacheKey])

  return { data, loading, error }
}
