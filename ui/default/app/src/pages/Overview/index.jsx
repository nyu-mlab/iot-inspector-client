import React from 'react'
import InspectingDevicesDashboard from './components/InspectingDevices'
import NetworkActivityDashboard from './components/NetworkActivity'
import EndpointDrawer from '../../components/EndpointDrawer'

const index = () => {
  return (
    <main className="flex-1 md:pr-64 lg:md:pr-80">
      <NetworkActivityDashboard />
      <InspectingDevicesDashboard />
      <EndpointDrawer />
    </main>
  )
}

export default index