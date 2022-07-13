import React, { Fragment } from 'react'
import propTypes from 'prop-types'

import { Dialog } from '@headlessui/react'

import  useModalDrawer  from '@hooks/useModalDrawer'

const ModalWrapper = ({ modal, props }) => {
  const { close } = useModalDrawer()

  ModalWrapper.propTypes = {
    modal: propTypes.elementType,
    props: propTypes.object
  }

  return (
    <>
      <Dialog
        as="div"
        className="relative z-10"
        open={true}
        onClose={() => {
          close({
            type: 'modal',
            name: 'DeviceDiscoveryDrawer'
          })
        }}>
        <div className="fixed inset-0 transition-opacity bg-gray-500 bg-opacity-75" />

        <div className="fixed inset-0 z-10 overflow-y-auto">
          <div className="flex items-end justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
            {/* This element is to trick the browser into centering the modal contents. */}
            <span
              className="hidden sm:inline-block sm:align-middle sm:h-screen"
              aria-hidden="true">
              &#8203;
            </span>
            <Dialog.Panel className="relative inline-block px-12 pt-5 pb-4 overflow-hidden text-left align-bottom transition-all transform bg-white rounded-lg shadow-xl sm:my-8 sm:align-middle sm:max-w-sm md:max-w-lg lg:max-w-2xl sm:w-full sm:p-6">
              {modal}
            </Dialog.Panel>
          </div>
        </div>
      </Dialog>
    </>
  )
}

export default ModalWrapper
