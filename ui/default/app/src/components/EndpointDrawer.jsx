import React from 'react'

const EndpointDrawer = () => {
  return (
    <aside className="h-[calc(100vh-48px)] p-6 shadow-2xl max-w-[300px] flex justify-between flex-col">
      <div>
      <h1>Communication Endpoints</h1>
      <ul>
        <li><a href="#" className="text-sm">Adobe</a></li>
        <li><a href="#" className="text-sm">Synology</a></li>
        <li><a href="#" className="text-sm">Google</a></li>
      </ul>
      <a href="#">View All</a>
      </div>
      <button className="w-full p-6 bg-green-100 rounded-lg">Scan Network</button>
    </aside>
  )
}

export default EndpointDrawer