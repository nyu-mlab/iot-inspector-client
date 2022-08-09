import React, { useState, Fragment } from 'react'
import { HiBell, HiCog, HiMenu, HiX } from "react-icons/hi";
import DataToggle from './DataToggle'
import AnalyzingTraffic from "./AnalyzingTraffic";
import Logo from './graphics/Logo'
import { Dialog, Tab, Switch, Disclosure, Menu, Transition } from '@headlessui/react'
import SettingsModal from "./header/SettingsModal";
import AchievmentsModal from "./header/AchievmentsModal";
import FAQModal from "./header/FAQModal";
import useUserConfigs from '@hooks/useUserConfigs'

const Header = () => {
  const [settingsOpen, setSettingsOpen] = useState(false)
  const { userConfigsData, userConfigsDataLoading } = useUserConfigs()

  return (
    <header className="header">
      <Disclosure as="nav" className="primary-nav">
        {({ open }) => (
          <>
            <div className="flex justify-between p-6 grow md:px-8 lg:px-12">
              <a href={userConfigsData?.userConfigs?.is_consent == 1 ? '/overview' : '/'} className="flex gap-2 font-semibold h2 text-dark">
                <Logo /> Home Data Inspector
              </a>
              <div className="flex items-center gap-4">

                {userConfigsData?.userConfigs?.is_consent == 1
                ? <div className="hidden gap-2 md:flex">
                  <AnalyzingTraffic />
                </div>
                : '/'
                }


                <div className="flex lg:hidden">
                  <Disclosure.Button className="inline-flex items-center justify-center p-2 text-gray-400 rounded-md hover:text-white hover:bg-secondary/80 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-primary">
                    <span className="sr-only">Open main menu</span>
                    {open ? (
                      <HiX className="block w-6 h-6" aria-hidden="true" />
                    ) : (
                      <HiMenu className="block w-6 h-6" aria-hidden="true" />
                    )}
                  </Disclosure.Button>
                </div>
              </div>
            </div>
            <div className="hidden gap-8 p-6 text-white lg:flex bg-dark">
              <DataToggle />
              {/*
          TODO: Notifications
          <button>
            <HiBell className="w-6 h-6" />
          </button> */}
              <button onClick={() => setSettingsOpen(true)}>
                <HiCog className="w-6 h-6 transition hover:rotate-180 hover:text-primary" />
              </button>
            </div>


            {/* Responsive Navigation */}
            <Disclosure.Panel className="lg:hidden">
              <div className="px-4 pt-2 pb-3 space-y-1">
                <Disclosure.Button
                  as="a"
                  href="/"
                  className="block pb-6 text-xl text-dark"
                >
                  Network Dashboard
                </Disclosure.Button>
                <Disclosure.Button
                  as="a"
                  href="/communication-endpoints/"
                  className="block pb-6 text-xl text-dark"
                >
                  Communication Endpoints
                </Disclosure.Button>
                <Disclosure.Button
                  as="button"
                  href="/communication-endpoints/"
                  className="block pb-6 text-xl font-semibold text-dark"
                  onClick={() => setSettingsOpen(true)}
                >
                  Settings
                </Disclosure.Button>
              </div>
              <div className="px-4 py-6 bg-dark lg:hidden">
                <DataToggle />
              </div>

              <hr />
              <div className="px-4 py-6 md:hidden">
                <AnalyzingTraffic />
              </div>
            </Disclosure.Panel>
          </>
        )}
      </Disclosure>
      <Transition show={settingsOpen} as={Fragment}>
        <Dialog
          // open={settingsOpen}
          onClose={() => setSettingsOpen(false)}
          className="relative z-50"
        >
          <Transition.Child
            as={Fragment}
            enter="ease-out duration-300"
            enterFrom="opacity-0"
            enterTo="opacity-100"
            leave="ease-in duration-200"
            leaveFrom="opacity-100"
            leaveTo="opacity-0"
          >
            <div className="modal-backdrop" aria-hidden="true" />
          </Transition.Child>
          <Transition.Child
            as={Fragment}
            enter="ease-out duration-300"
            enterFrom="opacity-0 scale-95"
            enterTo="opacity-100 scale-100"
            leave="ease-in duration-200"
            leaveFrom="opacity-100 scale-100"
            leaveTo="opacity-0 scale-95"
          >
            <div className="inspector-settings">
              <Dialog.Panel className="inspector-settings-panel">
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
                    <Tab as={Fragment}>
                      {({ selected }) => (
                        <button
                          className={
                            selected ? 'tab-nav-item tab-nav-item-active' : 'tab-nav-item'
                          }
                        >
                          Achievments
                        </button>
                      )}
                    </Tab>
                    <Tab as={Fragment}>
                      {({ selected }) => (
                        <button
                          className={
                            selected ? 'tab-nav-item tab-nav-item-active' : 'tab-nav-item'
                          }
                        >
                          FAQs
                        </button>
                      )}
                    </Tab>
                  </Tab.List>
                  <Tab.Panels className="px-8 py-6 md:py-8 md:px-12">
                    <Tab.Panel>
                      <SettingsModal />
                    </Tab.Panel>
                    <Tab.Panel >
                      <AchievmentsModal />
                    </Tab.Panel>
                    <Tab.Panel>
                      <FAQModal />
                    </Tab.Panel>
                  </Tab.Panels>
                </Tab.Group>
              </Dialog.Panel>
            </div>
          </Transition.Child>
        </Dialog>
      </Transition>

    </header>
  )
}

export default Header