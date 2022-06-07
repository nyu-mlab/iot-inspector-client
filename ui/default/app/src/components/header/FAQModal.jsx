import React from 'react'
import { Disclosure, Transition } from '@headlessui/react'
import { HiChevronDown } from "react-icons/hi";

const faqs = [
  {
    question: "Is team pricing available?",
    answer: "Lorem ipsum dolor sit amet, consectetur adipiscing elit. In ac dictum felis. Ut porta, arcu in faucibus aliquam, erat arcu convallis libero, quis varius mauris felis at massa."
  },
  {
    question: "Why is my network connecting to the U.S. Military?",
    answer: "Lorem ipsum dolor sit amet, consectetur adipiscing elit. In ac dictum felis. Ut porta, arcu in faucibus aliquam, erat arcu convallis libero, quis varius mauris felis at massa."
  }
]

const FAQModal = () => {
  return (
    <div>
      {faqs.map((faq) => (
    <Disclosure key={faq.question} as="div" className="py-4">
       {({ open }) => (
        <>
          <Disclosure.Button className="flex justify-between w-full">
            <span className={`${open ? 'text-black' : ''}text-gray-600 hover:text-black`}>{faq.question}</span>
            {/*
              Use the `open` render prop to rotate the icon when the panel is open
            */}
            <HiChevronDown
              className={`${open ? "transform -rotate-180" : ""} transition `}
            />
          </Disclosure.Button>

          <Transition
            show={open}
            enter="transition duration-100 ease-out"
            enterFrom="transform -translate-y-3 opacity-0"
            enterTo="transform translate-y-0 opacity-100"
            leave="transition duration-75 ease-out"
            leaveFrom="transform translate-x-0 opacity-100"
            leaveTo="transform -translate-y-3 opacity-0"
          >
          <Disclosure.Panel className='p-2 my-1 border-l-2 border-primary bg-gray-50'>
            <p className="text-gray-600">{faq.answer}</p>
          </Disclosure.Panel>
          </Transition>
        </>
      )}
    </Disclosure>
    ))}
    </div>
  )
}

export default FAQModal