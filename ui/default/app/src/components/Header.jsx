import React, { useState, Fragment } from 'react'
import { HiBell, HiCog, HiMenu, HiX } from "react-icons/hi";
import DataToggle from './DataToggle'
import AnalyzingTraffic from "./AnalyzingTraffic";
import Logo from './graphics/Logo'
import { Dialog, Tab, Switch, Disclosure, Menu, Transition } from '@headlessui/react'
import SettingsModal from "./header/SettingsModal";
import AchievmentsModal from "./header/AchievmentsModal";
import FAQModal from "./header/FAQModal";

const Header = () => {
  const [settingsOpen, setSettingsOpen] = useState(false)



  return (
    <header className="header">
      <Disclosure as="nav" className="flex flex-col justify-between lg:flex-row">
        {({ open }) => (
          <>
        <div className="flex justify-between p-6 grow md:px-8 lg:px-12">
          <div className="flex gap-2 font-semibold h2 text-dark">
            <Logo /> Home Data Inspector
          </div>
          <div className="flex items-center gap-4">

            <div className="hidden gap-2 md:flex">
              <AnalyzingTraffic />
            </div>

            <div className="flex lg:hidden">
              <Disclosure.Button className="inline-flex items-center justify-center p-2 text-gray-400 rounded-md hover:text-white hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-white">
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
          <button>
            <HiBell className="w-6 h-6" />
          </button>
          <button onClick={() => setSettingsOpen(true)}>
            <HiCog className="w-6 h-6 transition hover:rotate-180 hover:text-primary" />
          </button>
        </div>
        <Disclosure.Panel className="lg:hidden">
            <div className="px-2 pt-2 pb-3 space-y-1">
              {/* Current: "bg-gray-900 text-white", Default: "text-gray-300 hover:bg-gray-700 hover:text-white" */}
              <Disclosure.Button
                as="a"
                href="#"
                className="block px-3 py-2 text-base font-medium text-white bg-gray-900 rounded-md"
              >
                Network Dashboard
              </Disclosure.Button>
              <Disclosure.Button
                as="a"
                href="#"
                className="block px-3 py-2 text-base font-medium text-gray-300 rounded-md hover:bg-gray-700 hover:text-white"
              >
                Settings
              </Disclosure.Button>
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
        <div className="fixed inset-0 bg-dark/50 h-[calc(100vh-80px)] top-[80px]" aria-hidden="true" />
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
        <div className="fixed inset-0 flex items-center justify-center p-4 top-[80px]">
          <Dialog.Panel className="mx-auto bg-white sm:11/12 md:w-10/12 lg:w-8/12 max-w-5xl rounded-2xl min-h-[70%] max-h-[90%] overflow-scroll">
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