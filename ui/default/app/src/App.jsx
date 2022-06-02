// import react, {useEffect, useState} from 'react'
// import logo from './logo.svg';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'

import DefaultLayout from './layouts/DefaultLayout'
// import Header from './components/Header'
import EndpointDrawer from './components/EndpointDrawer'
// import DataCard from './components/DataCard'
import NetworkActivityDashboard from './components/NetworkActivityDashboard'
import InspectingDevicesDashboard from './components/InspectingDevicesDashboard'

function App() {
  return (
    <Router>

        <DefaultLayout>
          <div className="App">
            {/* <Header /> */}
            <main className="flex mt-[80px]">
              <div className="w-full md:w-[calc(100vw-300px)]">
                <Routes>
                  <Route path="/" element={<Dashboard />} />
                </Routes>
              </div>
              <EndpointDrawer />
            </main>
          </div>
        </DefaultLayout>

    </Router>
  )
}

// TODO: Move this....
function Dashboard() {
  return (
    <>
      <NetworkActivityDashboard />
      <InspectingDevicesDashboard />
    </>
  )
}

export default App
