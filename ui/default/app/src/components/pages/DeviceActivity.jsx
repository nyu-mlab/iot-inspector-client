import React from 'react'
import DefaultLayout from "../../layouts/DefaultLayout"
import DeviceDrawer from "../DeviceDrawer"
import EndpointList from "../EndpointList"
import BarChart from "../charts/BarChart"

const DeviceActivity = () => {
  return (
    <DefaultLayout>
      <main className="flex mt-[80px] bg-white h-[calc(100vh-80px)]">
        <div className="w-[calc(100vw-300px)]">
          <section className="w-full p-4">
            <h1 className="h2"><strong>Device Activity |</strong> [ device name ]</h1>
            <BarChart />
          </section>
          <section>
            <h2>Device Communication Endpoints</h2>
            <EndpointList />
          </section>
          <section>
            map chart
          </section>
          <section>
            <hr className="w-100" />
            <div className="flex justify-between py-8">
              <h2>Delete Device Data</h2>
              <button className="btn btn-primary">Delete adevice data</button>
            </div>

          </section>
        </div>

        <DeviceDrawer />
      </main>
    </DefaultLayout>
  )
}

export default DeviceActivity