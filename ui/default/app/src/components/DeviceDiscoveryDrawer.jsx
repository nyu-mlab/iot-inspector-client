import React, { useState } from 'react'
import DeviceDiscoveryCard from './DeviceDiscoveryCard'
import RefreshSpinner from './graphics/RefreshSpinner'
import useDevices from '@hooks/useDevices'
import { Field, Form, Formik } from 'formik'

const DeviceDiscoveryDrawer = () => {
  const { devicesData, devicesDataLoading, sortDevicesData } = useDevices()
  return (
    <>
      <div className="flex items-center gap-4 px-2">
        {/* <div className="w-8 h-8 animate-spin-slow">
          <RefreshSpinner />
        </div> */}
        <div>
          <h2>Select Devices to inspect on your network</h2>
          <p>Naming and tagging helps with our research.</p>
        </div>
      </div>

      {devicesDataLoading ? (
        <div className="skeleton h-[600px]"></div>
      ) : (
        <div className="flex flex-col flex-1 gap-2 py-4 overflow-auto border-b md:py-8">
          {devicesData.map((device) => (
            <DeviceDiscoveryCard key={device.device_id} device={device} />
          ))}
        </div>
      )}

      {/* <Formik className="flex justify-between py-4">
        <div className="flex items-center gap-2">
          <input type="checkbox" id="autoScan" checked />
          <label htmlFor="autoScan" className="p text-dark/50">Automatically inspect new devices as they are discovered</label>
        </div>
        <Field
          type="checkbox"
          name="toggle"
          label="Select All"
          className="w-4 h-4 !bg-gray-100"
        />
        <button
          type="submit"
          form="device-info-form"
          className="w-full btn btn-primary"
        >
          Monitor Devices</button>
      </Formik> */}
    </>
  )
}

export default DeviceDiscoveryDrawer
