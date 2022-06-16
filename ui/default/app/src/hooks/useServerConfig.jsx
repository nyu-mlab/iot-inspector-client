import { gql, useQuery } from '@apollo/client'
import React from 'react'

const useServerConfig = () => {
  const initialValues = {
    start_timestamp: null
  }

  const SERVER_TIMESTAMP_QUERY = gql`
    query Query {
      serverConfig {
        start_timestamp
      }
    }
  `

  const { data } = useQuery(SERVER_TIMESTAMP_QUERY)

  if (data) {
    return data.serverConfig
  }

  return initialValues
  // return {...initialValues, ...data.serverConfig}
}

export default useServerConfig
