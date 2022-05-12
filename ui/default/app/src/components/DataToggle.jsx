import React, { useState } from 'react'
import { Switch } from '@headlessui/react'

const DataToggle = () => {
   const [enabled, setEnabled] = useState(false)

  return (
    <Switch.Group>
      <div className="flex items-center gap-2 flex-nowrap">
      {/* <div className="inline"> */}
        <Switch
          checked={enabled}
          onChange={setEnabled}
          className="relative inline-flex items-center h-6 transition-colors rounded-full bg-light w-11 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2"
        >
          <span
            className={`${
              enabled ? 'translate-x-6 bg-green-400' : 'translate-x-1 bg-gray-400/50'
            } inline-block h-4 w-4 transform rounded-full  transition-transform`}
          />
        </Switch>
        <Switch.Label className="text-xs ">
          <span className="w-[30px] inline-block text-center">
          <strong>
            {
              enabled ? 'ON' : 'OFF'
            }
          </strong>
          </span>
          &nbsp; Contributing Research
        </Switch.Label>
      </div>
    </Switch.Group>
  )
}

export default DataToggle