import React from 'react'
import { HiBell, HiCog, HiRefresh } from "react-icons/hi";
import DataToggle from './DataToggle'




const Header = () => {

  return (
    <header className="fixed top-0 left-0 w-full bg-white shadow-md">
      <div className="flex justify-between">
        <div className="flex justify-between p-6 grow">
          <div>
            <a href="/" className="font-semibold h2 text-dark">
              Home Data Inspector
            </a>

          </div>
          <div className="flex gap-2">
            <span className="mt-px font-semibold mt-1/2 text-secondary h4">
              Analyzing 0 Kbps of traffic
            </span>
            <HiRefresh className="w-7 h-7 text-secondary animate-spin-slow" />
          </div>
        </div>
        <div className="flex gap-8 p-6 text-white bg-dark">
            <DataToggle />
          <button>
            <HiBell className="w-6 h-6" />
          </button>
          <button>
            <HiCog className="w-6 h-6" />
          </button>
        </div>
      </div>

    </header>
  )
}

export default Header