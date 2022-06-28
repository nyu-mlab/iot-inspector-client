import { gql } from '@apollo/client'
import React, { useEffect, useState } from 'react'
import Chart from 'react-apexcharts'
import { format } from 'date-fns'
import '../../utils/array'
import useServerConfig from '../../hooks/useServerConfig'
import { datesBetween } from '../../utils/utils'
import useNetworkDownloadActivity from '../../hooks/useNetworkDownloadActivity'

const BarChart = ({ deviceId }) => {
  const { start_timestamp } = useServerConfig()
  const [chartOptions, setChartOptions] = useState({
    chart: {
      id: 'bar',
      stacked: true,
    },
    xaxis: {
      // categories: [],
      // range: 30,
      categories: [1991],
      type: 'numeric'
    },
    options: {
      plotOptions: {
        bar: {
          borderRadius: '10px',
        },
      },
    },
  })
  const [chartSeries, setChartSeries] = useState([])
  const { networkDownloadActivity, networkDownloadActivityLoading } =
    useNetworkDownloadActivity({
      deviceId,
      // pullInterval: 180000, // 3 minutes
      filters: {
        sort: {
          by: 'ts_mod_3600',
          ascending: true,
        },
      },
    })

  useEffect(() => {
    if (!networkDownloadActivity.length) return
    
    // const dates = networkDownloadActivity?.map((activity) => {
    //   return activity?.groupList.map((a) =>
    //     format(a.ts_mod_3600 * 1000, 'yyyy-MM-dd HH:mm:ss')
    //   )
    // })[0].filter((v, i, a) => a.indexOf(v) === i);

    // console.log(dates)

    // setChartOptions({
    //   ...chartOptions,
    //   xaxis: {
    //     categories: dates,
    //   },
    // })


    // // // group items
    console.log("@DEBUG::06272022-044754", chartSeries);
    const chartData = networkDownloadActivity.map((data) => {
      const d = {}
      d.name = data.field
      // d.data = [[1, 30], [2,40], [1,45], [1,50], [1,49], [1,60], [1,70], [1,91]]
      // d.data = [{ x: '05/06/2014', y: [30, 40, 45, 50, 49, 60, 70, 91] }, { x: '05/08/2014', y: [30, 40, 45, 50, 49, 60, 70, 91] }]
      // d.data = data.groupList.map((dd) => dd.inbound_byte_count)
      d.data = data.groupList.map((dd) => {
        return [dd.ts_mod_3600, dd.inbound_byte_count]
      })
      return d
    })

    console.log(chartData)

    // setChartSeries([{ data:  [[1, 30], [2,40], [3,45], [1,50], [1,49], [1,60], [1,70], [1,91]] }])
    setChartSeries(chartData)
  }, [networkDownloadActivity])




  /*
  const variables = deviceId ? { deviceId } : null

  const networkDownloadActivityResponse = useQuery(
    NETWORK_DOWNLOAD_ACTIVITY_QUERY,
    {
    pollInterval: 60000, // 1 minute
  }
  )

  // populate x-axis / y-axis
  useEffect(() => {
    if (!start_timestamp) return

    let dates = start_timestamp
      ? datesBetween(new Date(start_timestamp * 1000), new Date(), 'hour')
      : []

    dates = dates?.map((date) => {
      return format(date, 'yyyy-MM-dd HH:mm:ss')
    })

    setChartOptions({
      ...chartOptions,
      xaxis: {
        categories: dates,
      },
    })

    if (!networkDownloadActivityResponse.data) return
    let yAxis = networkDownloadActivityResponse.data.flows
    // filter unique items
    yAxis = [
      ...new Map(yAxis.map((item) => [item['ts_mod_3600'], item])).values(),
    ]

    // group items
    yAxis = yAxis.groupBy('device_id')

    const chartData = yAxis.map((data) => {
      const d = {}
      d.name = data.field
      d.data = data.groupList.map((dd) => dd.inbound_byte_count)
      // We don't need the last element as its for the current hour...
      d.data.pop()
      return d
    })


    setChartSeries(chartData)
  }, [start_timestamp, networkDownloadActivityResponse])
  */

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
