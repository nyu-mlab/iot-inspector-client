import React from 'react'
import { BrowserRouter, useRoutes } from 'react-router-dom'
import OverviewRoutes from './Overview/routes'
import ConsentRoutes from './Consent/routes'
import CommunicationEndpointsRoutes from './CommunicationEndpoints/routes'
import DeviceActivityRoutes from './DeviceActivity/routes'
import GettingStartedRoutes from './GettingStarted/routes'
import SandboxRoutes from './Sandbox/routes'
import { ModalDrawerProvider } from '@contexts/ModalDrawerContext'
import { NotificationsProvider } from '@contexts/NotificationsContext'
import { UserConfigsProvider } from '@contexts/UserConfigsContext'
import { DeviceProvider } from '@contexts/DeviceContext'

const Routes = () => {
  return useRoutes([
    SandboxRoutes,
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
      <UserConfigsProvider>
        <DeviceProvider>
          <NotificationsProvider>
            <ModalDrawerProvider>
              <Routes />
            </ModalDrawerProvider>
          </NotificationsProvider>
        </DeviceProvider>
      </UserConfigsProvider>
    </BrowserRouter>
  )
}
