import React, { createContext, useContext } from 'react'
import { gql, useQuery } from '@apollo/client'

const DEVICES_QUERY = gql`
  query Devices($deviceId: String) {
    devices(device_id: $deviceId) {
      device_id
      auto_name
      ip
      mac
      outbound_byte_count
      device_info {
        device_name
        vendor_name
        tag_list
        is_inspected
      }
    }
  }
`

const initialState = {}

const DeviceContext = createContext(initialState)

const DeviceProvider = ({ children }) => {
  const {
    data: devicesData,
    loading: devicesDataLoading,
    error
  } = useQuery(DEVICES_QUERY, {
    fetchPolicy: 'network-only',
    pollInterval: 15000
  })

  const values = { devicesData, devicesDataLoading }
  return (
    <DeviceContext.Provider value={values}>{children}</DeviceContext.Provider>
  )
}

// const useDevices = () => useContext(DeviceContext)

export { DeviceContext, DeviceProvider }
