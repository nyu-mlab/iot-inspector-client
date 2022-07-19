import React from 'react'
import HomeSecurity from "@components/graphics/HomeSecurity"
import BackgroundScanning from "@components/graphics/BackgroundScanning"
import ResearchData from "@components/graphics/ResearchData"

const inspectorUseCase = [
  {
    label: 'Home Security',
    color: 'primary',
    key: 'homeSecurity',
    icon: <HomeSecurity />,
    description: 'Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam erat volutpat.'
  },
  {
    label: 'Background Scanning',
    color: 'blue-600',
    key: 'backgroundScanning',
    icon: <BackgroundScanning />,
    description: 'Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam erat volutpat.'
  },
  {
    label: 'Data for Research',
    color: 'dark',
    key: 'researchData',
    icon: <ResearchData />,
    description: 'Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam erat volutpat.'
  }
]

const Onboarding = () => {
  return (
    <>
      <div className="App">
        {/* <Header /> */}
        <main className="flex h-full bg-gray-100">
          <div className="w-full p-4 m-2 bg-white shadow-md md:m-8 rounded-2xl">
            <div className="flex flex-col items-center justify-center h-full max-w-6xl gap-8 mx-auto text-center">
              <h1>Start Inspecting</h1>
              <div className="grid w-full grid-cols-1 gap-4 md:grid-cols-3">

                {inspectorUseCase.map((card) => (
                <div className="flex flex-col gap-4 text-center" key={card.key}>
                  <div className="flex items-center justify-center border-b-8 border-primary bg-light rounded-xl">
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
      </div>
    </>
  )
}

export default Onboarding