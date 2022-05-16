import React from 'react'


const EndpointList = () => {
  return (
      <table className="w-full">
        <tr className="p-2 text-left text-white rounded-t-lg bg-dark">
          <th className="p-2">Remote Party</th>
          <th className="p-2">Country</th>
          <th className="p-2">Device</th>
          <th className="p-2">Data Usage</th>
          <th className="p-2">Last Updated</th>
        </tr>
        <tr className="bg-gray-100">
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