import { useLazyQuery } from '@apollo/client'
import React, { useEffect } from 'react'

const useIntervalQuery = (gqlQuery, variables = {}, ttl = 15000) => {
  const [getQuery, queryResponse] = useLazyQuery(gqlQuery, {
    fetchPolicy: 'network-only', // Doesn't check cache before making a network request
  })

  useEffect(() => {
    const asyncInit = async () => {
      await getQuery(variables)
      const interval = setInterval(() => getQuery(variables), ttl)
      return () => {
        clearInterval(interval)
      }
    }

    asyncInit()
  }, [])

  return queryResponse
}

export default useIntervalQuery
