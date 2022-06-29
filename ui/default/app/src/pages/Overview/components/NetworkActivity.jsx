import React from 'react'
import DataCard from '../../../components/DataCard' // TODO: 1. Move to aliases 2. create index files 3. relative components 4. move hooks to global, index to group https://github.com/ocupop/iot-inspector-client/issues/16
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
      {highUseageDataLoading ? (
        <>loading...</>
      ) : (
        <section className="flex flex-col gap-4">
          <h1>Network Activity</h1>
            <p>
              High data usage devices in the past 24 hours
              <br />
              <a href="#inspecting-devices">View all devices</a>
            </p>
          <BarChart />
          <div className="grid">
                      <div>

            <div className="grid gap-2 py-4 md:grid-cols-2 lg:grid-cols-3">
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
            <div className="grid gap-6 py-8 md:py-4">
              <hr />
          {networkActivityDataLoading ? (
          <div className="skeleton h-[114px]" />
          ) : (
            <div>
              <p>
                All monitored devices sent/recieved &nbsp;
                <strong>
                  {dataUseage(
                    networkActivityData?.ads_and_trackers +
                      networkActivityData?.unencrypted_http_traffic +
                      networkActivityData?.weak_encryption
                  )}
                </strong>
                &nbsp; of data
              </p>
              <div className="grid gap-2 py-4 md:grid-cols-2 lg:grid-cols-3">
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
          </div>
          </div>
        </section>
      )}
      <section className="flex flex-col gap-4 bg-gray-50">

      </section>
    </>
  )
}

export default NetworkActivityDashboard
