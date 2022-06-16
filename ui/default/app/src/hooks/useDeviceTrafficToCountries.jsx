import { gql, useQuery } from '@apollo/client'
import React, { useEffect, useState } from 'react'
import countries from '../constants/countries.json'
import useIntervalQuery from './useIntervalQuery'

const deviceCountriesQuery = gql`
  query Query {
    dataUploadedToCounterParty {
      device_id
      device {
        auto_name
      }
      outbound_byte_count
      last_updated_time_per_country
      country_code
    }
  }
`

const useDeviceTrafficToCountries = () => {
  const [deviceCountriesData, setDeviceCountriesData] = useState([])
  
  const { data: deviceCountriesRawData, loading: deviceCountriesRawLoading } =
  useIntervalQuery(deviceCountriesQuery, null, 4500)

  useEffect(() => {
    if (!deviceCountriesRawLoading && deviceCountriesRawData) {
      const data = deviceCountriesRawData?.dataUploadedToCounterParty?.map((device) => {
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