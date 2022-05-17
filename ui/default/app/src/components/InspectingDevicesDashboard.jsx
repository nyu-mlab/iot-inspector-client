import React, { useState } from 'react'
import { HiViewGrid, HiViewList, HiRefresh, HiSearch, HiOutlineArrowSmDown } from "react-icons/hi";
import DeviceItem from "./DeviceItem";
import { Switch } from '@headlessui/react'


const InspectingDevicesDashboard = () => {
  const [cardView, setCardView] = useState(false)


  return (
    <section className="bg-gray-50 flex-flex-col-gap-4">
      <div className="grid grid-cols-2 gap-4 w-fit">
        <div>
          <h2 className="h1">Inspecting Devices</h2>
          <p className="py-2">Naming & tagging helps with <a href="#">our research</a></p>
        </div>
        <HiRefresh className="w-auto h-full py-4 text-secondary animate-spin-slow" />
      </div>

    <div className="flex items-center gap-4">
      <form className="flex flex-1 ">
        <input type='text' id='searchDevices' className="w-full px-4 py-2 text-gray-600 bg-white border border-gray-400 rounded-md" placeholder="Search devices"/>
        <label for="searchDevices" className="sr-only"><HiSearch />Search devices</label>
      </form>
      <div className="flex items-center gap-1 p-2 text-sm text-white bg-gray-500 rounded-lg">Tags <HiOutlineArrowSmDown /></div>
      <div className="p-2 text-sm">Name</div>
      <div className="p-2 text-sm">Traffic</div>
      <div className="flex gap-3 px-2">
        {/* <HiViewGrid className="w-6 h-6 p-1 text-dark" />
        <HiViewList className="w-6 h-6 p-1 text-white rounded-lg bg-secondary" />
            <Switch
              checked={enabled}
              onChange={setEnabled}
              className={`${
                enabled ? 'bg-blue-600' : 'bg-gray-200'
              } relative inline-flex h-6 w-11 items-center rounded-full`}
            >
              <span className="sr-only">Enable notifications</span>
              <span
                className={`${
                  enabled ? 'translate-x-6' : 'translate-x-1'
                } inline-block h-4 w-4 transform rounded-full bg-white`}
              />
            </Switch> */}
            <Switch
              checked={cardView}
              onChange={setCardView}
              >
              <span className="flex">
                <HiViewGrid className={`${
                  cardView ? 'text-white rounded-lg bg-secondary' : 'text-dark'
                } w-6 h-6 p-1 `}/>
                <HiViewList className={`${
                  cardView ? 'text-dark' : 'text-white rounded-lg bg-secondary'
                } w-6 h-6 p-1 `}/>
              </span>
            </Switch>
      </div>
    </div>
      <ul>
        <li className="py-4">
          <DeviceItem />
          <DeviceItem />
          <DeviceItem />
        </li>
      </ul>
    </section>
  )
}

export default InspectingDevicesDashboard