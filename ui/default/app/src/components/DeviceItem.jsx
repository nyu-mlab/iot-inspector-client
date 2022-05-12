import React from 'react'

const DeviceItem = () => {
  return (
    <div className="flex w-full p-4 mb-4 bg-white border-l-8 border-green-500 rounded-lg shadow-sm">
            <div className="flex w-4/12 gap-4 px-4 border-r border-gray-300">
              <img src="https://via.placeholder.com/150" alt="{device}" className="w-auto h-12" />
              <div className="grid">
                <h3>Unknown Device</h3>
                <div className="flex justify-between text-xs">
                  <span>192.168.1.1</span>
                  <span>C6:xx:xx:xxxx</span>
                </div>
              </div>
            </div>
            <div className="flex items-center justify-start w-6/12 px-4 border-r border-gray-300">
              <div className="px-3 py-1 text-sm text-white bg-gray-600 rounded-full h-fit">
                tag
              </div>
            </div>
            <div className="flex items-center justify-center w-1/12 px-4 text-sm border-r gray-300 border-">0KB</div>
            <div className="flex items-center justify-center w-1/12 px-4 text-sm">
              <a href="#" className="">Details</a>
            </div>

          </div>
  )
}

export default DeviceItem