// import winston from 'winston';
// import { WinstonProvider } from 'winston-react';
import Router from './pages'
import { ModalDrawerProvider } from '@contexts/ModalDrawerContext'
import { NotificationsProvider } from '@contexts/NotificationsContext'

// const logger = winston.createLogger({
//   // ...
//   transports: [
//     // ...
//     new winston.transports.Console()
//   ]
// });

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
