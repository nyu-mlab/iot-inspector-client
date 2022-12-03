// import winston from 'winston';
// import { WinstonProvider } from 'winston-react';
import Router from './pages'
import { ModalDrawerProvider } from '@contexts/ModalDrawerContext'
import { NotificationsProvider } from '@contexts/NotificationsContext'
import { UserConfigsProvider } from '@contexts/UserConfigsContext'
import { DeviceProvider } from '@contexts/DeviceContext'

// const logger = winston.createLogger({
//   // ...
//   transports: [
//     // ...
//     new winston.transports.Console()
//   ]
// });

function App() {
  return (
    <UserConfigsProvider>
      <DeviceProvider>
        <NotificationsProvider>
          <ModalDrawerProvider>
            <div className='App'>
              <Router />
            </div>
          </ModalDrawerProvider>
        </NotificationsProvider>
      </DeviceProvider>
    </UserConfigsProvider>
  )
}

export default App
