import React, { useState, useEffect, useMemo } from 'react'
import { Field, Form, Formik } from 'formik'
import useDeviceInfo from '@hooks/useDeviceInfo'
import TextInput from '@components/fields/TextInput'
import CreateSelect from '@components/fields/CreateSelect'
import useDevices from '@hooks/useDevices'
import useNotifications from '@hooks/useNotifications'
import SELECTS from '@constants/selects'


const DeviceDrawer = ({ deviceId }) => {
  console.log("DeviceDrawer")
  const { updateDeviceInfo, updateDeviceInfoLoading, updatedDeviceInfo } =
    useDeviceInfo({ deviceId })

  const { devicesData, devicesDataLoading, error } = useDevices({ deviceId })
  const { showError } = useNotifications()
  useEffect(() => {
    if(error) showError(error.message)
  }, [error])

  const [initialValues, setInitialValues] = useState(undefined)

  const parseTags = (jsonString) => {
    let tags = JSON.parse(jsonString)
    tags = tags.map((tag) => ({ label: tag, value: tag }))
    return tags
  }

  const deviceSelects = useMemo(() => {
    // get all keywords into a value/label array.
    // filter out unique values only
    return Object.keys(SELECTS).map((key) => {
      return SELECTS[key].keywords.map(keyword => {
        return {
          label: keyword,
          value: keyword
        }
      })
    }).flat(1);

  }, [SELECTS])

  useEffect(() => {
    if (!devicesData?.devices.length) return

    const selectedDevice = devicesData.devices.find(d => d.device_id === deviceId)

    setInitialValues({
      deviceName:
        selectedDevice?.device_info?.device_name ||
        selectedDevice?.auto_name ||
        '',
      vendorName: selectedDevice?.device_info?.vendor_name || '',
      tags: parseTags(selectedDevice?.device_info?.tag_list) || [],
    })
  }, [devicesData])

  const handleSubmit = ({ deviceName, vendorName, tags }) => {
    const tagList = JSON.stringify(tags.map((tag) => tag.label))
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
        <div className="h-[600px]">
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
                  placeholder="Device Name"
                  component={TextInput}
                  className="w-full px-4 py-2 bg-gray-100 border-l-4 border-yellow-600 rounded-md"
                  onChange={(value) => setFieldValue('deviceName', value)}
                />
                <Field
                  autoComplete="off"
                  name="vendorName"
                  type="text"
                  label="Vendor"
                  placeholder="Vendor Name"
                  component={TextInput}
                  className="w-full px-4 py-2 bg-gray-100 border-l-4 border-yellow-600 rounded-md"
                  onChange={(value) => setFieldValue('vendorName', value)}
                />
                <Field
                  name="tags"
                  type="text"
                  component={CreateSelect}
                  options={deviceSelects}
                  isMulti
                  placeholder="Add Device Tags"
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
}

export default DeviceDrawer
