import React from 'react'
import HeaderNoConsent from '@components/HeaderNoConsent'

const DefaultLayout = ({ children }) => {
  return (
    <>
      <HeaderNoConsent />
      {children}
    </>
  )
}

export default DefaultLayout