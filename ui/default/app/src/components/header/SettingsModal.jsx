import React, { useState } from 'react'
import { Switch } from '@headlessui/react'
import ReactHtmlParser from 'react-html-parser'
import RefreshSpinner from "../graphics/RefreshSpinner"
import useCopy from '@hooks/useCopy'

const SettingsModal = () => {
  const [contributingResearch, setContributingResearch] = useState(false)
  const [autoInspect, setAutoInspect] = useState(false)
  const { loading, data } = useCopy('/settings.json')

  if(Object.keys(data).length === 0 && data.constructor === Object) {
    return (
      <div className="w-6 h-6 animate-spin-slow  mx-auto my-24">
        <RefreshSpinner />
      </div>
    )
  }

  return (
    <div  className="flex flex-col justify-between">
      <div className="flex flex-col flex-1 gap-6 pb-6 flex-nowrap md:pr-10 xl:pr-40">
        {data.contributingResearch &&
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
                <Switch.Label className="h4 text-dark">{data.contributingResearch.headline}</Switch.Label>
              </div>
              <div className="md:pl-14">
                {data && <div className='text-dark/80 [&>*]:text-dark/80 grid gap-4 [&>ul]:md:pl-6 [&>ul]:py-6 [&>ul]:text-sm [&>ul]:grid [&>ul]:gap-4' dangerouslySetInnerHTML={{__html: data.contributingResearch.copy}}/>}
              </div>
            </div>
          </Switch.Group>
        }
        {data.autoInspect &&
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
              <Switch.Label className="h4 text-dark">{data.autoInspect.headline}</Switch.Label>
            </div>
            <div className="md:pl-14">
              {data && <div  className='text-dark/80 [&>*]:text-dark/80 grid gap-4 [&>ul]:md:pl-6 [&>ul]:py-6 [&>ul]:text-sm [&>ul]:grid [&>ul]:gap-4' dangerouslySetInnerHTML={{__html: data.autoInspect.copy}}/>}
            </div>
            </div>
          </Switch.Group>
        }
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