import React, {createContext, useContext } from 'react'

const initialState = {
}

const MyContext = createContext(initialState)

const MyProvider = ({children}) => {
  const values={}
  return (
    <MyContext.Provider value={values}>
      {children}
    </MyContext.Provider>
  )
}

const useMyProvider = () => useContext(MyContext)

export { useMyProvider, MyProvider }
