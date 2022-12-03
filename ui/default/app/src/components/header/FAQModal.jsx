import React from 'react'
import { Disclosure, Transition } from '@headlessui/react'
import { HiChevronDown } from "react-icons/hi";
import useCopy from '@hooks/useCopy'
import RefreshSpinner from "../graphics/RefreshSpinner"



const FAQModal = () => {
  const { loading, data } = useCopy('/faq.json')

  if(Object.keys(data).length === 0 && data.constructor === Object) {
    return (
      <div className="w-6 h-6 animate-spin-slow  mx-auto my-24">
        <RefreshSpinner />
      </div>
    )
  }

  return (
    <div>
      <h2>{data.headline || ''}</h2>

      {data.sections && data.sections.map((section,i) => {
        if (!section.faqs || section.faqs.length == 0) return false

        return (
        <section key={`section_${i}`}>

          <h3>{section.title}</h3>

          {section.faqs.map((faq) => (
            <Disclosure key={faq.q} as="div" className="py-4">
            {({ open }) => (
             <>
               <Disclosure.Button className="flex justify-between w-full text-left">
                 <span className={`${open ? 'text-black' : ''}text-gray-600 hover:text-black`}>{faq.q}</span>
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
                 <div className="text-gray-600 [&>*]:text-gray-600 [&>p]:my-3 [&>p:first-child]:mt-0 [&>p:last-child]:mb-0 [&>ul]:grid [&>ul]:gap-3 [&>ul>li]:ml-5 [&>ul>li]:list-disc" dangerouslySetInnerHTML={{__html: faq.a}}/>
               </Disclosure.Panel>
               </Transition>
             </>
           )}
         </Disclosure>
          ))}
        </section>
        )

      })}



    </div>
  )
}

export default FAQModal