import React from 'react'
import loadable from '../../utils/loadable'

// pages
const GettingStarted = loadable(() => import('./index.jsx'))

// route definition
export default {
  path: '/',
  children: [{ index: true, element: <GettingStarted /> }]
}