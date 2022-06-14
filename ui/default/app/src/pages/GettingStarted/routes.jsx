import React from 'react'
import loadable from '../../utils/loadable'

// pages
const GettingStarted = loadable(() => import('./index.jsx'))

// route definition
export default {
  path: '/getting-started',
  children: [{ index: true, element: <GettingStarted /> }]
}