import React, { useEffect, useState } from 'react'
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

const useDevices = (props) => {
  // const [devicesData, setDevicesData] = useState([])
  const [filters, setFilters] = useState({})

  const variables = {
    ...(props || null),
  }
  const { data: devicesData, loading: devicesDataLoading, error } = useQuery(DEVICES_QUERY, {
    variables,
    fetchPolicy: 'network-only',
    pollInterval: 20000,
    // onCompleted: () => console.log('called'),
    // fetchPolicy: 'no-cache',
    // ...props?.queryOptions,
  })

  const sortDevicesData = (sortBy, direction = 'ASC') => {
    setFilters({
      sort: {
        by: sortBy,
        direction,
      },
    })
  }

  return {
    devicesData,
    devicesDataLoading,
    sortDevicesData,
    error: error ? error : null
  }
}

export default useDevices
