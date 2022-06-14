// import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import DefaultLayout from './layouts/DefaultLayout'
import EndpointDrawer from './components/EndpointDrawer'
import Router from './pages'

function App() {
  return (
    <DefaultLayout>
      <div className="App">
        <main className="flex">
          <div className="w-full md:w-[calc(100vw-275px)]">
            <Router />
          </div>
          <EndpointDrawer />
        </main>
      </div>
    </DefaultLayout>
  )
}

export default App
