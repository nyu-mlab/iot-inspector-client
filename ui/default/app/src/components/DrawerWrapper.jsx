import React, { Fragment } from 'react'
import propTypes from 'prop-types'

import { Dialog } from '@headlessui/react'

import  useModalDrawer  from '@hooks/useModalDrawer'

const DrawerWrapper = ({ modal, props }) => {
  const { close } = useModalDrawer()

  DrawerWrapper.propTypes = {
    modal: propTypes.elementType,
    props: propTypes.object
  }
console.log({modal})

  return (
    <>
    <div className="z-30 modal-backdrop"></div>
      <div className="z-30 slide-panel">
      {modal()}
    </div>


    </>
  )
}

export default DrawerWrapper
