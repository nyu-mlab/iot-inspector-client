import React from 'react'

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
  const [updateDeviceInfoFn, { data, loading, error }] =
    useMutation(UPDATE_DEVICE_INFO)

  const updateDeviceInfo = (
    { deviceName, vendorName, tagList, isInspected, isBlocked }
  ) => {
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
    updateDeviceInfo
    // loading
    // data
  }
}

export default useDeviceInfo
