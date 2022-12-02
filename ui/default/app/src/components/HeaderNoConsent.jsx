import React from 'react'
import { Link } from 'react-router-dom';
import Logo from './graphics/Logo'
import useUserConfigs from '@hooks/useUserConfigs'

const Header = () => {
  const { is_consent } = useUserConfigs()

  return (
    <header className="header">
      <nav className="primary-nav">
          <div className="flex justify-between p-6 grow md:px-8 lg:px-12">
            <Link to={is_consent == 1 ? '/overview' : '/'} className="flex gap-2 font-semibold h2 text-dark">
              <Logo /> Home Data Inspector
            </Link>
          </div>
      </nav>
    </header>
  )
}

export default Header