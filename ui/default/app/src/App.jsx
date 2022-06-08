// import react, {useEffect, useState} from 'react'
// import logo from './logo.svg';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import DefaultLayout from './layouts/DefaultLayout'
import EndpointDrawer from './components/EndpointDrawer'
import Dashboard from './pages/Dashboard'
import DeviceActivityDashboard from './pages/DeviceActivityDashboard'
import GettingStartedDashboard from './pages/GettingStartedDashboard'
import ConsentDashboard from './pages/ConsentDashboard'
import CommunicationEndpointsDashboard from './pages/CommunicationEndpointsDashboard'

function App() {
  return (
    <Router>
        <DefaultLayout>
          <div className="App">
            <main className="flex mt-[80px]">
              <div className="w-full md:w-[calc(100vw-275px)]">
                <Routes>
                  <Route path="/" element={<Dashboard />} />
                  <Route path="/getting-started" element={<GettingStartedDashboard />} />
                  <Route path="/consent" element={<ConsentDashboard />} />
                  <Route path="/device-activity" element={<DeviceActivityDashboard />} />
                  <Route path="/communication-endpoints" element={<CommunicationEndpointsDashboard />} />
                </Routes>
              </div>
              <EndpointDrawer />
            </main>
          </div>
        </DefaultLayout>
    </Router>
  )
}


export default App
