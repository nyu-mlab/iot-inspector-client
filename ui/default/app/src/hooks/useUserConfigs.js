import { useContext } from 'react'
import { UserConfigsContext } from '@contexts/UserConfigsContext'

export default function useUserConfits() {
  return useContext(UserConfigsContext)
}
