import React, { useEffect, useState } from 'react'
import Chart from 'react-apexcharts'
import { format } from 'date-fns'
import '../../utils/array'
import useServerConfig from '../../hooks/useServerConfig'
import useNetworkDownloadActivity from '../../hooks/useNetworkDownloadActivity'

const LineChart = ({ deviceId }) => {
  const { start_timestamp } = useServerConfig()
  const { networkDownloadActivity, networkDownloadActivityLoading } =
    useNetworkDownloadActivity({
      deviceId,
      pullInterval: 1500,
      filters: {
        sort: {
          by: 'ts',
          ascending: true,
        },
      },
    })
  const [chartOptions, setChartOptions] = useState({
    chart: {
      id: 'realtime',
      animations: {
        enabled: true,
        easing: 'linear',
        dynamicAnimation: {
          speed: 2000,
        },
      },
    },
    xaxis: {
      categories: [],
      range: 30,
    },
    stroke: {
      curve: 'smooth',
    },
  })

  const [chartSeries, setChartSeries] = useState([])

  useEffect(() => {
    if (!networkDownloadActivity.length) return

    const dates = networkDownloadActivity?.map((activity) => {
      return format(activity.ts * 1000, 'yyyy-MM-dd HH:mm:ss')
    })

    setChartOptions({
      ...chartOptions,
      xaxis: {
        categories: dates,
      },
    })

    // group items
    const yAxis = networkDownloadActivity.groupBy('device_id')

    const chartData = yAxis.map((data) => {
      const d = {}
      d.name = data.field
      d.data = data.groupList.map((dd) => dd.inbound_byte_count)
      return d
    })

    setChartSeries(chartData)
  }, [networkDownloadActivity])

  return (
    <>
      {networkDownloadActivityLoading ? (
        <>loading...</>
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
