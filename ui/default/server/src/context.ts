import { PrismaClient as NetworkTrafficClient } from '../prisma/generated/network_traffic_client'
import { PrismaClient as ConfigsClient } from '../prisma/generated/configs_client'

const networkTrafficPrismaClient = new NetworkTrafficClient()
const configsPrismaClient = new ConfigsClient()

export interface Context {
  NetworkTrafficClient: NetworkTrafficClient,
  ConfigsClient: ConfigsClient
}

export const context: Context = {
  NetworkTrafficClient: networkTrafficPrismaClient,
  ConfigsClient: configsPrismaClient
}
