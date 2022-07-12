import React, { useState } from 'react'
import { Dialog, RadioGroup } from '@headlessui/react'

const CreateGame = () => {
  const [image, setImage] = useState('startup')

  return (
    <>
      <div>
        <div className="mt-3 text-center sm:mt-5">
          <Dialog.Title as="h3" className="font-bold">
            New Game
          </Dialog.Title>
          <form className="flex flex-col gap-6 text-left">
            <div className="flex flex-col gap-1">
              <label htmlFor="gameName" className="text-sm">
                Game Name
              </label>
              <input
                type="text"
                id="gameName"
                className="p-2 !bg-white !border-gray-300 border rounded-md"
              />
            </div>
            <div className="flex flex-col gap-1">
              <RadioGroup value={image} onChange={setImage}>
                <RadioGroup.Label className="text-sm">
                  Cover Image
                </RadioGroup.Label>
                <div className="flex justify-between">
                  <RadioGroup.Option value="art 1">
                    {({ checked }) => (
                      <img
                        src="https://picsum.photos/100"
                        width={100}
                        height={100}
                        className={`${
                          checked ? 'border-primary' : 'border-transparent'
                        } border-2 border-sm rounded-md`}
                        alt=""
                      />
                    )}
                  </RadioGroup.Option>
                  <RadioGroup.Option value="art 2">
                    {({ checked }) => (
                      <img
                        src="https://picsum.photos/100"
                        width={100}
                        height={100}
                        className={`${
                          checked ? 'border-primary' : 'border-transparent'
                        } border-2 border-sm rounded-md`}
                        alt=""
                      />
                    )}
                  </RadioGroup.Option>
                  <RadioGroup.Option value="art 3">
                    {({ checked }) => (
                      <img
                        src="https://picsum.photos/100"
                        width={100}
                        height={100}
                        className={`${
                          checked ? 'border-primary' : 'border-transparent'
                        } border-2 border-sm rounded-md`}
                        alt=""
                      />
                    )}
                  </RadioGroup.Option>
                  <RadioGroup.Option value="art 4">
                    {({ checked }) => (
                      <img
                        src="https://picsum.photos/100"
                        width={100}
                        height={100}
                        className={`${
                          checked ? 'border-primary' : 'border-transparent'
                        } border-2 border-sm rounded-md`}
                        alt=""
                      />
                    )}
                  </RadioGroup.Option>
                  <RadioGroup.Option value="art 5">
                    {({ checked }) => (
                      <img
                        src="https://picsum.photos/100"
                        width={100}
                        height={100}
                        className={`${
                          checked ? 'border-primary' : 'border-transparent'
                        } border-2 border-sm rounded-md`}
                        alt=""
                      />
                    )}
                  </RadioGroup.Option>
                  <RadioGroup.Option value="art 6">
                    {({ checked }) => (
                      <img
                        src="https://picsum.photos/100"
                        width={100}
                        height={100}
                        className={`${
                          checked ? 'border-primary' : 'border-transparent'
                        } border-2 border-sm rounded-md`}
                        alt=""
                      />
                    )}
                  </RadioGroup.Option>
                </div>
              </RadioGroup>
            </div>
          </form>
        </div>
      </div>
      <div className="mt-5 sm:mt-6">
        <button
          type="button"
          className="inline-flex justify-center w-full px-4 py-2 text-base font-medium text-white transition bg-blue-200 border border-transparent rounded-md shadow-sm hover:bg-blue-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:bg-blue-300 sm:text-sm"
          onClick={() => {
            console.log('Create Game Action!')
          }}>
          Create game
        </button>
      </div>
    </>
  )
}

export default CreateGame
