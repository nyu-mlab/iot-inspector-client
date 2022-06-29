import React, { useEffect, useState, useMemo } from 'react'
import Chart from 'react-apexcharts'
import { format } from 'date-fns'
import { gql, useQuery } from '@apollo/client'
import '../../utils/array'
import useServerConfig from '../../hooks/useServerConfig'
import useChartActivityBySecond from '../../hooks/useChartActivityBySecond'

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
  const x = useQuery(CHART_ACTIVITY_BY_SECOND_QUERY, {
    variables: {
      deviceId,
      currentTime: Math.round(new Date().getTime() / 1000),
    },
  })

  // console.log(x)

  console.log("@DEBUG::06292022-034657", x);

  return <></>

  const [chartOptions, setChartOptions] = useState({
    chart: {
      id: 'realtime',
      animations: {
        enabled: true,
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

  // const chartOptions = useMemo(() => {
  //   return {
  //     chart: {
  //       id: 'realtime',
  //       animations: {
  //         enabled: true,
  //         easing: 'linear',
  //         dynamicAnimation: {
  //           speed: 1000,
  //         },
  //       },
  //     },
  //     xaxis: {
  //       categories:
  //         chartActivityBySecondData?.chartActivityBySecond?.xAxis || [],
  //       type: 'string',
  //       range: 10,
  //     },
  //     stroke: {
  //       curve: 'smooth',
  //     },
  //   }
  // }, [chartActivityBySecondData])

  // const chartSeries = useMemo(() => {
  //   return chartActivityBySecondData?.chartActivityBySecond?.yAxis || []
  // }, [chartActivityBySecondData])

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
