import React, { useState } from 'react'
import { Link } from 'react-router-dom';
import { useNavigate } from 'react-router-dom'
import useUserConfigs from '@hooks/useUserConfigs'
import ReactHtmlParser from 'react-html-parser'

import NoConsentLayout from '../../layouts/NoConsentLayout'
import useCopy from '@hooks/useCopy'

const Consent = () => {
  const { userConfigsDataLoading, updateUserConfigs } = useUserConfigs()
  const configdata = useUserConfigs()
  console.log("data",configdata)


  const navigate = useNavigate()

  const { loading, data } = useCopy('/consent.json')

  if (userConfigsDataLoading) {
    return ''
  }

  const handleSubmit = async (consentValue) => {
    await updateUserConfigs({
      isConsent: consentValue,
      canAutoInspectDevice: consentValue
    })
    // no consent given, redirect to the "Get Started" page.
    // if(!consentValue) navigate('/') TODO: Bring back when ready
  }

  return (
    <>
      <NoConsentLayout>
        <main className='flex w-full h-full bg-gray-100'>
          <div className='p-4 mx-auto bg-white shadow-md md:p-8 md:my-8 rounded-2xl h-fit'>
            <div className='flex flex-col items-center justify-center max-w-2xl gap-8 mx-auto text-center h-fit'>
              <h1>{data.headline || 'Consent Statement'}</h1>
              <div className='overflow-scroll h-72 md:px-8 '>
                {data && ReactHtmlParser(data.body)}
              </div>
              <hr className='w-full md:w-9/12' />
              <button className='btn btn-primary' onClick={() => handleSubmit(1)}>
                I hereby give my consent
              </button>
              <button className='text-dark/50 h4'  onClick={() => handleSubmit(0)}>
                No, I do not give my consent
              </button>
            </div>
          </div>
        </main>
      </NoConsentLayout>
    </>
  )
}

export default Consent
