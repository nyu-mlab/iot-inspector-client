import React, { useState } from 'react'
import DefaultLayout from "../../layouts/DefaultLayout"
import EndpointList from "../EndpointList"
import MapChart from "../charts/MapChart";
import { HiChevronRight } from "react-icons/hi";
import ReactTooltip from "react-tooltip";


const CommunicationEndpoints = () => {
  const [content, setContent] = useState("");
  console.log(content)

  return (
    <DefaultLayout>
      <main className="h-full">
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
            {/* <MapChart setTooltipContent={setContent} /> */}
            <ReactTooltip>{content}</ReactTooltip>
          </div>

          {/* <form>
            <label for="searchDevices">Search Communication Endpoints</label>
            <input type='text' id='searchDevices' className="px-4 py-2 text-gray-600 bg-white border border-gray-400 rounded-md" />
          </form> */}
          <EndpointList />

        </section>
      </main>
    </DefaultLayout>
  )
}

export default CommunicationEndpoints