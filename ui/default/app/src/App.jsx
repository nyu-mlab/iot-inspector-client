// import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import DefaultLayout from './layouts/DefaultLayout'
import Router from './pages'
import { ModalDrawerProvider } from '@contexts/ModalDrawerContext'
import { NotificationsProvider } from '@contexts/NotificationsContext'


function App() {
  return (
    <NotificationsProvider>
      <ModalDrawerProvider>
        <DefaultLayout>
          <div className="App">
            {/* <main className="flex-1 md:pr-64 lg:md:pr-80"> */}
            {/* <main className="flex-1"> */}
              {/* <div className=""> */}
                <Router />
              {/* </div> */}
            {/* </main> */}
          </div>
        </DefaultLayout>
      </ModalDrawerProvider>
    </NotificationsProvider>
  )
}

export default App
