import React from 'react'
import DataCard from '../../../components/DataCard'
import BarChart from '../../../components/charts/BarChart'
import useIntervalQuery from '../../../hooks/useIntervalQuery'
import { gql } from '@apollo/client'
import { dataUseage } from '../../../utils/utils'

const HIGH_USEAGE_QUERY = gql`
  query Query {
    devices {
      auto_name
      ip
      outbound_byte_count
    }
  }
`

const NETWORK_ACTIVITY_QUERY = gql`
  query Query {
    networkActivity {
      weak_encryption
      unencrypted_http_traffic
      ads_and_trackers
    }
  }
`

const NetworkActivityDashboard = () => {
  const networkActivityResponse = useIntervalQuery(
    NETWORK_ACTIVITY_QUERY,
    null,
    5000
  )

  const highUseageResponse = useIntervalQuery(HIGH_USEAGE_QUERY, null, 20000)

  if (highUseageResponse?.data?.devices) {
    // sort it
    highUseageResponse.data?.devices.sort((a, b) => {
      return b.outbound_byte_count - a.outbound_byte_count
    })

    highUseageResponse.data.devices = highUseageResponse?.data?.devices?.slice(
      0,
      3
    )
  }

  return (
    <>
      <section className="flex flex-col gap-4">
        <h1>Network Activity</h1>
        <BarChart />
      </section>
      <section className="flex flex-col gap-4 bg-gray-50">
        <div className="grid gap-6 py-8 lg:grid-cols-2 md:py-4">
          <div>
            <p>
              High data usage devices in the past 24 hours
              <br />
              <a href="#inspecting-devices">View all devices</a>
            </p>
            <div className="grid grid-cols-2 gap-2 py-4">
              {highUseageResponse?.data?.devices &&
                highUseageResponse?.data?.devices.map((device, i) => (
                  <DataCard key={i} bytes={device.outbound_byte_count}>
                    <span className="text-xs">{device.auto_name}</span>
                    <br />
                    <span className="text-xs">{device.ip}</span>
                  </DataCard>
                ))}
            </div>
          </div>
          {console.log(networkActivityResponse)}
          <div>
            <p>
              Monitored devices sent/recieved
              <br />
               <strong>
                {dataUseage(
                  networkActivityResponse?.data?.networkActivity
                  ?.ads_and_trackers + networkActivityResponse?.data?.networkActivity
                  ?.unencrypted_http_traffic + networkActivityResponse?.data?.networkActivity
                  ?.weak_encryption
                )}
              </strong>
            </p>
            <div className="grid grid-cols-2 gap-2 py-4">
              <DataCard
                bytes={
                  networkActivityResponse?.data?.networkActivity
                    ?.ads_and_trackers
                }
              >
                <span className="text-xs">Ads & Trackers</span>
              </DataCard>
              <DataCard
                bytes={
                  networkActivityResponse?.data?.networkActivity
                    ?.unencrypted_http_traffic
                }
              >
                <span className="text-xs">Unencrypted HTTP Traffic</span>
              </DataCard>
              <DataCard
                bytes={
                  networkActivityResponse?.data?.networkActivity
                    ?.weak_encryption
                }
              >
                <span className="text-xs">Weak Encryption</span>
              </DataCard>
            </div>
          </div>
        </div>
      </section>
    </>
  )
}

export default NetworkActivityDashboard
