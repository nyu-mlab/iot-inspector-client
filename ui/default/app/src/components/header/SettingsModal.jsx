import React, { useState } from 'react'
import { Switch } from '@headlessui/react'

const SettingsModal = () => {
  const [contributingResearch, setContributingResearch] = useState(false)
  const [autoInspect, setAutoInspect] = useState(false)


  return (
    <div  className="flex flex-col justify-between">
      <div className="flex flex-col flex-1 gap-6 pb-6 flex-nowrap md:pr-10 xl:pr-40">
        <Switch.Group>
          <div id="contributingResearch">
            <div className="flex items-center gap-2 py-2">
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
              <Switch.Label className="h4 text-dark">Contributing Research</Switch.Label>
            </div>
            <p className="text-dark/80">Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam erat volutpat. Ut wisi enim ad minim veniam, quis nostrud exerci tation ullamcorper suscipit lobortis nisl ut aliquip ex ea commodo consequat. Duis autem vel eum iriure dolor in hendrerit in vulputate velit esse molestie consequat, vel illum dolore eu feugiat nulla facilisis at vero eros et accumsan et iusto odio dignissim qui blandit praesent luptatum zzril delenit augue duis dolore te feugait nulla facilisi.</p>
          </div>
        </Switch.Group>
        <Switch.Group>
          <div id="autoInspect">
          <div className="flex items-center gap-2 py-2">
            <Switch
              checked={autoInspect}
              onChange={setAutoInspect}
              className="relative inline-flex items-center h-6 transition-colors rounded-full bg-light w-11 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2"
            >
              <span
                className={`${
                  autoInspect? 'translate-x-6 bg-green-400' : 'translate-x-1 bg-gray-400/50'
                } inline-block h-4 w-4 transform rounded-full  transition-transform`}
              />
            </Switch>
            <Switch.Label className="h4 text-dark">Automatically inspect new devices as they are discovered</Switch.Label>
          </div>
          <p className="text-dark/80">Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam erat volutpat. Ut wisi enim ad minim veniam, quis nostrud exerci tation ullamcorper suscipit lobortis nisl ut aliquip ex ea commodo consequat.</p>
          </div>
        </Switch.Group>
      </div>
        <hr className="w-full my-4" />

      <div className="flex items-end justify-between">
        <a href="#" className="btn btn-primary">Download Network Data</a>
        <a href="#">Delete all device data</a>
      </div>

  </div>
  )
}

export default SettingsModal