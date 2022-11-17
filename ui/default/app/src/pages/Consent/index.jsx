import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import useUserConfigs from '@hooks/useUserConfigs'
import NoConsentLayout from '../../layouts/NoConsentLayout'

const Consent = () => {
  const { userConfigsData, userConfigsDataLoading, updateUserConfigs } =
    useUserConfigs()
  const [canAutoInspectDevice, setCanAutoInspectDevice] = useState(true)
  const navigate = useNavigate()

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
                <p>
                  We may share some of your information with outside
                  researchers. We will remove your name, contact information,
                  and any other information that identifies you personally.
                  <a href=''>FAQ</a>
                </p>
                <p>
                  We will remove your name, contact information (excluding ZIP
                  code), and any other information that identifies you
                  personally from any data we share with outside researchers.
                </p>
                <p>
                  Consumer Reports conducts research studies with consumers to
                  understand their experiences with products and services they
                  use and their views on various consumer issues. Your responses
                  will be used to produce information designed to help consumers
                  in today's marketplace, to move the marketplace in ways that
                  protect and empower consumers, and to support engagement and
                  advocacy efforts to influence legislators, regulatory bodies,
                  and other marketplace actors.
                </p>
                <p>
                  This Internet of Things (IoT) study consists of 1) downloading
                  the HDI app and 2) running it in a browser window to better
                  understand how the devices in your home connect to the
                  internet, and identify potential security and privacy
                  violations.
                </p>
                <p>
                  We may share aggregated findings in an anonymized way at
                  Consumer Reports and NYU, so that our researchers can identify
                  security and privacy violations to keep consumers better
                  protected in the IoT space. We will remove your name, contact
                  information and any other information that might identify you
                  personally from any aggregated questionnaire that we share
                  with third parties.
                </p>
                <p>
                  We may follow up with you as part of our research and
                  reporting. We will not use any information that identifies you
                  in our reporting unless we contact you and you specifically
                  give us permission.
                </p>
                <p>
                  Learn more about this project.
                  <a href=''>Read our FAQs</a>
                </p>
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
