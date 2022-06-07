import React, { useState } from 'react'
import { Switch } from '@headlessui/react'

const DataToggle = () => {
   const [contributingResearch, setContributingResearch] = useState(false)

  return (
    <Switch.Group>
      <div className="flex items-center gap-2 flex-nowrap">
      {/* <div className="inline"> */}
        <Switch
          checked={contributingResearch}
          onChange={setContributingResearch}
          className="relative inline-flex items-center h-6 transition-colors rounded-full bg-light w-11 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2"
        >
          <span
            className={`${
              contributingResearch? 'translate-x-6 bg-green-400' : 'translate-x-1 bg-gray-400/50'
            } inline-block h-4 w-4 transform rounded-full  transition-transform`}
          />
        </Switch>
        <Switch.Label className="text-xs text-white">
          <span className="w-[30px] inline-block text-center">
          <strong>
            {
              contributingResearch ? 'ON' : 'OFF'
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