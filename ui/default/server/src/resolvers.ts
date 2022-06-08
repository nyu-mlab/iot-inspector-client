import { Context } from './context'

/**
 *
 * @param _parent
 * @param _args
 * @param context
 * @returns Type DeviceByCountry
 */
const deviceTrafficToCountries = async (
  _parent,
  _args: { device_id: string },
  context: Context,
) => {
  const response: any = await context.prisma.flows.groupBy({
    by: ['counterparty_country'],
    _max: { ts: true },
    _sum: { outbound_byte_count: true },
    where: {
      device_id: _args.device_id,
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

export { deviceTrafficToCountries }
