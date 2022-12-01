import React, { useState, Fragment } from 'react'
import { HiBell, HiCog, HiMenu, HiX } from "react-icons/hi";
import DataToggle from './DataToggle'
import Logo from './graphics/Logo'
import { Dialog, Tab, Switch, Disclosure, Menu, Transition } from '@headlessui/react'
import SettingsModal from "./header/SettingsModal";
import AchievmentsModal from "./header/AchievmentsModal";
import FAQModal from "./header/FAQModal";
import useUserConfigs from '@hooks/useUserConfigs'

const Header = () => {
  const [settingsOpen, setSettingsOpen] = useState(false)
  const { userConfigData, userConfigsDataLoading } = useUserConfigs()

  return (
    <header className="header">
      <nav className="primary-nav">
          <div className="flex justify-between p-6 grow md:px-8 lg:px-12">
            <a href={userConfigData?.userConfigs?.is_consent == 1 ? '/overview' : '/'} className="flex gap-2 font-semibold h2 text-dark">
              <Logo /> Home Data Inspector
            </a>
          </div>
      </nav>
    </header>
  )
}

export default Header