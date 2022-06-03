import React from 'react'
import ReactDOM from 'react-dom/client'
import DeviceActivity from "../src/components/pages/DeviceActivity"
import '../src/styles/index.css'

ReactDOM.createRoot(document.getElementById('deviceActivity')).render(
  <React.StrictMode>
    <DeviceActivity />
  </React.StrictMode>
)
