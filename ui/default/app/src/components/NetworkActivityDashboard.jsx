import React from 'react'
import DataCard from './DataCard'
import BarChart from './charts/BarChart'
import useIntervalQuery from '../hooks/useIntervalQuery'
import { gql } from '@apollo/client'
import { dataUseage } from '../utils/utils'

const HIGH_USEAGE_QUERY = gql`
  query Query {
    devices {
      auto_name
      ip
      outbound_byte_count
    }
  }
`

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
  const adsTrackingResponse = useIntervalQuery(ADS_AND_TRACKERS_QUERY, 5000)

  const unencryptedHttpTrafficResponse = useIntervalQuery(
    UNENCRYPTED_HTTP_TRAFFIC_QUERY,
    5000
  )

  const weakEncryptionResponse = useIntervalQuery(WEAK_ENCRYPTION_QUERY, 5000)

  const highUseageResponse = useIntervalQuery(HIGH_USEAGE_QUERY, 20000)

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
                highUseageResponse?.data?.devices.map((device) => (
                  <DataCard key={device.device_id} bytes={device.outbound_byte_count}>
                    <span className="text-xs">{device.auto_name}</span>
                    <br />
                    <span className="text-xs">{device.ip}</span>
                  </DataCard>
                ))}
            </div>
          </div>
          <div>
            <p>
              Monitored devices sent/recieved
              <br />
              <strong>
                {dataUseage(
                  adsTrackingResponse?.data?.adsAndTrackerBytes?._sum +
                    unencryptedHttpTrafficResponse?.data
                      ?.unencryptedHttpTrafficBytes?._sum +
                    weakEncryptionResponse?.data?.weakEncryptionBytes?._sum
                )}
              </strong>
            </p>
            <div className="grid grid-cols-2 gap-2 py-4">
              <DataCard
                bytes={adsTrackingResponse?.data?.adsAndTrackerBytes?._sum}
              >
                <span className="text-xs">Ads & Trackers</span>
              </DataCard>
              <DataCard
                bytes={
                  unencryptedHttpTrafficResponse?.data
                    ?.unencryptedHttpTrafficBytes?._sum
                }
              >
                <span className="text-xs">Unencrypted HTTP Traffic</span>
              </DataCard>
              <DataCard
                bytes={weakEncryptionResponse?.data?.weakEncryptionBytes?._sum}
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
