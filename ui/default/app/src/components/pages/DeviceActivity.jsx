import React from 'react'
import DefaultLayout from "../../layouts/DefaultLayout"
import DeviceDrawer from "../DeviceDrawer"
import EndpointList from "../EndpointList"

const DeviceActivity = () => {
  return (
    <DefaultLayout>
      <main className="flex mt-[80px] bg-gray-100 h-[calc(100vh-80px)]">
        <div className="w-[calc(100vw-300px)]">
              <section className="w-full p-4">
          <h1 className="h2"><strong>Device Activity |</strong> [ device name ]</h1>
          <div className="bg-gray-200 w-full h-[300px] my-4"></div>
        </section>
        <section>
          <h2>Device Communication Endpoints</h2>
          <EndpointList />
        </section>
        </div>

        <DeviceDrawer />
      </main>
    </DefaultLayout>
  )
}

export default DeviceActivity