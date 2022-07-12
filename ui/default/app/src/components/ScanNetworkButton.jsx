import React from 'react'
import useModalDrawer from '@hooks/useModalDrawer'

export default function ScanNetworkButton() {
const { open } = useModalDrawer()


  return (
    <>
    {console.log(open)}
      <button
        onClick={() => {
          open({
            type: 'modal',
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