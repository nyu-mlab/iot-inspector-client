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
            <div className="md:pl-14">
              <p className="text-dark/80">By toggling on this option, you are participating in a research study by contributing your network’s data to a larger research effort. The NYU researchers behind this study are particularly interested in learning more about the security and privacy of smart homes.</p>
              <p className="text-dark/80">
              If you agree to be in this study, HDI will securely and anonymously send some of the collected data to the NYU researchers. You can find out more about what data we share with the NYU researchers, and how the researchers protect your data by following this FAQ.
              </p>
              <dl className="grid gap-4 py-6 text-sm md:pl-6 text-dark/80">
                  <dt>Your participation is voluntary. You are free to toggle on/off this option as frequently and for as long as you like.</dt>
                  <dd><strong>Risks:</strong> When you agree to contribute your data to research, HDI may be slower and may consume extra bandwidth, as it transmits the collected data about your network to the NYU researchers.</dd>
                  <dd><strong>Benefits:</strong> You will feel good! — your altruism will lead to real-world data from your smart home being shared with security and privacy researchers.</dd>
              </dl>
            </div>
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
          <div className="md:pl-14">
            <p className="text-dark/80">Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam erat volutpat. Ut wisi enim ad minim veniam, quis nostrud exerci tation ullamcorper suscipit lobortis nisl ut aliquip ex ea commodo consequat.</p>
          </div>
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