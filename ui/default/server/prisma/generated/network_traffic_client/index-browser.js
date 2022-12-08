
Object.defineProperty(exports, "__esModule", { value: true });

const {
  Decimal,
  objectEnumValues,
  makeStrictEnum
} = require('./runtime/index-browser')


const Prisma = {}

exports.Prisma = Prisma

/**
 * Prisma Client JS version: 4.7.1
 * Query Engine version: 272861e07ab64f234d3ffc4094e32bd61775599c
 */
Prisma.prismaVersion = {
  client: "4.7.1",
  engine: "272861e07ab64f234d3ffc4094e32bd61775599c"
}

Prisma.PrismaClientKnownRequestError = () => {
  throw new Error(`PrismaClientKnownRequestError is unable to be run in the browser.
In case this error is unexpected for you, please report it in https://github.com/prisma/prisma/issues`,
)};
Prisma.PrismaClientUnknownRequestError = () => {
  throw new Error(`PrismaClientUnknownRequestError is unable to be run in the browser.
In case this error is unexpected for you, please report it in https://github.com/prisma/prisma/issues`,
)}
Prisma.PrismaClientRustPanicError = () => {
  throw new Error(`PrismaClientRustPanicError is unable to be run in the browser.
In case this error is unexpected for you, please report it in https://github.com/prisma/prisma/issues`,
)}
Prisma.PrismaClientInitializationError = () => {
  throw new Error(`PrismaClientInitializationError is unable to be run in the browser.
In case this error is unexpected for you, please report it in https://github.com/prisma/prisma/issues`,
)}
Prisma.PrismaClientValidationError = () => {
  throw new Error(`PrismaClientValidationError is unable to be run in the browser.
In case this error is unexpected for you, please report it in https://github.com/prisma/prisma/issues`,
)}
Prisma.NotFoundError = () => {
  throw new Error(`NotFoundError is unable to be run in the browser.
In case this error is unexpected for you, please report it in https://github.com/prisma/prisma/issues`,
)}
Prisma.Decimal = Decimal

/**
 * Re-export of sql-template-tag
 */
Prisma.sql = () => {
  throw new Error(`sqltag is unable to be run in the browser.
In case this error is unexpected for you, please report it in https://github.com/prisma/prisma/issues`,
)}
Prisma.empty = () => {
  throw new Error(`empty is unable to be run in the browser.
In case this error is unexpected for you, please report it in https://github.com/prisma/prisma/issues`,
)}
Prisma.join = () => {
  throw new Error(`join is unable to be run in the browser.
In case this error is unexpected for you, please report it in https://github.com/prisma/prisma/issues`,
)}
Prisma.raw = () => {
  throw new Error(`raw is unable to be run in the browser.
In case this error is unexpected for you, please report it in https://github.com/prisma/prisma/issues`,
)}
Prisma.validator = () => (val) => val


/**
 * Shorthand utilities for JSON filtering
 */
Prisma.DbNull = objectEnumValues.instances.DbNull
Prisma.JsonNull = objectEnumValues.instances.JsonNull
Prisma.AnyNull = objectEnumValues.instances.AnyNull

Prisma.NullTypes = {
  DbNull: objectEnumValues.classes.DbNull,
  JsonNull: objectEnumValues.classes.JsonNull,
  AnyNull: objectEnumValues.classes.AnyNull
}

/**
 * Enums
 */
// Based on
// https://github.com/microsoft/TypeScript/issues/3192#issuecomment-261720275
function makeEnum(x) { return x; }

exports.Prisma.CounterpartiesScalarFieldEnum = makeEnum({
  id: 'id',
  remote_ip: 'remote_ip',
  hostname: 'hostname',
  device_id: 'device_id',
  source: 'source',
  resolver_ip: 'resolver_ip',
  ts: 'ts'
});

exports.Prisma.DevicesScalarFieldEnum = makeEnum({
  device_id: 'device_id',
  ip: 'ip',
  mac: 'mac',
  dhcp_hostname_list: 'dhcp_hostname_list',
  netdisco_list: 'netdisco_list',
  user_agent_list: 'user_agent_list',
  syn_scan_port_list: 'syn_scan_port_list',
  auto_name: 'auto_name',
  last_updated_ts: 'last_updated_ts'
});

exports.Prisma.FlowsScalarFieldEnum = makeEnum({
  id: 'id',
  device_id: 'device_id',
  device_port: 'device_port',
  counterparty_ip: 'counterparty_ip',
  counterparty_port: 'counterparty_port',
  counterparty_hostname: 'counterparty_hostname',
  counterparty_friendly_name: 'counterparty_friendly_name',
  counterparty_country: 'counterparty_country',
  counterparty_is_ad_tracking: 'counterparty_is_ad_tracking',
  counterparty_local_device_id: 'counterparty_local_device_id',
  transport_layer_protocol: 'transport_layer_protocol',
  uses_weak_encryption: 'uses_weak_encryption',
  ts: 'ts',
  ts_mod_60: 'ts_mod_60',
  ts_mod_600: 'ts_mod_600',
  ts_mod_3600: 'ts_mod_3600',
  window_size: 'window_size',
  inbound_byte_count: 'inbound_byte_count',
  outbound_byte_count: 'outbound_byte_count',
  inbound_packet_count: 'inbound_packet_count',
  outbound_packet_count: 'outbound_packet_count'
});

exports.Prisma.SortOrder = makeEnum({
  asc: 'asc',
  desc: 'desc'
});

exports.Prisma.TransactionIsolationLevel = makeStrictEnum({
  Serializable: 'Serializable'
});


exports.Prisma.ModelName = makeEnum({
  counterparties: 'counterparties',
  devices: 'devices',
  flows: 'flows'
});

/**
 * Create the Client
 */
class PrismaClient {
  constructor() {
    throw new Error(
      `PrismaClient is unable to be run in the browser.
In case this error is unexpected for you, please report it in https://github.com/prisma/prisma/issues`,
    )
  }
}
exports.PrismaClient = PrismaClient

Object.assign(exports, Prisma)
