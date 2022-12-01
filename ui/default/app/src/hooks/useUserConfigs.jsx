import React, { useMemo, useEffect } from 'react'
import { gql, useMutation, useQuery } from '@apollo/client'
import useNotifications from '@hooks/useNotifications'
import { useState } from 'react'

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
  const [userConfigData, setUserConfigData] = useState()
  const { data: userConfigsRawData, loading: userConfigsDataLoading } = useQuery(USER_CONFIGS_QUERY)

  console.log("🐛 @DEBUG::12012022-113124A", userConfigData)

  // const [getUserConfigsFn, { called, loading: userConfigsDataLoading, data:userConfigsRawData  }] = useLazyQuery(
  //   GET_GREETING,
  //   { variables: { language: "english" } }
  // );

  const [
    updateUserConfigsFn,
    { data: updatedUserConfigsRawData, loading: updateUserConfigsLoading, error },
  ] = useMutation(UPDATE_USER_CONFIGS_MUTATION)

  // const userConfigsData = useMemo(() => {
  //   if (updatedUserConfigsRawData) {
  //     return { userConfigs: updatedUserConfigsRawData.updateUserConfigs}
  //   }
  //   return userConfigsRawData
  // }, [userConfigsRawData, updatedUserConfigsRawData])

  useEffect(() => {
    setUserConfigData(userConfigsRawData)
  }, [userConfigsRawData])
  

  const updateUserConfigs = async ({
    isConsent,
    canContributeToResearch,
    canAutoInspectDevice,
  }) => {
    const updatedConfigs = await updateUserConfigsFn({
      variables: {
        isConsent,
        canContributeToResearch,
        canAutoInspectDevice
      },
    })

    const x = {userConfigs: updatedUserConfigsRawData?.data?.updateUserConfigs}
    setUserConfigData(x)

    showSuccess("Success!")
  }

  return {
    userConfigData,
    // userConfigsData,
    userConfigsDataLoading,
    updateUserConfigs
  }
}

export default useUserConfigs