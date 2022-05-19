import React from 'react'

const DeviceItem = () => {
  return (
    <div className="device-item">
      <div className="device-info">
        <img src="https://via.placeholder.com/150" alt="{device}" className="hidden w-auto h-12 lg:block md:h-16" />
        <div className="grid overflow-scroll">
          <h3>Unknown Device</h3>
          <div className="flex justify-between text-xs md:block">
            <div>
              <p>
              192.168.1.1
              </p>
            </div>
            <div>
              <p>
              C6:xx:xx:xxxx
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
        <div className="flex items-center justify-center px-4 text-sm border-r border-gray-300 w-fit">0KB</div>
        <div className="flex items-center justify-center px-4 text-sm w-fit">
          <a href="/device-activity/" className="">Details</a>
        </div>
      </div>
    </div>
  )
}

export default DeviceItem