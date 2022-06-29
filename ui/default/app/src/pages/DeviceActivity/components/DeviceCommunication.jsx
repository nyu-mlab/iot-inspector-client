import React from 'react'
import MapChart from '../../../components/charts/MapChart'
import EndpointList from '../../../components/EndpointList'
import useDeviceTrafficToCountries from '../../../hooks/useDeviceTrafficToCountries'

const DeviceCommunication = ({ deviceId }) => {
  const { deviceCountriesData, deviceCountriesDataLoading } =
    useDeviceTrafficToCountries({deviceId, queryOptions: { pollInterval: 7000, }})

  if (deviceCountriesDataLoading) {
    return <>loading...</>
  }

  return (
    <>
      <section>
        <h2>Device Communication Endpoints</h2>
        <EndpointList data={deviceCountriesData} />
      </section>
      <section>
        <MapChart data={deviceCountriesData} />
      </section>
    </>
  )
}

export default DeviceCommunication
