import React from 'react'
import { Link } from 'react-router-dom'
import DeviceDrawer from './components/DeviceDrawer'
import LineChart from '@components/charts/LineChart'
import { HiChevronRight } from 'react-icons/hi'
import DeviceCommunication from './components/DeviceCommunication'
import DeviceName from './components/DeviceName'
import useDevices from '@hooks/useDevices'

const DeviceActivity = () => {
  const { selectedDevice } = useDevices()

  return (
    <main className='flex-1 md:pr-64 lg:md:pr-80'>
      <div className='flex bg-white'>
        <div className='w-full'>
          <section className='flex items-center gap-2 pb-2 w-fit'>
            <Link to='/overview'>Network Activity</Link>
            <HiChevronRight className='text-gray-600/50' />
            <span className='font-bold text-gray-600/50'>Device Activity</span>
          </section>
          <section className='relative'>
            <h1>
              <strong>Device Activity</strong> <DeviceName />
            </h1>
            <LineChart deviceId={selectedDevice?.device_id} />
          </section>
          <DeviceCommunication deviceId={selectedDevice?.device_id} />
          <section>
            <hr className='w-100' />
            {/* <div className='flex justify-between py-8'>
              <h2>Delete Device Data</h2>
              <button className='btn btn-primary'>Delete a device data</button>
            </div> */}
          </section>
        </div>
        <DeviceDrawer />
      </div>
    </main>
  )
}

export default DeviceActivity
