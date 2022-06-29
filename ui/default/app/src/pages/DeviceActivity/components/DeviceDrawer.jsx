import React from 'react'
import { Field, Form, Formik } from 'formik'
import useDeviceInfo from '../hooks/useDeviceInfo'
import TextInput from '../../../components/fields/TextInput'
import CreateSelect from '../../../components/fields/CreateSelect'

const DeviceDrawer = () => {
  const { updateDeviceInfo, updateDeviceInfoLoading, updatedDeviceInfo } =
    useDeviceInfo({ deviceId: 's1663' })

  const initialValues = {
    deviceName: 'TEMP:DEVICE_NAME_VALUE',
    vendorName: '',
    tags: []
  }

  const handleSubmit = (values) => {
    console.log(values)
    const tagList = values.tags.map(tag => tag.label)
    console.log(tagList)


    // const data = {
    //   deviceName: 'Custom Device Name1',
    //   vendorName: 'Custom Vendor Name1',
    //   tagList: JSON.stringify(['tag 1a', 'tag 2a', 'tag 3a']),
    // }

    // updateDeviceInfo(data)
  }

  return (
    <aside className="menu-drawer">
      <Formik
        initialValues={initialValues}
        onSubmit={(values) => handleSubmit(values)}
      >
        {({ values, setFieldValue, dirty }) => (
          <Form id="device-info-form">
            <Field
              autoComplete="off"
              name="deviceName"
              type="text"
              label="Device Name"
              component={TextInput}
              className="sr-only"
              onChange={(value) => setFieldValue('deviceName', value)}
            />
            <Field
              autoComplete="off"
              name="deviceType"
              type="text"
              label="Device Type"
              component={TextInput}
              className="sr-only"
              onChange={(value) => setFieldValue('deviceType', value)}
            />
            <Field
              autoComplete="off"
              name="vendorName"
              type="text"
              label="Manufacturer"
              component={TextInput}
              className="sr-only"
              onChange={(value) => setFieldValue('vendorName', value)}
            />
            <Field
              name="tags"
              type="text"
              component={CreateSelect}
              isMulti
              // options={searchDistanceOptions}
              onChange={(value) => {
                console.log(value)
                setFieldValue('tags', value)
              }}
              label="Tags"
            />
            <button
              type="submit"
              form="device-info-form"
              className="w-full btn btn-primary"
              // disabled={dirty ? false : true}
            >
              Save Device Details
            </button>
          </Form>
        )}
      </Formik>
    </aside>
  )

  return (
    <aside className="menu-drawer">
      <p>Naming and tagging helps with our research</p>
      <form className="flex flex-col gap-4 py-4">
        <div>
          <input
            type="input"
            id="deviceName"
            className="w-full px-4 py-2 bg-white border-l-4 border-yellow-600 rounded-md"
            placeholder="Device Name"
          />
          <label htmlFor="deviceName" className="sr-only">
            Device Name
          </label>
        </div>
        <div>
          <input
            type="input"
            id="deviceType"
            className="w-full px-4 py-2 bg-white border-l-4 border-yellow-600 rounded-md"
            placeholder="Device Type"
          />
          <label htmlFor="deviceType" className="sr-only">
            Device Type
          </label>
        </div>
        <div>
          <input
            type="input"
            id="manufacturerName"
            className="w-full px-4 py-2 bg-white border-l-4 border-yellow-600 rounded-md"
            placeholder="Manufacturer"
          />
          <label htmlFor="manufacturerName" className="sr-only">
            Manufacturer
          </label>
        </div>
      </form>
      <form className="flex flex-col flex-1 pb-4 md:pb-8 md:pt-4">
        <label htmlFor="tags" className="text-sm text-dark/50">
          Device Tags
        </label>
        <input
          type="input"
          id="tags"
          className="flex flex-1 w-full px-4 py-2 bg-white rounded-md"
        />
      </form>
      <button className="w-full btn btn-primary" onClick={onSubmit}>
        Save Device Details
      </button>
    </aside>
  )
}

export default DeviceDrawer
