import React from 'react'


const Header = () => {
  return (
    <header className="w-full bg-white shadow-lg">
      <div className="flex justify-between">
        <div className="flex justify-between w-full">
          <div>Home Data Inspector</div>
          <div>Analyzing 0 Kbps of traffic</div>
        </div>
        <div className="text-white bg-gray-900">
          Contributing Research
          <button>notifications</button>
          <button>settings</button>
        </div>
      </div>

    </header>
  )
}

export default Header