const winston = require('winston')
const { format, transports } = winston
const moment = require('moment');
const path = require('path')

const logFormat = format.printf(info => `${info.timestamp} ${info.level}: ${info.message}`)
const currentDate = new Date()
const formattedDate = moment(currentDate).format('YYYY-MM-DD HH_mm_ss')

const logger = winston.createLogger({
  level: 'info', //  debug < info < warn < error < disable,
  format: format.combine(
    format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
    // Format the metadata object
    format.metadata({ fillExcept: ['timestamp', 'message', 'level'] })
  ),
  transports: [
    new transports.Console({
      format: format.combine(
        format.colorize(),
        logFormat
      )
    }),
    new transports.File({
      filename: `logs/${formattedDate}_combined.log`,
      format: format.combine(
        // Render in one line in your log file.
        // If you use prettyPrint() here it will be really
        // difficult to exploit your logs files afterwards.
        format.json()
      )
    }),
    new transports.File({
      filename: `logs/${formattedDate}_error.log`,
      level: 'error',
      format: format.combine(
        // Render in one line in your log file.
        // If you use prettyPrint() here it will be really
        // difficult to exploit your logs files afterwards.
        format.json()
      )
    })
  ],
  exitOnError: false
})

module.exports = logger