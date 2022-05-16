import React from 'react'
import DefaultLayout from "../../layouts/DefaultLayout"
import EndpointList from "../EndpointList"

const CommunicationEndpoints = () => {
  return (
    <DefaultLayout>
      <main className="flex mt-[80px]  h-[calc(100vh-80px)]">
        <div className="w-full p-4">
          <h1>Communication Endpoints</h1>

          <div className="bg-gray-200 w-full h-[300px] my-4"></div>
          <form>
            <label for="searchDevices">Search Communication Endpoints</label>
            <input type='text' id='searchDevices' className="px-4 py-2 text-gray-600 bg-white border border-gray-400 rounded-md" />
          </form>
          <EndpointList />

        </div>
      </main>
    </DefaultLayout>
  )
}

export default CommunicationEndpoints