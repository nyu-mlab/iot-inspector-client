import { gql, useQuery } from '@apollo/client'
import React, { createContext, useContext } from 'react'

const USER_CONFIGS_QUERY = gql`
  query UserConfigs {
    userConfigs {
      is_consent
      can_auto_inspect_device
      can_contribute_to_research
    }
  }
`

const initialState = {
  userConfigData: {}
}

const UserConfigsContext = createContext(initialState)

const UserConfigsProvider = ({ children }) => {
  const { data: userConfigData, loading: userConfigsDataLoading } = useQuery(USER_CONFIGS_QUERY)

  const values = {
    userConfigData,
    foo: 'bar'
  }

  console.log("🐛 @DEBUG::12012022-032542P", values)

  return (
    <UserConfigsContext.Provider value={values}>
      {children}
    </UserConfigsContext.Provider>
  )
}

const useUserConfigs = () => useContext(UserConfigsContext)

export { useUserConfigs, UserConfigsProvider }
