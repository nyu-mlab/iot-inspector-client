import React from 'react'
import DataCard from './DataCard'
import BarChart from './charts/BarChart'
import useIntervalQuery from '../hooks/useIntervalQuery'
import { gql, useQuery } from '@apollo/client'

const ADS_AND_TRACKERS_QUERY = gql`
  query Query($currentTime: Int) {
    adsAndTrackerBytes(current_time: $currentTime) {
      _sum
    }
  }
`

const UNENCRYPTED_HTTP_TRAFFIC_QUERY = gql`
  query Query($currentTime: Int) {
    unencryptedHttpTrafficBytes(current_time: $currentTime) {
      _sum
    }
  }
`

const WEAK_ENCRYPTION_QUERY = gql`
  query Query($currentTime: Int) {
    weakEncryptionBytes(current_time: $currentTime) {
      _sum
    }
  }
`

const NetworkActivityDashboard = () => {
  const timestamp = Math.round(new Date().getTime() / 1000)

  const adsTrackingResponse = useIntervalQuery(
    ADS_AND_TRACKERS_QUERY,
    {
      variables: { currentTime: timestamp },
    },
    7000
  )

  const unencryptedHttpTrafficResponse = useIntervalQuery(
    UNENCRYPTED_HTTP_TRAFFIC_QUERY,
    {
      variables: { currentTime: timestamp },
    },
    7000
  )

  const weakEncryptionResponse = useIntervalQuery(
    WEAK_ENCRYPTION_QUERY,
    {
      variables: { currentTime: timestamp },
    },
    7000
  )

  // console.log(devicesResponse.data?.devices)
  // console.log("unencryptedHttpTrafficResponse", unencryptedHttpTrafficResponse?.data?.unencryptedHttpTrafficBytes?._sum)
  // console.log("weakEncryptionResponse", weakEncryptionResponse?.data?.weakEncryptionBytes?._sum)

  return (
    <>
      <section className="flex flex-col gap-4">
        <h1>Network Activity</h1>
        <BarChart />
        <div className="grid gap-6 py-8 lg:grid-cols-2 md:py-4">
          <div>
              <p>High data usage devices in the past 24 hours
                <br />
                <a href="#">View all devices</a>
              </p>
            <div className="grid grid-cols-2 gap-2 py-4">
              <DataCard bytes={null}>
                <span className="text-xs">Unknown Device</span>
                <span className="text-xs">192.168.0.12</span>
              </DataCard>
              <DataCard bytes={null}>
                <span className="text-xs">Unknown Device</span>
                <span className="text-xs">192.168.0.12</span>
              </DataCard>
              <DataCard bytes={null}>
                <span className="text-xs">Unknown Device</span>
                <span className="text-xs">192.168.0.12</span>
              </DataCard>
            </div>
          </div>
          <div>
            <p>
              Monitored devices sent/recieved
              <br />
              <strong>{
                adsTrackingResponse?.data?.adsAndTrackerBytes?._sum + unencryptedHttpTrafficResponse?.data?.unencryptedHttpTrafficBytes?._sum + weakEncryptionResponse?.data?.weakEncryptionBytes?._sum
                }</strong> Bytes of data
            </p>
            <div className="grid grid-cols-2 gap-2 py-4">
              <DataCard
                bytes={adsTrackingResponse?.data?.adsAndTrackerBytes?._sum}
              >
                <span className="text-xs">Ads & Trackers</span>
              </DataCard>
              <DataCard bytes={unencryptedHttpTrafficResponse?.data?.unencryptedHttpTrafficBytes?._sum}>
                <span className="text-xs">Unencrypted HTTP Traffic</span>
              </DataCard>
              <DataCard bytes={weakEncryptionResponse?.data?.weakEncryptionBytes?._sum}>
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
