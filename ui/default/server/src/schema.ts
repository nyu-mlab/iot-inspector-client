import { gql } from 'apollo-server'
import {
  devices,
  flows,
  serverConfig,
  dataUploadedToCounterParty,
  communicationEndpointNames,
  networkActivity,
  chartActivity,
  chartActivityBySecond,
  addDeviceInfo,
  userConfigs,
  updateUserConfigs
} from './resolvers'

export const typeDefs = gql`
  type ServerConfig {
    start_timestamp: Int
  }

  type DeviceByCountry {
    device_id: String
    counterparty_friendly_name: String
    counterparty_hostname: String
    country_code: String!
    outbound_byte_count: Int!
    last_updated_time_per_country: Float!
    device: Device
  }

  type NetworkActivity {
    weak_encryption: Int
    unencrypted_http_traffic: Int
    ads_and_trackers: Int
  }

  type CommunicationEndpointName {
    counterparty_hostname: String
  }

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
    last_updated_ts: Float!
    outbound_byte_count: Int # Included from the Flow Type
    flows: [Flow]
    device_info: DeviceInfo
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
    ts_mod_60: Float! # every 1 minute
    ts_mod_600: Float! # every 10 minutes
    ts_mod_3600: Float! # Every 1 hour
    window_size: Float!
    inbound_byte_count: Int!
    outbound_byte_count: Int!
    inbound_packet_count: Int!
    outbound_packet_count: Int!
  }

  type ChartActivityXAxis {
    name: String!
    data: [String]!
  }
  type ChartActivity {
    xAxis: [String]!
    yAxis: [ChartActivityXAxis]!
  }

  type DeviceInfo {
    device_id: String!
    device_name: String
    vendor_name: String
    tag_list: String
    is_inspected: Int
    is_blocked: Int
  }

  type UserConfigs {
    can_contribute_to_research: Int!
    can_auto_inspect_device: Int!
    is_consent: Int!
  }

  type Query {
    devices(device_id: String): [Device!]!
    flows(current_time: Int, device_id: String):  [Flow!]!
    chartActivity(device_id: String): ChartActivity!
    chartActivityBySecond(current_time: Int, device_id: String!): ChartActivity!
    dataUploadedToCounterParty(current_time: Int): [DeviceByCountry]
    communicationEndpointNames(device_id: String): [CommunicationEndpointName]!
    networkActivity(current_time: Int): NetworkActivity
    serverConfig: ServerConfig
    userConfigs: UserConfigs
  }

  type Mutation {
    addDeviceInfo(
      device_id: String!
      device_name: String
      vendor_name: String
      tag_list: String
      is_inspected: Int
      is_blocked: Int
    ): DeviceInfo
    updateUserConfigs(
      is_consent: Int
      can_auto_inspect_device: Int
      can_contribute_to_research: Int
    ): UserConfigs
  }
`

export const resolvers = {
  Query: {
    devices,
    flows,
    serverConfig,
    networkActivity,
    dataUploadedToCounterParty,
    communicationEndpointNames,
    chartActivity,
    chartActivityBySecond,
    userConfigs
  },
  Mutation: {
    addDeviceInfo,
    updateUserConfigs
  },
}
