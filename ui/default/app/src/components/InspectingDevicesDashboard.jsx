import React, { useState } from 'react'
import { HiViewGrid, HiViewList, HiRefresh, HiSearch, HiOutlineArrowSmDown } from "react-icons/hi";
import { BiSortAlt2 } from "react-icons/bi";
import RefreshSpinner from "./graphics/RefreshSpinner";
import DeviceItem from "./DeviceItem";
import { Switch } from '@headlessui/react'
import { gql, useQuery } from '@apollo/client';
import useIntervalQuery from '../hooks/useIntervalQuery';


const DEVICES_QUERY = gql`
  query Query {
    devices {
      device_id
      auto_name
      ip
      mac
      outbound_byte_count
    }
  }
`

const InspectingDevicesDashboard = () => {
  const [cardView, setCardView] = useState(false)
  const devicesResponse = useIntervalQuery(DEVICES_QUERY)

  return (
    <section className="bg-gray-50 flex-flex-col-gap-4" id="inspecting-devices">
      <div className="flex items-center w-full gap-4 md:gap-5">
        <div className="">
          <h2 className="h1">Inspecting Devices</h2>
          <p className="py-2">Naming & tagging helps with <a href="#">our research</a></p>
        </div>
        <div className="w-8 h-8 md:w-10 md:h-10 animate-spin-slow">
          <RefreshSpinner />
        </div>
      </div>

    <div className="grid grid-cols-4 gap-4 py-4 md:flex md:items-center">
      <form className="flex flex-1 order-last col-span-4 md:order-first">
        <input type='text' id='searchDevices' className="w-full px-4 py-2 text-gray-600 bg-white border border-gray-400 rounded-md" placeholder="Search devices by name or tag"/>
        <label htmlFor="searchDevices" className="sr-only"><HiSearch />Search devices by name or tag</label>
      </form>
      {/* <div className="flex items-center justify-center gap-1 p-2 text-sm text-white bg-gray-500 rounded-lg">
        Tags <HiOutlineArrowSmDown />
      </div> */}
      <button className="flex items-center justify-center gap-1 p-2 text-sm">
        Name
        <BiSortAlt2 className="w-4 h-4 text-gray-400" />
      </button>
      <button className="flex items-center justify-center gap-1 p-2 text-sm">
        Traffic
        <BiSortAlt2 className="w-4 h-4 text-gray-400"/>
      </button>
      <div className="flex items-center justify-center gap-3 px-2">
        {/* TODO - Add cardview for device-item */}

        <Switch
          checked={cardView}
          onChange={setCardView}
          >
          <span className="flex">
            <HiViewGrid className={`${
              cardView ? 'text-white rounded-lg bg-secondary' : 'text-dark'
            } w-10 h-10 md:w-8 md:h-8 p-1 `}/>
            <HiViewList className={`${
              cardView ? 'text-dark' : 'text-white rounded-lg bg-secondary'
            } w-10 h-10 md:w-8 md:h-8 p-1 `}/>
          </span>
        </Switch>
      </div>
    </div>
      <ul className={cardView ? 'grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4 md:gap-5' : ''}>
      {devicesResponse?.data?.devices?.map((device) => (
        <li key={device.device_id} className={`${cardView ? 'card-view' : 'list-view'
            } py-2`}>
          <DeviceItem device={device} />
        </li>
      ))}
      </ul>
    </section>
  )
}

export default InspectingDevicesDashboard