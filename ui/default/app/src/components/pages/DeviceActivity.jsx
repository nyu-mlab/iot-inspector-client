import React, { useEffect, useState } from 'react'
import DefaultLayout from '../../layouts/DefaultLayout'
import DeviceDrawer from '../DeviceDrawer'
import EndpointList from '../EndpointList'
import BarChart from '../charts/BarChart'
import MapChart from '../charts/MapChart'
import { HiChevronRight } from 'react-icons/hi'
import useQueryParam from '../../hooks/useQueryParam'
import useDeviceTrafficToCountries from '../../hooks/useDeviceTrafficToCountries'



const DeviceActivity = () => {
  const query = useQueryParam()
  const deviceId = query.get('deviceid')

  const deviceCountriesData = useDeviceTrafficToCountries(deviceId)

  return (
    <DefaultLayout>
      <main className="flex  bg-white h-[calc(100vh-80px)]">
        <div className="md:w-[calc(100vw-275px)]">
          <section className="flex items-center gap-2 pb-2 w-fit">
            <a href="/">Network Activity</a>
            <HiChevronRight className="text-gray-600/50" />
            <span className="font-bold text-gray-600/50">Device Activity</span>
          </section>
          <section className="relative">
            <h1>
              <strong>Device Activity</strong>{' '}
              <span className="font-thin"> [ device name ]</span>
            </h1>
            <BarChart />
          </section>
          <section>
            <h2>Device Communication Endpoints</h2>
            <EndpointList />
          </section>
          <section>
            <MapChart data={deviceCountriesData}/>
          </section>
          <section>
            <hr className="w-100" />
            <div className="flex justify-between py-8">
              <h2>Delete Device Data</h2>
              <button className="btn btn-primary">Delete a device data</button>
            </div>
          </section>
        </div>

        <DeviceDrawer />
      </main>
    </DefaultLayout>
  )
}

export default DeviceActivity
