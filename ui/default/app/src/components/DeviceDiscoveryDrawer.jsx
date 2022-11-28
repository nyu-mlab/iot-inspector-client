import React, { useState, useEffect } from 'react'
import DeviceDiscoveryCard from './DeviceDiscoveryCard'
import RefreshSpinner from './graphics/RefreshSpinner'
import useDevices from '@hooks/useDevices'
import useNotifications from '@hooks/useNotifications'
import { Field, Form, Formik } from 'formik'

const DeviceDiscoveryDrawer = () => {
  const { devicesData, devicesDataLoading, sortDevicesData, error } = useDevices()
  const { showError } = useNotifications()

  useEffect(() => {
    if(error) showError(error.message)
  }, [error])

  return (
    <>
      <div className="flex items-center gap-4 px-2">
        <div>
          <h2>Select Devices to inspect on your network</h2>
          <p>Naming and tagging helps with our research.</p>
        </div>
      </div>

      {devicesDataLoading ? (
        <div className="skeleton h-[600px]"></div>
      ) : (
        <div className="flex flex-col flex-1 gap-2 py-4 overflow-auto border-b md:py-8">
          {devicesData.devices.map((device) => (
            <DeviceDiscoveryCard key={device.device_id} device={device} />
          ))}
        </div>
      )}
    </>
  )
}

export default DeviceDiscoveryDrawer
