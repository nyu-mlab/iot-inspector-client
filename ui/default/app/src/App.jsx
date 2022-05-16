import react, {useEffect, useState} from 'react'
import logo from './logo.svg';
import DefaultLayout from "./layouts/DefaultLayout";
import Header from './components/Header'
import EndpointDrawer from './components/EndpointDrawer'
import DataCard from './components/DataCard'
import NetworkActivityDashboard from './components/NetworkActivityDashboard'
import InspectingDevicesDashboard from "./components/InspectingDevicesDashboard";


function App() {

  const [apiResponse, setApiResponse] = useState(null)

  useEffect(() => {
    fetch('/api/get_global_config')
    .then(response => response.json())
    .then(data => setApiResponse(data));
  }, [])


  return (
    <DefaultLayout>
      <div className="App">
        {/* <Header /> */}
        <main className="flex mt-[80px]">
          <div className="w-[calc(100vw-300px)]">
            <NetworkActivityDashboard />
            <InspectingDevicesDashboard />
          </div>
          <EndpointDrawer />
        </main>
      </div>
    </DefaultLayout>
  );
}

export default App;
