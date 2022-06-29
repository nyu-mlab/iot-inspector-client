import React from 'react'
import useDeviceInfo from '../hooks/useDeviceInfo'

const DeviceDrawer = () => {
  const { updateDeviceInfo, updateDeviceInfoLoading, updatedDeviceInfo } = useDeviceInfo({ deviceId: 's1663' })

  const onSubmit = (e) => {
    e.preventDefault()
    const data = {
      deviceName: 'Custom Device Name1',
      vendorName: 'Custom Vendor Name1',
      tagList: JSON.stringify(['tag 1a', 'tag 2a', 'tag 3a']),
    }

    updateDeviceInfo(data)
  }

  return (
    <aside className="menu-drawer">
      <p>Naming and tagging helps with our research</p>
      <form className="flex flex-col gap-4 py-4">
        <div>
          <input
            type="input"
            id="deviceName"
            className="w-full px-4 py-2 bg-white border-l-4 border-yellow-600 rounded-md"
            placeholder="Device Name"
          />
          <label htmlFor="deviceName" className="sr-only">
            Device Name
          </label>
        </div>
        <div>
          <input
            type="input"
            id="deviceType"
            className="w-full px-4 py-2 bg-white border-l-4 border-yellow-600 rounded-md"
            placeholder="Device Type"
          />
          <label htmlFor="deviceType" className="sr-only">
            Device Type
          </label>
        </div>
        <div>
          <input
            type="input"
            id="manufacturerName"
            className="w-full px-4 py-2 bg-white border-l-4 border-yellow-600 rounded-md"
            placeholder="Manufacturer"
          />
          <label htmlFor="manufacturerName" className="sr-only">
            Manufacturer
          </label>
        </div>
      </form>
      <form className="flex flex-col flex-1 pb-4 md:pb-8 md:pt-4">
        <label htmlFor="tags" className="text-sm text-dark/50">
          Device Tags
        </label>
        <input
          type="input"
          id="tags"
          className="flex flex-1 w-full px-4 py-2 bg-white rounded-md"
        />
      </form>
      <button className="w-full btn btn-primary" onClick={onSubmit}>
        Save Device Details
      </button>
    </aside>
  )
}

export default DeviceDrawer
