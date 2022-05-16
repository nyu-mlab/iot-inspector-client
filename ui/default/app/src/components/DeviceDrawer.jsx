import React from 'react'

const DeviceDrawer = () => {
  return (
    <aside className="h-[calc(100vh-80px)] p-6 shadow-md w-[300px] flex  flex-col justify-between fixed bg-white right-0 bottom-0">
      {/* <div className="flex-1 overflow-y-scroll"> */}
        <h3>Naming and tagging helps with our research</h3>


      {/* </div> */}
      <button className="w-full btn btn-primary">Save Device Details</button>
    </aside>
  )
}

export default DeviceDrawer