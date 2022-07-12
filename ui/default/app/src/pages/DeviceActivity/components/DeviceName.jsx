import React from 'react'
import useDevices from '@hooks/useDevices'

const DeviceName = (deviceId) => {
  const { devicesData, devicesDataLoading } = useDevices({
    deviceId,
    queryOptions: {
      pollInterval: 5000,
    },
  })
  return (
    <span className="font-thin">
      {devicesData[0]?.device_info?.device_name ||
        devicesData[0]?.auto_name ||
        'Unknown Device'}
    </span>
  )
}

export default DeviceName
