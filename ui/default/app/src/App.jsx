// import winston from 'winston';
// import { WinstonProvider } from 'winston-react';
import Router from './pages'

// const logger = winston.createLogger({
//   // ...
//   transports: [
//     // ...
//     new winston.transports.Console()
//   ]
// });

function App() {
  return (
    <div className='App'>
      <Router />
    </div>
  )
}

export default App
