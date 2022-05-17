import React from 'react'
import DataCard from './DataCard'
import BarChart from "./charts/BarChart"

const NetworkActivityDashboard = () => {
  return (
    <>
      <section className="flex flex-col gap-4 p-6 ">
        <h1>Network Activity</h1>
        {/* <div className="bg-gray-200 w-full h-[300px]"></div> */}
        <BarChart />
        <div className="grid grid-cols-4 gap-6">
          <div className="flex flex-col justify-center h-full">
            <p>High data usage devices in the past 24 hours</p>
            <a href="#">View all devices</a>
          </div>
          <DataCard />
          <DataCard />
          <DataCard />
        </div>
      </section>
      <section className="flex flex-col gap-4 bg-gray-50">
        <div className="grid grid-cols-2 gap-6">
          <div>
            <p>Monitored devices sent/recieved<br /><strong>0</strong> Bytes of data</p>
            <div className="grid grid-cols-2 gap-2 py-4">
              <DataCard />
              <DataCard />
              <DataCard />
              <DataCard />
            </div>
          </div>
          <div>
            <p><strong>13</strong> endpoints contacted<br />across <strong>3</strong> countries</p>
            <div className="grid grid-cols-2 gap-4 py-4">
              <DataCard />
              <DataCard />
              <DataCard />
              <DataCard />
            </div>
          </div>
        </div>
      </section>
    </>
  )
}

export default NetworkActivityDashboard