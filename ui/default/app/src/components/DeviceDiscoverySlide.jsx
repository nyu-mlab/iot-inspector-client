import React from 'react'
import DeviceDiscoveryCard from "./DeviceDiscoveryCard"
import RefreshSpinner from "./graphics/RefreshSpinner"

const DeviceDiscoverySlide = () => {
  return (
    <>
    <div className="modal-backdrop"></div>
    <div className="slide-panel">
      <div className="flex items-center gap-4 px-2">
        <div className="w-8 h-8 animate-spin-slow">
          <RefreshSpinner />
        </div>
        <div>
          <h2>Select Devices to inspect on your network</h2>
          <p>Naming and tagging helps with our research.</p>
        </div>
      </div>
      <div className="flex flex-col flex-1 gap-2 py-4 overflow-auto border-b md:py-8">
        <DeviceDiscoveryCard />
        <DeviceDiscoveryCard />
        <DeviceDiscoveryCard />
        <DeviceDiscoveryCard />
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
      <button className="w-fit btn btn-primary">Monitor Devices</button>
    </div>
    </>
  )
}

export default DeviceDiscoverySlide