import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import useUserConfigs from '@hooks/useUserConfigs'
import ReactHtmlParser from 'react-html-parser'

import NoConsentLayout from '../../layouts/NoConsentLayout'
import useCopy from '@hooks/useCopy'

const Consent = () => {
  const { userConfigsDataLoading, updateUserConfigs } = useUserConfigs()
  const navigate = useNavigate()

  const { loading, data } = useCopy('/consent.json')

  if (userConfigsDataLoading) {
    return ''
  }

  const handleSubmit = async () => {
    await updateUserConfigs({
      isConsent: 1,
      canAutoInspectDevice: 1
    })

    navigate('/overview')
  }

  return (
    <>
      <NoConsentLayout>
        <main className='flex w-full h-full bg-gray-100'>
          <div className='p-4 mx-auto bg-white shadow-md md:p-8 md:my-8 rounded-2xl h-fit'>
            <div className='flex flex-col items-center justify-center max-w-2xl gap-8 mx-auto text-center h-fit'>
              <h1>Consent Statement</h1>
              <div className='overflow-scroll h-72 md:px-8 '>
                {data && ReactHtmlParser(data.body)}
              </div>
              <hr className='w-full md:w-9/12' />
              <button className='btn btn-primary' onClick={handleSubmit}>
                I hereby give my consent
              </button>
              <a className='text-dark/50 h4' href='/'>
                No, I do not give my consent
              </a>
            </div>
          </div>
        </main>
      </NoConsentLayout>
    </>
  )
}

export default Consent
