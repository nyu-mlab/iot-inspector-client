import React from 'react'
import HomeSecurity from "@components/graphics/HomeSecurity"
import BackgroundScanning from "@components/graphics/BackgroundScanning"
import ResearchData from "@components/graphics/ResearchData"
import NoConsentLayout from '../../layouts/NoConsentLayout'


const inspectorUseCase = [
  {
    label: 'What is Home Data Inspector?',
    color: 'primary',
    key: 'homeSecurity',
    icon: <HomeSecurity />,
    description: 'This software monitors the network activities of all internet-connected devices in your home network (e.g., your “smart” electronics.  (For those who would like to see the open source software, click here).'
  },
  {
    label: 'Why you should care',
    color: 'blue-600',
    key: 'backgroundScanning',
    icon: <BackgroundScanning />,
    description: 'Our Home Data Inspector will let you see which devices in your home connect to the internet, see who those devices are sending data to, and identify potential security and privacy violations. '
  },
  {
    label: 'Why we care',
    color: 'dark',
    key: 'researchData',
    icon: <ResearchData />,
    description: 'Home Data Inspector is also a research tool – it can collect anonymized data that helps us better understand the impact of these connected devices on users security, privacy, and network performance.  We hope you’ll share your findings with our researchers! '
  }
]

const Onboarding = () => {
  return (
    <>
      <NoConsentLayout>
        <main className="flex flex-1 bg-gray-100">
          <div className="w-full p-4 m-2 bg-white shadow-md md:m-8 rounded-2xl">
            <div className="flex flex-col items-center justify-center h-full max-w-6xl gap-8 mx-auto text-center">
              <h1>Start Inspecting</h1>
              <div className="grid w-full grid-cols-1 gap-4 md:grid-cols-3">

                {inspectorUseCase.map((card) => (
                <div className="flex flex-col gap-4 text-center" key={card.key}>
                  <div className="flex items-center justify-center border-b-8 border-primary bg-light rounded-xl lg:p-6">
                    {card.icon}
                  </div>
                  <div className="flex flex-col gap-2 sm:px-4">
                  <h2>{card.label}</h2>
                  <p>{card.description}</p>
                  </div>
                </div>
                ))}
              </div>
              <a className="btn btn-primary" href="/consent">Get Started</a>
            </div>
          </div>

        </main>
      </NoConsentLayout>
    </>
  )
}

export default Onboarding