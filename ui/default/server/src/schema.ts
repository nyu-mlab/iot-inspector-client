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
  }

  type Query {
    device(device_id: String): Device
    devices: [Device!]!
  }
`

export const resolvers = {
  Query: {
    device: (_parent, args: { device_id: string }, context: Context) => {
      return context.prisma.device.findUnique({
        where: { device_id: args.device_id || undefined },
      })
    },
    devices: (_parent, _args, context: Context) => {
      return context.prisma.device.findMany()
    },
  },
}
