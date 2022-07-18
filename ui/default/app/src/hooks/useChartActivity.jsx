import React from 'react'
import { gql, useQuery } from '@apollo/client'
import { useMemo } from 'react'

const CHART_ACTIVITY_QUERY = gql`
  query Query {
    chartActivity {
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
  }

  const variables = {
    deviceId: props?.deviceId || null,
  }

  const {
    data: networkDownloadActivity,
    loading: networkDownloadActivityLoading,
  } = useQuery(CHART_ACTIVITY_QUERY, {
    variables,
    pollInterval: initialValues.pullInterval,
  })

  return {
    networkDownloadActivity,
    networkDownloadActivityLoading,
    // sortNetworkDownloadActivity,
  }
}

export default useChartActivity
