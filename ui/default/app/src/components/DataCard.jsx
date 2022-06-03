import React from 'react'

const DataCard = ({ children, bytes }) => {
  const kb = bytes && (bytes / 1000).toFixed(0)
  return (
    <div className="flex-1 p-2 bg-white border border-gray-200 rounded-lg shadow-sm">
      <div className="block">
        <span className="h1">{kb}</span><span className="text-sm h1">KB</span>
      </div>
      {children}
    </div>
  )
}

export default DataCard