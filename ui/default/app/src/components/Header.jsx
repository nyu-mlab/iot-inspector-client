import React, { useState, Fragment } from 'react'
import { HiBell, HiCog, HiRefresh } from "react-icons/hi";
import DataToggle from './DataToggle'
import Logo from './graphics/Logo'
import { Dialog, Tab, Switch } from '@headlessui/react'





const Header = () => {
  const [isOpen, setIsOpen] = useState(true)
  const [contributingResearch, setContributingResearch] = useState(false)
  const [autoInspect, setAutoInspect] = useState(false)

  return (
    <header className="header">
      <div className="flex justify-between">
        <div className="flex justify-between p-6 grow">
          <div className="flex gap-2 font-semibold h2 text-dark">
            <Logo /> Home Data Inspector
          </div>
          <div className="flex gap-2">
            <span className="mt-px font-semibold mt-1/2 text-secondary h4">
              Analyzing 0 Kbps of traffic
            </span>
            <HiRefresh className="w-7 h-7 text-secondary animate-spin-slow" />
          </div>
        </div>
        <div className="flex gap-8 p-6 text-white bg-dark">
            <DataToggle />
          <button>
            <HiBell className="w-6 h-6" />
          </button>
          <button onClick={() => setIsOpen(true)}>
            <HiCog className="w-6 h-6 transition hover:rotate-180 hover:text-primary" />
          </button>
        </div>
      </div>
      <Dialog
        open={isOpen}
        onClose={() => setIsOpen(false)}
        className="relative z-50"
      >
        <div class="fixed inset-0 bg-dark/50 h-[calc(100vh-80px)] top-[80px]" aria-hidden="true" />

        {/* Full-screen container to center the panel */}
        <div class="fixed inset-0 flex items-center justify-center p-4">
          {/* The actual dialog panel  */}
          <Dialog.Panel class="mx-auto max-w-5xl  rounded-2xl bg-white">
            <Tab.Group >
              <Tab.List className="tab-nav">
                <Tab as={Fragment}>
                  {({ selected }) => (
                  <button
                      className={
                        selected ? 'tab-nav-item tab-nav-item-active' : 'tab-nav-item'
                      }
                    >
                    Settings
                  </button>
                  )}
                </Tab>
                <Tab className="tab-nav-item">Achievments</Tab>
                <Tab className="tab-nav-item">FAQs</Tab>
              </Tab.List>
              <Tab.Panels>
                <Tab.Panel>
                  <div className="max-w-4xl px-8 py-6">
                     <Switch.Group>
                        <div className="flex flex-col gap-6 pb-6 flex-nowrap md:pr-40">
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
                        </div>
                        <hr className="w-full my-4" />
                        <div className="flex items-end justify-between">
                          <a href="#" className="btn btn-primary">Download Network Data</a>
                          <a href="#">Delete all device data</a>
                        </div>
                      </Switch.Group>
                  </div>
                </Tab.Panel>
                <Tab.Panel>Content 2</Tab.Panel>
                <Tab.Panel>Content 3</Tab.Panel>
              </Tab.Panels>
            </Tab.Group>
          </Dialog.Panel>
        </div>
      </Dialog>
    </header>
  )
}

export default Header