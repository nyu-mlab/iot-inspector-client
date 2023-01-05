import React from 'react'
import { Link } from 'react-router-dom';
import EndpointList from '@components/EndpointList'
import MapChart from '@components/charts/MapChart'
import EndpointDrawer from '@components/EndpointDrawer'
import { HiChevronRight } from 'react-icons/hi'
import useQueryParam from '@hooks/useQueryParam'
import useUserConfigs from '@hooks/useUserConfigs'
import useDeviceTrafficToCountries from '@hooks/useDeviceTrafficToCountries'

const CommunicationEndpoints = () => {
  const query = useQueryParam()
  const deviceId = query.get('deviceid')
  const { is_consent } = useUserConfigs()

  const { deviceCountriesData, deviceCountriesDataLoading } =
    useDeviceTrafficToCountries(deviceId)

  return (
    <>
      <main className="flex-1 md:pr-64 lg:md:pr-80">
        <section className="flex items-center gap-2 pb-2 w-fit">
          {/* <Link to={is_consent === 1 ? '/overview' : '/'}>Network Activity</Link> TODO: Bring back when ready */}
          <Link to={'/overview'}>Network Activity</Link>
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
      </main>
    </>
  )
}

export default CommunicationEndpoints
