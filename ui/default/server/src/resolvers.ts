import { Context } from './context'

// const SERVER_START_TIME = Math.round(new Date().getTime() / 1000)
const SERVER_START_TIME = Math.round(new Date('June 10, 2022 06:24:00').getTime() / 1000)

/**
 *
 * @param _parent
 * @param args
 * @param context
 * @returns Type Device
 */
const device = (_parent, args: { device_id: string }, context: Context) => {
  return context.prisma.devices.findUnique({
    where: { device_id: args.device_id || undefined },
  })
}

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
      device_id:  args.device_id || undefined
    },
    include: {
      device: true
    }
  })
}

/**
 *
 * @param _parent
 * @param args
 * @param context
 * @returns Type ServerConfig
 */
const serverConfig = (_parent, args, context: Context) => {
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
    by: ['device_id', 'counterparty_friendly_name', 'counterparty_country'],
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
 * @returns Type DeviceByCountry
 */
const deviceTrafficToCountries = async (
  _parent,
  args: { device_id: string },
  context: Context,
) => {
  const response: any = await context.prisma.flows.groupBy({
    by: ['counterparty_country'],
    _max: { ts: true },
    _sum: { outbound_byte_count: true },
    where: {
      device_id: args.device_id,
    },
  })

  const data = response.map((d) => {
    return {
      country_code: d.counterparty_country,
      outbound_byte_count: d._sum.outbound_byte_count,
      last_updated_time_per_country: d._max.ts,
    }
  })

  return data
}

/**
 *
 * @param _parent
 * @param args
 * @param context
 * @returns Type Flow
 */
const adsAndTrackerBytes = async (
  _parent,
  args: { current_time: number },
  context: Context,
) => {
  const flowsResult = await context.prisma.flows.aggregate({
    where: {
      counterparty_is_ad_tracking: 1,
      ts: { gte: args.current_time || SERVER_START_TIME },
    },
    _sum: {
      outbound_byte_count: true,
    },
  })
  return { _sum: flowsResult._sum.outbound_byte_count }
}

/**
 *
 * @param _parent
 * @param args
 * @param context
 * @returns Type Flow
 */
const unencryptedHttpTrafficBytes = async (
  _parent,
  args: { current_time: number },
  context: Context,
) => {
  const flowsResult = await context.prisma.flows.aggregate({
    where: {
      counterparty_port: 80,
      ts: { gte: args.current_time || SERVER_START_TIME },
    },
    _sum: {
      outbound_byte_count: true,
    },
  })
  return { _sum: flowsResult._sum.outbound_byte_count }
}

/**
 *
 * @param _parent
 * @param args
 * @param context
 * @returns Type Flow
 */
const weakEncryptionBytes = async (
  _parent,
  args: { current_time: number },
  context: Context,
) => {
  const flowsResult = await context.prisma.flows.aggregate({
    where: {
      counterparty_port: 80,
      ts: { gte: args.current_time || SERVER_START_TIME },
    },
    _sum: {
      outbound_byte_count: true,
    },
  })
  return { _sum: flowsResult._sum.outbound_byte_count }
}

// const communicationEndpointNames = (
//   _parent,
//   args: { device_id: string },
//   context: Context,
// ) => {
//   return context.prisma.flows.findMany({
//     where: {
//       ts: { gte: SERVER_START_TIME },
//       device_id:  args.device_id || undefined
//     },
//   })
// }

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
      counterparty_hostname: { not:"" }
    },
  })
  return response
}

export {
  device,
  devices,
  flows,
  serverConfig,
  deviceTrafficToCountries,
  adsAndTrackerBytes,
  unencryptedHttpTrafficBytes,
  weakEncryptionBytes,
  dataUploadedToCounterParty,
  communicationEndpointNames
}
