import { useContext } from 'react'
import { ModalDrawerContext } from '@contexts/ModalDrawerContext'

const useModalDrawer = () => useContext(ModalDrawerContext)

export default useModalDrawer
