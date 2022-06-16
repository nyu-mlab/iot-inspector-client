import React from 'react'
import loadable from '../../utils/loadable'

// pages
const CommunicationEndpoints = loadable(() => import('./index.jsx'))

// route definition
export default {
  path: '/communication-endpoints',
  children: [{ index: true, element: <CommunicationEndpoints /> }]
}