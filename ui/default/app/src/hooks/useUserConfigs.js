import { useContext } from 'react'
import { UserConfigsContext } from '@contexts/UserConfigsContext'

export default function useUserConfigs() {
  return useContext(UserConfigsContext)
}