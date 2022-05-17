import React from 'react'


const EndpointList = () => {
  return (
      <table className="w-full">
        <tr className="p-2 text-left text-white bg-dark">
          <th className="p-2 rounded-tl-md">Remote Party</th>
          <th className="p-2">Country</th>
          <th className="p-2">Device</th>
          <th className="p-2">Data Usage</th>
          <th className="p-2 rounded-tr-md">Last Updated</th>
        </tr>
        <tr className="even:bg-gray-100 odd:bg-white">
          <td className="p-2">[ remote party ]</td>
          <td className="p-2">[ country ]</td>
          <td className="p-2">[ device name ]</td>
          <td className="p-2">[ data usage ]</td>
          <td className="p-2">[ last update time ]</td>
        </tr>
        <tr className="even:bg-gray-100 odd:bg-white">
          <td className="p-2">[ remote party ]</td>
          <td className="p-2">[ country ]</td>
          <td className="p-2">[ device name ]</td>
          <td className="p-2">[ data usage ]</td>
          <td className="p-2">[ last update time ]</td>
        </tr>
        <tr className="even:bg-gray-100 odd:bg-white">
          <td className="p-2">[ remote party ]</td>
          <td className="p-2">[ country ]</td>
          <td className="p-2">[ device name ]</td>
          <td className="p-2">[ data usage ]</td>
          <td className="p-2">[ last update time ]</td>
        </tr>
      </table>
  )
}

export default EndpointList