// import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import DefaultLayout from './layouts/DefaultLayout'
import Router from './pages'
import { ModalDrawerProvider } from '@contexts/ModalDrawerContext'
import { NotificationsProvider } from '@contexts/NotificationsContext'


function App() {
  return (
    <NotificationsProvider>
      <ModalDrawerProvider>
        <div className="App">
          <Router />
        </div>
      </ModalDrawerProvider>
    </NotificationsProvider>
  )
}

export default App
