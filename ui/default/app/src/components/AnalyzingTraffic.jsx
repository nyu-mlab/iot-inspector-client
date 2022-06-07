import React from 'react'
import RefreshSpinner from "./graphics/RefreshSpinner"

const AnalyzingTraffic = () => {
  return (
    <div className="flex items-center gap-3">
      <span className="mt-px font-semibold mt-1/2 text-secondary h4">
        Analyzing 0 Kbps of traffic
      </span>
      <div className="w-6 h-6 animate-spin-slow">
        <RefreshSpinner />
      </div>
    </div>
  )
}

export default AnalyzingTraffic