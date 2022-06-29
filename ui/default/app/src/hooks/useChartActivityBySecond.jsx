import React from 'react'
import { gql, useQuery } from '@apollo/client'
import { useMemo } from 'react'

const CHART_ACTIVITY_BY_SECOND_QUERY = gql`
  query ChartActivityBySecond($currentTime: Int!, $deviceId: String!) {
    chartActivityBySecond(current_time: $currentTime, device_id: $deviceId) {
      xAxis
      yAxis {
        name
        data
      }
    }
  }
`

const useChartActivityBySecond = (props) => {
  console.log('@DEBUG::06272022-032704', 'useChartActivityBySecond', props)
  const initialValues = {
    pullInterval: props?.pullInterval || 600000,
    filters: {
      sort: {
        by: props?.filters?.sort?.by || 'ts',
        ascending: props?.filters?.sort?.ascending || true,
      },
    },
  }

  // const variables = props?.deviceId ? { deviceId: props.deviceId } : null
  const variables = {
    deviceId: props.deviceId || null,
    currentTime: Math.round(new Date().getTime() / 1000),
  }

  const {
    data,
    loading: chartActivityBySecondDataLoading,
  } = useQuery(CHART_ACTIVITY_BY_SECOND_QUERY, {
    variables,
    pollInterval: initialValues.pullInterval,
  })

const chartActivityBySecondData = useMemo(() => {
  return data
}, [data])

  // const chartActivityBySecondData = useMemo(() => {
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

  // const sortchartActivityBySecondData = (sortBy, ascending = true) => {
  //   setFilters({
  //     sort: {
  //       by: sortBy,
  //       ascending,
  //     },
  //   })
  // }

  return {
    chartActivityBySecondData,
    // chartActivityBySecondDataLoading,
    // sortchartActivityBySecondData,
  }
}

export default useChartActivityBySecond
