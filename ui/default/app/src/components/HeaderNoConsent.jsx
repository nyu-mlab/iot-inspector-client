import React, { useState, Fragment } from 'react'
import { Link } from 'react-router-dom';
import Logo from './graphics/Logo'
import useUserConfigs from '@hooks/useUserConfigs'

const Header = () => {
  const [settingsOpen, setSettingsOpen] = useState(false)
  const { userConfigData, userConfigsDataLoading } = useUserConfigs()

  return (
    <header className="header">
      <nav className="primary-nav">
          <div className="flex justify-between p-6 grow md:px-8 lg:px-12">
            <Link to={userConfigData?.is_consent == 1 ? '/overview' : '/'} className="flex gap-2 font-semibold h2 text-dark">
              <Logo /> Home Data Inspector
            </Link>
          </div>
      </nav>
    </header>
  )
}

export default Header