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
  const [devicesData, setDevicesData] = useState([])
  const [filters, setFilters] = useState({})

  const variables = {
    ...(props?.deviceId || null),
  }

  const { data, loading: devicesDataLoading } = useQuery(DEVICES_QUERY, {
    variables,
    ...props?.queryOptions,
  })

  useEffect(() => {
    if (data?.devices) {
      let d = data.devices // TODO: preset filters, filter here https://github.com/ocupop/iot-inspector-client/issues/18
      console.table(d)

      if (filters?.sort) {
        console.table('TODO: SORT')
        /*
        d = d.slice().sort((a, b) => {
          if (filters.sort.direction === 'DESC') {
            if (a[filters.sort.by] > b[filters.sort.by]) {
              console.log('@DEBUG::06232022-015741')
              return -1
            }

            if (a[filters.sort.by] > b[filters.sort.by]) {
              console.log('@DEBUG::06232022-015741')
              return 1
            }
          }

          if (a[filters.sort.by] > b[filters.sort.by]) {
            console.log('@DEBUG::06232022-015741')
            return 1
          }
          if (a[filters.sort.by] > b[filters.sort.by]) {
            console.log('@DEBUG::06232022-015741')
            return -1
          }
          return 0
        })
      }

      console.group()
      for (const x of d) {
        console.log(x.auto_name, x.outbound_byte_count)
      }
      console.groupEnd()
      */
      }

      setDevicesData(d)
    }
  }, [data?.devices, filters])

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
  }
}

export default useDevices
