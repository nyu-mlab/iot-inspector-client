import React, { useState } from 'react'
import { Switch } from '@headlessui/react'
import useUserConfigs from '@hooks/useUserConfigs'

const DataToggle = () => {
   const [contributingResearch, setContributingResearch] = useState(false)
   const { userConfigsData, userConfigsDataLoading, updateUserConfigs } = useUserConfigs()

  const handleSwitchChange = async () => {
    await updateUserConfigs({
      canContributeToResearch: !userConfigsData.userConfigs.can_contribute_to_research ? 1 : 0
    })
  }

  if (userConfigsDataLoading) {
    return ''
  }

  return (
    <Switch.Group>
      <div className="flex items-center gap-2 flex-nowrap">
      {/* <div className="inline"> */}
        <Switch
          checked={userConfigsData?.userConfigs.can_contribute_to_research ? true : false}
          onChange={handleSwitchChange}
          className="relative inline-flex items-center h-6 transition-colors rounded-full bg-light w-11 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2"
        >
          <span
            className={`${
              userConfigsData?.userConfigs.can_contribute_to_research? 'translate-x-6 bg-green-400' : 'translate-x-1 bg-gray-400/50'
            } inline-block h-4 w-4 transform rounded-full  transition-transform`}
          />
        </Switch>
        <Switch.Label className="text-xs text-white">
          <span className="w-[30px] inline-block text-center">
          <strong>
            {
              userConfigsData?.userConfigs.can_contribute_to_research ? 'ON' : 'OFF'
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