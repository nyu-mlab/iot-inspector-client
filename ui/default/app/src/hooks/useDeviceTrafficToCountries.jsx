import React from 'react'
import { gql, useQuery } from '@apollo/client'
import { useMemo } from 'react'
import countries from '../constants/countries.json'

const deviceCountriesQuery = gql`
  query Query {
    dataUploadedToCounterParty {
      device_id
      device {
        auto_name
        # device_info
      }
      outbound_byte_count
      last_updated_time_per_country
      country_code
      counterparty_hostname
    }
  }
`

const useDeviceTrafficToCountries = (props) => {
  // const [deviceCountriesData, setDeviceCountriesData] = useState([])

  const { data, loading: deviceCountriesDataLoading } = useQuery(
    deviceCountriesQuery,
    {
      pollInterval: 7000,
    }
  )

  const calculate = (data) => {
    if (!data) return []
    let rawData = data.map((device) => {
      const country = countries.find((c) => c.country === device.country_code)
      return {
        ...device,
        ...country,
      }
    })

    if (props?.deviceId) {
      rawData = rawData?.filter((d) => d.device_id === props.deviceId)
    }

    return rawData
  }

  const deviceCountriesData = useMemo(() => calculate(data?.dataUploadedToCounterParty), [data?.dataUploadedToCounterParty])

  return {
    deviceCountriesData,
    deviceCountriesDataLoading,
  }
}

export default useDeviceTrafficToCountries
