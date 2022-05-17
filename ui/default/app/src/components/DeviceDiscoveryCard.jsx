import React from 'react'

const DeviceDiscoveryCard = () => {
  return (
     <div className="relative p-3 bg-white rounded-md shadow-sm">
      <form className="absolute top-2 right-3">
        <input type="checkbox" id="deviceID" checked/>
        <label htmlFor="deviceID" className="sr-only">Device Name</label>
      </form>
      <h3>Unknown Device</h3>
      <div className="flex flex-row">
        <p>19.168.0.1</p>
        <p>C6:xx:xx:xx:xx:xx</p>
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