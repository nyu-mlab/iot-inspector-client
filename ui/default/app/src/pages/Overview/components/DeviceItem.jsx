import React, { useState, useEffect } from 'react'
import PropTypes from 'prop-types'
import { dataUseage } from '@utils/utils'
import SELECTS from '@constants/selects'

const DeviceItem = ({ device }) => {
  const [deviceImage, setDeviceImage] = useState(
    'https://via.placeholder.com/150'
  )
  const [tags, setTags] = useState([])

  useEffect(() => {
    const tagList = JSON.parse(device.device_info.tag_list)
    setTags(tagList)

    for (const select in SELECTS) {
      if (SELECTS[select].keywords.some((r) => tagList.includes(r))) {
        setDeviceImage(SELECTS[select].image)
      }
    }
  }, [device.device_info.tag_list])

  return (
    // device item classes based on filled in details -- status-empty / status-inprogress / status-complete
    <div className='device-item status-empty'>
      <div className='device-info'>
        <img
          src={deviceImage}
          alt={device ? device.auto_name : 'Unknown Device'}
          className='hidden w-auto h-12 lg:block md:h-16'
        />
        <div className='px-4'>
          <h3>
            {device?.device_info?.device_name ||
              device?.auto_name ||
              'Unknown Device'}
          </h3>
          <p className='text-xs'>
            {device && device.ip}
            <br />
            {device && device.mac}
          </p>
        </div>
      </div>

      <div className='device-tags'>
        {tags.map((tag) => (
          <div className='tag' key={tag}>
            {tag}
          </div>
        ))}
      </div>
      <div className='device-details'>
        {device && (
          <div className='flex items-center justify-center px-4 text-sm border-r border-gray-300 w-fit'>
            {dataUseage(device.outbound_byte_count)}
          </div>
        )}
        <div className='flex items-center justify-center px-4 text-sm w-fit'>
          <a
            href={`/device-activity?deviceid=${device.device_id}`}
            className=''
          >
            Details
          </a>
        </div>
      </div>
    </div>
  )
}

DeviceItem.propTypes = {
  tags: PropTypes.array
}

export default DeviceItem
