import { gql } from '@apollo/client'
import React, { useEffect, useState } from 'react'
import Chart from 'react-apexcharts'
import { format } from 'date-fns'
import '../../utils/array'
import useServerConfig from '../../hooks/useServerConfig'
import { datesBetween } from '../../utils/utils'
import useNetworkDownloadActivity from '../../hooks/useNetworkDownloadActivity'

// TODO:
// - Check server time stamp if gte an hour:
// hours will be your xaxis, use the most recent 8

// - seconds / 1 min / 10 min / 1 hour

// Server star time at 0 (server just started)
// local time < +60 minutes
//  get data by minute
// Local time > +60 minutes
//  get data by 10 minutes (taking the last 6, which is the last hour)
// local time > +6 hours
//  get data by hour (taking the last 6, which is the last 6 hours)

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
      categories:  [
           '2022-06-27 18:00:00',
           '2022-06-27 19:00:00',
           '2022-06-27 20:00:00',
           '2022-06-27 21:00:00',
           '2022-06-27 22:00:00',
           '2022-06-27 23:00:00',
           '2022-06-28 00:00:00',
           '2022-06-28 07:00:00',
           '2022-06-28 08:00:00',
           '2022-06-28 09:00:00',
           '2022-06-28 10:00:00',
           '2022-06-28 11:00:00',
           '2022-06-28 12:00:00',
           '2022-06-28 13:00:00'
         ],
      type: 'string',
    },
    options: {
      plotOptions: {
        bar: {
          borderRadius: '10px',
        },
      },
    },
  })
  const [chartSeries, setChartSeries] = useState([
    {
      name: 's1663',
      data: [
        11539, 17059, 18357, 18513, 18049, 17807, 428, 454, 18154, 13702, 15270,
        14557, 13557, 2715,
      ],
    },
    {
      name: 's5242',
      data: [
        12429, 17715, 17858, 17010, 18870, 16472, 371, 463, 17511, 15447, 16828,
        14693, 14613, 2833,
      ],
    },
    {
      name: 's5969',
      data: [
        12537, 19359, 16781, 17843, 17961, 18183, 817, 257, 18059, 14470, 16635,
        15007, 14239, 3056,
      ],
    },
    {
      name: 's6866',
      data: [
        11468, 18189, 18763, 17409, 16491, 17361, 678, 428, 18281, 14864, 15752,
        14847, 14038, 2869,
      ],
    },
    {
      name: 's7311',
      data: [
        12539, 17985, 17644, 18193, 17398, 17781, 787, 832, 17634, 15790, 15559,
        14472, 13639, 2297,
      ],
    },
    {
      name: 's7634',
      data: [
        11910, 18602, 16128, 18755, 17221, 18662, 754, 516, 19166, 14607, 15910,
        14799, 13538, 2378,
      ],
    },
    {
      name: 's7890',
      data: [
        11181, 18282, 18186, 18470, 19123, 18243, 480, 528, 18473, 15221, 16099,
        13693, 13057, 3008,
      ],
    },
    {
      name: 's8808',
      data: [
        10870, 18880, 16557, 17544, 17632, 17083, 271, 535, 17780, 14355, 16394,
        13960, 14508, 2655,
      ],
    },
    {
      name: 's8961',
      data: [
        12066, 18219, 17138, 16743, 17761, 18205, 617, 483, 17154, 15059, 15905,
        14776, 14274, 2610,
      ],
    },
    {
      name: 's9376',
      data: [
        12290, 18371, 17691, 16478, 17747, 17488, 416, 532, 17676, 14284, 17925,
        14155, 14848, 2906,
      ],
    },
  ])

  // const { networkDownloadActivity, networkDownloadActivityLoading } =
  //   useNetworkDownloadActivity({
  //     deviceId,
  //     // pullInterval: 180000, // 3 minutes
  //     filters: {
  //       sort: {
  //         by: 'ts_mod_3600',
  //         ascending: true,
  //       },
  //     },
  //   })

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
