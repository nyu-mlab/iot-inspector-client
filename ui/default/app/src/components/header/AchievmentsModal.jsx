import React from 'react'
import NetworkTrafficBadge from "../graphics/NetworkTrafficBadge"

const AchievmentsModal = () => {
  return (
    <div className="grid md:grid-cols-3 lg:grid-cols-4 md:gap-4 lg:gap-6">
      <div className="achievement-card">
        <NetworkTrafficBadge />
        <div className="flex items-center gap-2 md:gap-3">
          <h1>10</h1>
          <p className="">Hours of network traffic collected</p>
        </div>
      </div>
    </div>
  )
}

export default AchievmentsModal