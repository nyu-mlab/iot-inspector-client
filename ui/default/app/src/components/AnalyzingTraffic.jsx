import React from 'react'
import useServerConfig from '../hooks/useServerConfig'
import RefreshSpinner from "./graphics/RefreshSpinner"
import { format } from 'date-fns'

const AnalyzingTraffic = () => {
  const { start_timestamp } = useServerConfig()
  
  return (
    <div className="flex items-center gap-3">
      <span className="mt-px font-semibold mt-1/2 text-secondary h4">
        Analyzing 0 Kbps of traffic
      </span>
      <div className="w-6 h-6 animate-spin-slow">
        <RefreshSpinner />
      </div>
      <br />
      <div>
        Running Since: {start_timestamp && format(new Date(start_timestamp*1000), 'yyyy-MM-dd HH:mm:ss')}
      </div>
    </div>
  )
}

export default AnalyzingTraffic