import { gql } from '@apollo/client'
import React, { useEffect, useState } from 'react'
import Chart from 'react-apexcharts'
import { format } from 'date-fns'
import '../../utils/array'
import useIntervalQuery from '../../hooks/useIntervalQuery'
import useServerConfig from '../../hooks/useServerConfig'
import { datesBetween } from '../../utils/utils'

const NETWORK_DOWNLOAD_ACTIVITY_QUERY = gql`
  query Query($deviceId: String) {
    flows(device_id: $deviceId) {
      device_id
      ts_mod_600
      ts_mod_3600
      inbound_byte_count
    }
  }
`

const BarChart = ({ deviceId }) => {
  const { start_timestamp } = useServerConfig()
  const [chartOptions, setChartOptions] = useState({
    chart: {
      id: 'bar',
      stacked: true,
    },
    xaxis: {
      categories: [],
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

  const variables = deviceId ? { deviceId } : null
  const networkDownloadActivityResponse = useIntervalQuery(
    NETWORK_DOWNLOAD_ACTIVITY_QUERY,
    variables,
    60000 // 1 minute
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

/*
class BarChart extends Component {
  constructor(props) {
    super(props);

    this.state = {
      options: {
        chart: {
          id: "bar",
          stacked: true
        },
        xaxis: {
          categories: ['2pm', '3pm', '4pm', '5pm', '6pm', '7pm', '8pm', '9pm']
        },
        options: {
          plotOptions: {
            bar: {
              borderRadius: '10px'
            }
          }
        }
      },
      series: [
        {
          name: "device 1",
          data: [30, 40, 45, 50, 49, 60, 70, 91]
        },
        {
          name: "device 2",
          data: [16, 10, 5, 5, 9, 6, 7, 1]
        },
        {
          name: "device 3",
          data: [16, 10, 5, 5, 9, 6, 7, 1]
        },
      ]
    };
  }
  render() {
    return (
      <div className="network-bar-chart">
          <div className="row">
            <div className="mixed-chart">
              <Chart
                options={this.state.options}
                series={this.state.series}
                type="bar"
                width="100%"
                height="300"
              />
            </div>
          </div>
        </div>
    )
  }
}*/

export default BarChart
