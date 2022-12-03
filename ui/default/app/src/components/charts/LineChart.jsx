import React, { useEffect, useState } from 'react'
import Chart from 'react-apexcharts'
import { gql, useQuery } from '@apollo/client'
import '../../utils/array'

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

const LineChart = ({ deviceId }) => {
  const chartActivityBySecondDataLoading = false
  const {
    data:chartActivityBySecondData ,
  } = useQuery(CHART_ACTIVITY_BY_SECOND_QUERY, {
    variables: {
      deviceId,
      currentTime: Math.round(new Date().getTime() / 1000),
    },
    pollInterval:2000,
  })

  const [chartOptions, setChartOptions] = useState({
    chart: {
      id: 'realtime',
      animations: {
        enabled: false,
        easing: 'linear',
        dynamicAnimation: {
          speed: 1500,
        },
      },
    },
    xaxis: {
      categories: [],
      type: 'string',
      range: 10,
    },
    stroke: {
      curve: 'smooth',
    },
  })

  const [chartSeries, setChartSeries] = useState([])

  useEffect(() => {
    if (!chartActivityBySecondData?.chartActivityBySecond) return
    setChartOptions({
      ...chartOptions,
      xaxis: {
        categories: chartActivityBySecondData?.chartActivityBySecond.xAxis,
      },
    })

    setChartSeries( chartActivityBySecondData?.chartActivityBySecond.yAxis)
  }, [chartActivityBySecondData?.chartActivityBySecond])


  return (
    <>
      {chartActivityBySecondDataLoading ? (
        <div className="skeleton h-[300px]">
        </div>
      ) : (
        <div className="network-bar-chart">
          <div className="row">
            <div className="mixed-chart">
              <Chart
                options={chartOptions}
                series={chartSeries}
                type="line"
                width="100%"
                height="300"
              />
            </div>
          </div>
        </div>
      )}
    </>
  )
}

export default LineChart
