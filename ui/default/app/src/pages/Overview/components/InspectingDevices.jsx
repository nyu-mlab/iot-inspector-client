import React, { useEffect, useState } from 'react'
import { HiViewGrid, HiViewList, HiSearch } from 'react-icons/hi'
import { BiSortAlt2 } from 'react-icons/bi'

import DeviceItem from './DeviceItem'
import { Switch } from '@headlessui/react'
import RefreshSpinner from '../../../components/graphics/RefreshSpinner'
import useDevices from '../hooks/useDevices'

const InspectingDevicesDashboard = () => {
  const { devicesData, devicesDataLoading, sortDevicesData } = useDevices()
  const [searchValue, setSearchValue] = useState('')
  const [sortDirection, setSortDirection] = useState('ASC')
  const [cardView, setCardView] = useState(false)

  return (
    <section className="bg-gray-50 flex-flex-col-gap-4" id="inspecting-devices">
      <div className="flex items-center w-full gap-4 md:gap-5">
        <div className="">
          <h2 className="h1">Inspecting Devices</h2>
          <p className="py-2">Naming & tagging helps with our research</p>
        </div>
        <div className="w-8 h-8 md:w-10 md:h-10 animate-spin-slow">
          <RefreshSpinner />
        </div>
      </div>

      <div className="grid grid-cols-4 gap-4 py-4 md:flex md:items-center">
        <form className="flex flex-1 order-last col-span-4 md:order-first">
          <input
            type="text"
            name="search"
            id="searchDevices"
            value={searchValue}
            onChange={(e) => setSearchValue(e.target.value)}
            className="w-full px-4 py-2 text-gray-600 bg-white border border-gray-400 rounded-md"
            placeholder="Search devices by name or tag"
          />
          <label htmlFor="searchDevices" className="sr-only">
            <HiSearch />
            Search devices by name or tag
          </label>
        </form>
        <button className="flex items-center justify-center gap-1 p-2 text-sm">
          Name
          <BiSortAlt2 className="w-4 h-4 text-gray-400" />
        </button>
        <button
          className="flex items-center justify-center gap-1 p-2 text-sm"
          onClick={() => {
            const s = sortDirection === 'ASC' ? 'DESC' : 'ASC' // TODO: boolean https://github.com/ocupop/iot-inspector-client/issues/18
            setSortDirection(s)
            sortDevicesData('outbound_byte_count', sortDirection)

          }}
        >
          Traffic
          <BiSortAlt2 className="w-4 h-4 text-gray-400" />
        </button>
        <div className="flex items-center justify-center gap-3 px-2">
          <Switch checked={cardView} onChange={setCardView}>
            <span className="flex">
              <HiViewGrid
                className={`${
                  cardView ? 'text-white rounded-lg bg-secondary' : 'text-dark'
                } w-10 h-10 md:w-8 md:h-8 p-1 `}
              />
              <HiViewList
                className={`${
                  cardView ? 'text-dark' : 'text-white rounded-lg bg-secondary'
                } w-10 h-10 md:w-8 md:h-8 p-1 `}
              />
            </span>
          </Switch>
        </div>
      </div>
      {devicesDataLoading ? (
        <div className="skeleton h-[600px]">
        </div>
      ) : (
        <ul className={cardView ? 'card-grid' : 'min-h-[200px]'}>
          {devicesData
          // TODO move this filter into a hook https://github.com/ocupop/iot-inspector-client/issues/18
            ?.filter((device) => {
              if (!searchValue) return true
              if (
                device.auto_name
                  .toLowerCase()
                  .includes(searchValue.toLowerCase())
              ) {
                return true
              }
            })
            .map((device) => (
              <li
                key={device.device_id}
                className={`${cardView ? 'card-view' : 'list-view'} py-2`}
              >
                <DeviceItem device={device} />
              </li>
            ))}
        </ul>
      )}
    </section>
  )
}

export default InspectingDevicesDashboard
