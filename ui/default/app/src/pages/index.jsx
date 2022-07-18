import React from 'react'
import { BrowserRouter, useRoutes } from 'react-router-dom'
import OverviewRoutes from './Overview/routes'
import ConsentRoutes from './Consent/routes'
import CommunicationEndpointsRoutes from './CommunicationEndpoints/routes'
import DeviceActivityRoutes from './DeviceActivity/routes'
import GettingStartedRoutes from './GettingStarted/routes'


const Routes = () => {
  return useRoutes([
    OverviewRoutes,
    ConsentRoutes,
    CommunicationEndpointsRoutes,
    DeviceActivityRoutes,
    GettingStartedRoutes
  ])
}


export default function Router() {
  return (
    <BrowserRouter>
      <Routes />
    </BrowserRouter>
  )
}