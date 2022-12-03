import React from 'react'
import useDevices from '@hooks/useDevices'

const DeviceName = () => {
  const { selectedDevice } = useDevices()

  return (
    <span className="font-thin">
      {selectedDevice?.device_info?.device_name ||
        selectedDevice?.auto_name ||
        'Unknown Device'}
    </span>
  )
}

export default DeviceName
