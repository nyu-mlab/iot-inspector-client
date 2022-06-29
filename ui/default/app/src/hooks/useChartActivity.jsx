import React from 'react'
import { gql, useQuery } from '@apollo/client'
import { useMemo } from 'react'

const CHART_ACTIVITY_QUERY = gql`
  query Query($currentTime: Int!) {
    chartActivity(current_time: $currentTime) {
      xAxis
      yAxis {
        name
        data
      }
    }
  }
`

const useChartActivity = (props) => {
  const initialValues = {
    pullInterval: props?.pullInterval || 600000,
    filters: {
      sort: {
        by: props?.filters?.sort?.by || 'ts',
        ascending: props?.filters?.sort?.ascending || true,
      },
    },
  }

  const variables = {
    deviceId: props?.deviceId || null,
    currentTime: Math.round((new Date()).getTime() / 1000)
  }

  const {
    data: networkDownloadActivity,
    loading: networkDownloadActivityLoading,
  } = useQuery(CHART_ACTIVITY_QUERY, {
    variables,
    // pollInterval: initialValues.pullInterval,
  })

  // const networkDownloadActivity = useMemo(() => {
  //   const d = data.flows
  //     .slice()
  //     .sort((a, b) => {
  //       if (
  //         a[initialValues.filters.sort.by] < b[initialValues.filters.sort.by]
  //       ) {
  //         return -1
  //       }
  //       if (
  //         a[initialValues.filters.sort.by] > b[initialValues.filters.sort.by]
  //       ) {
  //         return 1
  //       }

  //       return 0
  //     })
  //     .groupBy('device_id')

  //   return d
  // }, [data?.flows])

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

export default useChartActivity
