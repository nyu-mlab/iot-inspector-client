import react, {useEffect, useState} from 'react'
import logo from './logo.svg';
import './App.css';
import Header from './components/Header'
import EndpointDrawer from './components/EndpointDrawer'

function App() {

  const [apiResponse, setApiResponse] = useState(null)

  useEffect(() => {
    fetch('/api/get_global_config')
    .then(response => response.json())
    .then(data => setApiResponse(data));
  }, [])


  return (
    <div className="App">
      <Header />
      <main className="flex">
        <div className="flex-1">
          <section className="flex flex-col gap-4 p-6">
            <h1>Network Activity</h1>
            <div className="bg-gray-200 w-full h-[300px]"></div>
            <div className="grid grid-cols-4 gap-6">
              <div>
                <p>High data usage devices in the past 24 hours</p>
                <a href="#">View all devices</a>
              </div>
              <div className="p-2 border border-gray-200 rounded-lg shadow-sm">
                <div className="block">
                  <span className="h1">911</span><span className="text-sm h1">KB</span>
                </div>
                <span className="text-xs">Unknown Device</span>
                <span className="text-xs">192.168.0.12</span>
              </div>
            </div>
          </section>
          <section className="flex flex-col gap-4 p-6 bg-gray-100">
            <div className="grid grid-cols-2">
              <div>
                <p>Monitored devices sent/recieved<br /><strong>0</strong> Bytes of data</p>
              </div>
              <div><p><strong>13</strong> endpoints contacted<br />across <strong>3</strong> countries</p></div>
            </div>
          </section>
          <section className="p-6 bg-gray-200 flex-flex-col-gap-4">
            <h1>Inspecting Devices</h1>
            <p>Naming & tagging helps with <a href="#">our research</a></p>
            <div className="bg-gray-400">search bar</div>
            <ul>
              <li className="py-4">
                <div className="w-full bg-white rounded-lg shadow-lg">Unknown Device</div>
              </li>
            </ul>
          </section>
        </div>
        <EndpointDrawer />
      </main>
    </div>
  );
}

export default App;
