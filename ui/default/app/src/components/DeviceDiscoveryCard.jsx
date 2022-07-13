import React from 'react'
import PropTypes from 'prop-types'
import { dataUseage } from '@utils/utils'

const DeviceDiscoveryCard = ({ device }) => {
  return (
     <div className="device-discovery-card">
      <form className="absolute top-2 right-3">
        <input type="checkbox" id="deviceID" checked/>
        <label htmlFor="deviceID" className="sr-only">Device Name</label>
      </form>
      <h3>{device?.device_info?.device_name ||
        device?.auto_name ||
        'Unknown Device'}</h3>
      <div className="flex flex-row gap-4">
        <p>{device && device.ip}</p>
        <p>{device && device.mac}</p>
      </div>
      <form className="grid grid-cols-3 gap-2 py-2">
        <div>
          <input type="input" id="deviceName" className="w-full p-2 bg-gray-100" placeholder="Device Name"/>
          <label htmlFor="deviceName" className="sr-only">Device Name</label>
        </div>
        <div>
          <input type="input" id="deviceType" className="w-full p-2 bg-gray-100" placeholder="Device Type"/>
          <label htmlFor="deviceType" className="sr-only">Device Type</label>
        </div>
        <div>
          <input type="input" id="manufacturerName" className="w-full p-2 bg-gray-100" placeholder="Manufacturer"/>
          <label htmlFor="manufacturerName" className="sr-only">Manufacturer</label>
        </div>
      </form>
    </div>
  )
}

export default DeviceDiscoveryCard