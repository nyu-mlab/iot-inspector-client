import React, { useState } from 'react'
import DefaultLayout from "../../layouts/DefaultLayout"
import EndpointList from "../EndpointList"
import MapChart from "../charts/MapChart";
import { HiChevronRight } from "react-icons/hi";
import ReactTooltip from "react-tooltip";

import useQueryParam from '../../hooks/useQueryParam'
import useDeviceTrafficToCountries from '../../hooks/useDeviceTrafficToCountries'


const CommunicationEndpoints = () => {
  const query = useQueryParam()
  const deviceId = query.get('deviceid')

  let deviceCountriesData = useDeviceTrafficToCountries(deviceId)
  deviceCountriesData = deviceCountriesData?.filter(d => d.device_id === deviceId)

  // if (!deviceCountriesData?.length) {
  //   return <></>
  // }

  return (
    <>
        <section className="flex items-center gap-2 pb-2 w-fit">
            <a href="/" >
              Network Activity
            </a>
            <HiChevronRight  className="text-gray-600/50"/>
            <span className="font-bold text-gray-600/50">Communication Endpoints</span>
          </section>
        <section>
          <h1>Communication Endpoints</h1>
          <div>
             <MapChart data={deviceCountriesData}/>
            {/* <MapChart setTooltipContent={setContent} /> */}
            {/* <ReactTooltip>{content}</ReactTooltip> */}
          </div>

          <EndpointList data={deviceCountriesData}/>

        </section>
        </>
  )
}

export default CommunicationEndpoints