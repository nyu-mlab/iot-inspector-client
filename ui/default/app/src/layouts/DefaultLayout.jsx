import React from 'react'
import Header from '@components/Header'

const DefaultLayout = ({ children }) => {
  return (
    <>
      <Header />
      {children}
    </>
  )
}

export default DefaultLayout