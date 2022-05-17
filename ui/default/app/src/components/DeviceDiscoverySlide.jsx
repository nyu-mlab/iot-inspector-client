import React from 'react'
import DeviceDiscoveryCard from "./DeviceDiscoveryCard"

const DeviceDiscoverySlide = () => {
  return (
    <div className="absolute top-[80px] right-0 z-10 w-3/4 h-[calc(100vh-80px)] bg-gray-100 p-4 shadow-lg flex justify-between flex-col">
      <div className="">
        <h2>Select Devices to inspect on your network</h2>
        <p>Naming and tagging helps with our research.</p>
      </div>
      <div className="flex flex-col flex-1 gap-2 py-4 overflow-auto border-b">
        <DeviceDiscoveryCard />
        <DeviceDiscoveryCard />
        <DeviceDiscoveryCard />
      </div>
      <form className="flex justify-between py-4">
        <div className="flex items-center gap-2">
          <input type="checkbox" id="autoScan" checked/>
          <label htmlFor="autoScan" className="p text-dark/50">Automatically inspect new devices as they are discovered</label>
        </div>
        <div className="flex items-center gap-2">
          <label htmlFor="selectAllDevices" className="text-dark"><strong>Select All</strong></label>
          <input type="checkbox" id="selectAllDevices" checked/>
        </div>
      </form>
      <button className="w-fit btn btn-primary">Scan Network</button>
    </div>
  )
}

export default DeviceDiscoverySlide