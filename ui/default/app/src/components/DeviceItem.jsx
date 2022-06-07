import React from 'react'
import { dataUseage } from '../utils/utils'

const DeviceItem = ({ device }) => {
  return (
    <div className="device-item">
      <div className="device-info">
        <img src="https://via.placeholder.com/150" alt="{device}" className="hidden w-auto h-12 lg:block md:h-16" />
        <div className="grid overflow-scroll">
          <h3>{device ? device.auto_name : 'Unknown Device'}</h3>
          <div className="flex justify-between text-xs md:block">
            <div>
              <p>
              {device && device.ip}
              </p>
            </div>
            <div>
              <p>
              {device && device.mac}
              </p>
            </div>
          </div>
        </div>
      </div>
      <div className="device-tags">
        <div className="px-4 py-1 text-sm text-white bg-gray-600 rounded-full h-fit">
          tag
        </div>
      </div>
      <div className="flex">
        {device && (<div className="flex items-center justify-center px-4 text-sm border-r border-gray-300 w-fit">{dataUseage(device.outbound_byte_count)}</div>)}
        <div className="flex items-center justify-center px-4 text-sm w-fit">
          <a href={`/device-activity?deviceid=${device.device_id}`} className="">Details</a>
        </div>
      </div>
    </div>
  )
}

export default DeviceItem