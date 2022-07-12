// import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import DefaultLayout from './layouts/DefaultLayout'
import Router from './pages'

function App() {
  return (
    <DefaultLayout>
      <div className="App">
        <main className="flex-1 md:pr-64 lg:md:pr-80">
          <div className="">
            <Router />
          </div>
        </main>
      </div>
    </DefaultLayout>
  )
}

export default App
