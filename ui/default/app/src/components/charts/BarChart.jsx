import { gql } from '@apollo/client'
import React, { useMemo } from 'react'
import Chart from 'react-apexcharts'
import '@utils/array'

import useChartActivity from '@hooks/useChartActivity'
import useDevices from '@hooks/useDevices'

const BarChart = ({ deviceId }) => {
  const { networkDownloadActivity, networkDownloadActivityLoading } =
    useChartActivity({ pullInterval: 60000 })

  const { devicesData } = useDevices()

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
    if (!devicesData || !networkDownloadActivity) return []
    let data = networkDownloadActivity
    data = data.chartActivity.yAxis.map(activity => {
      const device = devicesData.find(d => d.device_id === activity.name)

      return {
        ...activity,
        name: device.device_info.device_name || device.auto_name || `Unknown Device - ${d.device_id}`
      }
    })

    data = {
      ...networkDownloadActivity,
      chartActivity: {
        yAxis: data
      }
    }

    return data?.chartActivity?.yAxis.slice(0, 3) || []
  }, [networkDownloadActivity, devicesData])

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
