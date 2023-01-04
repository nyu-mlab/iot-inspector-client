import React from 'react'
import Header from '@components/Header'
import useUserConfigs from '@hooks/useUserConfigs'
import Consent  from '../pages/Consent/index.jsx'

const DefaultLayout = ({ children }) => {
  const { is_consent } = useUserConfigs()

  // if(!is_consent) return <Consent/>  // TODO: Bring back when ready

  return (
    <>
      <Header />
      { children }
    </>
  )
}

export default DefaultLayout