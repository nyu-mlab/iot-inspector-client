import { gql } from '@apollo/client'
import React, { useMemo } from 'react'
import Chart from 'react-apexcharts'
import '../../utils/array'

import useChartActivity from '../../hooks/useChartActivity'

const BarChart = ({ deviceId }) => {
  const { networkDownloadActivity, networkDownloadActivityLoading } =
    useChartActivity({ pullInterval: 60000 })

  const chartOptions = useMemo(() => {
    return {
      chart: {
        id: 'bar',
        stacked: true,
      },
      xaxis: {
        // categories: [],
        categories: networkDownloadActivity?.chartActivity?.xAxis || [],
        type: 'string',
      },
      options: {
        plotOptions: {
          bar: {
            borderRadius: '10px',
          },
        },
      },
    }
  }, [networkDownloadActivity])

  const chartSeries = useMemo(() => {
    return networkDownloadActivity?.chartActivity?.yAxis.slice(0,3) || []
  }, [networkDownloadActivity])

  return (
    <div className="network-bar-chart">
      <div className="row">
        <div className="mixed-chart">
          <Chart
            options={chartOptions}
            series={chartSeries}
            type="bar"
            width="100%"
            height="300"
          />
        </div>
      </div>
    </div>
  )
}

export default BarChart
