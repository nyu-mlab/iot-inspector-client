import { gql, useQuery } from '@apollo/client'
import React, { useEffect, useState } from 'react'
import countries from '../constants/countries.json'

const deviceCountriesQuery = gql`
  query Query($deviceId: String!) {
    deviceTrafficToCountries(device_id: $deviceId) {
      outbound_byte_count
      last_updated_time_per_country
      country_code
    }
  }
`

const useDeviceTrafficToCountries = (deviceId) => {
  const [deviceCountriesData, setDeviceCountriesData] = useState([])
  
  const { data: deviceCountriesRawData, loading: deviceCountriesRawLoading } =
    useQuery(deviceCountriesQuery, {
      variables: {
        deviceId,
      },
    })

  useEffect(() => {
    if (!deviceCountriesRawLoading) {
      const data = deviceCountriesRawData?.deviceTrafficToCountries?.map((device) => {
        const country = countries.find((c) => c.country === device.country_code)
        return {
          ...device,
          ...country,
        }
      })
      setDeviceCountriesData(data)
    }
  }, [deviceCountriesRawLoading])

  return deviceCountriesData
}

export default useDeviceTrafficToCountries