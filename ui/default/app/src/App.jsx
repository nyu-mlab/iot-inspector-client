// import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import DefaultLayout from './layouts/DefaultLayout'
import Router from './pages'
import { ModalDrawerProvider } from '@contexts/ModalDrawerContext'

function App() {
  return (
    <ModalDrawerProvider>
    <DefaultLayout>
      <div className="App">
        <main className="flex-1 md:pr-64 lg:md:pr-80">
          <div className="">
            <Router />
          </div>
        </main>
      </div>
    </DefaultLayout>
    </ModalDrawerProvider>
  )
}

export default App
