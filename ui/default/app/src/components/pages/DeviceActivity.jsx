import React from 'react'
import DefaultLayout from "../../layouts/DefaultLayout"
import DeviceDrawer from "../DeviceDrawer"
import EndpointList from "../EndpointList"
import BarChart from "../charts/BarChart"
import MapChart from "../charts/MapChart"
import { HiChevronRight } from "react-icons/hi";



const DeviceActivity = () => {
  return (
    <DefaultLayout>
      <main className="flex mt-[80px] bg-white h-[calc(100vh-80px)]">
        <div className="md:w-[calc(100vw-300px)]">
          <section className="flex items-center gap-2 pb-2 w-fit">
            <a href="/" >
              Network Activity
            </a>
            <HiChevronRight  className="text-gray-600/50"/>
            <span className="font-bold text-gray-600/50">Device Activity</span>
          </section>
          <section className="relative">


            <h1><strong>Device Activity</strong> <span className="font-thin"> [ device name ]</span></h1>
            <BarChart />
          </section>
          <section>
            <h2>Device Communication Endpoints</h2>
            <EndpointList />
          </section>
          <section>
            <MapChart />
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