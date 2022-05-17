import React, { Component } from 'react'
import Chart from "react-apexcharts";

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
}

export default BarChart