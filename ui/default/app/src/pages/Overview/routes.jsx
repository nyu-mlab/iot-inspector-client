import React from 'react'
import loadable from '../../utils/loadable'

// pages
const Overview = loadable(() => import('./index.jsx'))

// route definition
export default {
  path: '/overview',
  children: [{ index: true, element: <Overview /> }]
}