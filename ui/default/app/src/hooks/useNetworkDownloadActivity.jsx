import React from 'react'
import { gql, useQuery } from '@apollo/client'
import { useMemo } from 'react'

const NETWORK_DOWNLOAD_ACTIVITY_QUERY = gql`
  query Query($deviceId: String) {
    flows(device_id: $deviceId) {
      device_id
      ts
      ts_mod_3600
      inbound_byte_count
    }
  }
`

const useNetworkDownloadActivity = (props) => {
  console.log("@DEBUG::06272022-032704", 'useNetworkDownloadActivity', props);
  const initialValues = {
    pullInterval: props.pullInterval || 600000,
    filters: {
      sort: {
        by: props?.filters?.sort?.by ||  'ts',
        ascending: props?.filters?.sort?.ascending ||  true,
      },
    }
  }

  const variables = props?.deviceId ? { deviceId: props.deviceId } : null

  const { data, loading: networkDownloadActivityLoading } = useQuery(
    NETWORK_DOWNLOAD_ACTIVITY_QUERY,
    {
      variables,
      pollInterval: initialValues.pullInterval,
    }
  )

  const calculate = (data) => {
    if (!data) return []
    // const d = data.slice().sort((a, b) => {
    //   if (a[initialValues.filters.sort.by] < b[initialValues.filters.sort.by]) {
    //     return -1
    //   }
    //   if (a[initialValues.filters.sort.by] > b[initialValues.filters.sort.by]) {
    //     return 1
    //   }

    //   return 0
    // }).groupBy('device_id')

    // return d
    return data.groupBy('device_id')
  }

  const networkDownloadActivity = useMemo(() => calculate(data?.flows), [data?.flows])

  // const sortNetworkDownloadActivity = (sortBy, ascending = true) => {
  //   setFilters({
  //     sort: {
  //       by: sortBy,
  //       ascending,
  //     },
  //   })
  // }

  return {
    networkDownloadActivity,
    networkDownloadActivityLoading,
    // sortNetworkDownloadActivity,
  }
}

export default useNetworkDownloadActivity
