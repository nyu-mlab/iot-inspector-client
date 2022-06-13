import React from 'react'
import useServerConfig from '../hooks/useServerConfig'
import RefreshSpinner from "./graphics/RefreshSpinner"
import { format } from 'date-fns'

const AnalyzingTraffic = () => {
  const { start_timestamp } = useServerConfig()

  return (
    <div className="flex items-center gap-3">
      <div className="w-6 h-6 animate-spin-slow">
        <RefreshSpinner />
      </div>
      <span className="mt-px font-semibold mt-1/2 text-secondary h4">
        Analyzing traffic since {start_timestamp && format(new Date(start_timestamp*1000), 'HH:mm:ss')} hours
      </span>
    </div>
  )
}

export default AnalyzingTraffic