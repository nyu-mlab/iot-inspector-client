import React from 'react'

const EndpointDrawer = () => {
  return (
    <aside className="h-[calc(100vh-80px)] p-6 shadow-md w-[300px] flex  flex-col justify-between fixed bg-white right-0 bottom-0">
      {/* <div className="flex-1 overflow-y-scroll"> */}
        <h2>Communication Endpoints</h2>
        <div  className="flex-1 py-4 overflow-y-scroll">
          <ul>
            <li className="py-0.5"><a href="#" className="text-xs transition text-dark hover:text-secondary">Adobe</a></li>
            <li className="py-0.5"><a href="#" className="text-xs transition text-dark hover:text-secondary">Synology</a></li>
            <li className="py-0.5"><a href="#" className="text-xs transition text-dark hover:text-secondary">Google</a></li>
          </ul>
        </div>

        <div className="relative h-12 my-8">
          <div className="absolute w-full transform -translate-x-1/2 -translate-y-1/2 top-1/2 left-1/2">
            <div className="w-full h-px bg-secondary"></div>
          </div>
          <div className="absolute transform -translate-x-1/2 -translate-y-1/2 top-1/2 left-1/2">
            <a href="#" className="p-5 font-semibold bg-white text-secondary">View All</a>
          </div>
        </div>


      {/* </div> */}
      <button className="w-full p-4 text-lg font-bold tracking-wide rounded-lg bg-primary text-dark">Scan Network</button>
    </aside>
  )
}

export default EndpointDrawer