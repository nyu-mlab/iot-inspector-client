import React, { useState } from 'react'
import { Field, Form, Formik } from 'formik'
import useDeviceInfo from '@hooks/useDeviceInfo'
import TextInput from '@components/fields/TextInput'
import CreateSelect from '@components/fields/CreateSelect'
import useDevices from '@hooks/useDevices'
import { useEffect } from 'react'


const DeviceDrawer = ({ deviceId }) => {
  const { updateDeviceInfo, updateDeviceInfoLoading, updatedDeviceInfo } =
    useDeviceInfo({ deviceId })
  const { devicesData, devicesDataLoading } = useDevices({ deviceId })

  const [initialValues, setInitialValues] = useState(undefined)

  const parseTags = (jsonString) => {
    let tags = JSON.parse(jsonString)
    tags = tags.map((tag) => ({ label: tag, value: tag }))
    return tags
  }

  useEffect(() => {
    if (!devicesData.length) return

    const selectedDevice = devicesData.find(d => d.device_id === deviceId)

    console.log("@DEBUG::07132022-100303", selectedDevice);
    setInitialValues({
      deviceName:
        selectedDevice?.device_info?.device_name ||
        selectedDevice?.auto_name ||
        '',
      vendorName: selectedDevice?.device_info?.vendor_name || '',
      tags: parseTags(selectedDevice?.device_info?.tag_list) || [],
    })
  }, [devicesData])

  const handleSubmit = ({deviceName, vendorName, tags}) => {
    const tagList = JSON.stringify(tags.map((tag) => tag.label))
    console.log()
    const data = {
      deviceName,
      vendorName,
      tagList
    }

    updateDeviceInfo(data)
  }

  return (
    <aside className="menu-drawer device-details">
      {!initialValues ? (
        <div className="h-[600px] p-8">
          <div className="h-full skeleton" />
        </div>
      ) : (
        <Formik
          initialValues={initialValues}
          onSubmit={(values) => handleSubmit(values)}
        >
          {({ values, setFieldValue, dirty }) => (
            <Form id="device-info-form" className="flex flex-col justify-between h-full">
              <div className="grid gap-4">
              <Field
                autoComplete="off"
                name="deviceName"
                type="text"
                label="Device Name"
                component={TextInput}
                className="w-full px-4 py-2 bg-gray-100 border-l-4 border-yellow-600 rounded-md"
                onChange={(value) => setFieldValue('deviceName', value)}
              />
              <Field
                autoComplete="off"
                name="vendorName"
                type="text"
                label="Manufacturer"
                component={TextInput}
                className="w-full px-4 py-2 bg-gray-100 border-l-4 border-yellow-600 rounded-md"
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
              </div>
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
      )}
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
