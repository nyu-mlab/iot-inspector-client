import { Context } from './context'
import { add, sub, format } from 'date-fns'

// const SERVER_START_TIME = Math.round(new Date().getTime() / 1000)
const SERVER_START_TIME = Math.round(
  new Date('June 29, 2022 10:00:00').getTime() / 1000,
)

enum TimeType {
  ts = 'ts',
  ts_mod_60 = 'ts_mod_60',
  ts_mod_600 = 'ts_mod_600',
  ts_mod_3600 = 'ts_mod_3600',
}

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

const unixTime = (date) => {
  return Math.round(date.getTime() / 1000)
}

const groupBy = function (array, key) {
  return array.reduce(function (rv, x) {
    ;(rv[x[key]] = rv[x[key]] || []).push(x)
    return rv
  }, {})
}

const generateFlowXYChartData = async (
  timeType: TimeType,
  time: Date,
  context: Context,
  timeSort: any='lt',
  totalAmount: number=-6,
  device_id?: String,
) => {
  const params: any = {
    by: ['device_id', timeType],
    where: {
      device_id: device_id || undefined,
      [timeType]: { [timeSort]: unixTime(time) },
    },
    _sum: {
      outbound_byte_count: true,
    },
  }

  let data = await context.NetworkTrafficClient.flows.groupBy(params)

  const xAxis: any = data
    .map((item) => format(item[timeType] * 1000, 'yyyy-MM-dd HH:mm:ss'))
    .filter((value, index, self) => self.indexOf(value) === index)
    .slice(totalAmount)

    
  let yAxis = groupBy(data, 'device_id')
  yAxis = Object.keys(yAxis).map((key) => {
    return {
      name: key,
      data: yAxis[key].map((flow) => {
        return flow._sum.outbound_byte_count
      }).slice(totalAmount)
    }
  })

  return {
    xAxis,
    yAxis,
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

// Server star time at 0 (server just started)
// client time < +60 minutes
//  get data by minute
// client time > +60 minutes
//  get data by 10 minutes (taking the last 6, which is the last hour)
// client time > +6 hours (server time)
//  get data by hour (taking the last 6, which is the last 6 hours)
const chartActivity = async (
  _parent,
  args: { device_id: string },
  context: Context,
) => {
  const currentTime = new Date()

  const serverDatePlus1Hour = add(new Date(SERVER_START_TIME * 1000), {
    hours: 1,
  })
  const serverDatePlus6Hours = add(new Date(SERVER_START_TIME * 1000), {
    hours: 6,
  })

  console.log(`server time: ${new Date(SERVER_START_TIME * 1000)}`)
  console.log(`client time: ${currentTime}`)
  console.log(`server time +1 hour: ${serverDatePlus1Hour}`)
  console.log(`server time +6 hours: ${serverDatePlus6Hours}`)
  console.log('-----------------------')

  let data: any = {}
  // get by hour
  // should expect 6 results
  if (currentTime >= serverDatePlus6Hours) {
    console.log('get data by ts_mod_3600 (1 hour)')
    data = await generateFlowXYChartData(
      TimeType.ts_mod_3600,
      currentTime,
      context,
    )

    return data
  }

  // get by 10 minute
  // should expect 6 results
  if (currentTime >= serverDatePlus1Hour) {
    console.log('get data by ts_mod_600 (10 minutes)')
    data = await generateFlowXYChartData(
      TimeType.ts_mod_600,
      currentTime,
      context,
    )

    return data
  }

  // get by minute
  // should expect 6 results
  console.log('get data by ts_mod_60 (1 minute)')
  data = await generateFlowXYChartData(
    TimeType.ts_mod_60,
    currentTime,
    context,
  )

  return data
}

const chartActivityBySecond = async (
  _parent,
  args: { current_time: number; device_id: string },
  context: Context,
) => {
  console.log(args.current_time)
  const currentTimeSub1Hour = sub(new Date(), {
    minutes: 1,
  })
  console.log(currentTimeSub1Hour)
  const data = await generateFlowXYChartData(
    TimeType.ts,
    currentTimeSub1Hour,
    context,
    'gt',
    -20,
    args.device_id,
  )

  console.log(data)

  return data
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
  chartActivityBySecond,
}
