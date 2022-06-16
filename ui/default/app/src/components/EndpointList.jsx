import React from 'react'
// import { format } from 'date-fns'
import { dataUseage } from '../utils/utils'
import { format } from 'timeago.js';

const EndpointList = ({ data }) => {
  return (
      <table className="min-w-full my-4 overflow-hidden border-collapse divide-y divide-gray-300 rounded-t-lg">
        <thead className=" bg-dark">
            <tr>
              <th scope="col" className="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-light sm:pl-6">
                Remote Party
              </th>
              <th
                scope="col"
                className="hidden px-3 py-3.5 text-left text-sm font-semibold text-light sm:table-cell"
              >
                Country
              </th>
              <th
                scope="col"
                className="hidden px-3 py-3.5 text-left text-sm font-semibold text-light sm:table-cell"
              >
                Device
              </th>
              <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-light">
                Data Usage
              </th>
              <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-light">
                Last Updated
              </th>

            </tr>
          </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {data.map((device, i) => (
            <tr key={device.device_id+i}>
              <td className="w-full py-4 pl-4 pr-3 text-sm font-medium text-dark max-w-0 sm:w-auto sm:max-w-none sm:pl-6">
                {device.counterparty_hostname}
                <dl className="font-normal lg:hidden">
                  <dt className="sr-only">Device Name</dt>
                  <dd className="mt-1 text-gray-700 truncate">{device.counterparty_hostname}</dd>
                  <dt className="sr-only sm:hidden">Country</dt>
                  <dd className="mt-1 text-gray-500 truncate sm:hidden">{device.name}</dd>
                </dl>
              </td>

              <td className="hidden px-3 py-4 text-sm text-gray-500 sm:table-cell">{device.name}</td>
              <td className="hidden px-3 py-4 text-sm text-gray-500 sm:table-cell"><a href={`/device-activity?deviceid=${device.device_id}`}>{device.device.auto_name}</a></td>
              <td className="px-3 py-4 text-sm text-gray-500">{dataUseage(device.outbound_byte_count)}</td>
              <td className="px-3 py-4 text-sm text-gray-500">{format(new Date(device.last_updated_time_per_country*1000), 'en_US', 'yyyy-MM-dd HH:mm:ss')}</td>
            </tr>
          ))}
        </tbody>

        {/* <tr className="even:bg-gray-100 odd:bg-white">
          <td className="p-2">[ remote party ]</td>
          <td className="p-2">[ country ]</td>
          <td className="p-2">[ device name ]</td>
          <td className="p-2">[ data usage ]</td>
          <td className="p-2">[ last update time ]</td>
        </tr> */}
      </table>
  )
}

export default EndpointList