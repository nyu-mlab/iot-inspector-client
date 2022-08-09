import React from 'react'
import useDevices from '@hooks/useDevices'

const DeviceName = ({deviceId}) => {
  const { devicesData, devicesDataLoading } = useDevices({
    deviceId,
  })

  return (
    <>testing</>
    // <span className="font-thin">
    //   {devicesData.devices[0]?.device_info?.device_name ||
    //     devicesData.devices[0]?.auto_name ||
    //     'Unknown Device'}
    // </span>
  )
}

export default DeviceName
