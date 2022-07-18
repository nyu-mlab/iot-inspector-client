import React from 'react'
import EndpointList from '@components/EndpointList'
import MapChart from '@components/charts/MapChart'
import EndpointDrawer from '../../components/EndpointDrawer'
import { HiChevronRight } from 'react-icons/hi'
import useQueryParam from '@hooks/useQueryParam'
import useDeviceTrafficToCountries from '@hooks/useDeviceTrafficToCountries'

const CommunicationEndpoints = () => {
  const query = useQueryParam()
  const deviceId = query.get('deviceid')

  const { deviceCountriesData, deviceCountriesDataLoading } =
    useDeviceTrafficToCountries(deviceId)

  return (
    <>
      <section className="flex items-center gap-2 pb-2 w-fit">
        <a href="/">Network Activity</a>
        <HiChevronRight className="text-gray-600/50" />
        <span className="font-bold text-gray-600/50">
          Communication Endpoints
        </span>
      </section>
      <section>
        <h1>Communication Endpoints</h1>
        {deviceCountriesDataLoading ? (

          <div className="h-full skeleton" />
        ) : (
          <>
            <div>
              <MapChart data={deviceCountriesData} />
            </div>
            <EndpointList data={deviceCountriesData} />
          </>
        )}
      </section>
      <EndpointDrawer />
    </>
  )
}

export default CommunicationEndpoints
