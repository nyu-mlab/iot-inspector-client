import { gql, useQuery } from '@apollo/client'
import React, { useEffect, useState } from 'react'
import countries from '../constants/countries.json'

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
      counterparty_hostname
    }
  }
`

const useDeviceTrafficToCountries = ({ deviceId }) => {
  const [deviceCountriesData, setDeviceCountriesData] = useState([])

  const { data, loading: deviceCountriesDataLoading } = useQuery(
    deviceCountriesQuery,
    {
      pollInterval: 5000,
    }
  )

  useEffect(() => {
    if (data?.dataUploadedToCounterParty) {
      let rawData = data.dataUploadedToCounterParty?.map((device) => {
        const country = countries.find((c) => c.country === device.country_code)
        return {
          ...device,
          ...country,
        }
      })

      if (deviceId) {
        rawData = rawData?.filter((d) => d.device_id === deviceId)
      }

      setDeviceCountriesData(rawData)
    }
  }, [data?.dataUploadedToCounterParty])

  return {
    deviceCountriesData,
    deviceCountriesDataLoading,
  }
}

export default useDeviceTrafficToCountries
