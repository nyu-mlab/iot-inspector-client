import React, { Fragment } from 'react'
import propTypes from 'prop-types'
import { Dialog, Transition } from '@headlessui/react'

// import { Dialog } from '@headlessui/react'

import  useModalDrawer  from '@hooks/useModalDrawer'

const DrawerWrapper = ({ modal, props }) => {
  const { close } = useModalDrawer()

  DrawerWrapper.propTypes = {
    modal: propTypes.elementType,
    props: propTypes.object
  }

  return (
    <>
    <Dialog
        as="div"
        className="relative z-20"
        open={true}
        onClose={() => {
          close({
            type: 'drawer',
            name: 'DeviceDiscoveryDrawer'
          })
        }}>


        <div className="fixed inset-0" />
        <div className="fixed inset-0 overflow-hidden">
          <div className="absolute inset-0 overflow-hidden">
            <div className="fixed inset-y-0 right-0 flex max-w-full pl-10 pointer-events-none sm:pl-16">



              <Dialog.Panel className="w-screen max-w-2xl pointer-events-auto">
                  <div className="flex flex-col h-full py-6 overflow-y-scroll bg-white shadow-xl">
                    <div className="px-4 sm:px-6">
                      <div className="flex items-start justify-between">
                        <div className="flex items-center ml-3 h-7">
                          <button
                            type="button"
                            className="text-gray-400 bg-white rounded-md hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                            // onClick={() => setOpen(false)}
                          >
                            <span className="sr-only">Close panel</span>
                          </button>
                        </div>
                      </div>
                    </div>
                    <div className="relative flex-1 px-4 pt-12 mt-6 sm:px-6">
                      {modal()}
                    </div>
                  </div>
                </Dialog.Panel>



            </div>
          </div>
        </div>




      {/* <div className="z-30 modal-backdrop"></div> */}
      {/* <Dialog.Panel className="z-30 slide-panel">
        {modal()}
      </Dialog.Panel> */}
    </Dialog>


    </>
  )
}

export default DrawerWrapper
