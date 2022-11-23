import React from 'react'
import HomeSecurity from "@components/graphics/HomeSecurity"
import BackgroundScanning from "@components/graphics/BackgroundScanning"
import ResearchData from "@components/graphics/ResearchData"
import NoConsentLayout from '../../layouts/NoConsentLayout'
import useCopy from '@hooks/useCopy'




const Onboarding = () => {
  const { loading, data } = useCopy('/start.json')


  const inspectorUseCase = [
    {
      label: data.sections ? data.sections[0].headline : '',
      color: 'primary',
      key: 'homeSecurity',
      icon: <HomeSecurity />,
      description: data.sections ? data.sections[0].copy : '',
    },
    {
      label: data.sections ? data.sections[1].headline : '',
      color: 'blue-600',
      key: 'backgroundScanning',
      icon: <BackgroundScanning />,
      description: data.sections ? data.sections[1].copy : '',
    },
    {
      label: data.sections ? data.sections[2].headline : '',
      color: 'dark',
      key: 'researchData',
      icon: <ResearchData />,
      description: data.sections ? data.sections[2].copy : '',
    }
  ]

  return (
    <>
      <NoConsentLayout>
        <main className="flex flex-1 bg-gray-100">
          <div className="w-full p-4 m-2 bg-white shadow-md md:m-8 rounded-2xl">
            <div className="flex flex-col items-center justify-center h-full max-w-6xl gap-8 mx-auto text-center">
              <h1>{data.headline || 'Start Inspectin'}</h1>
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
              <a className="btn btn-primary" href="/consent">{data.cta_label ? data.cta_label : 'Get Started'}</a>
            </div>
          </div>

        </main>
      </NoConsentLayout>
    </>
  )
}

export default Onboarding