import React from 'react'
import loadable from '../../utils/loadable'

// pages
const Consent = loadable(() => import('./index.jsx'))

// route definition
export default {
  path: '/consent',
  children: [{ index: true, element: <Consent /> }]
}