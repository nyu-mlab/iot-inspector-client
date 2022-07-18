import React from 'react'
import { gql, useMutation } from '@apollo/client'

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

const useDeviceInfo = ({ deviceId }) => {
  const [
    updateDeviceInfoFn,
    { data: updatedDeviceInfo, loading: updateDeviceInfoLoading, error },
  ] = useMutation(UPDATE_DEVICE_INFO)

  const updateDeviceInfo = ({
    deviceName,
    vendorName,
    tagList,
    isInspected,
    isBlocked,
  }) => {
    updateDeviceInfoFn({
      variables: {
        deviceId,
        deviceName,
        vendorName,
        tagList,
        isInspected,
        isBlocked,
      },
    })
  }

  return {
    updateDeviceInfo,
    updateDeviceInfoLoading,
    updatedDeviceInfo,
  }
}

export default useDeviceInfo
