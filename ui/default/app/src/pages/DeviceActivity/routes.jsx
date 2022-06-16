import React from 'react'
import loadable from '../../utils/loadable'

// pages
const DeviceActivity = loadable(() => import('./index.jsx'))

// route definition
export default {
  path: '/device-activity',
  children: [{ index: true, element: <DeviceActivity /> }]
}