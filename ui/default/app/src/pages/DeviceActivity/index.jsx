import React from 'react'
import DeviceDrawer from './components/DeviceDrawer'
import LineChart from '@components/charts/LineChart'
import { HiChevronRight } from 'react-icons/hi'
import useQueryParam from '@hooks/useQueryParam'
import DeviceCommunication from './components/DeviceCommunication'
import DeviceName from './components/DeviceName'

const DeviceActivity = () => {
  const query = useQueryParam()
  const deviceId = query.get('deviceid')

  return (
    <main className="flex-1 md:pr-64 lg:md:pr-80">
      <div className="flex bg-white">
      <div className="w-full">
        <section className="flex items-center gap-2 pb-2 w-fit">
          <a href="/">Network Activity</a>
          <HiChevronRight className="text-gray-600/50" />
          <span className="font-bold text-gray-600/50">Device Activity</span>
        </section>
        <section className="relative">
          <h1>
            <strong>Device Activity</strong>{' '}<DeviceName deviceId={deviceId} />
            {/* <span className="font-thin">
              {deviceCountriesData &&
                deviceCountriesData.length > 0 &&
                deviceCountriesData[0].device.auto_name}
            </span> */}
          </h1>
          <LineChart deviceId={deviceId} />
        </section>
        <DeviceCommunication deviceId={deviceId} />
        <section>
          <hr className="w-100" />
          <div className="flex justify-between py-8">
            <h2>Delete Device Data</h2>
            <button className="btn btn-primary">Delete a device data</button>
          </div>
        </section>
      </div>
      <DeviceDrawer deviceId={deviceId} />
      </div>
    </main>
  )
}

export default DeviceActivity
