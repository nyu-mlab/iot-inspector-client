import React, { useEffect, useState } from 'react'
import DeviceDrawer from './components/DeviceDrawer'
import EndpointList from './components/EndpointList'
import BarChart from '../../components/charts/BarChart'
import MapChart from '../../components/charts/MapChart'
import { HiChevronRight } from 'react-icons/hi'
import useQueryParam from '../../hooks/useQueryParam'
import useDeviceTrafficToCountries from '../../hooks/useDeviceTrafficToCountries'



const DeviceActivity = () => {
  const query = useQueryParam()
  const deviceId = query.get('deviceid')

  let deviceCountriesData = useDeviceTrafficToCountries(deviceId)
  deviceCountriesData = deviceCountriesData?.filter(d => d.device_id === deviceId)

  if (!deviceCountriesData?.length) {
    return <></>
  }

  return (
      <div className="flex  bg-white h-[calc(100vh-80px)]">
        <div className="w-full">
          <section className="flex items-center gap-2 pb-2 w-fit">
            <a href="/">Network Activity</a>
            <HiChevronRight className="text-gray-600/50" />
            <span className="font-bold text-gray-600/50">Device Activity</span>
          </section>
          <section className="relative">
            <h1>
              <strong>Device Activity</strong>{' '}
              <span className="font-thin">{ deviceCountriesData && deviceCountriesData.length > 0 && deviceCountriesData[0].device.auto_name}</span>
            </h1>
            <BarChart deviceId={deviceId} />
          </section>
          <section>
            <h2>Device Communication Endpoints</h2>
            <EndpointList data={deviceCountriesData} />
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
      </div>
  )
}

export default DeviceActivity
