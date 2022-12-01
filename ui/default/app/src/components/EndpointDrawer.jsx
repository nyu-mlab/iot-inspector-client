import { gql, useLazyQuery, useQuery } from '@apollo/client'
import React, { useEffect } from 'react'

import ScanNetworkButton from './ScanNetworkButton'

const COMMUNICATION_NAMES_QUERY = gql`
  query Query($deviceId: String) {
    communicationEndpointNames(device_id: $deviceId) {
      counterparty_hostname
    }
  }
`
const EndpointDrawer = ({ deviceId }) => {
  // const [loadCommunicationNames, { called, loading, data }] = useLazyQuery(
  //   COMMUNICATION_NAMES_QUERY
  // )

  // useEffect(() => {
  //   // const variables = deviceId ? { deviceId } : null
  //   loadCommunicationNames()
  // }, [])

  const { data, loading } = useQuery(COMMUNICATION_NAMES_QUERY, {
    fetchPolicy: 'network-only',
    pollInterval: 20000,
    // onCompleted: () => console.log('called'),
    // fetchPolicy: 'no-cache',
    // ...props?.queryOptions,
  })

  if (loading) {
    return <></>
  }

  return (
    <>
      <aside className='menu-drawer'>
        <div className='flex flex-col flex-1 min-h-0'>
          <h2 className='pr-16'>
            Communication
            <br />
            Endpoints
          </h2>
          <div className='flex flex-col flex-1 py-4 overflow-y-scroll'>
            <ul>
              {data?.communicationEndpointNames?.map((endpoints, i) => (
                <li key={i} className='py-0.5'>
                  <a
                    href='#'
                    className='text-xs transition text-dark hover:text-secondary'
                  >
                    {endpoints.counterparty_hostname}
                  </a>
                </li>
              ))}
            </ul>
          </div>
        </div>
        <div className='relative h-12 my-8'>
          <div className='absolute w-full transform -translate-x-1/2 -translate-y-1/2 top-1/2 left-1/2'>
            <div className='w-full h-px bg-secondary'></div>
          </div>
          <div className='absolute transform -translate-x-1/2 -translate-y-1/2 top-1/2 left-1/2'>
            <a
              href='/communication-endpoints/'
              className='p-5 font-semibold bg-white text-secondary'
            >
              View All
            </a>
          </div>
        </div>
        <ScanNetworkButton />
      </aside>
    </>
  )
}

export default EndpointDrawer
