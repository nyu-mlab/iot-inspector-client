import React from 'react'
import InspectingDevicesDashboard from '../components/InspectingDevicesDashboard'
import NetworkActivityDashboard from '../components/NetworkActivityDashboard'

const Dashboard = () => {
  return (
    <>
      <NetworkActivityDashboard />
      <InspectingDevicesDashboard />
    </>
  )
}

export default Dashboard