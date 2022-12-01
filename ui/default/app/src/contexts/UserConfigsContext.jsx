import React, { createContext, useState, useEffect } from 'react'
import PropTypes from 'prop-types'
import useNotifications from '@hooks/useNotifications'
import { gql, useMutation, useLazyQuery } from '@apollo/client'


const UPDATE_USER_CONFIGS_MUTATION = gql`
mutation Mutation($isConsent: Int, $canContributeToResearch: Int, $canAutoInspectDevice: Int) {
    updateUserConfigs(is_consent: $isConsent, can_contribute_to_research: $canContributeToResearch, can_auto_inspect_device: $canAutoInspectDevice) {
      can_contribute_to_research
      can_auto_inspect_device
      is_consent
    }
  }
`

const USER_CONFIGS_QUERY = gql`
query UserConfigs {
    userConfigs {
      is_consent
      can_auto_inspect_device
      can_contribute_to_research
    }
  }
`
// ----------------------------------------------------------------------

const UserConfigsContext = createContext()

UserConfigsProvider.propTypes = {
  children: PropTypes.node
}

function UserConfigsProvider({ children }) {
  const { showSuccess, showWarning } = useNotifications()
  const [userConfigData, setUserConfigData] = useState()
  const [loading, setLoading] = useState(false)
  const [getConfigData] = useLazyQuery(USER_CONFIGS_QUERY)
  const [updateUserConfigsFn] = useMutation(UPDATE_USER_CONFIGS_MUTATION)

  useEffect(() => {
    const fetchData = async () => {
      const { data: {userConfigs}, loading }= await getConfigData()
      setUserConfigData({ ...userConfigs })
    }
    fetchData().catch(console.error);
  }, [])

  const updateUserConfigs = async ({
    isConsent,
    canContributeToResearch,
    canAutoInspectDevice,
  }) => {
    const { data: {updateUserConfigs}, loading: updateUserConfigsLoading, error } = await updateUserConfigsFn({
      variables: {
        isConsent,
        canContributeToResearch,
        canAutoInspectDevice
      },
    })
    setUserConfigData({
      ...updateUserConfigs
    })
    setLoading(loading)
    if(isConsent){
      showSuccess("Success!")
    } else {
      showWarning("Returning to home")
    }
  }

  const value = {
    userConfigData,
    userConfigsDataLoading:loading,
    updateUserConfigs
  }

  return (
    <UserConfigsContext.Provider value={value}>{children}</UserConfigsContext.Provider>
  )
}

export { UserConfigsProvider, UserConfigsContext }
