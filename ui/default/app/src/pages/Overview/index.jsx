import React from 'react'
import InspectingDevicesDashboard from './components/InspectingDevices'
import NetworkActivityDashboard from './components/NetworkActivity'

const index = () => {
  return (
    <>
      <NetworkActivityDashboard />
      <InspectingDevicesDashboard />
    </>
  )
}

export default index