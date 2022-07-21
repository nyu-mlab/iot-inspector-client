import React from 'react'
import { gql, useMutation } from '@apollo/client'
import useNotifications from '@hooks/useNotifications'

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
  const { showSuccess } = useNotifications()

  const [
    updateDeviceInfoFn,
    { data: updatedDeviceInfo, loading: updateDeviceInfoLoading, error },
  ] = useMutation(UPDATE_DEVICE_INFO)

  const updateDeviceInfo = async ({
    deviceName,
    vendorName,
    tagList,
    isInspected,
    isBlocked,
  }, showToast = true) => {
    await updateDeviceInfoFn({
      variables: {
        deviceId,
        deviceName,
        vendorName,
        tagList,
        isInspected,
        isBlocked,
      },
    })

    if (showToast) {
      showSuccess("Record Updated")
    }

  }

  return {
    updateDeviceInfo,
    updateDeviceInfoLoading,
    updatedDeviceInfo,
  }
}

export default useDeviceInfo
