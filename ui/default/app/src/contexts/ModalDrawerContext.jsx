import React, { createContext, useState } from 'react'
import PropTypes from 'prop-types'
import ModalWrapper from '@components/ModalWrapper'
import DrawerWrapper from '@components/DrawerWrapper'
import DeviceDiscoveryDrawer from '@components/DeviceDiscoveryDrawer'



const initialState = {
  type: null,
  open: false,
  modalComponent: null,
  props: {}
}

const modalLookup = {
    DeviceDiscoveryDrawer
}


const ModalDrawerContext = createContext(initialState)

const ModalDrawerProvider = ({ children }) => {
  const [data, setData] = useState(initialState)

  const open = ({ type, name, props }) => {
    if (type !== 'modal' && type !== 'drawer') {
      throw new Error('Please supply valid type, either modal or drawer')
    }

    if (type === 'modal') {
      const modalComponent = modalLookup[name]
      setData({ type, open: true, modalComponent, props })
    }

    if (type === 'drawer') {
      const modalComponent = modalLookup[name]
      setData({ type, open: true, modalComponent, props })
    }
  }

  const close = ({ type, name }) => {
    if (type !== 'modal' && type !== 'drawer') {
      throw new Error('Please supply valid type, either modal or drawer')
    }
    setData({ type, open: false, name })
  }

  return (
    <ModalDrawerContext.Provider value={{ open, close }}>
        {data.open && data.type === 'modal' && (
          <ModalWrapper modal={data.modalComponent} props={data.props} />
        )}
        {data.open && data.type === 'drawer' && (
          <DrawerWrapper modal={data.modalComponent} props={data.props} />
        )}
      {children}
    </ModalDrawerContext.Provider>
  )
}

ModalDrawerProvider.propTypes = {
  children: PropTypes.node
}

export { ModalDrawerProvider, ModalDrawerContext }
