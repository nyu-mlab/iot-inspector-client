import React from 'react'
import InspectingDevicesDashboard from './components/InspectingDevices'
import NetworkActivityDashboard from './components/NetworkActivity'
import EndpointDrawer from '../../components/EndpointDrawer'

const index = () => {
  return (
    <>
      <NetworkActivityDashboard />
      <InspectingDevicesDashboard />
      <EndpointDrawer />
    </>
  )
}

export default index