import React from 'react'
import loadable from '../../utils/loadable'

// pages
const InspectingDevicesDashboard = loadable(() => import('./InspectingDevicesDashboard.jsx'))

// route definition
export default {
  path: '/sandbox/inspecting-devices',
  children: [{ index: true, element: <InspectingDevicesDashboard /> }]
}