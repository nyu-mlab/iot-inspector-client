import React from 'react'
import PropTypes from 'prop-types'
import { Field, Form, Formik } from 'formik'
import { dataUseage } from '@utils/utils'
import TextInput from '@components/fields/TextInput'


const DeviceDiscoveryCard = ({ device }) => {
  return (
    <Formik>
     <div className="device-discovery-card">
      <div className="flex justify-between">
      <div>
        <h3>{device?.device_info?.device_name ||
          device?.auto_name ||
          'Unknown Device'}</h3>
        <div className="flex flex-row gap-4">
          <p>{device && device.ip}</p>
          <p>{device && device.mac}</p>
        </div>
      </div>
      <Field
          type="checkbox"
          name="toggle"
          className="w-4 h-4 !bg-gray-100"
        />
        </div>
        <div className="grid grid-cols-3 gap-2 py-2 network-devices">
          <Field
            autoComplete="off"
            name="deviceName"
            type="text"
            label="Device Name"
            placeholder="Device Name"
            component={TextInput}
            className="w-full p-1 bg-gray-100 rounded-md"
            onChange={(value) => setFieldValue('deviceName', value)}
          />
          <Field
            autoComplete="off"
            name="deviceType"
            type="text"
            label="Device Type"
            placeholder="Device Type"
            component={TextInput}
            className="w-full p-1 bg-gray-100 rounded-md"
            onChange={(value) => setFieldValue('deviceType', value)}
          />
          <Field
            autoComplete="off"
            name="vendorName"
            type="text"
            label="Manufacturer"
            placeholder="Manufacturer"
            component={TextInput}
            className="w-full p-1 bg-gray-100 rounded-md"
            onChange={(value) => setFieldValue('vendorName', value)}
          />
        </div>


    </div>
    </Formik>
  )
}

export default DeviceDiscoveryCard