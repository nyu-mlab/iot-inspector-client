import React from 'react'

const DataCard = () => {
  return (
    <div className="flex-1 p-2 bg-white border border-gray-200 rounded-lg shadow-sm">
      <div className="block">
        <span className="h1">911</span><span className="text-sm h1">KB</span>
      </div>
      <span className="text-xs">Unknown Device</span>
      <span className="text-xs">192.168.0.12</span>
    </div>
  )
}

export default DataCard