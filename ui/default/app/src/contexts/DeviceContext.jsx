import React, { createContext, useContext, useMemo } from 'react'
import useQueryParam from '@hooks/useQueryParam'
import { gql, useQuery, useMutation } from '@apollo/client'
import useNotifications from '@hooks/useNotifications'

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

const UPDATE_DEVICE_INFO = gql`
  mutation Mutation(
    $deviceId: String!
    $deviceName: String
    $vendorName: String
    $tagList: String
    $isInspected: Int
    $isBlocked: Int
  ) {
    addDeviceInfo(
      device_id: $deviceId
      device_name: $deviceName
      vendor_name: $vendorName
      tag_list: $tagList
      is_inspected: $isInspected
      is_blocked: $isBlocked
    ) {
      device_id
      device_name
      vendor_name
      tag_list
      is_inspected
      is_blocked
    }
  }
`

const initialState = {
  selectedDevice: {},
  devicesDataLoading: true,
  devicesData: { devices: [] }
}

const DeviceContext = createContext(initialState)

const DeviceProvider = ({ children }) => {
  const query = useQueryParam()
  const selectedDeviceId = query.get('deviceid')
  const { showSuccess, showError } = useNotifications()

  const {
    data: devicesData,
    loading: devicesDataLoading,
    error: devicesError,
    refetch: refetchDevices
  } = useQuery(DEVICES_QUERY, {
    fetchPolicy: 'network-only',
    pollInterval: 15000
  })

  if(devicesError) showError(devicesError.message) //  NO_DEVICES

  const selectedDevice = useMemo(() => {
    if (devicesData?.devices.length && selectedDeviceId) {
      return devicesData.devices.find((d) => d.device_id === selectedDeviceId)
    }
  }, [devicesData, selectedDeviceId])

  const [updateDeviceInfoFn] = useMutation(UPDATE_DEVICE_INFO)

  const updateDeviceInfo = async (
    { deviceName, vendorName, tagList, isInspected, isBlocked },
    showToast = true,
    device_id = null
  ) => {
    const deviceId = device_id ? device_id : selectedDevice.device_id

    await updateDeviceInfoFn({
      variables: {
        deviceId,
        deviceName,
        vendorName,
        tagList,
        isInspected,
        isBlocked
      }
    })

    await refetchDevices()

    if (showToast) {
      showSuccess('SUCCESS_RECORD_UPDATED')
    }
  }

  const values = {
    devicesData,
    devicesDataLoading,
    selectedDevice,
    updateDeviceInfo,
    devicesError
  }
  return (
    <DeviceContext.Provider value={values}>{children}</DeviceContext.Provider>
  )
}

// const useDevices = () => useContext(DeviceContext)

export { DeviceContext, DeviceProvider }
