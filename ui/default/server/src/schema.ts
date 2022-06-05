import { gql } from 'apollo-server'
import { Context } from './context'

export const typeDefs = gql`
  type Device {
    id: ID
    device_id: String!
    ip: String!
    mac: String!
    dhcp_hostname_list: String!
    netdisco_list: String!
    user_agent_list: String!
    syn_scan_port_list: String!
    auto_name: String!
    last_updated_ts: Int!
    flows: [Flow]
  }

  type Flow {
    id: ID
    device: Device
    device_id: ID!
    device_port: Int!
    counterparty_ip: String!
    counterparty_port: Int!
    counterparty_hostname: String!
    counterparty_friendly_name: String!
    counterparty_country: String!
    counterparty_is_ad_tracking: Int!
    counterparty_local_device_id: ID!
    transport_layer_protocol: String!
    uses_weak_encryption: Int!
    ts: Float!
    ts_mod_60: Float!
    ts_mod_600: Float!
    ts_mod_3600: Float!
    window_size: Float!
    inbound_byte_count: Int!
    outbound_byte_count: Int!
    inbound_packet_count: Int!
    outbound_packet_count: Int!
    _sum: Int
  }

  type Query {
    device(device_id: String): Device
    devices: [Device!]!
    flows: [Flow!]!
    # deviceUsageBytes(current_time: Int): Flow
    adsAndTrackerBytes(current_time: Int): Flow
    unencryptedHttpTrafficBytes(current_time: Int): Flow
    weakEncryptionBytes(current_time: Int): Flow
  }
`

export const resolvers = {
  Query: {
    device: (_parent, args: { device_id: string }, context: Context) => {
      return context.prisma.devices.findUnique({
        where: { device_id: args.device_id || undefined },
      })
    },
    devices: (_parent, _args, context: Context) => {
      return context.prisma.devices.findMany()
    },
    flows: (_parent, _args, context: Context) => {
      return context.prisma.flows.findMany()
    },
    adsAndTrackerBytes: async (
      _parent,
      args: { current_time: number },
      context: Context,
    ) => {
      const flowsResult = await context.prisma.flows.aggregate({
        where: {
          counterparty_is_ad_tracking: 1,
          ts: { gte: (args.current_time || 1654111436) - 3600.0 * 24.0 },
        },
        _sum: {
          outbound_byte_count: true
        }
      })
      return { _sum: flowsResult._sum.outbound_byte_count }
    },
    unencryptedHttpTrafficBytes: async (
      _parent,
      args: { current_time: number },
      context: Context,
    ) => {
      const flowsResult = await context.prisma.flows.aggregate({
        where: {
          counterparty_port: 80,
          ts: { gte: (args.current_time || 1654111436) - 3600.0 * 24.0 },
        },
        _sum: {
          outbound_byte_count: true
        }
      })
      return { _sum: flowsResult._sum.outbound_byte_count }
    },
    weakEncryptionBytes: async (
      _parent,
      args: { current_time: number },
      context: Context,
    ) => {
      const flowsResult = await context.prisma.flows.aggregate({
        where: {
          counterparty_port: 80,
          ts: { gte: (args.current_time || 1654111436) - 3600.0 * 24.0 },
        },
        _sum: {
          outbound_byte_count: true
        }
      })
      return { _sum: flowsResult._sum.outbound_byte_count }
    },
  },
}
