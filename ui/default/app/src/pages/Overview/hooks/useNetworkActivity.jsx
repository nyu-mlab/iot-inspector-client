import { gql, useQuery } from '@apollo/client'
import React, { useEffect, useState } from 'react'

const NETWORK_ACTIVITY_QUERY = gql`
  query Query {
    networkActivity {
      weak_encryption
      unencrypted_http_traffic
      ads_and_trackers
    }
  }
`

const useNetworkActivity = () => {
  const [networkActivityData, setNetworkActivityData] = useState([])  // TODO: Can we leverage useMemo in place https://github.com/ocupop/iot-inspector-client/issues/17

  const { data, loading: networkActivityDataLoading } = useQuery(
    NETWORK_ACTIVITY_QUERY,
    {
      pollInterval: 5000,
    }
  )

  useEffect(() => {
    if (data?.networkActivity) {
      setNetworkActivityData(data.networkActivity)
    }
  }, [data?.networkActivity])

  return {
    networkActivityData,
    networkActivityDataLoading,
  }
}

export default useNetworkActivity
