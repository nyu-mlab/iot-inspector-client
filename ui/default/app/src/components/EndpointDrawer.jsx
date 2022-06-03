import { gql, useQuery } from '@apollo/client'
import React from 'react'
import DeviceDiscoverySlide from './DeviceDiscoverySlide'

const DEVICES_QUERY = gql`
  query Query {
    devices {
      device_id
      auto_name
    }
  }
`

const EndpointDrawer = () => {
  const devicesResponse = useQuery(DEVICES_QUERY)
  return (
    <>
      <aside className="menu-drawer">
        <h2>Communication Endpoints</h2>
        <div className="flex-1 py-4 overflow-y-scroll">
          <ul>
            {devicesResponse?.data?.devices?.map((device) => (
              <li key={device.device_id} className="py-0.5">
                <a
                  href="#"
                  className="text-xs transition text-dark hover:text-secondary"
                >
                  {device.auto_name}
                </a>
              </li>
            ))}
            {/* <li className="py-0.5"><a href="#" className="text-xs transition text-dark hover:text-secondary">Adobe</a></li>
            <li className="py-0.5"><a href="#" className="text-xs transition text-dark hover:text-secondary">Synology</a></li>
            <li className="py-0.5"><a href="#" className="text-xs transition text-dark hover:text-secondary">Google</a></li> */}
          </ul>
        </div>
        <div className="relative h-12 my-8">
          <div className="absolute w-full transform -translate-x-1/2 -translate-y-1/2 top-1/2 left-1/2">
            <div className="w-full h-px bg-secondary"></div>
          </div>
          <div className="absolute transform -translate-x-1/2 -translate-y-1/2 top-1/2 left-1/2">
            <a
              href="/communication-endpoints/"
              className="p-5 font-semibold bg-white text-secondary"
            >
              View All
            </a>
          </div>
        </div>
        <button className="w-full btn btn-primary">Scan Network</button>
        {/* <DeviceDiscoverySlide /> */}
      </aside>
    </>
  )
}

export default EndpointDrawer
