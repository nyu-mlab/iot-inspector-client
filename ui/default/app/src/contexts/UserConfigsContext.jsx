import { gql, useMutation, useQuery } from '@apollo/client'
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

const UPDATE_USER_CONFIGS_MUTATION = gql`
  mutation Mutation(
    $isConsent: Int
    $canContributeToResearch: Int
    $canAutoInspectDevice: Int
  ) {
    updateUserConfigs(
      is_consent: $isConsent
      can_contribute_to_research: $canContributeToResearch
      can_auto_inspect_device: $canAutoInspectDevice
    ) {
      can_contribute_to_research
      can_auto_inspect_device
      is_consent
    }
  }
`

const initialState = {
  can_contribute_to_research: 0,
  is_consent: 0,
  can_auto_inspect_device: 0
}

const UserConfigsContext = createContext(initialState)

const UserConfigsProvider = ({ children }) => {
  const {
    data: userConfigData,
    loading: userConfigsDataLoading,
    refetch
  } = useQuery(USER_CONFIGS_QUERY)

  const [updateUserConfigsFn] = useMutation(UPDATE_USER_CONFIGS_MUTATION)

  const updateUserConfigs = async ({
    isConsent,
    canContributeToResearch,
    canAutoInspectDevice
  }) => {
    await updateUserConfigsFn({
      variables: {
        isConsent,
        canContributeToResearch,
        canAutoInspectDevice
      }
    })

    // refetch user configs
    await refetch()
  }

  const value = {
    ...userConfigData?.userConfigs,
    userConfigsDataLoading,
    updateUserConfigs
  }

  return (
    <>
      <UserConfigsContext.Provider value={value}>
        {children}
      </UserConfigsContext.Provider>
    </>
  )
}

// TODO: We can't use this within app... look into why
const useUserConfigs = () => useContext(UserConfigsContext)

export { UserConfigsContext, UserConfigsProvider }
