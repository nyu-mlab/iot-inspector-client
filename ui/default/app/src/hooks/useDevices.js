import { useContext } from 'react'
import { DeviceContext } from '@contexts/DeviceContext'

export default function useDevices() {
  return useContext(DeviceContext)
}