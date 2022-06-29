import React, { useEffect, useState } from 'react'
import { gql, useQuery } from '@apollo/client'

const HIGH_USEAGE_QUERY = gql`
  query Query {
    devices {
      auto_name
      ip
      outbound_byte_count
    }
  }
`

const useHighUseage = () => {
  const [highUseageData, setHighUseageData] = useState([])

  const { data, loading: highUseageDataLoading } = useQuery(HIGH_USEAGE_QUERY)

  useEffect(() => {
    if (data?.devices) {
      // sort by most useage
      // Note, need to slice here because devices is a read-only property
      const sorted = data?.devices.slice().sort((a, b) => {
        return b.outbound_byte_count - a.outbound_byte_count
      })

      setHighUseageData(sorted)
    }
  }, [data?.devices])

  return {
    highUseageData,
    highUseageDataLoading,
  }
}

export default useHighUseage
