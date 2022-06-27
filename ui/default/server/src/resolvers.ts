import { Context } from './context'

// const SERVER_START_TIME = Math.round(new Date().getTime() / 1000)
const SERVER_START_TIME = Math.round(
  new Date('June 26, 2022 06:24:00').getTime() / 1000,
)


const getDeviceById = async (deviceId: string, context: Context) => {
  const device = await context.NetworkTrafficClient.devices.findUnique({
    where: {
      device_id: deviceId
    },
  })

  return device
}

const getDeviceInfoById = async (deviceId: string, context: Context) => {
  const deviceInfo = await context.ConfigsClient.device_info.findUnique({
    where: {
      device_id: deviceId
    },
  })

  return deviceInfo
}

/**
 * Maps DeviceInfo to a Device
 * 
 * @param deviceId 
 * @param context 
 * @return Device with DeviceInfo
 */
const getDeviceInfoForDevice = async (deviceId: string, context: Context) => {
  const device = await getDeviceById(deviceId, context)
  const deviceInfo = await getDeviceInfoById(deviceId, context)

  return {
    ...device,
    device_info: deviceInfo
  }
}

/**
 *
 * @param _parent
 * @param args
 * @param context
 * @returns Array Type Devices
 */
const devices = async (_parent, args, context: Context) => {
  const devicesResult = await context.NetworkTrafficClient.flows.groupBy({
    by: ['device_id'],
    _sum: {
      outbound_byte_count: true,
    },
  })
  // map the devices to the flow device_id
  let devices = await Promise.all(
    devicesResult.map(async (flow) => {
      const mappedDevice = await getDeviceInfoForDevice(flow.device_id, context)
      return {
        ...mappedDevice,
        outbound_byte_count: flow._sum.outbound_byte_count,
      }
    }),
  )

  return devices
}

/**
 *
 * @param _parent
 * @param args
 * @param context
 * @returns Array Type Flow
 */
const flows = async (
  _parent,
  args: { current_time: number; device_id: string },
  context: Context,
) => {
  const flows = await context.NetworkTrafficClient.flows.findMany({
    where: {
      ts: { gte: args.current_time || SERVER_START_TIME },
      device_id: args.device_id || undefined,
    }
  })

  // TODO:
  //  - This is really slow... perhaps we should map on client side?

  // map device to flows
  // let devices = await Promise.all(
  //   flows.map(async (flow) => {
  //     const mappedDevice = await getDeviceInfoForDevice(flow.device_id, context)
  //     return {
  //       ...flow,
  //       device: mappedDevice
  //     }
  //   }),
  // )

  return flows

}

/**
 *
 * @param _parent
 * @returns Type ServerConfig
 */
const serverConfig = (_parent) => {
  return {
    start_timestamp: SERVER_START_TIME,
  }
}

/**
 * Show how much data is uploaded to each counterparty
 *
 * @param _parent
 * @param args
 * @param context
 * @returns Type Array Flow
 */
const dataUploadedToCounterParty = async (
  _parent,
  args: { current_time: number },
  context: Context,
) => {
  const response: any = await context.NetworkTrafficClient.flows.groupBy({
    by: [
      'device_id',
      'counterparty_friendly_name',
      'counterparty_country',
      'counterparty_hostname',
    ],
    _sum: { outbound_byte_count: true },
    _max: { ts: true },
    where: {
      ts: { gte: args.current_time || SERVER_START_TIME },
    },
  })

  const devices = await Promise.all(
    response.map(async (flow) => {
      const device = await context.NetworkTrafficClient.devices.findUnique({
        where: {
          device_id: flow.device_id,
        },
      })

      return {
        device: device,
        device_id: flow.device_id,
        counterparty_friendly_name: flow.counterparty_friendly_name,
        counterparty_hostname: flow.counterparty_hostname,
        country_code: flow.counterparty_country,
        outbound_byte_count: flow._sum.outbound_byte_count,
        last_updated_time_per_country: flow._max.ts,
      }
    }),
  )

  return devices
}


/**
 * 
 * @param _parent 
 * @param args 
 * @param context 
 * @returns Network Activity In Bytes
 */
const networkActivity = async (
  _parent,
  args: { current_time: number },
  context: Context,
) => {
  const weakEncryption = await context.NetworkTrafficClient.flows.aggregate({
    where: {
      uses_weak_encryption: 1,
      ts: { gte: args.current_time || SERVER_START_TIME },
    },
    _sum: {
      outbound_byte_count: true,
    },
  })

  const unencryptedHttpTraffic = await context.NetworkTrafficClient.flows.aggregate({
    where: {
      counterparty_port: 80,
      ts: { gte: args.current_time || SERVER_START_TIME },
    },
    _sum: {
      outbound_byte_count: true,
    },
  })

  const adsAndTracker = await context.NetworkTrafficClient.flows.aggregate({
    where: {
      counterparty_is_ad_tracking: 1,
      ts: { gte: args.current_time || SERVER_START_TIME },
    },
    _sum: {
      outbound_byte_count: true,
    },
  })

  return {
    weak_encryption: weakEncryption._sum.outbound_byte_count,
    unencrypted_http_traffic: unencryptedHttpTraffic._sum.outbound_byte_count,
    ads_and_trackers: adsAndTracker._sum.outbound_byte_count,
  }
}

/**
 * 
 * @param _parent 
 * @param args 
 * @param context 
 * @returns Counter Party Host Names
 */
const communicationEndpointNames = async (
  _parent,
  args: { device_id: string },
  context: Context,
) => {
  const response: any = await context.NetworkTrafficClient.flows.groupBy({
    by: ['counterparty_hostname'],
    where: {
      ts: { gte: SERVER_START_TIME },
      device_id: args.device_id || undefined,
      counterparty_hostname: { not: '' },
    },
  })
  return response
}

/**
 * Adds a Device Info
 * 
 * @param _parent 
 * @param args 
 * @param context 
 * @returns 
 */
 const addDeviceInfo = async (
  _parent,
  args: {
    device_id: string,
    device_name: string
    vendor_name: string,
    tag_list: string,
    is_inspected: number,
    is_blocked: number
  },
  context: Context,
) => {
  const updatedDeviceInfo = await context.ConfigsClient.device_info.update({
    where: {
      device_id: args.device_id
    },
    data: {
      ...args
    }
  })
  console.log(updatedDeviceInfo)
  return updatedDeviceInfo
}

export {
  devices,
  addDeviceInfo,
  flows,
  serverConfig,
  dataUploadedToCounterParty,
  communicationEndpointNames,
  networkActivity
}
