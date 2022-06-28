import { Context } from './context'
import { add, format } from 'date-fns'

// const SERVER_START_TIME = Math.round(new Date().getTime() / 1000)
const SERVER_START_TIME = Math.round(
  new Date('June 27, 2022 10:50:00').getTime() / 1000,
)

const getDeviceById = async (deviceId: string, context: Context) => {
  const device = await context.NetworkTrafficClient.devices.findUnique({
    where: {
      device_id: deviceId,
    },
  })

  return device
}

const getDeviceInfoById = async (deviceId: string, context: Context) => {
  const deviceInfo = await context.ConfigsClient.device_info.findUnique({
    where: {
      device_id: deviceId,
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
  const device_info = await getDeviceInfoById(deviceId, context)

  return {
    ...device,
    device_info,
  }
}

/**
 *
 * @param _parent
 * @param args
 * @param context
 * @returns Array Type Devices
 */
const devices = async (
  _parent,
  args: { device_id: string },
  context: Context,
) => {
  const devicesResult = await context.NetworkTrafficClient.flows.groupBy({
    by: ['device_id'],
    _sum: {
      outbound_byte_count: true,
    },
  })
  // map the devices to the flow device_id
  let devices = await Promise.all(
    devicesResult.map(async (flow) => {
      const deviceId = args.device_id || flow.device_id
      const mappedDevice = await getDeviceInfoForDevice(deviceId, context)
      return {
        ...mappedDevice,
        outbound_byte_count: flow._sum.outbound_byte_count,
      }
    }),
  )

  if (args.device_id) {
    return [devices[0]]
  }

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
    },
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

const unixTime = (date) => {
  return Math.round(date.getTime() / 1000)
}

const groupBy = function (array, key) {
  return array.reduce(function (rv, x) {
    ;(rv[x[key]] = rv[x[key]] || []).push(x)
    return rv
  }, {})
}

const chartActivity = async (
  _parent,
  args: { current_time: number; device_id: string },
  context: Context,
) => {
  const currentTime = new Date(args.current_time * 1000)
  const datePlus1Hour = add(new Date(SERVER_START_TIME * 1000), { hours: 1 })
  const datePlus6Hours = add(new Date(SERVER_START_TIME * 1000), { hours: 6 })

  console.log(currentTime, ' - ', datePlus1Hour)

  let flows: any = []
  // get by hour
  // should expect 6 results
  if (currentTime > datePlus6Hours) {
    console.log('get data by ts_mod_3600')

    const data = await context.NetworkTrafficClient.flows.groupBy({
      by: ['device_id', 'ts_mod_3600'],
      where: {
        device_id: args.device_id || undefined,
        ts_mod_3600: { gt: unixTime(datePlus6Hours) },
      },
      _sum: {
        outbound_byte_count: true,
      },
    })

    const xAxis = data
      .map((item) => format(item.ts_mod_3600*1000, 'yyyy-MM-dd HH:mm:ss'))
      .filter((value, index, self) => self.indexOf(value) === index)

      console.log(xAxis)

    let yAxis = groupBy(data, 'device_id')
    yAxis = Object.keys(yAxis).map((key, index) => {
      return {
        name: key,
        data: yAxis[key].map((flow) => {
          return flow._sum.outbound_byte_count
        }),
      }
    })

    console.log(yAxis)
    console.log(xAxis)

    // const xAxis = data.map((flow) => {
    //   // return { name: flow.device_id
    //   // data: flow.
    //   // }
    // })

    // const chartData = {
    //   categories: [],
    //   series: [
    //     {name: 'foo', data:[]}
    //   ]
    // }
  }
  // get by minute
  // should expect 6 results
  else if (currentTime < datePlus1Hour) {
    console.log('get data by ts_mod_60')
  }

  // get by 10 minute
  // should expect 6 results
  else if (currentTime > datePlus1Hour) {
    console.log('get data by ts_mod_600')
  }

  // const flows = await context.NetworkTrafficClient.flows.findMany({
  //   where: {
  //     ts: { gte: args.current_time || SERVER_START_TIME },
  //     device_id: args.device_id || undefined,
  //   },
  // })

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
      // const device = await context.NetworkTrafficClient.devices.findUnique({
      //   where: {
      //     device_id: flow.device_id,
      //   },
      // })
      const device = getDeviceInfoForDevice(flow.device_id, context)

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

  const unencryptedHttpTraffic =
    await context.NetworkTrafficClient.flows.aggregate({
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
    device_id: string
    device_name: string
    vendor_name: string
    tag_list: string
    is_inspected: number
    is_blocked: number
  },
  context: Context,
) => {
  const updatedDeviceInfo = await context.ConfigsClient.device_info.update({
    where: {
      device_id: args.device_id,
    },
    data: {
      ...args,
    },
  })

  return updatedDeviceInfo
}

export {
  devices,
  addDeviceInfo,
  flows,
  serverConfig,
  dataUploadedToCounterParty,
  communicationEndpointNames,
  networkActivity,
  chartActivity,
}
