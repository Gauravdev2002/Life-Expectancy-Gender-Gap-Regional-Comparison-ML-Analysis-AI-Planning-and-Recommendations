// src/hooks/useFetch.js
// Simple custom hook to fetch data from the API.
// Usage:  const { data, loading, error } = useFetch(fetchOverview)

import { useState, useEffect } from 'react'

/**
 * @param {Function} fetchFn – An async function that returns data (from api.js)
 */
export default function useFetch(fetchFn) {
  const [data,    setData]    = useState(null)
  const [loading, setLoading] = useState(true)
  const [error,   setError]   = useState(null)

  useEffect(() => {
    let cancelled = false   // prevent state update after unmount

    setLoading(true)
    setError(null)

    fetchFn()
      .then((result) => { if (!cancelled) setData(result) })
      .catch((err)   => { if (!cancelled) setError(err.message) })
      .finally(()    => { if (!cancelled) setLoading(false) })

    return () => { cancelled = true }
  }, [])  // runs once on mount

  return { data, loading, error }
}
