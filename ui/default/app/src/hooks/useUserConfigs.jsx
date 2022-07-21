import React, { useMemo } from 'react'
import { gql, useMutation, useQuery } from '@apollo/client'
import useNotifications from '@hooks/useNotifications'

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

const useUserConfigs = () => {
  const { showSuccess } = useNotifications()
  const { data: userConfigsRawData, loading: userConfigsDataLoading } = useQuery(USER_CONFIGS_QUERY)

  const [
    updateUserConfigsFn,
    { data: updatedUserConfigsRawData, loading: updateUserConfigsLoading, error },
  ] = useMutation(UPDATE_USER_CONFIGS_MUTATION)

  const userConfigsData = useMemo(() => {
    if (updatedUserConfigsRawData) {
      return { userConfigs: updatedUserConfigsRawData.updateUserConfigs}
    }
    return userConfigsRawData
  }, [userConfigsRawData, updatedUserConfigsRawData])

  const updateUserConfigs = async ({
    isConsent,
    canContributeToResearch,
    canAutoInspectDevice,
  }) => {
    await updateUserConfigsFn({
      variables: {
        isConsent,
        canContributeToResearch,
        canAutoInspectDevice
      },
    })

    showSuccess("Success!")
  }

  return {
    userConfigsData,
    userConfigsDataLoading,
    updateUserConfigs
  }
}

export default useUserConfigs