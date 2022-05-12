import React from 'react'
import { HiBell, HiCog, HiRefresh } from "react-icons/hi";
import DeviceItem from "./DeviceItem";

const InspectingDevicesDashboard = () => {
  return (
    <section className="bg-gray-50 flex-flex-col-gap-4">
      <div className="grid grid-cols-2 gap-4 w-fit">
        <div>
          <h2 className="h1">Inspecting Devices</h2>
          <p className="py-2">Naming & tagging helps with <a href="#">our research</a></p>
        </div>
        <HiRefresh className="w-auto h-full py-4 text-secondary animate-spin-slow" />
      </div>
      <div className="px-4 py-2 text-gray-600 bg-white border border-gray-400 rounded-md">
        Search devices
      </div>

      <ul>
        <li className="py-4">
          <DeviceItem />
          <DeviceItem />
          <DeviceItem />
        </li>
      </ul>
    </section>
  )
}

export default InspectingDevicesDashboard