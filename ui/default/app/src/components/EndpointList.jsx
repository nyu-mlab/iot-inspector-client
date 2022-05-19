import React from 'react'

const endpoints = [
  {
    id: '[ device id ]',
    party: '[ remote party ]',
    country: '[ country ]',
    device: '[ device name ]',
    data: '[ data usage ]',
    updated: '[ last update time ]',
  }
]

const EndpointList = () => {
  return (
      <table className="min-w-full overflow-hidden border-collapse divide-y divide-gray-300 rounded-t-lg">
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
          {endpoints.map((endpoint) => (
            <tr key={endpoint.id}>
              <td className="w-full py-4 pl-4 pr-3 text-sm font-medium text-dark max-w-0 sm:w-auto sm:max-w-none sm:pl-6">
                {endpoint.party}
                <dl className="font-normal lg:hidden">
                  <dt className="sr-only">Device Name</dt>
                  <dd className="mt-1 text-gray-700 truncate">{endpoint.device}</dd>
                  <dt className="sr-only sm:hidden">Country</dt>
                  <dd className="mt-1 text-gray-500 truncate sm:hidden">{endpoint.country}</dd>
                </dl>
              </td>

              <td className="hidden px-3 py-4 text-sm text-gray-500 sm:table-cell">{endpoint.country}</td>
              <td className="hidden px-3 py-4 text-sm text-gray-500 sm:table-cell">{endpoint.device}</td>
              <td className="px-3 py-4 text-sm text-gray-500">{endpoint.data}</td>
              <td className="px-3 py-4 text-sm text-gray-500">{endpoint.updated}</td>
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