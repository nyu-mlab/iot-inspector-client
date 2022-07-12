import React from 'react'
import useModalDrawer from '@hooks/useModalDrawer'

export default function ScanNetworkButton() {
const { open } = useModalDrawer()


  return (
    <>
      <button
        onClick={() => {
          open({
            type: 'drawer',
            name: 'DeviceDiscoveryDrawer',
            props: {
              foo: 'bar'
            }
          })
        }}
        className="w-full btn btn-primary">
          Scan Network
      </button>
    </>
  )
}