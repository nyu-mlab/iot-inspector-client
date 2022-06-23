import React from 'react'
import DataCard from '../../../components/DataCard'
import BarChart from '../../../components/charts/BarChart'
import { dataUseage } from '../../../utils/utils'
import useHighUseage from '../hooks/useHighUseage'
import useNetworkActivity from '../hooks/useNetworkActivity'

const NetworkActivityDashboard = () => {
  const { highUseageData, highUseageDataLoading } = useHighUseage()
  const { networkActivityDataLoading, networkActivityData } =
    useNetworkActivity()

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
              {highUseageDataLoading && <>loading...</>}
              {highUseageData &&
                highUseageData.slice(0, 3).map((device, i) => (
                  <DataCard key={i} bytes={device.outbound_byte_count}>
                    <span className="text-xs">{device.auto_name}</span>
                    <br />
                    <span className="text-xs">{device.ip}</span>
                  </DataCard>
                ))}
            </div>
          </div>
          {networkActivityDataLoading ? (
            <>loading...</>
          ) : (
            <div>
              <p>
                Monitored devices sent/recieved
                <br />
                <strong>
                  {dataUseage(
                    networkActivityData?.ads_and_trackers +
                      networkActivityData?.unencrypted_http_traffic +
                      networkActivityData?.weak_encryption
                  )}
                </strong>
              </p>
              <div className="grid grid-cols-2 gap-2 py-4">
                <DataCard bytes={networkActivityData?.ads_and_trackers}>
                  <span className="text-xs">Ads & Trackers</span>
                </DataCard>
                <DataCard bytes={networkActivityData?.unencrypted_http_traffic}>
                  <span className="text-xs">Unencrypted HTTP Traffic</span>
                </DataCard>
                <DataCard bytes={networkActivityData?.weak_encryption}>
                  <span className="text-xs">Weak Encryption</span>
                </DataCard>
              </div>
            </div>
          )}
        </div>
      </section>
    </>
  )
}

export default NetworkActivityDashboard
