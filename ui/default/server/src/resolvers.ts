import { Context } from './context'

// const SERVER_START_TIME = Math.round(new Date().getTime() / 1000)
const SERVER_START_TIME = Math.round(
  new Date('June 18, 2022 06:24:00').getTime() / 1000,
)

/**
 *
 * @param _parent
 * @param args
 * @param context
 * @returns Array Type Devices
 */
const devices = async (_parent, args, context: Context) => {
  const devicesResult = await context.prisma.flows.groupBy({
    by: ['device_id'],
    _sum: {
      outbound_byte_count: true,
    },
  })
  // map the devices to the flow device_id
  let devices = await Promise.all(
    devicesResult.map(async (flow) => {
      const mappedDevices = await context.prisma.devices.findUnique({
        where: {
          device_id: flow.device_id,
        },
      })
      return {
        ...mappedDevices,
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
const flows = (
  _parent,
  args: { current_time: number; device_id: string },
  context: Context,
) => {
  return context.prisma.flows.findMany({
    where: {
      ts: { gte: args.current_time || SERVER_START_TIME },
      device_id: args.device_id || undefined,
    },
    include: {
      device: true,
    },
  })
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
  const response: any = await context.prisma.flows.groupBy({
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
      const device = await context.prisma.devices.findUnique({
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
  const weakEncryption = await context.prisma.flows.aggregate({
    where: {
      uses_weak_encryption: 1,
      ts: { gte: args.current_time || SERVER_START_TIME },
    },
    _sum: {
      outbound_byte_count: true,
    },
  })

  const unencryptedHttpTraffic = await context.prisma.flows.aggregate({
    where: {
      counterparty_port: 80,
      ts: { gte: args.current_time || SERVER_START_TIME },
    },
    _sum: {
      outbound_byte_count: true,
    },
  })

  const adsAndTracker = await context.prisma.flows.aggregate({
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
  const response: any = await context.prisma.flows.groupBy({
    by: ['counterparty_hostname'],
    where: {
      ts: { gte: SERVER_START_TIME },
      device_id: args.device_id || undefined,
      counterparty_hostname: { not: '' },
    },
  })
  return response
}

export {
  devices,
  flows,
  serverConfig,
  dataUploadedToCounterParty,
  communicationEndpointNames,
  networkActivity
}
