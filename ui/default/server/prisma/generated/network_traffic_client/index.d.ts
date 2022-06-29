
/**
 * Client
**/

import * as runtime from './runtime/index';
declare const prisma: unique symbol
export type PrismaPromise<A> = Promise<A> & {[prisma]: true}
type UnwrapPromise<P extends any> = P extends Promise<infer R> ? R : P
type UnwrapTuple<Tuple extends readonly unknown[]> = {
  [K in keyof Tuple]: K extends `${number}` ? Tuple[K] extends PrismaPromise<infer X> ? X : UnwrapPromise<Tuple[K]> : UnwrapPromise<Tuple[K]>
};


/**
 * Model counterparties
 * 
 */
export type counterparties = {
  id: number
  remote_ip: string
  hostname: string
  device_id: string
  source: string
  resolver_ip: string
  ts: number
}

/**
 * Model devices
 * 
 */
export type devices = {
  device_id: string
  ip: string
  mac: string
  dhcp_hostname_list: string
  netdisco_list: string
  user_agent_list: string
  syn_scan_port_list: string
  auto_name: string
  last_updated_ts: number
}

/**
 * Model flows
 * 
 */
export type flows = {
  id: number
  device_id: string
  device_port: number
  counterparty_ip: string
  counterparty_port: number
  counterparty_hostname: string
  counterparty_friendly_name: string
  counterparty_country: string
  counterparty_is_ad_tracking: number
  counterparty_local_device_id: string
  transport_layer_protocol: string
  uses_weak_encryption: number
  ts: number
  ts_mod_60: number
  ts_mod_600: number
  ts_mod_3600: number
  window_size: number
  inbound_byte_count: number
  outbound_byte_count: number
  inbound_packet_count: number
  outbound_packet_count: number
}


/**
 * ##  Prisma Client ʲˢ
 * 
 * Type-safe database client for TypeScript & Node.js
 * @example
 * ```
 * const prisma = new PrismaClient()
 * // Fetch zero or more Counterparties
 * const counterparties = await prisma.counterparties.findMany()
 * ```
 *
 * 
 * Read more in our [docs](https://www.prisma.io/docs/reference/tools-and-interfaces/prisma-client).
 */
export class PrismaClient<
  T extends Prisma.PrismaClientOptions = Prisma.PrismaClientOptions,
  U = 'log' extends keyof T ? T['log'] extends Array<Prisma.LogLevel | Prisma.LogDefinition> ? Prisma.GetEvents<T['log']> : never : never,
  GlobalReject = 'rejectOnNotFound' extends keyof T
    ? T['rejectOnNotFound']
    : false
      > {
      /**
       * @private
       */
      private fetcher;
      /**
       * @private
       */
      private readonly dmmf;
      /**
       * @private
       */
      private connectionPromise?;
      /**
       * @private
       */
      private disconnectionPromise?;
      /**
       * @private
       */
      private readonly engineConfig;
      /**
       * @private
       */
      private readonly measurePerformance;

    /**
   * ##  Prisma Client ʲˢ
   * 
   * Type-safe database client for TypeScript & Node.js
   * @example
   * ```
   * const prisma = new PrismaClient()
   * // Fetch zero or more Counterparties
   * const counterparties = await prisma.counterparties.findMany()
   * ```
   *
   * 
   * Read more in our [docs](https://www.prisma.io/docs/reference/tools-and-interfaces/prisma-client).
   */

  constructor(optionsArg ?: Prisma.Subset<T, Prisma.PrismaClientOptions>);
  $on<V extends (U | 'beforeExit')>(eventType: V, callback: (event: V extends 'query' ? Prisma.QueryEvent : V extends 'beforeExit' ? () => Promise<void> : Prisma.LogEvent) => void): void;

  /**
   * Connect with the database
   */
  $connect(): Promise<void>;

  /**
   * Disconnect from the database
   */
  $disconnect(): Promise<void>;

  /**
   * Add a middleware
   */
  $use(cb: Prisma.Middleware): void

/**
   * Executes a prepared raw query and returns the number of affected rows.
   * @example
   * ```
   * const result = await prisma.$executeRaw`UPDATE User SET cool = ${true} WHERE email = ${'user@email.com'};`
   * ```
   * 
   * Read more in our [docs](https://www.prisma.io/docs/reference/tools-and-interfaces/prisma-client/raw-database-access).
   */
  $executeRaw<T = unknown>(query: TemplateStringsArray | Prisma.Sql, ...values: any[]): PrismaPromise<number>;

  /**
   * Executes a raw query and returns the number of affected rows.
   * Susceptible to SQL injections, see documentation.
   * @example
   * ```
   * const result = await prisma.$executeRawUnsafe('UPDATE User SET cool = $1 WHERE email = $2 ;', true, 'user@email.com')
   * ```
   * 
   * Read more in our [docs](https://www.prisma.io/docs/reference/tools-and-interfaces/prisma-client/raw-database-access).
   */
  $executeRawUnsafe<T = unknown>(query: string, ...values: any[]): PrismaPromise<number>;

  /**
   * Performs a prepared raw query and returns the `SELECT` data.
   * @example
   * ```
   * const result = await prisma.$queryRaw`SELECT * FROM User WHERE id = ${1} OR email = ${'user@email.com'};`
   * ```
   * 
   * Read more in our [docs](https://www.prisma.io/docs/reference/tools-and-interfaces/prisma-client/raw-database-access).
   */
  $queryRaw<T = unknown>(query: TemplateStringsArray | Prisma.Sql, ...values: any[]): PrismaPromise<T>;

  /**
   * Performs a raw query and returns the `SELECT` data.
   * Susceptible to SQL injections, see documentation.
   * @example
   * ```
   * const result = await prisma.$queryRawUnsafe('SELECT * FROM User WHERE id = $1 OR email = $2;', 1, 'user@email.com')
   * ```
   * 
   * Read more in our [docs](https://www.prisma.io/docs/reference/tools-and-interfaces/prisma-client/raw-database-access).
   */
  $queryRawUnsafe<T = unknown>(query: string, ...values: any[]): PrismaPromise<T>;

  /**
   * Allows the running of a sequence of read/write operations that are guaranteed to either succeed or fail as a whole.
   * @example
   * ```
   * const [george, bob, alice] = await prisma.$transaction([
   *   prisma.user.create({ data: { name: 'George' } }),
   *   prisma.user.create({ data: { name: 'Bob' } }),
   *   prisma.user.create({ data: { name: 'Alice' } }),
   * ])
   * ```
   * 
   * Read more in our [docs](https://www.prisma.io/docs/concepts/components/prisma-client/transactions).
   */
  $transaction<P extends PrismaPromise<any>[]>(arg: [...P]): Promise<UnwrapTuple<P>>;

      /**
   * `prisma.counterparties`: Exposes CRUD operations for the **counterparties** model.
    * Example usage:
    * ```ts
    * // Fetch zero or more Counterparties
    * const counterparties = await prisma.counterparties.findMany()
    * ```
    */
  get counterparties(): Prisma.counterpartiesDelegate<GlobalReject>;

  /**
   * `prisma.devices`: Exposes CRUD operations for the **devices** model.
    * Example usage:
    * ```ts
    * // Fetch zero or more Devices
    * const devices = await prisma.devices.findMany()
    * ```
    */
  get devices(): Prisma.devicesDelegate<GlobalReject>;

  /**
   * `prisma.flows`: Exposes CRUD operations for the **flows** model.
    * Example usage:
    * ```ts
    * // Fetch zero or more Flows
    * const flows = await prisma.flows.findMany()
    * ```
    */
  get flows(): Prisma.flowsDelegate<GlobalReject>;
}

export namespace Prisma {
  export import DMMF = runtime.DMMF

  /**
   * Prisma Errors
   */
  export import PrismaClientKnownRequestError = runtime.PrismaClientKnownRequestError
  export import PrismaClientUnknownRequestError = runtime.PrismaClientUnknownRequestError
  export import PrismaClientRustPanicError = runtime.PrismaClientRustPanicError
  export import PrismaClientInitializationError = runtime.PrismaClientInitializationError
  export import PrismaClientValidationError = runtime.PrismaClientValidationError

  /**
   * Re-export of sql-template-tag
   */
  export import sql = runtime.sqltag
  export import empty = runtime.empty
  export import join = runtime.join
  export import raw = runtime.raw
  export import Sql = runtime.Sql

  /**
   * Decimal.js
   */
  export import Decimal = runtime.Decimal

  /**
   * Prisma Client JS version: 3.14.0
   * Query Engine version: 461d6a05159055555eb7dfb337c9fb271cbd4d7e
   */
  export type PrismaVersion = {
    client: string
  }

  export const prismaVersion: PrismaVersion 

  /**
   * Utility Types
   */

  /**
   * From https://github.com/sindresorhus/type-fest/
   * Matches a JSON object.
   * This type can be useful to enforce some input to be JSON-compatible or as a super-type to be extended from. 
   */
  export type JsonObject = {[Key in string]?: JsonValue}

  /**
   * From https://github.com/sindresorhus/type-fest/
   * Matches a JSON array.
   */
  export interface JsonArray extends Array<JsonValue> {}

  /**
   * From https://github.com/sindresorhus/type-fest/
   * Matches any valid JSON value.
   */
  export type JsonValue = string | number | boolean | JsonObject | JsonArray | null

  /**
   * Matches a JSON object.
   * Unlike `JsonObject`, this type allows undefined and read-only properties.
   */
  export type InputJsonObject = {readonly [Key in string]?: InputJsonValue | null}

  /**
   * Matches a JSON array.
   * Unlike `JsonArray`, readonly arrays are assignable to this type.
   */
  export interface InputJsonArray extends ReadonlyArray<InputJsonValue | null> {}

  /**
   * Matches any valid value that can be used as an input for operations like
   * create and update as the value of a JSON field. Unlike `JsonValue`, this
   * type allows read-only arrays and read-only object properties and disallows
   * `null` at the top level.
   *
   * `null` cannot be used as the value of a JSON field because its meaning
   * would be ambiguous. Use `Prisma.JsonNull` to store the JSON null value or
   * `Prisma.DbNull` to clear the JSON value and set the field to the database
   * NULL value instead.
   *
   * @see https://www.prisma.io/docs/concepts/components/prisma-client/working-with-fields/working-with-json-fields#filtering-by-null-values
   */
  export type InputJsonValue = string | number | boolean | InputJsonObject | InputJsonArray

  /**
   * Helper for filtering JSON entries that have `null` on the database (empty on the db)
   * 
   * @see https://www.prisma.io/docs/concepts/components/prisma-client/working-with-fields/working-with-json-fields#filtering-on-a-json-field
   */
  export const DbNull: 'DbNull'

  /**
   * Helper for filtering JSON entries that have JSON `null` values (not empty on the db)
   * 
   * @see https://www.prisma.io/docs/concepts/components/prisma-client/working-with-fields/working-with-json-fields#filtering-on-a-json-field
   */
  export const JsonNull: 'JsonNull'

  /**
   * Helper for filtering JSON entries that are `Prisma.DbNull` or `Prisma.JsonNull`
   * 
   * @see https://www.prisma.io/docs/concepts/components/prisma-client/working-with-fields/working-with-json-fields#filtering-on-a-json-field
   */
  export const AnyNull: 'AnyNull'

  type SelectAndInclude = {
    select: any
    include: any
  }
  type HasSelect = {
    select: any
  }
  type HasInclude = {
    include: any
  }
  type CheckSelect<T, S, U> = T extends SelectAndInclude
    ? 'Please either choose `select` or `include`'
    : T extends HasSelect
    ? U
    : T extends HasInclude
    ? U
    : S

  /**
   * Get the type of the value, that the Promise holds.
   */
  export type PromiseType<T extends PromiseLike<any>> = T extends PromiseLike<infer U> ? U : T;

  /**
   * Get the return type of a function which returns a Promise.
   */
  export type PromiseReturnType<T extends (...args: any) => Promise<any>> = PromiseType<ReturnType<T>>

  /**
   * From T, pick a set of properties whose keys are in the union K
   */
  type Prisma__Pick<T, K extends keyof T> = {
      [P in K]: T[P];
  };


  export type Enumerable<T> = T | Array<T>;

  export type RequiredKeys<T> = {
    [K in keyof T]-?: {} extends Prisma__Pick<T, K> ? never : K
  }[keyof T]

  export type TruthyKeys<T> = {
    [key in keyof T]: T[key] extends false | undefined | null ? never : key
  }[keyof T]

  export type TrueKeys<T> = TruthyKeys<Prisma__Pick<T, RequiredKeys<T>>>

  /**
   * Subset
   * @desc From `T` pick properties that exist in `U`. Simple version of Intersection
   */
  export type Subset<T, U> = {
    [key in keyof T]: key extends keyof U ? T[key] : never;
  };

  /**
   * SelectSubset
   * @desc From `T` pick properties that exist in `U`. Simple version of Intersection.
   * Additionally, it validates, if both select and include are present. If the case, it errors.
   */
  export type SelectSubset<T, U> = {
    [key in keyof T]: key extends keyof U ? T[key] : never
  } &
    (T extends SelectAndInclude
      ? 'Please either choose `select` or `include`.'
      : {})

  /**
   * Subset + Intersection
   * @desc From `T` pick properties that exist in `U` and intersect `K`
   */
  export type SubsetIntersection<T, U, K> = {
    [key in keyof T]: key extends keyof U ? T[key] : never
  } &
    K

  type Without<T, U> = { [P in Exclude<keyof T, keyof U>]?: never };

  /**
   * XOR is needed to have a real mutually exclusive union type
   * https://stackoverflow.com/questions/42123407/does-typescript-support-mutually-exclusive-types
   */
  type XOR<T, U> =
    T extends object ?
    U extends object ?
      (Without<T, U> & U) | (Without<U, T> & T)
    : U : T


  /**
   * Is T a Record?
   */
  type IsObject<T extends any> = T extends Array<any>
  ? False
  : T extends Date
  ? False
  : T extends Buffer
  ? False
  : T extends BigInt
  ? False
  : T extends object
  ? True
  : False


  /**
   * If it's T[], return T
   */
  export type UnEnumerate<T extends unknown> = T extends Array<infer U> ? U : T

  /**
   * From ts-toolbelt
   */

  type __Either<O extends object, K extends Key> = Omit<O, K> &
    {
      // Merge all but K
      [P in K]: Prisma__Pick<O, P & keyof O> // With K possibilities
    }[K]

  type EitherStrict<O extends object, K extends Key> = Strict<__Either<O, K>>

  type EitherLoose<O extends object, K extends Key> = ComputeRaw<__Either<O, K>>

  type _Either<
    O extends object,
    K extends Key,
    strict extends Boolean
  > = {
    1: EitherStrict<O, K>
    0: EitherLoose<O, K>
  }[strict]

  type Either<
    O extends object,
    K extends Key,
    strict extends Boolean = 1
  > = O extends unknown ? _Either<O, K, strict> : never

  export type Union = any

  type PatchUndefined<O extends object, O1 extends object> = {
    [K in keyof O]: O[K] extends undefined ? At<O1, K> : O[K]
  } & {}

  /** Helper Types for "Merge" **/
  export type IntersectOf<U extends Union> = (
    U extends unknown ? (k: U) => void : never
  ) extends (k: infer I) => void
    ? I
    : never

  export type Overwrite<O extends object, O1 extends object> = {
      [K in keyof O]: K extends keyof O1 ? O1[K] : O[K];
  } & {};

  type _Merge<U extends object> = IntersectOf<Overwrite<U, {
      [K in keyof U]-?: At<U, K>;
  }>>;

  type Key = string | number | symbol;
  type AtBasic<O extends object, K extends Key> = K extends keyof O ? O[K] : never;
  type AtStrict<O extends object, K extends Key> = O[K & keyof O];
  type AtLoose<O extends object, K extends Key> = O extends unknown ? AtStrict<O, K> : never;
  export type At<O extends object, K extends Key, strict extends Boolean = 1> = {
      1: AtStrict<O, K>;
      0: AtLoose<O, K>;
  }[strict];

  export type ComputeRaw<A extends any> = A extends Function ? A : {
    [K in keyof A]: A[K];
  } & {};

  export type OptionalFlat<O> = {
    [K in keyof O]?: O[K];
  } & {};

  type _Record<K extends keyof any, T> = {
    [P in K]: T;
  };

  type _Strict<U, _U = U> = U extends unknown ? U & OptionalFlat<_Record<Exclude<Keys<_U>, keyof U>, never>> : never;

  export type Strict<U extends object> = ComputeRaw<_Strict<U>>;
  /** End Helper Types for "Merge" **/

  export type Merge<U extends object> = ComputeRaw<_Merge<Strict<U>>>;

  /**
  A [[Boolean]]
  */
  export type Boolean = True | False

  // /**
  // 1
  // */
  export type True = 1

  /**
  0
  */
  export type False = 0

  export type Not<B extends Boolean> = {
    0: 1
    1: 0
  }[B]

  export type Extends<A1 extends any, A2 extends any> = [A1] extends [never]
    ? 0 // anything `never` is false
    : A1 extends A2
    ? 1
    : 0

  export type Has<U extends Union, U1 extends Union> = Not<
    Extends<Exclude<U1, U>, U1>
  >

  export type Or<B1 extends Boolean, B2 extends Boolean> = {
    0: {
      0: 0
      1: 1
    }
    1: {
      0: 1
      1: 1
    }
  }[B1][B2]

  export type Keys<U extends Union> = U extends unknown ? keyof U : never

  type Exact<A, W = unknown> = 
  W extends unknown ? A extends Narrowable ? Cast<A, W> : Cast<
  {[K in keyof A]: K extends keyof W ? Exact<A[K], W[K]> : never},
  {[K in keyof W]: K extends keyof A ? Exact<A[K], W[K]> : W[K]}>
  : never;

  type Narrowable = string | number | boolean | bigint;

  type Cast<A, B> = A extends B ? A : B;

  export const type: unique symbol;

  export function validator<V>(): <S>(select: Exact<S, V>) => S;

  /**
   * Used by group by
   */

  export type GetScalarType<T, O> = O extends object ? {
    [P in keyof T]: P extends keyof O
      ? O[P]
      : never
  } : never

  type FieldPaths<
    T,
    U = Omit<T, '_avg' | '_sum' | '_count' | '_min' | '_max'>
  > = IsObject<T> extends True ? U : T

  type GetHavingFields<T> = {
    [K in keyof T]: Or<
      Or<Extends<'OR', K>, Extends<'AND', K>>,
      Extends<'NOT', K>
    > extends True
      ? // infer is only needed to not hit TS limit
        // based on the brilliant idea of Pierre-Antoine Mills
        // https://github.com/microsoft/TypeScript/issues/30188#issuecomment-478938437
        T[K] extends infer TK
        ? GetHavingFields<UnEnumerate<TK> extends object ? Merge<UnEnumerate<TK>> : never>
        : never
      : {} extends FieldPaths<T[K]>
      ? never
      : K
  }[keyof T]

  /**
   * Convert tuple to union
   */
  type _TupleToUnion<T> = T extends (infer E)[] ? E : never
  type TupleToUnion<K extends readonly any[]> = _TupleToUnion<K>
  type MaybeTupleToUnion<T> = T extends any[] ? TupleToUnion<T> : T

  /**
   * Like `Pick`, but with an array
   */
  type PickArray<T, K extends Array<keyof T>> = Prisma__Pick<T, TupleToUnion<K>>

  /**
   * Exclude all keys with underscores
   */
  type ExcludeUnderscoreKeys<T extends string> = T extends `_${string}` ? never : T

  class PrismaClientFetcher {
    private readonly prisma;
    private readonly debug;
    private readonly hooks?;
    constructor(prisma: PrismaClient<any, any>, debug?: boolean, hooks?: Hooks | undefined);
    request<T>(document: any, dataPath?: string[], rootField?: string, typeName?: string, isList?: boolean, callsite?: string): Promise<T>;
    sanitizeMessage(message: string): string;
    protected unpack(document: any, data: any, path: string[], rootField?: string, isList?: boolean): any;
  }

  export const ModelName: {
    counterparties: 'counterparties',
    devices: 'devices',
    flows: 'flows'
  };

  export type ModelName = (typeof ModelName)[keyof typeof ModelName]


  export type Datasources = {
    db?: Datasource
  }

  export type RejectOnNotFound = boolean | ((error: Error) => Error)
  export type RejectPerModel = { [P in ModelName]?: RejectOnNotFound }
  export type RejectPerOperation =  { [P in "findUnique" | "findFirst"]?: RejectPerModel | RejectOnNotFound } 
  type IsReject<T> = T extends true ? True : T extends (err: Error) => Error ? True : False
  export type HasReject<
    GlobalRejectSettings extends Prisma.PrismaClientOptions['rejectOnNotFound'],
    LocalRejectSettings,
    Action extends PrismaAction,
    Model extends ModelName
  > = LocalRejectSettings extends RejectOnNotFound
    ? IsReject<LocalRejectSettings>
    : GlobalRejectSettings extends RejectPerOperation
    ? Action extends keyof GlobalRejectSettings
      ? GlobalRejectSettings[Action] extends RejectOnNotFound
        ? IsReject<GlobalRejectSettings[Action]>
        : GlobalRejectSettings[Action] extends RejectPerModel
        ? Model extends keyof GlobalRejectSettings[Action]
          ? IsReject<GlobalRejectSettings[Action][Model]>
          : False
        : False
      : False
    : IsReject<GlobalRejectSettings>
  export type ErrorFormat = 'pretty' | 'colorless' | 'minimal'

  export interface PrismaClientOptions {
    /**
     * Configure findUnique/findFirst to throw an error if the query returns null. 
     *  * @example
     * ```
     * // Reject on both findUnique/findFirst
     * rejectOnNotFound: true
     * // Reject only on findFirst with a custom error
     * rejectOnNotFound: { findFirst: (err) => new Error("Custom Error")}
     * // Reject on user.findUnique with a custom error
     * rejectOnNotFound: { findUnique: {User: (err) => new Error("User not found")}}
     * ```
     */
    rejectOnNotFound?: RejectOnNotFound | RejectPerOperation
    /**
     * Overwrites the datasource url from your prisma.schema file
     */
    datasources?: Datasources

    /**
     * @default "colorless"
     */
    errorFormat?: ErrorFormat

    /**
     * @example
     * ```
     * // Defaults to stdout
     * log: ['query', 'info', 'warn', 'error']
     * 
     * // Emit as events
     * log: [
     *  { emit: 'stdout', level: 'query' },
     *  { emit: 'stdout', level: 'info' },
     *  { emit: 'stdout', level: 'warn' }
     *  { emit: 'stdout', level: 'error' }
     * ]
     * ```
     * Read more in our [docs](https://www.prisma.io/docs/reference/tools-and-interfaces/prisma-client/logging#the-log-option).
     */
    log?: Array<LogLevel | LogDefinition>
  }

  export type Hooks = {
    beforeRequest?: (options: { query: string, path: string[], rootField?: string, typeName?: string, document: any }) => any
  }

  /* Types for Logging */
  export type LogLevel = 'info' | 'query' | 'warn' | 'error'
  export type LogDefinition = {
    level: LogLevel
    emit: 'stdout' | 'event'
  }

  export type GetLogType<T extends LogLevel | LogDefinition> = T extends LogDefinition ? T['emit'] extends 'event' ? T['level'] : never : never
  export type GetEvents<T extends any> = T extends Array<LogLevel | LogDefinition> ?
    GetLogType<T[0]> | GetLogType<T[1]> | GetLogType<T[2]> | GetLogType<T[3]>
    : never

  export type QueryEvent = {
    timestamp: Date
    query: string
    params: string
    duration: number
    target: string
  }

  export type LogEvent = {
    timestamp: Date
    message: string
    target: string
  }
  /* End Types for Logging */


  export type PrismaAction =
    | 'findUnique'
    | 'findMany'
    | 'findFirst'
    | 'create'
    | 'createMany'
    | 'update'
    | 'updateMany'
    | 'upsert'
    | 'delete'
    | 'deleteMany'
    | 'executeRaw'
    | 'queryRaw'
    | 'aggregate'
    | 'count'
    | 'runCommandRaw'
    | 'findRaw'

  /**
   * These options are being passed in to the middleware as "params"
   */
  export type MiddlewareParams = {
    model?: ModelName
    action: PrismaAction
    args: any
    dataPath: string[]
    runInTransaction: boolean
  }

  /**
   * The `T` type makes sure, that the `return proceed` is not forgotten in the middleware implementation
   */
  export type Middleware<T = any> = (
    params: MiddlewareParams,
    next: (params: MiddlewareParams) => Promise<T>,
  ) => Promise<T>

  // tested in getLogLevel.test.ts
  export function getLogLevel(log: Array<LogLevel | LogDefinition>): LogLevel | undefined;

  export type Datasource = {
    url?: string
  }

  /**
   * Count Types
   */


  /**
   * Count Type DevicesCountOutputType
   */


  export type DevicesCountOutputType = {
    flows: number
  }

  export type DevicesCountOutputTypeSelect = {
    flows?: boolean
  }

  export type DevicesCountOutputTypeGetPayload<
    S extends boolean | null | undefined | DevicesCountOutputTypeArgs,
    U = keyof S
      > = S extends true
        ? DevicesCountOutputType
    : S extends undefined
    ? never
    : S extends DevicesCountOutputTypeArgs
    ?'include' extends U
    ? DevicesCountOutputType 
    : 'select' extends U
    ? {
    [P in TrueKeys<S['select']>]:
    P extends keyof DevicesCountOutputType ? DevicesCountOutputType[P] : never
  } 
    : DevicesCountOutputType
  : DevicesCountOutputType




  // Custom InputTypes

  /**
   * DevicesCountOutputType without action
   */
  export type DevicesCountOutputTypeArgs = {
    /**
     * Select specific fields to fetch from the DevicesCountOutputType
     * 
    **/
    select?: DevicesCountOutputTypeSelect | null
  }



  /**
   * Models
   */

  /**
   * Model counterparties
   */


  export type AggregateCounterparties = {
    _count: CounterpartiesCountAggregateOutputType | null
    _avg: CounterpartiesAvgAggregateOutputType | null
    _sum: CounterpartiesSumAggregateOutputType | null
    _min: CounterpartiesMinAggregateOutputType | null
    _max: CounterpartiesMaxAggregateOutputType | null
  }

  export type CounterpartiesAvgAggregateOutputType = {
    id: number | null
    ts: number | null
  }

  export type CounterpartiesSumAggregateOutputType = {
    id: number | null
    ts: number | null
  }

  export type CounterpartiesMinAggregateOutputType = {
    id: number | null
    remote_ip: string | null
    hostname: string | null
    device_id: string | null
    source: string | null
    resolver_ip: string | null
    ts: number | null
  }

  export type CounterpartiesMaxAggregateOutputType = {
    id: number | null
    remote_ip: string | null
    hostname: string | null
    device_id: string | null
    source: string | null
    resolver_ip: string | null
    ts: number | null
  }

  export type CounterpartiesCountAggregateOutputType = {
    id: number
    remote_ip: number
    hostname: number
    device_id: number
    source: number
    resolver_ip: number
    ts: number
    _all: number
  }


  export type CounterpartiesAvgAggregateInputType = {
    id?: true
    ts?: true
  }

  export type CounterpartiesSumAggregateInputType = {
    id?: true
    ts?: true
  }

  export type CounterpartiesMinAggregateInputType = {
    id?: true
    remote_ip?: true
    hostname?: true
    device_id?: true
    source?: true
    resolver_ip?: true
    ts?: true
  }

  export type CounterpartiesMaxAggregateInputType = {
    id?: true
    remote_ip?: true
    hostname?: true
    device_id?: true
    source?: true
    resolver_ip?: true
    ts?: true
  }

  export type CounterpartiesCountAggregateInputType = {
    id?: true
    remote_ip?: true
    hostname?: true
    device_id?: true
    source?: true
    resolver_ip?: true
    ts?: true
    _all?: true
  }

  export type CounterpartiesAggregateArgs = {
    /**
     * Filter which counterparties to aggregate.
     * 
    **/
    where?: counterpartiesWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of counterparties to fetch.
     * 
    **/
    orderBy?: Enumerable<counterpartiesOrderByWithRelationInput>
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the start position
     * 
    **/
    cursor?: counterpartiesWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` counterparties from the position of the cursor.
     * 
    **/
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` counterparties.
     * 
    **/
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Count returned counterparties
    **/
    _count?: true | CounterpartiesCountAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to average
    **/
    _avg?: CounterpartiesAvgAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to sum
    **/
    _sum?: CounterpartiesSumAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to find the minimum value
    **/
    _min?: CounterpartiesMinAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to find the maximum value
    **/
    _max?: CounterpartiesMaxAggregateInputType
  }

  export type GetCounterpartiesAggregateType<T extends CounterpartiesAggregateArgs> = {
        [P in keyof T & keyof AggregateCounterparties]: P extends '_count' | 'count'
      ? T[P] extends true
        ? number
        : GetScalarType<T[P], AggregateCounterparties[P]>
      : GetScalarType<T[P], AggregateCounterparties[P]>
  }




  export type CounterpartiesGroupByArgs = {
    where?: counterpartiesWhereInput
    orderBy?: Enumerable<counterpartiesOrderByWithAggregationInput>
    by: Array<CounterpartiesScalarFieldEnum>
    having?: counterpartiesScalarWhereWithAggregatesInput
    take?: number
    skip?: number
    _count?: CounterpartiesCountAggregateInputType | true
    _avg?: CounterpartiesAvgAggregateInputType
    _sum?: CounterpartiesSumAggregateInputType
    _min?: CounterpartiesMinAggregateInputType
    _max?: CounterpartiesMaxAggregateInputType
  }


  export type CounterpartiesGroupByOutputType = {
    id: number
    remote_ip: string
    hostname: string
    device_id: string
    source: string
    resolver_ip: string
    ts: number
    _count: CounterpartiesCountAggregateOutputType | null
    _avg: CounterpartiesAvgAggregateOutputType | null
    _sum: CounterpartiesSumAggregateOutputType | null
    _min: CounterpartiesMinAggregateOutputType | null
    _max: CounterpartiesMaxAggregateOutputType | null
  }

  type GetCounterpartiesGroupByPayload<T extends CounterpartiesGroupByArgs> = PrismaPromise<
    Array<
      PickArray<CounterpartiesGroupByOutputType, T['by']> &
        {
          [P in ((keyof T) & (keyof CounterpartiesGroupByOutputType))]: P extends '_count'
            ? T[P] extends boolean
              ? number
              : GetScalarType<T[P], CounterpartiesGroupByOutputType[P]>
            : GetScalarType<T[P], CounterpartiesGroupByOutputType[P]>
        }
      >
    >


  export type counterpartiesSelect = {
    id?: boolean
    remote_ip?: boolean
    hostname?: boolean
    device_id?: boolean
    source?: boolean
    resolver_ip?: boolean
    ts?: boolean
  }

  export type counterpartiesGetPayload<
    S extends boolean | null | undefined | counterpartiesArgs,
    U = keyof S
      > = S extends true
        ? counterparties
    : S extends undefined
    ? never
    : S extends counterpartiesArgs | counterpartiesFindManyArgs
    ?'include' extends U
    ? counterparties 
    : 'select' extends U
    ? {
    [P in TrueKeys<S['select']>]:
    P extends keyof counterparties ? counterparties[P] : never
  } 
    : counterparties
  : counterparties


  type counterpartiesCountArgs = Merge<
    Omit<counterpartiesFindManyArgs, 'select' | 'include'> & {
      select?: CounterpartiesCountAggregateInputType | true
    }
  >

  export interface counterpartiesDelegate<GlobalRejectSettings> {
    /**
     * Find zero or one Counterparties that matches the filter.
     * @param {counterpartiesFindUniqueArgs} args - Arguments to find a Counterparties
     * @example
     * // Get one Counterparties
     * const counterparties = await prisma.counterparties.findUnique({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
    **/
    findUnique<T extends counterpartiesFindUniqueArgs,  LocalRejectSettings = T["rejectOnNotFound"] extends RejectOnNotFound ? T['rejectOnNotFound'] : undefined>(
      args: SelectSubset<T, counterpartiesFindUniqueArgs>
    ): HasReject<GlobalRejectSettings, LocalRejectSettings, 'findUnique', 'counterparties'> extends True ? CheckSelect<T, Prisma__counterpartiesClient<counterparties>, Prisma__counterpartiesClient<counterpartiesGetPayload<T>>> : CheckSelect<T, Prisma__counterpartiesClient<counterparties | null >, Prisma__counterpartiesClient<counterpartiesGetPayload<T> | null >>

    /**
     * Find the first Counterparties that matches the filter.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {counterpartiesFindFirstArgs} args - Arguments to find a Counterparties
     * @example
     * // Get one Counterparties
     * const counterparties = await prisma.counterparties.findFirst({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
    **/
    findFirst<T extends counterpartiesFindFirstArgs,  LocalRejectSettings = T["rejectOnNotFound"] extends RejectOnNotFound ? T['rejectOnNotFound'] : undefined>(
      args?: SelectSubset<T, counterpartiesFindFirstArgs>
    ): HasReject<GlobalRejectSettings, LocalRejectSettings, 'findFirst', 'counterparties'> extends True ? CheckSelect<T, Prisma__counterpartiesClient<counterparties>, Prisma__counterpartiesClient<counterpartiesGetPayload<T>>> : CheckSelect<T, Prisma__counterpartiesClient<counterparties | null >, Prisma__counterpartiesClient<counterpartiesGetPayload<T> | null >>

    /**
     * Find zero or more Counterparties that matches the filter.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {counterpartiesFindManyArgs=} args - Arguments to filter and select certain fields only.
     * @example
     * // Get all Counterparties
     * const counterparties = await prisma.counterparties.findMany()
     * 
     * // Get first 10 Counterparties
     * const counterparties = await prisma.counterparties.findMany({ take: 10 })
     * 
     * // Only select the `id`
     * const counterpartiesWithIdOnly = await prisma.counterparties.findMany({ select: { id: true } })
     * 
    **/
    findMany<T extends counterpartiesFindManyArgs>(
      args?: SelectSubset<T, counterpartiesFindManyArgs>
    ): CheckSelect<T, PrismaPromise<Array<counterparties>>, PrismaPromise<Array<counterpartiesGetPayload<T>>>>

    /**
     * Create a Counterparties.
     * @param {counterpartiesCreateArgs} args - Arguments to create a Counterparties.
     * @example
     * // Create one Counterparties
     * const Counterparties = await prisma.counterparties.create({
     *   data: {
     *     // ... data to create a Counterparties
     *   }
     * })
     * 
    **/
    create<T extends counterpartiesCreateArgs>(
      args: SelectSubset<T, counterpartiesCreateArgs>
    ): CheckSelect<T, Prisma__counterpartiesClient<counterparties>, Prisma__counterpartiesClient<counterpartiesGetPayload<T>>>

    /**
     * Delete a Counterparties.
     * @param {counterpartiesDeleteArgs} args - Arguments to delete one Counterparties.
     * @example
     * // Delete one Counterparties
     * const Counterparties = await prisma.counterparties.delete({
     *   where: {
     *     // ... filter to delete one Counterparties
     *   }
     * })
     * 
    **/
    delete<T extends counterpartiesDeleteArgs>(
      args: SelectSubset<T, counterpartiesDeleteArgs>
    ): CheckSelect<T, Prisma__counterpartiesClient<counterparties>, Prisma__counterpartiesClient<counterpartiesGetPayload<T>>>

    /**
     * Update one Counterparties.
     * @param {counterpartiesUpdateArgs} args - Arguments to update one Counterparties.
     * @example
     * // Update one Counterparties
     * const counterparties = await prisma.counterparties.update({
     *   where: {
     *     // ... provide filter here
     *   },
     *   data: {
     *     // ... provide data here
     *   }
     * })
     * 
    **/
    update<T extends counterpartiesUpdateArgs>(
      args: SelectSubset<T, counterpartiesUpdateArgs>
    ): CheckSelect<T, Prisma__counterpartiesClient<counterparties>, Prisma__counterpartiesClient<counterpartiesGetPayload<T>>>

    /**
     * Delete zero or more Counterparties.
     * @param {counterpartiesDeleteManyArgs} args - Arguments to filter Counterparties to delete.
     * @example
     * // Delete a few Counterparties
     * const { count } = await prisma.counterparties.deleteMany({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     * 
    **/
    deleteMany<T extends counterpartiesDeleteManyArgs>(
      args?: SelectSubset<T, counterpartiesDeleteManyArgs>
    ): PrismaPromise<BatchPayload>

    /**
     * Update zero or more Counterparties.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {counterpartiesUpdateManyArgs} args - Arguments to update one or more rows.
     * @example
     * // Update many Counterparties
     * const counterparties = await prisma.counterparties.updateMany({
     *   where: {
     *     // ... provide filter here
     *   },
     *   data: {
     *     // ... provide data here
     *   }
     * })
     * 
    **/
    updateMany<T extends counterpartiesUpdateManyArgs>(
      args: SelectSubset<T, counterpartiesUpdateManyArgs>
    ): PrismaPromise<BatchPayload>

    /**
     * Create or update one Counterparties.
     * @param {counterpartiesUpsertArgs} args - Arguments to update or create a Counterparties.
     * @example
     * // Update or create a Counterparties
     * const counterparties = await prisma.counterparties.upsert({
     *   create: {
     *     // ... data to create a Counterparties
     *   },
     *   update: {
     *     // ... in case it already exists, update
     *   },
     *   where: {
     *     // ... the filter for the Counterparties we want to update
     *   }
     * })
    **/
    upsert<T extends counterpartiesUpsertArgs>(
      args: SelectSubset<T, counterpartiesUpsertArgs>
    ): CheckSelect<T, Prisma__counterpartiesClient<counterparties>, Prisma__counterpartiesClient<counterpartiesGetPayload<T>>>

    /**
     * Count the number of Counterparties.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {counterpartiesCountArgs} args - Arguments to filter Counterparties to count.
     * @example
     * // Count the number of Counterparties
     * const count = await prisma.counterparties.count({
     *   where: {
     *     // ... the filter for the Counterparties we want to count
     *   }
     * })
    **/
    count<T extends counterpartiesCountArgs>(
      args?: Subset<T, counterpartiesCountArgs>,
    ): PrismaPromise<
      T extends _Record<'select', any>
        ? T['select'] extends true
          ? number
          : GetScalarType<T['select'], CounterpartiesCountAggregateOutputType>
        : number
    >

    /**
     * Allows you to perform aggregations operations on a Counterparties.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {CounterpartiesAggregateArgs} args - Select which aggregations you would like to apply and on what fields.
     * @example
     * // Ordered by age ascending
     * // Where email contains prisma.io
     * // Limited to the 10 users
     * const aggregations = await prisma.user.aggregate({
     *   _avg: {
     *     age: true,
     *   },
     *   where: {
     *     email: {
     *       contains: "prisma.io",
     *     },
     *   },
     *   orderBy: {
     *     age: "asc",
     *   },
     *   take: 10,
     * })
    **/
    aggregate<T extends CounterpartiesAggregateArgs>(args: Subset<T, CounterpartiesAggregateArgs>): PrismaPromise<GetCounterpartiesAggregateType<T>>

    /**
     * Group by Counterparties.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {CounterpartiesGroupByArgs} args - Group by arguments.
     * @example
     * // Group by city, order by createdAt, get count
     * const result = await prisma.user.groupBy({
     *   by: ['city', 'createdAt'],
     *   orderBy: {
     *     createdAt: true
     *   },
     *   _count: {
     *     _all: true
     *   },
     * })
     * 
    **/
    groupBy<
      T extends CounterpartiesGroupByArgs,
      HasSelectOrTake extends Or<
        Extends<'skip', Keys<T>>,
        Extends<'take', Keys<T>>
      >,
      OrderByArg extends True extends HasSelectOrTake
        ? { orderBy: CounterpartiesGroupByArgs['orderBy'] }
        : { orderBy?: CounterpartiesGroupByArgs['orderBy'] },
      OrderFields extends ExcludeUnderscoreKeys<Keys<MaybeTupleToUnion<T['orderBy']>>>,
      ByFields extends TupleToUnion<T['by']>,
      ByValid extends Has<ByFields, OrderFields>,
      HavingFields extends GetHavingFields<T['having']>,
      HavingValid extends Has<ByFields, HavingFields>,
      ByEmpty extends T['by'] extends never[] ? True : False,
      InputErrors extends ByEmpty extends True
      ? `Error: "by" must not be empty.`
      : HavingValid extends False
      ? {
          [P in HavingFields]: P extends ByFields
            ? never
            : P extends string
            ? `Error: Field "${P}" used in "having" needs to be provided in "by".`
            : [
                Error,
                'Field ',
                P,
                ` in "having" needs to be provided in "by"`,
              ]
        }[HavingFields]
      : 'take' extends Keys<T>
      ? 'orderBy' extends Keys<T>
        ? ByValid extends True
          ? {}
          : {
              [P in OrderFields]: P extends ByFields
                ? never
                : `Error: Field "${P}" in "orderBy" needs to be provided in "by"`
            }[OrderFields]
        : 'Error: If you provide "take", you also need to provide "orderBy"'
      : 'skip' extends Keys<T>
      ? 'orderBy' extends Keys<T>
        ? ByValid extends True
          ? {}
          : {
              [P in OrderFields]: P extends ByFields
                ? never
                : `Error: Field "${P}" in "orderBy" needs to be provided in "by"`
            }[OrderFields]
        : 'Error: If you provide "skip", you also need to provide "orderBy"'
      : ByValid extends True
      ? {}
      : {
          [P in OrderFields]: P extends ByFields
            ? never
            : `Error: Field "${P}" in "orderBy" needs to be provided in "by"`
        }[OrderFields]
    >(args: SubsetIntersection<T, CounterpartiesGroupByArgs, OrderByArg> & InputErrors): {} extends InputErrors ? GetCounterpartiesGroupByPayload<T> : PrismaPromise<InputErrors>
  }

  /**
   * The delegate class that acts as a "Promise-like" for counterparties.
   * Why is this prefixed with `Prisma__`?
   * Because we want to prevent naming conflicts as mentioned in
   * https://github.com/prisma/prisma-client-js/issues/707
   */
  export class Prisma__counterpartiesClient<T> implements PrismaPromise<T> {
    [prisma]: true;
    private readonly _dmmf;
    private readonly _fetcher;
    private readonly _queryType;
    private readonly _rootField;
    private readonly _clientMethod;
    private readonly _args;
    private readonly _dataPath;
    private readonly _errorFormat;
    private readonly _measurePerformance?;
    private _isList;
    private _callsite;
    private _requestPromise?;
    constructor(_dmmf: runtime.DMMFClass, _fetcher: PrismaClientFetcher, _queryType: 'query' | 'mutation', _rootField: string, _clientMethod: string, _args: any, _dataPath: string[], _errorFormat: ErrorFormat, _measurePerformance?: boolean | undefined, _isList?: boolean);
    readonly [Symbol.toStringTag]: 'PrismaClientPromise';


    private get _document();
    /**
     * Attaches callbacks for the resolution and/or rejection of the Promise.
     * @param onfulfilled The callback to execute when the Promise is resolved.
     * @param onrejected The callback to execute when the Promise is rejected.
     * @returns A Promise for the completion of which ever callback is executed.
     */
    then<TResult1 = T, TResult2 = never>(onfulfilled?: ((value: T) => TResult1 | PromiseLike<TResult1>) | undefined | null, onrejected?: ((reason: any) => TResult2 | PromiseLike<TResult2>) | undefined | null): Promise<TResult1 | TResult2>;
    /**
     * Attaches a callback for only the rejection of the Promise.
     * @param onrejected The callback to execute when the Promise is rejected.
     * @returns A Promise for the completion of the callback.
     */
    catch<TResult = never>(onrejected?: ((reason: any) => TResult | PromiseLike<TResult>) | undefined | null): Promise<T | TResult>;
    /**
     * Attaches a callback that is invoked when the Promise is settled (fulfilled or rejected). The
     * resolved value cannot be modified from the callback.
     * @param onfinally The callback to execute when the Promise is settled (fulfilled or rejected).
     * @returns A Promise for the completion of the callback.
     */
    finally(onfinally?: (() => void) | undefined | null): Promise<T>;
  }

  // Custom InputTypes

  /**
   * counterparties findUnique
   */
  export type counterpartiesFindUniqueArgs = {
    /**
     * Select specific fields to fetch from the counterparties
     * 
    **/
    select?: counterpartiesSelect | null
    /**
     * Throw an Error if a counterparties can't be found
     * 
    **/
    rejectOnNotFound?: RejectOnNotFound
    /**
     * Filter, which counterparties to fetch.
     * 
    **/
    where: counterpartiesWhereUniqueInput
  }


  /**
   * counterparties findFirst
   */
  export type counterpartiesFindFirstArgs = {
    /**
     * Select specific fields to fetch from the counterparties
     * 
    **/
    select?: counterpartiesSelect | null
    /**
     * Throw an Error if a counterparties can't be found
     * 
    **/
    rejectOnNotFound?: RejectOnNotFound
    /**
     * Filter, which counterparties to fetch.
     * 
    **/
    where?: counterpartiesWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of counterparties to fetch.
     * 
    **/
    orderBy?: Enumerable<counterpartiesOrderByWithRelationInput>
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for searching for counterparties.
     * 
    **/
    cursor?: counterpartiesWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` counterparties from the position of the cursor.
     * 
    **/
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` counterparties.
     * 
    **/
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/distinct Distinct Docs}
     * 
     * Filter by unique combinations of counterparties.
     * 
    **/
    distinct?: Enumerable<CounterpartiesScalarFieldEnum>
  }


  /**
   * counterparties findMany
   */
  export type counterpartiesFindManyArgs = {
    /**
     * Select specific fields to fetch from the counterparties
     * 
    **/
    select?: counterpartiesSelect | null
    /**
     * Filter, which counterparties to fetch.
     * 
    **/
    where?: counterpartiesWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of counterparties to fetch.
     * 
    **/
    orderBy?: Enumerable<counterpartiesOrderByWithRelationInput>
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for listing counterparties.
     * 
    **/
    cursor?: counterpartiesWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` counterparties from the position of the cursor.
     * 
    **/
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` counterparties.
     * 
    **/
    skip?: number
    distinct?: Enumerable<CounterpartiesScalarFieldEnum>
  }


  /**
   * counterparties create
   */
  export type counterpartiesCreateArgs = {
    /**
     * Select specific fields to fetch from the counterparties
     * 
    **/
    select?: counterpartiesSelect | null
    /**
     * The data needed to create a counterparties.
     * 
    **/
    data: XOR<counterpartiesCreateInput, counterpartiesUncheckedCreateInput>
  }


  /**
   * counterparties update
   */
  export type counterpartiesUpdateArgs = {
    /**
     * Select specific fields to fetch from the counterparties
     * 
    **/
    select?: counterpartiesSelect | null
    /**
     * The data needed to update a counterparties.
     * 
    **/
    data: XOR<counterpartiesUpdateInput, counterpartiesUncheckedUpdateInput>
    /**
     * Choose, which counterparties to update.
     * 
    **/
    where: counterpartiesWhereUniqueInput
  }


  /**
   * counterparties updateMany
   */
  export type counterpartiesUpdateManyArgs = {
    /**
     * The data used to update counterparties.
     * 
    **/
    data: XOR<counterpartiesUpdateManyMutationInput, counterpartiesUncheckedUpdateManyInput>
    /**
     * Filter which counterparties to update
     * 
    **/
    where?: counterpartiesWhereInput
  }


  /**
   * counterparties upsert
   */
  export type counterpartiesUpsertArgs = {
    /**
     * Select specific fields to fetch from the counterparties
     * 
    **/
    select?: counterpartiesSelect | null
    /**
     * The filter to search for the counterparties to update in case it exists.
     * 
    **/
    where: counterpartiesWhereUniqueInput
    /**
     * In case the counterparties found by the `where` argument doesn't exist, create a new counterparties with this data.
     * 
    **/
    create: XOR<counterpartiesCreateInput, counterpartiesUncheckedCreateInput>
    /**
     * In case the counterparties was found with the provided `where` argument, update it with this data.
     * 
    **/
    update: XOR<counterpartiesUpdateInput, counterpartiesUncheckedUpdateInput>
  }


  /**
   * counterparties delete
   */
  export type counterpartiesDeleteArgs = {
    /**
     * Select specific fields to fetch from the counterparties
     * 
    **/
    select?: counterpartiesSelect | null
    /**
     * Filter which counterparties to delete.
     * 
    **/
    where: counterpartiesWhereUniqueInput
  }


  /**
   * counterparties deleteMany
   */
  export type counterpartiesDeleteManyArgs = {
    /**
     * Filter which counterparties to delete
     * 
    **/
    where?: counterpartiesWhereInput
  }


  /**
   * counterparties without action
   */
  export type counterpartiesArgs = {
    /**
     * Select specific fields to fetch from the counterparties
     * 
    **/
    select?: counterpartiesSelect | null
  }



  /**
   * Model devices
   */


  export type AggregateDevices = {
    _count: DevicesCountAggregateOutputType | null
    _avg: DevicesAvgAggregateOutputType | null
    _sum: DevicesSumAggregateOutputType | null
    _min: DevicesMinAggregateOutputType | null
    _max: DevicesMaxAggregateOutputType | null
  }

  export type DevicesAvgAggregateOutputType = {
    last_updated_ts: number | null
  }

  export type DevicesSumAggregateOutputType = {
    last_updated_ts: number | null
  }

  export type DevicesMinAggregateOutputType = {
    device_id: string | null
    ip: string | null
    mac: string | null
    dhcp_hostname_list: string | null
    netdisco_list: string | null
    user_agent_list: string | null
    syn_scan_port_list: string | null
    auto_name: string | null
    last_updated_ts: number | null
  }

  export type DevicesMaxAggregateOutputType = {
    device_id: string | null
    ip: string | null
    mac: string | null
    dhcp_hostname_list: string | null
    netdisco_list: string | null
    user_agent_list: string | null
    syn_scan_port_list: string | null
    auto_name: string | null
    last_updated_ts: number | null
  }

  export type DevicesCountAggregateOutputType = {
    device_id: number
    ip: number
    mac: number
    dhcp_hostname_list: number
    netdisco_list: number
    user_agent_list: number
    syn_scan_port_list: number
    auto_name: number
    last_updated_ts: number
    _all: number
  }


  export type DevicesAvgAggregateInputType = {
    last_updated_ts?: true
  }

  export type DevicesSumAggregateInputType = {
    last_updated_ts?: true
  }

  export type DevicesMinAggregateInputType = {
    device_id?: true
    ip?: true
    mac?: true
    dhcp_hostname_list?: true
    netdisco_list?: true
    user_agent_list?: true
    syn_scan_port_list?: true
    auto_name?: true
    last_updated_ts?: true
  }

  export type DevicesMaxAggregateInputType = {
    device_id?: true
    ip?: true
    mac?: true
    dhcp_hostname_list?: true
    netdisco_list?: true
    user_agent_list?: true
    syn_scan_port_list?: true
    auto_name?: true
    last_updated_ts?: true
  }

  export type DevicesCountAggregateInputType = {
    device_id?: true
    ip?: true
    mac?: true
    dhcp_hostname_list?: true
    netdisco_list?: true
    user_agent_list?: true
    syn_scan_port_list?: true
    auto_name?: true
    last_updated_ts?: true
    _all?: true
  }

  export type DevicesAggregateArgs = {
    /**
     * Filter which devices to aggregate.
     * 
    **/
    where?: devicesWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of devices to fetch.
     * 
    **/
    orderBy?: Enumerable<devicesOrderByWithRelationInput>
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the start position
     * 
    **/
    cursor?: devicesWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` devices from the position of the cursor.
     * 
    **/
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` devices.
     * 
    **/
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Count returned devices
    **/
    _count?: true | DevicesCountAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to average
    **/
    _avg?: DevicesAvgAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to sum
    **/
    _sum?: DevicesSumAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to find the minimum value
    **/
    _min?: DevicesMinAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to find the maximum value
    **/
    _max?: DevicesMaxAggregateInputType
  }

  export type GetDevicesAggregateType<T extends DevicesAggregateArgs> = {
        [P in keyof T & keyof AggregateDevices]: P extends '_count' | 'count'
      ? T[P] extends true
        ? number
        : GetScalarType<T[P], AggregateDevices[P]>
      : GetScalarType<T[P], AggregateDevices[P]>
  }




  export type DevicesGroupByArgs = {
    where?: devicesWhereInput
    orderBy?: Enumerable<devicesOrderByWithAggregationInput>
    by: Array<DevicesScalarFieldEnum>
    having?: devicesScalarWhereWithAggregatesInput
    take?: number
    skip?: number
    _count?: DevicesCountAggregateInputType | true
    _avg?: DevicesAvgAggregateInputType
    _sum?: DevicesSumAggregateInputType
    _min?: DevicesMinAggregateInputType
    _max?: DevicesMaxAggregateInputType
  }


  export type DevicesGroupByOutputType = {
    device_id: string
    ip: string
    mac: string
    dhcp_hostname_list: string
    netdisco_list: string
    user_agent_list: string
    syn_scan_port_list: string
    auto_name: string
    last_updated_ts: number
    _count: DevicesCountAggregateOutputType | null
    _avg: DevicesAvgAggregateOutputType | null
    _sum: DevicesSumAggregateOutputType | null
    _min: DevicesMinAggregateOutputType | null
    _max: DevicesMaxAggregateOutputType | null
  }

  type GetDevicesGroupByPayload<T extends DevicesGroupByArgs> = PrismaPromise<
    Array<
      PickArray<DevicesGroupByOutputType, T['by']> &
        {
          [P in ((keyof T) & (keyof DevicesGroupByOutputType))]: P extends '_count'
            ? T[P] extends boolean
              ? number
              : GetScalarType<T[P], DevicesGroupByOutputType[P]>
            : GetScalarType<T[P], DevicesGroupByOutputType[P]>
        }
      >
    >


  export type devicesSelect = {
    device_id?: boolean
    ip?: boolean
    mac?: boolean
    dhcp_hostname_list?: boolean
    netdisco_list?: boolean
    user_agent_list?: boolean
    syn_scan_port_list?: boolean
    auto_name?: boolean
    last_updated_ts?: boolean
    flows?: boolean | flowsFindManyArgs
    _count?: boolean | DevicesCountOutputTypeArgs
  }

  export type devicesInclude = {
    flows?: boolean | flowsFindManyArgs
    _count?: boolean | DevicesCountOutputTypeArgs
  }

  export type devicesGetPayload<
    S extends boolean | null | undefined | devicesArgs,
    U = keyof S
      > = S extends true
        ? devices
    : S extends undefined
    ? never
    : S extends devicesArgs | devicesFindManyArgs
    ?'include' extends U
    ? devices  & {
    [P in TrueKeys<S['include']>]:
        P extends 'flows' ? Array < flowsGetPayload<S['include'][P]>>  :
        P extends '_count' ? DevicesCountOutputTypeGetPayload<S['include'][P]> :  never
  } 
    : 'select' extends U
    ? {
    [P in TrueKeys<S['select']>]:
        P extends 'flows' ? Array < flowsGetPayload<S['select'][P]>>  :
        P extends '_count' ? DevicesCountOutputTypeGetPayload<S['select'][P]> :  P extends keyof devices ? devices[P] : never
  } 
    : devices
  : devices


  type devicesCountArgs = Merge<
    Omit<devicesFindManyArgs, 'select' | 'include'> & {
      select?: DevicesCountAggregateInputType | true
    }
  >

  export interface devicesDelegate<GlobalRejectSettings> {
    /**
     * Find zero or one Devices that matches the filter.
     * @param {devicesFindUniqueArgs} args - Arguments to find a Devices
     * @example
     * // Get one Devices
     * const devices = await prisma.devices.findUnique({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
    **/
    findUnique<T extends devicesFindUniqueArgs,  LocalRejectSettings = T["rejectOnNotFound"] extends RejectOnNotFound ? T['rejectOnNotFound'] : undefined>(
      args: SelectSubset<T, devicesFindUniqueArgs>
    ): HasReject<GlobalRejectSettings, LocalRejectSettings, 'findUnique', 'devices'> extends True ? CheckSelect<T, Prisma__devicesClient<devices>, Prisma__devicesClient<devicesGetPayload<T>>> : CheckSelect<T, Prisma__devicesClient<devices | null >, Prisma__devicesClient<devicesGetPayload<T> | null >>

    /**
     * Find the first Devices that matches the filter.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {devicesFindFirstArgs} args - Arguments to find a Devices
     * @example
     * // Get one Devices
     * const devices = await prisma.devices.findFirst({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
    **/
    findFirst<T extends devicesFindFirstArgs,  LocalRejectSettings = T["rejectOnNotFound"] extends RejectOnNotFound ? T['rejectOnNotFound'] : undefined>(
      args?: SelectSubset<T, devicesFindFirstArgs>
    ): HasReject<GlobalRejectSettings, LocalRejectSettings, 'findFirst', 'devices'> extends True ? CheckSelect<T, Prisma__devicesClient<devices>, Prisma__devicesClient<devicesGetPayload<T>>> : CheckSelect<T, Prisma__devicesClient<devices | null >, Prisma__devicesClient<devicesGetPayload<T> | null >>

    /**
     * Find zero or more Devices that matches the filter.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {devicesFindManyArgs=} args - Arguments to filter and select certain fields only.
     * @example
     * // Get all Devices
     * const devices = await prisma.devices.findMany()
     * 
     * // Get first 10 Devices
     * const devices = await prisma.devices.findMany({ take: 10 })
     * 
     * // Only select the `device_id`
     * const devicesWithDevice_idOnly = await prisma.devices.findMany({ select: { device_id: true } })
     * 
    **/
    findMany<T extends devicesFindManyArgs>(
      args?: SelectSubset<T, devicesFindManyArgs>
    ): CheckSelect<T, PrismaPromise<Array<devices>>, PrismaPromise<Array<devicesGetPayload<T>>>>

    /**
     * Create a Devices.
     * @param {devicesCreateArgs} args - Arguments to create a Devices.
     * @example
     * // Create one Devices
     * const Devices = await prisma.devices.create({
     *   data: {
     *     // ... data to create a Devices
     *   }
     * })
     * 
    **/
    create<T extends devicesCreateArgs>(
      args: SelectSubset<T, devicesCreateArgs>
    ): CheckSelect<T, Prisma__devicesClient<devices>, Prisma__devicesClient<devicesGetPayload<T>>>

    /**
     * Delete a Devices.
     * @param {devicesDeleteArgs} args - Arguments to delete one Devices.
     * @example
     * // Delete one Devices
     * const Devices = await prisma.devices.delete({
     *   where: {
     *     // ... filter to delete one Devices
     *   }
     * })
     * 
    **/
    delete<T extends devicesDeleteArgs>(
      args: SelectSubset<T, devicesDeleteArgs>
    ): CheckSelect<T, Prisma__devicesClient<devices>, Prisma__devicesClient<devicesGetPayload<T>>>

    /**
     * Update one Devices.
     * @param {devicesUpdateArgs} args - Arguments to update one Devices.
     * @example
     * // Update one Devices
     * const devices = await prisma.devices.update({
     *   where: {
     *     // ... provide filter here
     *   },
     *   data: {
     *     // ... provide data here
     *   }
     * })
     * 
    **/
    update<T extends devicesUpdateArgs>(
      args: SelectSubset<T, devicesUpdateArgs>
    ): CheckSelect<T, Prisma__devicesClient<devices>, Prisma__devicesClient<devicesGetPayload<T>>>

    /**
     * Delete zero or more Devices.
     * @param {devicesDeleteManyArgs} args - Arguments to filter Devices to delete.
     * @example
     * // Delete a few Devices
     * const { count } = await prisma.devices.deleteMany({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     * 
    **/
    deleteMany<T extends devicesDeleteManyArgs>(
      args?: SelectSubset<T, devicesDeleteManyArgs>
    ): PrismaPromise<BatchPayload>

    /**
     * Update zero or more Devices.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {devicesUpdateManyArgs} args - Arguments to update one or more rows.
     * @example
     * // Update many Devices
     * const devices = await prisma.devices.updateMany({
     *   where: {
     *     // ... provide filter here
     *   },
     *   data: {
     *     // ... provide data here
     *   }
     * })
     * 
    **/
    updateMany<T extends devicesUpdateManyArgs>(
      args: SelectSubset<T, devicesUpdateManyArgs>
    ): PrismaPromise<BatchPayload>

    /**
     * Create or update one Devices.
     * @param {devicesUpsertArgs} args - Arguments to update or create a Devices.
     * @example
     * // Update or create a Devices
     * const devices = await prisma.devices.upsert({
     *   create: {
     *     // ... data to create a Devices
     *   },
     *   update: {
     *     // ... in case it already exists, update
     *   },
     *   where: {
     *     // ... the filter for the Devices we want to update
     *   }
     * })
    **/
    upsert<T extends devicesUpsertArgs>(
      args: SelectSubset<T, devicesUpsertArgs>
    ): CheckSelect<T, Prisma__devicesClient<devices>, Prisma__devicesClient<devicesGetPayload<T>>>

    /**
     * Count the number of Devices.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {devicesCountArgs} args - Arguments to filter Devices to count.
     * @example
     * // Count the number of Devices
     * const count = await prisma.devices.count({
     *   where: {
     *     // ... the filter for the Devices we want to count
     *   }
     * })
    **/
    count<T extends devicesCountArgs>(
      args?: Subset<T, devicesCountArgs>,
    ): PrismaPromise<
      T extends _Record<'select', any>
        ? T['select'] extends true
          ? number
          : GetScalarType<T['select'], DevicesCountAggregateOutputType>
        : number
    >

    /**
     * Allows you to perform aggregations operations on a Devices.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {DevicesAggregateArgs} args - Select which aggregations you would like to apply and on what fields.
     * @example
     * // Ordered by age ascending
     * // Where email contains prisma.io
     * // Limited to the 10 users
     * const aggregations = await prisma.user.aggregate({
     *   _avg: {
     *     age: true,
     *   },
     *   where: {
     *     email: {
     *       contains: "prisma.io",
     *     },
     *   },
     *   orderBy: {
     *     age: "asc",
     *   },
     *   take: 10,
     * })
    **/
    aggregate<T extends DevicesAggregateArgs>(args: Subset<T, DevicesAggregateArgs>): PrismaPromise<GetDevicesAggregateType<T>>

    /**
     * Group by Devices.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {DevicesGroupByArgs} args - Group by arguments.
     * @example
     * // Group by city, order by createdAt, get count
     * const result = await prisma.user.groupBy({
     *   by: ['city', 'createdAt'],
     *   orderBy: {
     *     createdAt: true
     *   },
     *   _count: {
     *     _all: true
     *   },
     * })
     * 
    **/
    groupBy<
      T extends DevicesGroupByArgs,
      HasSelectOrTake extends Or<
        Extends<'skip', Keys<T>>,
        Extends<'take', Keys<T>>
      >,
      OrderByArg extends True extends HasSelectOrTake
        ? { orderBy: DevicesGroupByArgs['orderBy'] }
        : { orderBy?: DevicesGroupByArgs['orderBy'] },
      OrderFields extends ExcludeUnderscoreKeys<Keys<MaybeTupleToUnion<T['orderBy']>>>,
      ByFields extends TupleToUnion<T['by']>,
      ByValid extends Has<ByFields, OrderFields>,
      HavingFields extends GetHavingFields<T['having']>,
      HavingValid extends Has<ByFields, HavingFields>,
      ByEmpty extends T['by'] extends never[] ? True : False,
      InputErrors extends ByEmpty extends True
      ? `Error: "by" must not be empty.`
      : HavingValid extends False
      ? {
          [P in HavingFields]: P extends ByFields
            ? never
            : P extends string
            ? `Error: Field "${P}" used in "having" needs to be provided in "by".`
            : [
                Error,
                'Field ',
                P,
                ` in "having" needs to be provided in "by"`,
              ]
        }[HavingFields]
      : 'take' extends Keys<T>
      ? 'orderBy' extends Keys<T>
        ? ByValid extends True
          ? {}
          : {
              [P in OrderFields]: P extends ByFields
                ? never
                : `Error: Field "${P}" in "orderBy" needs to be provided in "by"`
            }[OrderFields]
        : 'Error: If you provide "take", you also need to provide "orderBy"'
      : 'skip' extends Keys<T>
      ? 'orderBy' extends Keys<T>
        ? ByValid extends True
          ? {}
          : {
              [P in OrderFields]: P extends ByFields
                ? never
                : `Error: Field "${P}" in "orderBy" needs to be provided in "by"`
            }[OrderFields]
        : 'Error: If you provide "skip", you also need to provide "orderBy"'
      : ByValid extends True
      ? {}
      : {
          [P in OrderFields]: P extends ByFields
            ? never
            : `Error: Field "${P}" in "orderBy" needs to be provided in "by"`
        }[OrderFields]
    >(args: SubsetIntersection<T, DevicesGroupByArgs, OrderByArg> & InputErrors): {} extends InputErrors ? GetDevicesGroupByPayload<T> : PrismaPromise<InputErrors>
  }

  /**
   * The delegate class that acts as a "Promise-like" for devices.
   * Why is this prefixed with `Prisma__`?
   * Because we want to prevent naming conflicts as mentioned in
   * https://github.com/prisma/prisma-client-js/issues/707
   */
  export class Prisma__devicesClient<T> implements PrismaPromise<T> {
    [prisma]: true;
    private readonly _dmmf;
    private readonly _fetcher;
    private readonly _queryType;
    private readonly _rootField;
    private readonly _clientMethod;
    private readonly _args;
    private readonly _dataPath;
    private readonly _errorFormat;
    private readonly _measurePerformance?;
    private _isList;
    private _callsite;
    private _requestPromise?;
    constructor(_dmmf: runtime.DMMFClass, _fetcher: PrismaClientFetcher, _queryType: 'query' | 'mutation', _rootField: string, _clientMethod: string, _args: any, _dataPath: string[], _errorFormat: ErrorFormat, _measurePerformance?: boolean | undefined, _isList?: boolean);
    readonly [Symbol.toStringTag]: 'PrismaClientPromise';

    flows<T extends flowsFindManyArgs = {}>(args?: Subset<T, flowsFindManyArgs>): CheckSelect<T, PrismaPromise<Array<flows>>, PrismaPromise<Array<flowsGetPayload<T>>>>;

    private get _document();
    /**
     * Attaches callbacks for the resolution and/or rejection of the Promise.
     * @param onfulfilled The callback to execute when the Promise is resolved.
     * @param onrejected The callback to execute when the Promise is rejected.
     * @returns A Promise for the completion of which ever callback is executed.
     */
    then<TResult1 = T, TResult2 = never>(onfulfilled?: ((value: T) => TResult1 | PromiseLike<TResult1>) | undefined | null, onrejected?: ((reason: any) => TResult2 | PromiseLike<TResult2>) | undefined | null): Promise<TResult1 | TResult2>;
    /**
     * Attaches a callback for only the rejection of the Promise.
     * @param onrejected The callback to execute when the Promise is rejected.
     * @returns A Promise for the completion of the callback.
     */
    catch<TResult = never>(onrejected?: ((reason: any) => TResult | PromiseLike<TResult>) | undefined | null): Promise<T | TResult>;
    /**
     * Attaches a callback that is invoked when the Promise is settled (fulfilled or rejected). The
     * resolved value cannot be modified from the callback.
     * @param onfinally The callback to execute when the Promise is settled (fulfilled or rejected).
     * @returns A Promise for the completion of the callback.
     */
    finally(onfinally?: (() => void) | undefined | null): Promise<T>;
  }

  // Custom InputTypes

  /**
   * devices findUnique
   */
  export type devicesFindUniqueArgs = {
    /**
     * Select specific fields to fetch from the devices
     * 
    **/
    select?: devicesSelect | null
    /**
     * Choose, which related nodes to fetch as well.
     * 
    **/
    include?: devicesInclude | null
    /**
     * Throw an Error if a devices can't be found
     * 
    **/
    rejectOnNotFound?: RejectOnNotFound
    /**
     * Filter, which devices to fetch.
     * 
    **/
    where: devicesWhereUniqueInput
  }


  /**
   * devices findFirst
   */
  export type devicesFindFirstArgs = {
    /**
     * Select specific fields to fetch from the devices
     * 
    **/
    select?: devicesSelect | null
    /**
     * Choose, which related nodes to fetch as well.
     * 
    **/
    include?: devicesInclude | null
    /**
     * Throw an Error if a devices can't be found
     * 
    **/
    rejectOnNotFound?: RejectOnNotFound
    /**
     * Filter, which devices to fetch.
     * 
    **/
    where?: devicesWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of devices to fetch.
     * 
    **/
    orderBy?: Enumerable<devicesOrderByWithRelationInput>
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for searching for devices.
     * 
    **/
    cursor?: devicesWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` devices from the position of the cursor.
     * 
    **/
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` devices.
     * 
    **/
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/distinct Distinct Docs}
     * 
     * Filter by unique combinations of devices.
     * 
    **/
    distinct?: Enumerable<DevicesScalarFieldEnum>
  }


  /**
   * devices findMany
   */
  export type devicesFindManyArgs = {
    /**
     * Select specific fields to fetch from the devices
     * 
    **/
    select?: devicesSelect | null
    /**
     * Choose, which related nodes to fetch as well.
     * 
    **/
    include?: devicesInclude | null
    /**
     * Filter, which devices to fetch.
     * 
    **/
    where?: devicesWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of devices to fetch.
     * 
    **/
    orderBy?: Enumerable<devicesOrderByWithRelationInput>
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for listing devices.
     * 
    **/
    cursor?: devicesWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` devices from the position of the cursor.
     * 
    **/
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` devices.
     * 
    **/
    skip?: number
    distinct?: Enumerable<DevicesScalarFieldEnum>
  }


  /**
   * devices create
   */
  export type devicesCreateArgs = {
    /**
     * Select specific fields to fetch from the devices
     * 
    **/
    select?: devicesSelect | null
    /**
     * Choose, which related nodes to fetch as well.
     * 
    **/
    include?: devicesInclude | null
    /**
     * The data needed to create a devices.
     * 
    **/
    data: XOR<devicesCreateInput, devicesUncheckedCreateInput>
  }


  /**
   * devices update
   */
  export type devicesUpdateArgs = {
    /**
     * Select specific fields to fetch from the devices
     * 
    **/
    select?: devicesSelect | null
    /**
     * Choose, which related nodes to fetch as well.
     * 
    **/
    include?: devicesInclude | null
    /**
     * The data needed to update a devices.
     * 
    **/
    data: XOR<devicesUpdateInput, devicesUncheckedUpdateInput>
    /**
     * Choose, which devices to update.
     * 
    **/
    where: devicesWhereUniqueInput
  }


  /**
   * devices updateMany
   */
  export type devicesUpdateManyArgs = {
    /**
     * The data used to update devices.
     * 
    **/
    data: XOR<devicesUpdateManyMutationInput, devicesUncheckedUpdateManyInput>
    /**
     * Filter which devices to update
     * 
    **/
    where?: devicesWhereInput
  }


  /**
   * devices upsert
   */
  export type devicesUpsertArgs = {
    /**
     * Select specific fields to fetch from the devices
     * 
    **/
    select?: devicesSelect | null
    /**
     * Choose, which related nodes to fetch as well.
     * 
    **/
    include?: devicesInclude | null
    /**
     * The filter to search for the devices to update in case it exists.
     * 
    **/
    where: devicesWhereUniqueInput
    /**
     * In case the devices found by the `where` argument doesn't exist, create a new devices with this data.
     * 
    **/
    create: XOR<devicesCreateInput, devicesUncheckedCreateInput>
    /**
     * In case the devices was found with the provided `where` argument, update it with this data.
     * 
    **/
    update: XOR<devicesUpdateInput, devicesUncheckedUpdateInput>
  }


  /**
   * devices delete
   */
  export type devicesDeleteArgs = {
    /**
     * Select specific fields to fetch from the devices
     * 
    **/
    select?: devicesSelect | null
    /**
     * Choose, which related nodes to fetch as well.
     * 
    **/
    include?: devicesInclude | null
    /**
     * Filter which devices to delete.
     * 
    **/
    where: devicesWhereUniqueInput
  }


  /**
   * devices deleteMany
   */
  export type devicesDeleteManyArgs = {
    /**
     * Filter which devices to delete
     * 
    **/
    where?: devicesWhereInput
  }


  /**
   * devices without action
   */
  export type devicesArgs = {
    /**
     * Select specific fields to fetch from the devices
     * 
    **/
    select?: devicesSelect | null
    /**
     * Choose, which related nodes to fetch as well.
     * 
    **/
    include?: devicesInclude | null
  }



  /**
   * Model flows
   */


  export type AggregateFlows = {
    _count: FlowsCountAggregateOutputType | null
    _avg: FlowsAvgAggregateOutputType | null
    _sum: FlowsSumAggregateOutputType | null
    _min: FlowsMinAggregateOutputType | null
    _max: FlowsMaxAggregateOutputType | null
  }

  export type FlowsAvgAggregateOutputType = {
    id: number | null
    device_port: number | null
    counterparty_port: number | null
    counterparty_is_ad_tracking: number | null
    uses_weak_encryption: number | null
    ts: number | null
    ts_mod_60: number | null
    ts_mod_600: number | null
    ts_mod_3600: number | null
    window_size: number | null
    inbound_byte_count: number | null
    outbound_byte_count: number | null
    inbound_packet_count: number | null
    outbound_packet_count: number | null
  }

  export type FlowsSumAggregateOutputType = {
    id: number | null
    device_port: number | null
    counterparty_port: number | null
    counterparty_is_ad_tracking: number | null
    uses_weak_encryption: number | null
    ts: number | null
    ts_mod_60: number | null
    ts_mod_600: number | null
    ts_mod_3600: number | null
    window_size: number | null
    inbound_byte_count: number | null
    outbound_byte_count: number | null
    inbound_packet_count: number | null
    outbound_packet_count: number | null
  }

  export type FlowsMinAggregateOutputType = {
    id: number | null
    device_id: string | null
    device_port: number | null
    counterparty_ip: string | null
    counterparty_port: number | null
    counterparty_hostname: string | null
    counterparty_friendly_name: string | null
    counterparty_country: string | null
    counterparty_is_ad_tracking: number | null
    counterparty_local_device_id: string | null
    transport_layer_protocol: string | null
    uses_weak_encryption: number | null
    ts: number | null
    ts_mod_60: number | null
    ts_mod_600: number | null
    ts_mod_3600: number | null
    window_size: number | null
    inbound_byte_count: number | null
    outbound_byte_count: number | null
    inbound_packet_count: number | null
    outbound_packet_count: number | null
  }

  export type FlowsMaxAggregateOutputType = {
    id: number | null
    device_id: string | null
    device_port: number | null
    counterparty_ip: string | null
    counterparty_port: number | null
    counterparty_hostname: string | null
    counterparty_friendly_name: string | null
    counterparty_country: string | null
    counterparty_is_ad_tracking: number | null
    counterparty_local_device_id: string | null
    transport_layer_protocol: string | null
    uses_weak_encryption: number | null
    ts: number | null
    ts_mod_60: number | null
    ts_mod_600: number | null
    ts_mod_3600: number | null
    window_size: number | null
    inbound_byte_count: number | null
    outbound_byte_count: number | null
    inbound_packet_count: number | null
    outbound_packet_count: number | null
  }

  export type FlowsCountAggregateOutputType = {
    id: number
    device_id: number
    device_port: number
    counterparty_ip: number
    counterparty_port: number
    counterparty_hostname: number
    counterparty_friendly_name: number
    counterparty_country: number
    counterparty_is_ad_tracking: number
    counterparty_local_device_id: number
    transport_layer_protocol: number
    uses_weak_encryption: number
    ts: number
    ts_mod_60: number
    ts_mod_600: number
    ts_mod_3600: number
    window_size: number
    inbound_byte_count: number
    outbound_byte_count: number
    inbound_packet_count: number
    outbound_packet_count: number
    _all: number
  }


  export type FlowsAvgAggregateInputType = {
    id?: true
    device_port?: true
    counterparty_port?: true
    counterparty_is_ad_tracking?: true
    uses_weak_encryption?: true
    ts?: true
    ts_mod_60?: true
    ts_mod_600?: true
    ts_mod_3600?: true
    window_size?: true
    inbound_byte_count?: true
    outbound_byte_count?: true
    inbound_packet_count?: true
    outbound_packet_count?: true
  }

  export type FlowsSumAggregateInputType = {
    id?: true
    device_port?: true
    counterparty_port?: true
    counterparty_is_ad_tracking?: true
    uses_weak_encryption?: true
    ts?: true
    ts_mod_60?: true
    ts_mod_600?: true
    ts_mod_3600?: true
    window_size?: true
    inbound_byte_count?: true
    outbound_byte_count?: true
    inbound_packet_count?: true
    outbound_packet_count?: true
  }

  export type FlowsMinAggregateInputType = {
    id?: true
    device_id?: true
    device_port?: true
    counterparty_ip?: true
    counterparty_port?: true
    counterparty_hostname?: true
    counterparty_friendly_name?: true
    counterparty_country?: true
    counterparty_is_ad_tracking?: true
    counterparty_local_device_id?: true
    transport_layer_protocol?: true
    uses_weak_encryption?: true
    ts?: true
    ts_mod_60?: true
    ts_mod_600?: true
    ts_mod_3600?: true
    window_size?: true
    inbound_byte_count?: true
    outbound_byte_count?: true
    inbound_packet_count?: true
    outbound_packet_count?: true
  }

  export type FlowsMaxAggregateInputType = {
    id?: true
    device_id?: true
    device_port?: true
    counterparty_ip?: true
    counterparty_port?: true
    counterparty_hostname?: true
    counterparty_friendly_name?: true
    counterparty_country?: true
    counterparty_is_ad_tracking?: true
    counterparty_local_device_id?: true
    transport_layer_protocol?: true
    uses_weak_encryption?: true
    ts?: true
    ts_mod_60?: true
    ts_mod_600?: true
    ts_mod_3600?: true
    window_size?: true
    inbound_byte_count?: true
    outbound_byte_count?: true
    inbound_packet_count?: true
    outbound_packet_count?: true
  }

  export type FlowsCountAggregateInputType = {
    id?: true
    device_id?: true
    device_port?: true
    counterparty_ip?: true
    counterparty_port?: true
    counterparty_hostname?: true
    counterparty_friendly_name?: true
    counterparty_country?: true
    counterparty_is_ad_tracking?: true
    counterparty_local_device_id?: true
    transport_layer_protocol?: true
    uses_weak_encryption?: true
    ts?: true
    ts_mod_60?: true
    ts_mod_600?: true
    ts_mod_3600?: true
    window_size?: true
    inbound_byte_count?: true
    outbound_byte_count?: true
    inbound_packet_count?: true
    outbound_packet_count?: true
    _all?: true
  }

  export type FlowsAggregateArgs = {
    /**
     * Filter which flows to aggregate.
     * 
    **/
    where?: flowsWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of flows to fetch.
     * 
    **/
    orderBy?: Enumerable<flowsOrderByWithRelationInput>
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the start position
     * 
    **/
    cursor?: flowsWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` flows from the position of the cursor.
     * 
    **/
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` flows.
     * 
    **/
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Count returned flows
    **/
    _count?: true | FlowsCountAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to average
    **/
    _avg?: FlowsAvgAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to sum
    **/
    _sum?: FlowsSumAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to find the minimum value
    **/
    _min?: FlowsMinAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to find the maximum value
    **/
    _max?: FlowsMaxAggregateInputType
  }

  export type GetFlowsAggregateType<T extends FlowsAggregateArgs> = {
        [P in keyof T & keyof AggregateFlows]: P extends '_count' | 'count'
      ? T[P] extends true
        ? number
        : GetScalarType<T[P], AggregateFlows[P]>
      : GetScalarType<T[P], AggregateFlows[P]>
  }




  export type FlowsGroupByArgs = {
    where?: flowsWhereInput
    orderBy?: Enumerable<flowsOrderByWithAggregationInput>
    by: Array<FlowsScalarFieldEnum>
    having?: flowsScalarWhereWithAggregatesInput
    take?: number
    skip?: number
    _count?: FlowsCountAggregateInputType | true
    _avg?: FlowsAvgAggregateInputType
    _sum?: FlowsSumAggregateInputType
    _min?: FlowsMinAggregateInputType
    _max?: FlowsMaxAggregateInputType
  }


  export type FlowsGroupByOutputType = {
    id: number
    device_id: string
    device_port: number
    counterparty_ip: string
    counterparty_port: number
    counterparty_hostname: string
    counterparty_friendly_name: string
    counterparty_country: string
    counterparty_is_ad_tracking: number
    counterparty_local_device_id: string
    transport_layer_protocol: string
    uses_weak_encryption: number
    ts: number
    ts_mod_60: number
    ts_mod_600: number
    ts_mod_3600: number
    window_size: number
    inbound_byte_count: number
    outbound_byte_count: number
    inbound_packet_count: number
    outbound_packet_count: number
    _count: FlowsCountAggregateOutputType | null
    _avg: FlowsAvgAggregateOutputType | null
    _sum: FlowsSumAggregateOutputType | null
    _min: FlowsMinAggregateOutputType | null
    _max: FlowsMaxAggregateOutputType | null
  }

  type GetFlowsGroupByPayload<T extends FlowsGroupByArgs> = PrismaPromise<
    Array<
      PickArray<FlowsGroupByOutputType, T['by']> &
        {
          [P in ((keyof T) & (keyof FlowsGroupByOutputType))]: P extends '_count'
            ? T[P] extends boolean
              ? number
              : GetScalarType<T[P], FlowsGroupByOutputType[P]>
            : GetScalarType<T[P], FlowsGroupByOutputType[P]>
        }
      >
    >


  export type flowsSelect = {
    id?: boolean
    device_id?: boolean
    device?: boolean | devicesArgs
    device_port?: boolean
    counterparty_ip?: boolean
    counterparty_port?: boolean
    counterparty_hostname?: boolean
    counterparty_friendly_name?: boolean
    counterparty_country?: boolean
    counterparty_is_ad_tracking?: boolean
    counterparty_local_device_id?: boolean
    transport_layer_protocol?: boolean
    uses_weak_encryption?: boolean
    ts?: boolean
    ts_mod_60?: boolean
    ts_mod_600?: boolean
    ts_mod_3600?: boolean
    window_size?: boolean
    inbound_byte_count?: boolean
    outbound_byte_count?: boolean
    inbound_packet_count?: boolean
    outbound_packet_count?: boolean
  }

  export type flowsInclude = {
    device?: boolean | devicesArgs
  }

  export type flowsGetPayload<
    S extends boolean | null | undefined | flowsArgs,
    U = keyof S
      > = S extends true
        ? flows
    : S extends undefined
    ? never
    : S extends flowsArgs | flowsFindManyArgs
    ?'include' extends U
    ? flows  & {
    [P in TrueKeys<S['include']>]:
        P extends 'device' ? devicesGetPayload<S['include'][P]> :  never
  } 
    : 'select' extends U
    ? {
    [P in TrueKeys<S['select']>]:
        P extends 'device' ? devicesGetPayload<S['select'][P]> :  P extends keyof flows ? flows[P] : never
  } 
    : flows
  : flows


  type flowsCountArgs = Merge<
    Omit<flowsFindManyArgs, 'select' | 'include'> & {
      select?: FlowsCountAggregateInputType | true
    }
  >

  export interface flowsDelegate<GlobalRejectSettings> {
    /**
     * Find zero or one Flows that matches the filter.
     * @param {flowsFindUniqueArgs} args - Arguments to find a Flows
     * @example
     * // Get one Flows
     * const flows = await prisma.flows.findUnique({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
    **/
    findUnique<T extends flowsFindUniqueArgs,  LocalRejectSettings = T["rejectOnNotFound"] extends RejectOnNotFound ? T['rejectOnNotFound'] : undefined>(
      args: SelectSubset<T, flowsFindUniqueArgs>
    ): HasReject<GlobalRejectSettings, LocalRejectSettings, 'findUnique', 'flows'> extends True ? CheckSelect<T, Prisma__flowsClient<flows>, Prisma__flowsClient<flowsGetPayload<T>>> : CheckSelect<T, Prisma__flowsClient<flows | null >, Prisma__flowsClient<flowsGetPayload<T> | null >>

    /**
     * Find the first Flows that matches the filter.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {flowsFindFirstArgs} args - Arguments to find a Flows
     * @example
     * // Get one Flows
     * const flows = await prisma.flows.findFirst({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
    **/
    findFirst<T extends flowsFindFirstArgs,  LocalRejectSettings = T["rejectOnNotFound"] extends RejectOnNotFound ? T['rejectOnNotFound'] : undefined>(
      args?: SelectSubset<T, flowsFindFirstArgs>
    ): HasReject<GlobalRejectSettings, LocalRejectSettings, 'findFirst', 'flows'> extends True ? CheckSelect<T, Prisma__flowsClient<flows>, Prisma__flowsClient<flowsGetPayload<T>>> : CheckSelect<T, Prisma__flowsClient<flows | null >, Prisma__flowsClient<flowsGetPayload<T> | null >>

    /**
     * Find zero or more Flows that matches the filter.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {flowsFindManyArgs=} args - Arguments to filter and select certain fields only.
     * @example
     * // Get all Flows
     * const flows = await prisma.flows.findMany()
     * 
     * // Get first 10 Flows
     * const flows = await prisma.flows.findMany({ take: 10 })
     * 
     * // Only select the `id`
     * const flowsWithIdOnly = await prisma.flows.findMany({ select: { id: true } })
     * 
    **/
    findMany<T extends flowsFindManyArgs>(
      args?: SelectSubset<T, flowsFindManyArgs>
    ): CheckSelect<T, PrismaPromise<Array<flows>>, PrismaPromise<Array<flowsGetPayload<T>>>>

    /**
     * Create a Flows.
     * @param {flowsCreateArgs} args - Arguments to create a Flows.
     * @example
     * // Create one Flows
     * const Flows = await prisma.flows.create({
     *   data: {
     *     // ... data to create a Flows
     *   }
     * })
     * 
    **/
    create<T extends flowsCreateArgs>(
      args: SelectSubset<T, flowsCreateArgs>
    ): CheckSelect<T, Prisma__flowsClient<flows>, Prisma__flowsClient<flowsGetPayload<T>>>

    /**
     * Delete a Flows.
     * @param {flowsDeleteArgs} args - Arguments to delete one Flows.
     * @example
     * // Delete one Flows
     * const Flows = await prisma.flows.delete({
     *   where: {
     *     // ... filter to delete one Flows
     *   }
     * })
     * 
    **/
    delete<T extends flowsDeleteArgs>(
      args: SelectSubset<T, flowsDeleteArgs>
    ): CheckSelect<T, Prisma__flowsClient<flows>, Prisma__flowsClient<flowsGetPayload<T>>>

    /**
     * Update one Flows.
     * @param {flowsUpdateArgs} args - Arguments to update one Flows.
     * @example
     * // Update one Flows
     * const flows = await prisma.flows.update({
     *   where: {
     *     // ... provide filter here
     *   },
     *   data: {
     *     // ... provide data here
     *   }
     * })
     * 
    **/
    update<T extends flowsUpdateArgs>(
      args: SelectSubset<T, flowsUpdateArgs>
    ): CheckSelect<T, Prisma__flowsClient<flows>, Prisma__flowsClient<flowsGetPayload<T>>>

    /**
     * Delete zero or more Flows.
     * @param {flowsDeleteManyArgs} args - Arguments to filter Flows to delete.
     * @example
     * // Delete a few Flows
     * const { count } = await prisma.flows.deleteMany({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     * 
    **/
    deleteMany<T extends flowsDeleteManyArgs>(
      args?: SelectSubset<T, flowsDeleteManyArgs>
    ): PrismaPromise<BatchPayload>

    /**
     * Update zero or more Flows.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {flowsUpdateManyArgs} args - Arguments to update one or more rows.
     * @example
     * // Update many Flows
     * const flows = await prisma.flows.updateMany({
     *   where: {
     *     // ... provide filter here
     *   },
     *   data: {
     *     // ... provide data here
     *   }
     * })
     * 
    **/
    updateMany<T extends flowsUpdateManyArgs>(
      args: SelectSubset<T, flowsUpdateManyArgs>
    ): PrismaPromise<BatchPayload>

    /**
     * Create or update one Flows.
     * @param {flowsUpsertArgs} args - Arguments to update or create a Flows.
     * @example
     * // Update or create a Flows
     * const flows = await prisma.flows.upsert({
     *   create: {
     *     // ... data to create a Flows
     *   },
     *   update: {
     *     // ... in case it already exists, update
     *   },
     *   where: {
     *     // ... the filter for the Flows we want to update
     *   }
     * })
    **/
    upsert<T extends flowsUpsertArgs>(
      args: SelectSubset<T, flowsUpsertArgs>
    ): CheckSelect<T, Prisma__flowsClient<flows>, Prisma__flowsClient<flowsGetPayload<T>>>

    /**
     * Count the number of Flows.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {flowsCountArgs} args - Arguments to filter Flows to count.
     * @example
     * // Count the number of Flows
     * const count = await prisma.flows.count({
     *   where: {
     *     // ... the filter for the Flows we want to count
     *   }
     * })
    **/
    count<T extends flowsCountArgs>(
      args?: Subset<T, flowsCountArgs>,
    ): PrismaPromise<
      T extends _Record<'select', any>
        ? T['select'] extends true
          ? number
          : GetScalarType<T['select'], FlowsCountAggregateOutputType>
        : number
    >

    /**
     * Allows you to perform aggregations operations on a Flows.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {FlowsAggregateArgs} args - Select which aggregations you would like to apply and on what fields.
     * @example
     * // Ordered by age ascending
     * // Where email contains prisma.io
     * // Limited to the 10 users
     * const aggregations = await prisma.user.aggregate({
     *   _avg: {
     *     age: true,
     *   },
     *   where: {
     *     email: {
     *       contains: "prisma.io",
     *     },
     *   },
     *   orderBy: {
     *     age: "asc",
     *   },
     *   take: 10,
     * })
    **/
    aggregate<T extends FlowsAggregateArgs>(args: Subset<T, FlowsAggregateArgs>): PrismaPromise<GetFlowsAggregateType<T>>

    /**
     * Group by Flows.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {FlowsGroupByArgs} args - Group by arguments.
     * @example
     * // Group by city, order by createdAt, get count
     * const result = await prisma.user.groupBy({
     *   by: ['city', 'createdAt'],
     *   orderBy: {
     *     createdAt: true
     *   },
     *   _count: {
     *     _all: true
     *   },
     * })
     * 
    **/
    groupBy<
      T extends FlowsGroupByArgs,
      HasSelectOrTake extends Or<
        Extends<'skip', Keys<T>>,
        Extends<'take', Keys<T>>
      >,
      OrderByArg extends True extends HasSelectOrTake
        ? { orderBy: FlowsGroupByArgs['orderBy'] }
        : { orderBy?: FlowsGroupByArgs['orderBy'] },
      OrderFields extends ExcludeUnderscoreKeys<Keys<MaybeTupleToUnion<T['orderBy']>>>,
      ByFields extends TupleToUnion<T['by']>,
      ByValid extends Has<ByFields, OrderFields>,
      HavingFields extends GetHavingFields<T['having']>,
      HavingValid extends Has<ByFields, HavingFields>,
      ByEmpty extends T['by'] extends never[] ? True : False,
      InputErrors extends ByEmpty extends True
      ? `Error: "by" must not be empty.`
      : HavingValid extends False
      ? {
          [P in HavingFields]: P extends ByFields
            ? never
            : P extends string
            ? `Error: Field "${P}" used in "having" needs to be provided in "by".`
            : [
                Error,
                'Field ',
                P,
                ` in "having" needs to be provided in "by"`,
              ]
        }[HavingFields]
      : 'take' extends Keys<T>
      ? 'orderBy' extends Keys<T>
        ? ByValid extends True
          ? {}
          : {
              [P in OrderFields]: P extends ByFields
                ? never
                : `Error: Field "${P}" in "orderBy" needs to be provided in "by"`
            }[OrderFields]
        : 'Error: If you provide "take", you also need to provide "orderBy"'
      : 'skip' extends Keys<T>
      ? 'orderBy' extends Keys<T>
        ? ByValid extends True
          ? {}
          : {
              [P in OrderFields]: P extends ByFields
                ? never
                : `Error: Field "${P}" in "orderBy" needs to be provided in "by"`
            }[OrderFields]
        : 'Error: If you provide "skip", you also need to provide "orderBy"'
      : ByValid extends True
      ? {}
      : {
          [P in OrderFields]: P extends ByFields
            ? never
            : `Error: Field "${P}" in "orderBy" needs to be provided in "by"`
        }[OrderFields]
    >(args: SubsetIntersection<T, FlowsGroupByArgs, OrderByArg> & InputErrors): {} extends InputErrors ? GetFlowsGroupByPayload<T> : PrismaPromise<InputErrors>
  }

  /**
   * The delegate class that acts as a "Promise-like" for flows.
   * Why is this prefixed with `Prisma__`?
   * Because we want to prevent naming conflicts as mentioned in
   * https://github.com/prisma/prisma-client-js/issues/707
   */
  export class Prisma__flowsClient<T> implements PrismaPromise<T> {
    [prisma]: true;
    private readonly _dmmf;
    private readonly _fetcher;
    private readonly _queryType;
    private readonly _rootField;
    private readonly _clientMethod;
    private readonly _args;
    private readonly _dataPath;
    private readonly _errorFormat;
    private readonly _measurePerformance?;
    private _isList;
    private _callsite;
    private _requestPromise?;
    constructor(_dmmf: runtime.DMMFClass, _fetcher: PrismaClientFetcher, _queryType: 'query' | 'mutation', _rootField: string, _clientMethod: string, _args: any, _dataPath: string[], _errorFormat: ErrorFormat, _measurePerformance?: boolean | undefined, _isList?: boolean);
    readonly [Symbol.toStringTag]: 'PrismaClientPromise';

    device<T extends devicesArgs = {}>(args?: Subset<T, devicesArgs>): CheckSelect<T, Prisma__devicesClient<devices | null >, Prisma__devicesClient<devicesGetPayload<T> | null >>;

    private get _document();
    /**
     * Attaches callbacks for the resolution and/or rejection of the Promise.
     * @param onfulfilled The callback to execute when the Promise is resolved.
     * @param onrejected The callback to execute when the Promise is rejected.
     * @returns A Promise for the completion of which ever callback is executed.
     */
    then<TResult1 = T, TResult2 = never>(onfulfilled?: ((value: T) => TResult1 | PromiseLike<TResult1>) | undefined | null, onrejected?: ((reason: any) => TResult2 | PromiseLike<TResult2>) | undefined | null): Promise<TResult1 | TResult2>;
    /**
     * Attaches a callback for only the rejection of the Promise.
     * @param onrejected The callback to execute when the Promise is rejected.
     * @returns A Promise for the completion of the callback.
     */
    catch<TResult = never>(onrejected?: ((reason: any) => TResult | PromiseLike<TResult>) | undefined | null): Promise<T | TResult>;
    /**
     * Attaches a callback that is invoked when the Promise is settled (fulfilled or rejected). The
     * resolved value cannot be modified from the callback.
     * @param onfinally The callback to execute when the Promise is settled (fulfilled or rejected).
     * @returns A Promise for the completion of the callback.
     */
    finally(onfinally?: (() => void) | undefined | null): Promise<T>;
  }

  // Custom InputTypes

  /**
   * flows findUnique
   */
  export type flowsFindUniqueArgs = {
    /**
     * Select specific fields to fetch from the flows
     * 
    **/
    select?: flowsSelect | null
    /**
     * Choose, which related nodes to fetch as well.
     * 
    **/
    include?: flowsInclude | null
    /**
     * Throw an Error if a flows can't be found
     * 
    **/
    rejectOnNotFound?: RejectOnNotFound
    /**
     * Filter, which flows to fetch.
     * 
    **/
    where: flowsWhereUniqueInput
  }


  /**
   * flows findFirst
   */
  export type flowsFindFirstArgs = {
    /**
     * Select specific fields to fetch from the flows
     * 
    **/
    select?: flowsSelect | null
    /**
     * Choose, which related nodes to fetch as well.
     * 
    **/
    include?: flowsInclude | null
    /**
     * Throw an Error if a flows can't be found
     * 
    **/
    rejectOnNotFound?: RejectOnNotFound
    /**
     * Filter, which flows to fetch.
     * 
    **/
    where?: flowsWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of flows to fetch.
     * 
    **/
    orderBy?: Enumerable<flowsOrderByWithRelationInput>
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for searching for flows.
     * 
    **/
    cursor?: flowsWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` flows from the position of the cursor.
     * 
    **/
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` flows.
     * 
    **/
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/distinct Distinct Docs}
     * 
     * Filter by unique combinations of flows.
     * 
    **/
    distinct?: Enumerable<FlowsScalarFieldEnum>
  }


  /**
   * flows findMany
   */
  export type flowsFindManyArgs = {
    /**
     * Select specific fields to fetch from the flows
     * 
    **/
    select?: flowsSelect | null
    /**
     * Choose, which related nodes to fetch as well.
     * 
    **/
    include?: flowsInclude | null
    /**
     * Filter, which flows to fetch.
     * 
    **/
    where?: flowsWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of flows to fetch.
     * 
    **/
    orderBy?: Enumerable<flowsOrderByWithRelationInput>
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for listing flows.
     * 
    **/
    cursor?: flowsWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` flows from the position of the cursor.
     * 
    **/
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` flows.
     * 
    **/
    skip?: number
    distinct?: Enumerable<FlowsScalarFieldEnum>
  }


  /**
   * flows create
   */
  export type flowsCreateArgs = {
    /**
     * Select specific fields to fetch from the flows
     * 
    **/
    select?: flowsSelect | null
    /**
     * Choose, which related nodes to fetch as well.
     * 
    **/
    include?: flowsInclude | null
    /**
     * The data needed to create a flows.
     * 
    **/
    data: XOR<flowsCreateInput, flowsUncheckedCreateInput>
  }


  /**
   * flows update
   */
  export type flowsUpdateArgs = {
    /**
     * Select specific fields to fetch from the flows
     * 
    **/
    select?: flowsSelect | null
    /**
     * Choose, which related nodes to fetch as well.
     * 
    **/
    include?: flowsInclude | null
    /**
     * The data needed to update a flows.
     * 
    **/
    data: XOR<flowsUpdateInput, flowsUncheckedUpdateInput>
    /**
     * Choose, which flows to update.
     * 
    **/
    where: flowsWhereUniqueInput
  }


  /**
   * flows updateMany
   */
  export type flowsUpdateManyArgs = {
    /**
     * The data used to update flows.
     * 
    **/
    data: XOR<flowsUpdateManyMutationInput, flowsUncheckedUpdateManyInput>
    /**
     * Filter which flows to update
     * 
    **/
    where?: flowsWhereInput
  }


  /**
   * flows upsert
   */
  export type flowsUpsertArgs = {
    /**
     * Select specific fields to fetch from the flows
     * 
    **/
    select?: flowsSelect | null
    /**
     * Choose, which related nodes to fetch as well.
     * 
    **/
    include?: flowsInclude | null
    /**
     * The filter to search for the flows to update in case it exists.
     * 
    **/
    where: flowsWhereUniqueInput
    /**
     * In case the flows found by the `where` argument doesn't exist, create a new flows with this data.
     * 
    **/
    create: XOR<flowsCreateInput, flowsUncheckedCreateInput>
    /**
     * In case the flows was found with the provided `where` argument, update it with this data.
     * 
    **/
    update: XOR<flowsUpdateInput, flowsUncheckedUpdateInput>
  }


  /**
   * flows delete
   */
  export type flowsDeleteArgs = {
    /**
     * Select specific fields to fetch from the flows
     * 
    **/
    select?: flowsSelect | null
    /**
     * Choose, which related nodes to fetch as well.
     * 
    **/
    include?: flowsInclude | null
    /**
     * Filter which flows to delete.
     * 
    **/
    where: flowsWhereUniqueInput
  }


  /**
   * flows deleteMany
   */
  export type flowsDeleteManyArgs = {
    /**
     * Filter which flows to delete
     * 
    **/
    where?: flowsWhereInput
  }


  /**
   * flows without action
   */
  export type flowsArgs = {
    /**
     * Select specific fields to fetch from the flows
     * 
    **/
    select?: flowsSelect | null
    /**
     * Choose, which related nodes to fetch as well.
     * 
    **/
    include?: flowsInclude | null
  }



  /**
   * Enums
   */

  // Based on
  // https://github.com/microsoft/TypeScript/issues/3192#issuecomment-261720275

  export const CounterpartiesScalarFieldEnum: {
    id: 'id',
    remote_ip: 'remote_ip',
    hostname: 'hostname',
    device_id: 'device_id',
    source: 'source',
    resolver_ip: 'resolver_ip',
    ts: 'ts'
  };

  export type CounterpartiesScalarFieldEnum = (typeof CounterpartiesScalarFieldEnum)[keyof typeof CounterpartiesScalarFieldEnum]


  export const DevicesScalarFieldEnum: {
    device_id: 'device_id',
    ip: 'ip',
    mac: 'mac',
    dhcp_hostname_list: 'dhcp_hostname_list',
    netdisco_list: 'netdisco_list',
    user_agent_list: 'user_agent_list',
    syn_scan_port_list: 'syn_scan_port_list',
    auto_name: 'auto_name',
    last_updated_ts: 'last_updated_ts'
  };

  export type DevicesScalarFieldEnum = (typeof DevicesScalarFieldEnum)[keyof typeof DevicesScalarFieldEnum]


  export const FlowsScalarFieldEnum: {
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
  };

  export type FlowsScalarFieldEnum = (typeof FlowsScalarFieldEnum)[keyof typeof FlowsScalarFieldEnum]


  export const SortOrder: {
    asc: 'asc',
    desc: 'desc'
  };

  export type SortOrder = (typeof SortOrder)[keyof typeof SortOrder]


  /**
   * Deep Input Types
   */


  export type counterpartiesWhereInput = {
    AND?: Enumerable<counterpartiesWhereInput>
    OR?: Enumerable<counterpartiesWhereInput>
    NOT?: Enumerable<counterpartiesWhereInput>
    id?: IntFilter | number
    remote_ip?: StringFilter | string
    hostname?: StringFilter | string
    device_id?: StringFilter | string
    source?: StringFilter | string
    resolver_ip?: StringFilter | string
    ts?: FloatFilter | number
  }

  export type counterpartiesOrderByWithRelationInput = {
    id?: SortOrder
    remote_ip?: SortOrder
    hostname?: SortOrder
    device_id?: SortOrder
    source?: SortOrder
    resolver_ip?: SortOrder
    ts?: SortOrder
  }

  export type counterpartiesWhereUniqueInput = {
    id?: number
  }

  export type counterpartiesOrderByWithAggregationInput = {
    id?: SortOrder
    remote_ip?: SortOrder
    hostname?: SortOrder
    device_id?: SortOrder
    source?: SortOrder
    resolver_ip?: SortOrder
    ts?: SortOrder
    _count?: counterpartiesCountOrderByAggregateInput
    _avg?: counterpartiesAvgOrderByAggregateInput
    _max?: counterpartiesMaxOrderByAggregateInput
    _min?: counterpartiesMinOrderByAggregateInput
    _sum?: counterpartiesSumOrderByAggregateInput
  }

  export type counterpartiesScalarWhereWithAggregatesInput = {
    AND?: Enumerable<counterpartiesScalarWhereWithAggregatesInput>
    OR?: Enumerable<counterpartiesScalarWhereWithAggregatesInput>
    NOT?: Enumerable<counterpartiesScalarWhereWithAggregatesInput>
    id?: IntWithAggregatesFilter | number
    remote_ip?: StringWithAggregatesFilter | string
    hostname?: StringWithAggregatesFilter | string
    device_id?: StringWithAggregatesFilter | string
    source?: StringWithAggregatesFilter | string
    resolver_ip?: StringWithAggregatesFilter | string
    ts?: FloatWithAggregatesFilter | number
  }

  export type devicesWhereInput = {
    AND?: Enumerable<devicesWhereInput>
    OR?: Enumerable<devicesWhereInput>
    NOT?: Enumerable<devicesWhereInput>
    device_id?: StringFilter | string
    ip?: StringFilter | string
    mac?: StringFilter | string
    dhcp_hostname_list?: StringFilter | string
    netdisco_list?: StringFilter | string
    user_agent_list?: StringFilter | string
    syn_scan_port_list?: StringFilter | string
    auto_name?: StringFilter | string
    last_updated_ts?: FloatFilter | number
    flows?: FlowsListRelationFilter
  }

  export type devicesOrderByWithRelationInput = {
    device_id?: SortOrder
    ip?: SortOrder
    mac?: SortOrder
    dhcp_hostname_list?: SortOrder
    netdisco_list?: SortOrder
    user_agent_list?: SortOrder
    syn_scan_port_list?: SortOrder
    auto_name?: SortOrder
    last_updated_ts?: SortOrder
    flows?: flowsOrderByRelationAggregateInput
  }

  export type devicesWhereUniqueInput = {
    device_id?: string
  }

  export type devicesOrderByWithAggregationInput = {
    device_id?: SortOrder
    ip?: SortOrder
    mac?: SortOrder
    dhcp_hostname_list?: SortOrder
    netdisco_list?: SortOrder
    user_agent_list?: SortOrder
    syn_scan_port_list?: SortOrder
    auto_name?: SortOrder
    last_updated_ts?: SortOrder
    _count?: devicesCountOrderByAggregateInput
    _avg?: devicesAvgOrderByAggregateInput
    _max?: devicesMaxOrderByAggregateInput
    _min?: devicesMinOrderByAggregateInput
    _sum?: devicesSumOrderByAggregateInput
  }

  export type devicesScalarWhereWithAggregatesInput = {
    AND?: Enumerable<devicesScalarWhereWithAggregatesInput>
    OR?: Enumerable<devicesScalarWhereWithAggregatesInput>
    NOT?: Enumerable<devicesScalarWhereWithAggregatesInput>
    device_id?: StringWithAggregatesFilter | string
    ip?: StringWithAggregatesFilter | string
    mac?: StringWithAggregatesFilter | string
    dhcp_hostname_list?: StringWithAggregatesFilter | string
    netdisco_list?: StringWithAggregatesFilter | string
    user_agent_list?: StringWithAggregatesFilter | string
    syn_scan_port_list?: StringWithAggregatesFilter | string
    auto_name?: StringWithAggregatesFilter | string
    last_updated_ts?: FloatWithAggregatesFilter | number
  }

  export type flowsWhereInput = {
    AND?: Enumerable<flowsWhereInput>
    OR?: Enumerable<flowsWhereInput>
    NOT?: Enumerable<flowsWhereInput>
    id?: IntFilter | number
    device_id?: StringFilter | string
    device?: XOR<DevicesRelationFilter, devicesWhereInput>
    device_port?: IntFilter | number
    counterparty_ip?: StringFilter | string
    counterparty_port?: IntFilter | number
    counterparty_hostname?: StringFilter | string
    counterparty_friendly_name?: StringFilter | string
    counterparty_country?: StringFilter | string
    counterparty_is_ad_tracking?: IntFilter | number
    counterparty_local_device_id?: StringFilter | string
    transport_layer_protocol?: StringFilter | string
    uses_weak_encryption?: IntFilter | number
    ts?: FloatFilter | number
    ts_mod_60?: FloatFilter | number
    ts_mod_600?: FloatFilter | number
    ts_mod_3600?: FloatFilter | number
    window_size?: FloatFilter | number
    inbound_byte_count?: IntFilter | number
    outbound_byte_count?: IntFilter | number
    inbound_packet_count?: IntFilter | number
    outbound_packet_count?: IntFilter | number
  }

  export type flowsOrderByWithRelationInput = {
    id?: SortOrder
    device_id?: SortOrder
    device?: devicesOrderByWithRelationInput
    device_port?: SortOrder
    counterparty_ip?: SortOrder
    counterparty_port?: SortOrder
    counterparty_hostname?: SortOrder
    counterparty_friendly_name?: SortOrder
    counterparty_country?: SortOrder
    counterparty_is_ad_tracking?: SortOrder
    counterparty_local_device_id?: SortOrder
    transport_layer_protocol?: SortOrder
    uses_weak_encryption?: SortOrder
    ts?: SortOrder
    ts_mod_60?: SortOrder
    ts_mod_600?: SortOrder
    ts_mod_3600?: SortOrder
    window_size?: SortOrder
    inbound_byte_count?: SortOrder
    outbound_byte_count?: SortOrder
    inbound_packet_count?: SortOrder
    outbound_packet_count?: SortOrder
  }

  export type flowsWhereUniqueInput = {
    id?: number
  }

  export type flowsOrderByWithAggregationInput = {
    id?: SortOrder
    device_id?: SortOrder
    device_port?: SortOrder
    counterparty_ip?: SortOrder
    counterparty_port?: SortOrder
    counterparty_hostname?: SortOrder
    counterparty_friendly_name?: SortOrder
    counterparty_country?: SortOrder
    counterparty_is_ad_tracking?: SortOrder
    counterparty_local_device_id?: SortOrder
    transport_layer_protocol?: SortOrder
    uses_weak_encryption?: SortOrder
    ts?: SortOrder
    ts_mod_60?: SortOrder
    ts_mod_600?: SortOrder
    ts_mod_3600?: SortOrder
    window_size?: SortOrder
    inbound_byte_count?: SortOrder
    outbound_byte_count?: SortOrder
    inbound_packet_count?: SortOrder
    outbound_packet_count?: SortOrder
    _count?: flowsCountOrderByAggregateInput
    _avg?: flowsAvgOrderByAggregateInput
    _max?: flowsMaxOrderByAggregateInput
    _min?: flowsMinOrderByAggregateInput
    _sum?: flowsSumOrderByAggregateInput
  }

  export type flowsScalarWhereWithAggregatesInput = {
    AND?: Enumerable<flowsScalarWhereWithAggregatesInput>
    OR?: Enumerable<flowsScalarWhereWithAggregatesInput>
    NOT?: Enumerable<flowsScalarWhereWithAggregatesInput>
    id?: IntWithAggregatesFilter | number
    device_id?: StringWithAggregatesFilter | string
    device_port?: IntWithAggregatesFilter | number
    counterparty_ip?: StringWithAggregatesFilter | string
    counterparty_port?: IntWithAggregatesFilter | number
    counterparty_hostname?: StringWithAggregatesFilter | string
    counterparty_friendly_name?: StringWithAggregatesFilter | string
    counterparty_country?: StringWithAggregatesFilter | string
    counterparty_is_ad_tracking?: IntWithAggregatesFilter | number
    counterparty_local_device_id?: StringWithAggregatesFilter | string
    transport_layer_protocol?: StringWithAggregatesFilter | string
    uses_weak_encryption?: IntWithAggregatesFilter | number
    ts?: FloatWithAggregatesFilter | number
    ts_mod_60?: FloatWithAggregatesFilter | number
    ts_mod_600?: FloatWithAggregatesFilter | number
    ts_mod_3600?: FloatWithAggregatesFilter | number
    window_size?: FloatWithAggregatesFilter | number
    inbound_byte_count?: IntWithAggregatesFilter | number
    outbound_byte_count?: IntWithAggregatesFilter | number
    inbound_packet_count?: IntWithAggregatesFilter | number
    outbound_packet_count?: IntWithAggregatesFilter | number
  }

  export type counterpartiesCreateInput = {
    remote_ip: string
    hostname: string
    device_id: string
    source: string
    resolver_ip?: string
    ts: number
  }

  export type counterpartiesUncheckedCreateInput = {
    id?: number
    remote_ip: string
    hostname: string
    device_id: string
    source: string
    resolver_ip?: string
    ts: number
  }

  export type counterpartiesUpdateInput = {
    remote_ip?: StringFieldUpdateOperationsInput | string
    hostname?: StringFieldUpdateOperationsInput | string
    device_id?: StringFieldUpdateOperationsInput | string
    source?: StringFieldUpdateOperationsInput | string
    resolver_ip?: StringFieldUpdateOperationsInput | string
    ts?: FloatFieldUpdateOperationsInput | number
  }

  export type counterpartiesUncheckedUpdateInput = {
    id?: IntFieldUpdateOperationsInput | number
    remote_ip?: StringFieldUpdateOperationsInput | string
    hostname?: StringFieldUpdateOperationsInput | string
    device_id?: StringFieldUpdateOperationsInput | string
    source?: StringFieldUpdateOperationsInput | string
    resolver_ip?: StringFieldUpdateOperationsInput | string
    ts?: FloatFieldUpdateOperationsInput | number
  }

  export type counterpartiesUpdateManyMutationInput = {
    remote_ip?: StringFieldUpdateOperationsInput | string
    hostname?: StringFieldUpdateOperationsInput | string
    device_id?: StringFieldUpdateOperationsInput | string
    source?: StringFieldUpdateOperationsInput | string
    resolver_ip?: StringFieldUpdateOperationsInput | string
    ts?: FloatFieldUpdateOperationsInput | number
  }

  export type counterpartiesUncheckedUpdateManyInput = {
    id?: IntFieldUpdateOperationsInput | number
    remote_ip?: StringFieldUpdateOperationsInput | string
    hostname?: StringFieldUpdateOperationsInput | string
    device_id?: StringFieldUpdateOperationsInput | string
    source?: StringFieldUpdateOperationsInput | string
    resolver_ip?: StringFieldUpdateOperationsInput | string
    ts?: FloatFieldUpdateOperationsInput | number
  }

  export type devicesCreateInput = {
    device_id: string
    ip: string
    mac: string
    dhcp_hostname_list?: string
    netdisco_list?: string
    user_agent_list?: string
    syn_scan_port_list?: string
    auto_name?: string
    last_updated_ts: number
    flows?: flowsCreateNestedManyWithoutDeviceInput
  }

  export type devicesUncheckedCreateInput = {
    device_id: string
    ip: string
    mac: string
    dhcp_hostname_list?: string
    netdisco_list?: string
    user_agent_list?: string
    syn_scan_port_list?: string
    auto_name?: string
    last_updated_ts: number
    flows?: flowsUncheckedCreateNestedManyWithoutDeviceInput
  }

  export type devicesUpdateInput = {
    device_id?: StringFieldUpdateOperationsInput | string
    ip?: StringFieldUpdateOperationsInput | string
    mac?: StringFieldUpdateOperationsInput | string
    dhcp_hostname_list?: StringFieldUpdateOperationsInput | string
    netdisco_list?: StringFieldUpdateOperationsInput | string
    user_agent_list?: StringFieldUpdateOperationsInput | string
    syn_scan_port_list?: StringFieldUpdateOperationsInput | string
    auto_name?: StringFieldUpdateOperationsInput | string
    last_updated_ts?: FloatFieldUpdateOperationsInput | number
    flows?: flowsUpdateManyWithoutDeviceInput
  }

  export type devicesUncheckedUpdateInput = {
    device_id?: StringFieldUpdateOperationsInput | string
    ip?: StringFieldUpdateOperationsInput | string
    mac?: StringFieldUpdateOperationsInput | string
    dhcp_hostname_list?: StringFieldUpdateOperationsInput | string
    netdisco_list?: StringFieldUpdateOperationsInput | string
    user_agent_list?: StringFieldUpdateOperationsInput | string
    syn_scan_port_list?: StringFieldUpdateOperationsInput | string
    auto_name?: StringFieldUpdateOperationsInput | string
    last_updated_ts?: FloatFieldUpdateOperationsInput | number
    flows?: flowsUncheckedUpdateManyWithoutDeviceInput
  }

  export type devicesUpdateManyMutationInput = {
    device_id?: StringFieldUpdateOperationsInput | string
    ip?: StringFieldUpdateOperationsInput | string
    mac?: StringFieldUpdateOperationsInput | string
    dhcp_hostname_list?: StringFieldUpdateOperationsInput | string
    netdisco_list?: StringFieldUpdateOperationsInput | string
    user_agent_list?: StringFieldUpdateOperationsInput | string
    syn_scan_port_list?: StringFieldUpdateOperationsInput | string
    auto_name?: StringFieldUpdateOperationsInput | string
    last_updated_ts?: FloatFieldUpdateOperationsInput | number
  }

  export type devicesUncheckedUpdateManyInput = {
    device_id?: StringFieldUpdateOperationsInput | string
    ip?: StringFieldUpdateOperationsInput | string
    mac?: StringFieldUpdateOperationsInput | string
    dhcp_hostname_list?: StringFieldUpdateOperationsInput | string
    netdisco_list?: StringFieldUpdateOperationsInput | string
    user_agent_list?: StringFieldUpdateOperationsInput | string
    syn_scan_port_list?: StringFieldUpdateOperationsInput | string
    auto_name?: StringFieldUpdateOperationsInput | string
    last_updated_ts?: FloatFieldUpdateOperationsInput | number
  }

  export type flowsCreateInput = {
    device: devicesCreateNestedOneWithoutFlowsInput
    device_port?: number
    counterparty_ip: string
    counterparty_port?: number
    counterparty_hostname?: string
    counterparty_friendly_name?: string
    counterparty_country?: string
    counterparty_is_ad_tracking?: number
    counterparty_local_device_id?: string
    transport_layer_protocol?: string
    uses_weak_encryption?: number
    ts: number
    ts_mod_60: number
    ts_mod_600: number
    ts_mod_3600: number
    window_size: number
    inbound_byte_count?: number
    outbound_byte_count?: number
    inbound_packet_count?: number
    outbound_packet_count?: number
  }

  export type flowsUncheckedCreateInput = {
    id?: number
    device_id: string
    device_port?: number
    counterparty_ip: string
    counterparty_port?: number
    counterparty_hostname?: string
    counterparty_friendly_name?: string
    counterparty_country?: string
    counterparty_is_ad_tracking?: number
    counterparty_local_device_id?: string
    transport_layer_protocol?: string
    uses_weak_encryption?: number
    ts: number
    ts_mod_60: number
    ts_mod_600: number
    ts_mod_3600: number
    window_size: number
    inbound_byte_count?: number
    outbound_byte_count?: number
    inbound_packet_count?: number
    outbound_packet_count?: number
  }

  export type flowsUpdateInput = {
    device?: devicesUpdateOneRequiredWithoutFlowsInput
    device_port?: IntFieldUpdateOperationsInput | number
    counterparty_ip?: StringFieldUpdateOperationsInput | string
    counterparty_port?: IntFieldUpdateOperationsInput | number
    counterparty_hostname?: StringFieldUpdateOperationsInput | string
    counterparty_friendly_name?: StringFieldUpdateOperationsInput | string
    counterparty_country?: StringFieldUpdateOperationsInput | string
    counterparty_is_ad_tracking?: IntFieldUpdateOperationsInput | number
    counterparty_local_device_id?: StringFieldUpdateOperationsInput | string
    transport_layer_protocol?: StringFieldUpdateOperationsInput | string
    uses_weak_encryption?: IntFieldUpdateOperationsInput | number
    ts?: FloatFieldUpdateOperationsInput | number
    ts_mod_60?: FloatFieldUpdateOperationsInput | number
    ts_mod_600?: FloatFieldUpdateOperationsInput | number
    ts_mod_3600?: FloatFieldUpdateOperationsInput | number
    window_size?: FloatFieldUpdateOperationsInput | number
    inbound_byte_count?: IntFieldUpdateOperationsInput | number
    outbound_byte_count?: IntFieldUpdateOperationsInput | number
    inbound_packet_count?: IntFieldUpdateOperationsInput | number
    outbound_packet_count?: IntFieldUpdateOperationsInput | number
  }

  export type flowsUncheckedUpdateInput = {
    id?: IntFieldUpdateOperationsInput | number
    device_id?: StringFieldUpdateOperationsInput | string
    device_port?: IntFieldUpdateOperationsInput | number
    counterparty_ip?: StringFieldUpdateOperationsInput | string
    counterparty_port?: IntFieldUpdateOperationsInput | number
    counterparty_hostname?: StringFieldUpdateOperationsInput | string
    counterparty_friendly_name?: StringFieldUpdateOperationsInput | string
    counterparty_country?: StringFieldUpdateOperationsInput | string
    counterparty_is_ad_tracking?: IntFieldUpdateOperationsInput | number
    counterparty_local_device_id?: StringFieldUpdateOperationsInput | string
    transport_layer_protocol?: StringFieldUpdateOperationsInput | string
    uses_weak_encryption?: IntFieldUpdateOperationsInput | number
    ts?: FloatFieldUpdateOperationsInput | number
    ts_mod_60?: FloatFieldUpdateOperationsInput | number
    ts_mod_600?: FloatFieldUpdateOperationsInput | number
    ts_mod_3600?: FloatFieldUpdateOperationsInput | number
    window_size?: FloatFieldUpdateOperationsInput | number
    inbound_byte_count?: IntFieldUpdateOperationsInput | number
    outbound_byte_count?: IntFieldUpdateOperationsInput | number
    inbound_packet_count?: IntFieldUpdateOperationsInput | number
    outbound_packet_count?: IntFieldUpdateOperationsInput | number
  }

  export type flowsUpdateManyMutationInput = {
    device_port?: IntFieldUpdateOperationsInput | number
    counterparty_ip?: StringFieldUpdateOperationsInput | string
    counterparty_port?: IntFieldUpdateOperationsInput | number
    counterparty_hostname?: StringFieldUpdateOperationsInput | string
    counterparty_friendly_name?: StringFieldUpdateOperationsInput | string
    counterparty_country?: StringFieldUpdateOperationsInput | string
    counterparty_is_ad_tracking?: IntFieldUpdateOperationsInput | number
    counterparty_local_device_id?: StringFieldUpdateOperationsInput | string
    transport_layer_protocol?: StringFieldUpdateOperationsInput | string
    uses_weak_encryption?: IntFieldUpdateOperationsInput | number
    ts?: FloatFieldUpdateOperationsInput | number
    ts_mod_60?: FloatFieldUpdateOperationsInput | number
    ts_mod_600?: FloatFieldUpdateOperationsInput | number
    ts_mod_3600?: FloatFieldUpdateOperationsInput | number
    window_size?: FloatFieldUpdateOperationsInput | number
    inbound_byte_count?: IntFieldUpdateOperationsInput | number
    outbound_byte_count?: IntFieldUpdateOperationsInput | number
    inbound_packet_count?: IntFieldUpdateOperationsInput | number
    outbound_packet_count?: IntFieldUpdateOperationsInput | number
  }

  export type flowsUncheckedUpdateManyInput = {
    id?: IntFieldUpdateOperationsInput | number
    device_id?: StringFieldUpdateOperationsInput | string
    device_port?: IntFieldUpdateOperationsInput | number
    counterparty_ip?: StringFieldUpdateOperationsInput | string
    counterparty_port?: IntFieldUpdateOperationsInput | number
    counterparty_hostname?: StringFieldUpdateOperationsInput | string
    counterparty_friendly_name?: StringFieldUpdateOperationsInput | string
    counterparty_country?: StringFieldUpdateOperationsInput | string
    counterparty_is_ad_tracking?: IntFieldUpdateOperationsInput | number
    counterparty_local_device_id?: StringFieldUpdateOperationsInput | string
    transport_layer_protocol?: StringFieldUpdateOperationsInput | string
    uses_weak_encryption?: IntFieldUpdateOperationsInput | number
    ts?: FloatFieldUpdateOperationsInput | number
    ts_mod_60?: FloatFieldUpdateOperationsInput | number
    ts_mod_600?: FloatFieldUpdateOperationsInput | number
    ts_mod_3600?: FloatFieldUpdateOperationsInput | number
    window_size?: FloatFieldUpdateOperationsInput | number
    inbound_byte_count?: IntFieldUpdateOperationsInput | number
    outbound_byte_count?: IntFieldUpdateOperationsInput | number
    inbound_packet_count?: IntFieldUpdateOperationsInput | number
    outbound_packet_count?: IntFieldUpdateOperationsInput | number
  }

  export type IntFilter = {
    equals?: number
    in?: Enumerable<number>
    notIn?: Enumerable<number>
    lt?: number
    lte?: number
    gt?: number
    gte?: number
    not?: NestedIntFilter | number
  }

  export type StringFilter = {
    equals?: string
    in?: Enumerable<string>
    notIn?: Enumerable<string>
    lt?: string
    lte?: string
    gt?: string
    gte?: string
    contains?: string
    startsWith?: string
    endsWith?: string
    not?: NestedStringFilter | string
  }

  export type FloatFilter = {
    equals?: number
    in?: Enumerable<number>
    notIn?: Enumerable<number>
    lt?: number
    lte?: number
    gt?: number
    gte?: number
    not?: NestedFloatFilter | number
  }

  export type counterpartiesCountOrderByAggregateInput = {
    id?: SortOrder
    remote_ip?: SortOrder
    hostname?: SortOrder
    device_id?: SortOrder
    source?: SortOrder
    resolver_ip?: SortOrder
    ts?: SortOrder
  }

  export type counterpartiesAvgOrderByAggregateInput = {
    id?: SortOrder
    ts?: SortOrder
  }

  export type counterpartiesMaxOrderByAggregateInput = {
    id?: SortOrder
    remote_ip?: SortOrder
    hostname?: SortOrder
    device_id?: SortOrder
    source?: SortOrder
    resolver_ip?: SortOrder
    ts?: SortOrder
  }

  export type counterpartiesMinOrderByAggregateInput = {
    id?: SortOrder
    remote_ip?: SortOrder
    hostname?: SortOrder
    device_id?: SortOrder
    source?: SortOrder
    resolver_ip?: SortOrder
    ts?: SortOrder
  }

  export type counterpartiesSumOrderByAggregateInput = {
    id?: SortOrder
    ts?: SortOrder
  }

  export type IntWithAggregatesFilter = {
    equals?: number
    in?: Enumerable<number>
    notIn?: Enumerable<number>
    lt?: number
    lte?: number
    gt?: number
    gte?: number
    not?: NestedIntWithAggregatesFilter | number
    _count?: NestedIntFilter
    _avg?: NestedFloatFilter
    _sum?: NestedIntFilter
    _min?: NestedIntFilter
    _max?: NestedIntFilter
  }

  export type StringWithAggregatesFilter = {
    equals?: string
    in?: Enumerable<string>
    notIn?: Enumerable<string>
    lt?: string
    lte?: string
    gt?: string
    gte?: string
    contains?: string
    startsWith?: string
    endsWith?: string
    not?: NestedStringWithAggregatesFilter | string
    _count?: NestedIntFilter
    _min?: NestedStringFilter
    _max?: NestedStringFilter
  }

  export type FloatWithAggregatesFilter = {
    equals?: number
    in?: Enumerable<number>
    notIn?: Enumerable<number>
    lt?: number
    lte?: number
    gt?: number
    gte?: number
    not?: NestedFloatWithAggregatesFilter | number
    _count?: NestedIntFilter
    _avg?: NestedFloatFilter
    _sum?: NestedFloatFilter
    _min?: NestedFloatFilter
    _max?: NestedFloatFilter
  }

  export type FlowsListRelationFilter = {
    every?: flowsWhereInput
    some?: flowsWhereInput
    none?: flowsWhereInput
  }

  export type flowsOrderByRelationAggregateInput = {
    _count?: SortOrder
  }

  export type devicesCountOrderByAggregateInput = {
    device_id?: SortOrder
    ip?: SortOrder
    mac?: SortOrder
    dhcp_hostname_list?: SortOrder
    netdisco_list?: SortOrder
    user_agent_list?: SortOrder
    syn_scan_port_list?: SortOrder
    auto_name?: SortOrder
    last_updated_ts?: SortOrder
  }

  export type devicesAvgOrderByAggregateInput = {
    last_updated_ts?: SortOrder
  }

  export type devicesMaxOrderByAggregateInput = {
    device_id?: SortOrder
    ip?: SortOrder
    mac?: SortOrder
    dhcp_hostname_list?: SortOrder
    netdisco_list?: SortOrder
    user_agent_list?: SortOrder
    syn_scan_port_list?: SortOrder
    auto_name?: SortOrder
    last_updated_ts?: SortOrder
  }

  export type devicesMinOrderByAggregateInput = {
    device_id?: SortOrder
    ip?: SortOrder
    mac?: SortOrder
    dhcp_hostname_list?: SortOrder
    netdisco_list?: SortOrder
    user_agent_list?: SortOrder
    syn_scan_port_list?: SortOrder
    auto_name?: SortOrder
    last_updated_ts?: SortOrder
  }

  export type devicesSumOrderByAggregateInput = {
    last_updated_ts?: SortOrder
  }

  export type DevicesRelationFilter = {
    is?: devicesWhereInput
    isNot?: devicesWhereInput
  }

  export type flowsCountOrderByAggregateInput = {
    id?: SortOrder
    device_id?: SortOrder
    device_port?: SortOrder
    counterparty_ip?: SortOrder
    counterparty_port?: SortOrder
    counterparty_hostname?: SortOrder
    counterparty_friendly_name?: SortOrder
    counterparty_country?: SortOrder
    counterparty_is_ad_tracking?: SortOrder
    counterparty_local_device_id?: SortOrder
    transport_layer_protocol?: SortOrder
    uses_weak_encryption?: SortOrder
    ts?: SortOrder
    ts_mod_60?: SortOrder
    ts_mod_600?: SortOrder
    ts_mod_3600?: SortOrder
    window_size?: SortOrder
    inbound_byte_count?: SortOrder
    outbound_byte_count?: SortOrder
    inbound_packet_count?: SortOrder
    outbound_packet_count?: SortOrder
  }

  export type flowsAvgOrderByAggregateInput = {
    id?: SortOrder
    device_port?: SortOrder
    counterparty_port?: SortOrder
    counterparty_is_ad_tracking?: SortOrder
    uses_weak_encryption?: SortOrder
    ts?: SortOrder
    ts_mod_60?: SortOrder
    ts_mod_600?: SortOrder
    ts_mod_3600?: SortOrder
    window_size?: SortOrder
    inbound_byte_count?: SortOrder
    outbound_byte_count?: SortOrder
    inbound_packet_count?: SortOrder
    outbound_packet_count?: SortOrder
  }

  export type flowsMaxOrderByAggregateInput = {
    id?: SortOrder
    device_id?: SortOrder
    device_port?: SortOrder
    counterparty_ip?: SortOrder
    counterparty_port?: SortOrder
    counterparty_hostname?: SortOrder
    counterparty_friendly_name?: SortOrder
    counterparty_country?: SortOrder
    counterparty_is_ad_tracking?: SortOrder
    counterparty_local_device_id?: SortOrder
    transport_layer_protocol?: SortOrder
    uses_weak_encryption?: SortOrder
    ts?: SortOrder
    ts_mod_60?: SortOrder
    ts_mod_600?: SortOrder
    ts_mod_3600?: SortOrder
    window_size?: SortOrder
    inbound_byte_count?: SortOrder
    outbound_byte_count?: SortOrder
    inbound_packet_count?: SortOrder
    outbound_packet_count?: SortOrder
  }

  export type flowsMinOrderByAggregateInput = {
    id?: SortOrder
    device_id?: SortOrder
    device_port?: SortOrder
    counterparty_ip?: SortOrder
    counterparty_port?: SortOrder
    counterparty_hostname?: SortOrder
    counterparty_friendly_name?: SortOrder
    counterparty_country?: SortOrder
    counterparty_is_ad_tracking?: SortOrder
    counterparty_local_device_id?: SortOrder
    transport_layer_protocol?: SortOrder
    uses_weak_encryption?: SortOrder
    ts?: SortOrder
    ts_mod_60?: SortOrder
    ts_mod_600?: SortOrder
    ts_mod_3600?: SortOrder
    window_size?: SortOrder
    inbound_byte_count?: SortOrder
    outbound_byte_count?: SortOrder
    inbound_packet_count?: SortOrder
    outbound_packet_count?: SortOrder
  }

  export type flowsSumOrderByAggregateInput = {
    id?: SortOrder
    device_port?: SortOrder
    counterparty_port?: SortOrder
    counterparty_is_ad_tracking?: SortOrder
    uses_weak_encryption?: SortOrder
    ts?: SortOrder
    ts_mod_60?: SortOrder
    ts_mod_600?: SortOrder
    ts_mod_3600?: SortOrder
    window_size?: SortOrder
    inbound_byte_count?: SortOrder
    outbound_byte_count?: SortOrder
    inbound_packet_count?: SortOrder
    outbound_packet_count?: SortOrder
  }

  export type StringFieldUpdateOperationsInput = {
    set?: string
  }

  export type FloatFieldUpdateOperationsInput = {
    set?: number
    increment?: number
    decrement?: number
    multiply?: number
    divide?: number
  }

  export type IntFieldUpdateOperationsInput = {
    set?: number
    increment?: number
    decrement?: number
    multiply?: number
    divide?: number
  }

  export type flowsCreateNestedManyWithoutDeviceInput = {
    create?: XOR<Enumerable<flowsCreateWithoutDeviceInput>, Enumerable<flowsUncheckedCreateWithoutDeviceInput>>
    connectOrCreate?: Enumerable<flowsCreateOrConnectWithoutDeviceInput>
    connect?: Enumerable<flowsWhereUniqueInput>
  }

  export type flowsUncheckedCreateNestedManyWithoutDeviceInput = {
    create?: XOR<Enumerable<flowsCreateWithoutDeviceInput>, Enumerable<flowsUncheckedCreateWithoutDeviceInput>>
    connectOrCreate?: Enumerable<flowsCreateOrConnectWithoutDeviceInput>
    connect?: Enumerable<flowsWhereUniqueInput>
  }

  export type flowsUpdateManyWithoutDeviceInput = {
    create?: XOR<Enumerable<flowsCreateWithoutDeviceInput>, Enumerable<flowsUncheckedCreateWithoutDeviceInput>>
    connectOrCreate?: Enumerable<flowsCreateOrConnectWithoutDeviceInput>
    upsert?: Enumerable<flowsUpsertWithWhereUniqueWithoutDeviceInput>
    set?: Enumerable<flowsWhereUniqueInput>
    disconnect?: Enumerable<flowsWhereUniqueInput>
    delete?: Enumerable<flowsWhereUniqueInput>
    connect?: Enumerable<flowsWhereUniqueInput>
    update?: Enumerable<flowsUpdateWithWhereUniqueWithoutDeviceInput>
    updateMany?: Enumerable<flowsUpdateManyWithWhereWithoutDeviceInput>
    deleteMany?: Enumerable<flowsScalarWhereInput>
  }

  export type flowsUncheckedUpdateManyWithoutDeviceInput = {
    create?: XOR<Enumerable<flowsCreateWithoutDeviceInput>, Enumerable<flowsUncheckedCreateWithoutDeviceInput>>
    connectOrCreate?: Enumerable<flowsCreateOrConnectWithoutDeviceInput>
    upsert?: Enumerable<flowsUpsertWithWhereUniqueWithoutDeviceInput>
    set?: Enumerable<flowsWhereUniqueInput>
    disconnect?: Enumerable<flowsWhereUniqueInput>
    delete?: Enumerable<flowsWhereUniqueInput>
    connect?: Enumerable<flowsWhereUniqueInput>
    update?: Enumerable<flowsUpdateWithWhereUniqueWithoutDeviceInput>
    updateMany?: Enumerable<flowsUpdateManyWithWhereWithoutDeviceInput>
    deleteMany?: Enumerable<flowsScalarWhereInput>
  }

  export type devicesCreateNestedOneWithoutFlowsInput = {
    create?: XOR<devicesCreateWithoutFlowsInput, devicesUncheckedCreateWithoutFlowsInput>
    connectOrCreate?: devicesCreateOrConnectWithoutFlowsInput
    connect?: devicesWhereUniqueInput
  }

  export type devicesUpdateOneRequiredWithoutFlowsInput = {
    create?: XOR<devicesCreateWithoutFlowsInput, devicesUncheckedCreateWithoutFlowsInput>
    connectOrCreate?: devicesCreateOrConnectWithoutFlowsInput
    upsert?: devicesUpsertWithoutFlowsInput
    connect?: devicesWhereUniqueInput
    update?: XOR<devicesUpdateWithoutFlowsInput, devicesUncheckedUpdateWithoutFlowsInput>
  }

  export type NestedIntFilter = {
    equals?: number
    in?: Enumerable<number>
    notIn?: Enumerable<number>
    lt?: number
    lte?: number
    gt?: number
    gte?: number
    not?: NestedIntFilter | number
  }

  export type NestedStringFilter = {
    equals?: string
    in?: Enumerable<string>
    notIn?: Enumerable<string>
    lt?: string
    lte?: string
    gt?: string
    gte?: string
    contains?: string
    startsWith?: string
    endsWith?: string
    not?: NestedStringFilter | string
  }

  export type NestedFloatFilter = {
    equals?: number
    in?: Enumerable<number>
    notIn?: Enumerable<number>
    lt?: number
    lte?: number
    gt?: number
    gte?: number
    not?: NestedFloatFilter | number
  }

  export type NestedIntWithAggregatesFilter = {
    equals?: number
    in?: Enumerable<number>
    notIn?: Enumerable<number>
    lt?: number
    lte?: number
    gt?: number
    gte?: number
    not?: NestedIntWithAggregatesFilter | number
    _count?: NestedIntFilter
    _avg?: NestedFloatFilter
    _sum?: NestedIntFilter
    _min?: NestedIntFilter
    _max?: NestedIntFilter
  }

  export type NestedStringWithAggregatesFilter = {
    equals?: string
    in?: Enumerable<string>
    notIn?: Enumerable<string>
    lt?: string
    lte?: string
    gt?: string
    gte?: string
    contains?: string
    startsWith?: string
    endsWith?: string
    not?: NestedStringWithAggregatesFilter | string
    _count?: NestedIntFilter
    _min?: NestedStringFilter
    _max?: NestedStringFilter
  }

  export type NestedFloatWithAggregatesFilter = {
    equals?: number
    in?: Enumerable<number>
    notIn?: Enumerable<number>
    lt?: number
    lte?: number
    gt?: number
    gte?: number
    not?: NestedFloatWithAggregatesFilter | number
    _count?: NestedIntFilter
    _avg?: NestedFloatFilter
    _sum?: NestedFloatFilter
    _min?: NestedFloatFilter
    _max?: NestedFloatFilter
  }

  export type flowsCreateWithoutDeviceInput = {
    device_port?: number
    counterparty_ip: string
    counterparty_port?: number
    counterparty_hostname?: string
    counterparty_friendly_name?: string
    counterparty_country?: string
    counterparty_is_ad_tracking?: number
    counterparty_local_device_id?: string
    transport_layer_protocol?: string
    uses_weak_encryption?: number
    ts: number
    ts_mod_60: number
    ts_mod_600: number
    ts_mod_3600: number
    window_size: number
    inbound_byte_count?: number
    outbound_byte_count?: number
    inbound_packet_count?: number
    outbound_packet_count?: number
  }

  export type flowsUncheckedCreateWithoutDeviceInput = {
    id?: number
    device_port?: number
    counterparty_ip: string
    counterparty_port?: number
    counterparty_hostname?: string
    counterparty_friendly_name?: string
    counterparty_country?: string
    counterparty_is_ad_tracking?: number
    counterparty_local_device_id?: string
    transport_layer_protocol?: string
    uses_weak_encryption?: number
    ts: number
    ts_mod_60: number
    ts_mod_600: number
    ts_mod_3600: number
    window_size: number
    inbound_byte_count?: number
    outbound_byte_count?: number
    inbound_packet_count?: number
    outbound_packet_count?: number
  }

  export type flowsCreateOrConnectWithoutDeviceInput = {
    where: flowsWhereUniqueInput
    create: XOR<flowsCreateWithoutDeviceInput, flowsUncheckedCreateWithoutDeviceInput>
  }

  export type flowsUpsertWithWhereUniqueWithoutDeviceInput = {
    where: flowsWhereUniqueInput
    update: XOR<flowsUpdateWithoutDeviceInput, flowsUncheckedUpdateWithoutDeviceInput>
    create: XOR<flowsCreateWithoutDeviceInput, flowsUncheckedCreateWithoutDeviceInput>
  }

  export type flowsUpdateWithWhereUniqueWithoutDeviceInput = {
    where: flowsWhereUniqueInput
    data: XOR<flowsUpdateWithoutDeviceInput, flowsUncheckedUpdateWithoutDeviceInput>
  }

  export type flowsUpdateManyWithWhereWithoutDeviceInput = {
    where: flowsScalarWhereInput
    data: XOR<flowsUpdateManyMutationInput, flowsUncheckedUpdateManyWithoutFlowsInput>
  }

  export type flowsScalarWhereInput = {
    AND?: Enumerable<flowsScalarWhereInput>
    OR?: Enumerable<flowsScalarWhereInput>
    NOT?: Enumerable<flowsScalarWhereInput>
    id?: IntFilter | number
    device_id?: StringFilter | string
    device_port?: IntFilter | number
    counterparty_ip?: StringFilter | string
    counterparty_port?: IntFilter | number
    counterparty_hostname?: StringFilter | string
    counterparty_friendly_name?: StringFilter | string
    counterparty_country?: StringFilter | string
    counterparty_is_ad_tracking?: IntFilter | number
    counterparty_local_device_id?: StringFilter | string
    transport_layer_protocol?: StringFilter | string
    uses_weak_encryption?: IntFilter | number
    ts?: FloatFilter | number
    ts_mod_60?: FloatFilter | number
    ts_mod_600?: FloatFilter | number
    ts_mod_3600?: FloatFilter | number
    window_size?: FloatFilter | number
    inbound_byte_count?: IntFilter | number
    outbound_byte_count?: IntFilter | number
    inbound_packet_count?: IntFilter | number
    outbound_packet_count?: IntFilter | number
  }

  export type devicesCreateWithoutFlowsInput = {
    device_id: string
    ip: string
    mac: string
    dhcp_hostname_list?: string
    netdisco_list?: string
    user_agent_list?: string
    syn_scan_port_list?: string
    auto_name?: string
    last_updated_ts: number
  }

  export type devicesUncheckedCreateWithoutFlowsInput = {
    device_id: string
    ip: string
    mac: string
    dhcp_hostname_list?: string
    netdisco_list?: string
    user_agent_list?: string
    syn_scan_port_list?: string
    auto_name?: string
    last_updated_ts: number
  }

  export type devicesCreateOrConnectWithoutFlowsInput = {
    where: devicesWhereUniqueInput
    create: XOR<devicesCreateWithoutFlowsInput, devicesUncheckedCreateWithoutFlowsInput>
  }

  export type devicesUpsertWithoutFlowsInput = {
    update: XOR<devicesUpdateWithoutFlowsInput, devicesUncheckedUpdateWithoutFlowsInput>
    create: XOR<devicesCreateWithoutFlowsInput, devicesUncheckedCreateWithoutFlowsInput>
  }

  export type devicesUpdateWithoutFlowsInput = {
    device_id?: StringFieldUpdateOperationsInput | string
    ip?: StringFieldUpdateOperationsInput | string
    mac?: StringFieldUpdateOperationsInput | string
    dhcp_hostname_list?: StringFieldUpdateOperationsInput | string
    netdisco_list?: StringFieldUpdateOperationsInput | string
    user_agent_list?: StringFieldUpdateOperationsInput | string
    syn_scan_port_list?: StringFieldUpdateOperationsInput | string
    auto_name?: StringFieldUpdateOperationsInput | string
    last_updated_ts?: FloatFieldUpdateOperationsInput | number
  }

  export type devicesUncheckedUpdateWithoutFlowsInput = {
    device_id?: StringFieldUpdateOperationsInput | string
    ip?: StringFieldUpdateOperationsInput | string
    mac?: StringFieldUpdateOperationsInput | string
    dhcp_hostname_list?: StringFieldUpdateOperationsInput | string
    netdisco_list?: StringFieldUpdateOperationsInput | string
    user_agent_list?: StringFieldUpdateOperationsInput | string
    syn_scan_port_list?: StringFieldUpdateOperationsInput | string
    auto_name?: StringFieldUpdateOperationsInput | string
    last_updated_ts?: FloatFieldUpdateOperationsInput | number
  }

  export type flowsUpdateWithoutDeviceInput = {
    device_port?: IntFieldUpdateOperationsInput | number
    counterparty_ip?: StringFieldUpdateOperationsInput | string
    counterparty_port?: IntFieldUpdateOperationsInput | number
    counterparty_hostname?: StringFieldUpdateOperationsInput | string
    counterparty_friendly_name?: StringFieldUpdateOperationsInput | string
    counterparty_country?: StringFieldUpdateOperationsInput | string
    counterparty_is_ad_tracking?: IntFieldUpdateOperationsInput | number
    counterparty_local_device_id?: StringFieldUpdateOperationsInput | string
    transport_layer_protocol?: StringFieldUpdateOperationsInput | string
    uses_weak_encryption?: IntFieldUpdateOperationsInput | number
    ts?: FloatFieldUpdateOperationsInput | number
    ts_mod_60?: FloatFieldUpdateOperationsInput | number
    ts_mod_600?: FloatFieldUpdateOperationsInput | number
    ts_mod_3600?: FloatFieldUpdateOperationsInput | number
    window_size?: FloatFieldUpdateOperationsInput | number
    inbound_byte_count?: IntFieldUpdateOperationsInput | number
    outbound_byte_count?: IntFieldUpdateOperationsInput | number
    inbound_packet_count?: IntFieldUpdateOperationsInput | number
    outbound_packet_count?: IntFieldUpdateOperationsInput | number
  }

  export type flowsUncheckedUpdateWithoutDeviceInput = {
    id?: IntFieldUpdateOperationsInput | number
    device_port?: IntFieldUpdateOperationsInput | number
    counterparty_ip?: StringFieldUpdateOperationsInput | string
    counterparty_port?: IntFieldUpdateOperationsInput | number
    counterparty_hostname?: StringFieldUpdateOperationsInput | string
    counterparty_friendly_name?: StringFieldUpdateOperationsInput | string
    counterparty_country?: StringFieldUpdateOperationsInput | string
    counterparty_is_ad_tracking?: IntFieldUpdateOperationsInput | number
    counterparty_local_device_id?: StringFieldUpdateOperationsInput | string
    transport_layer_protocol?: StringFieldUpdateOperationsInput | string
    uses_weak_encryption?: IntFieldUpdateOperationsInput | number
    ts?: FloatFieldUpdateOperationsInput | number
    ts_mod_60?: FloatFieldUpdateOperationsInput | number
    ts_mod_600?: FloatFieldUpdateOperationsInput | number
    ts_mod_3600?: FloatFieldUpdateOperationsInput | number
    window_size?: FloatFieldUpdateOperationsInput | number
    inbound_byte_count?: IntFieldUpdateOperationsInput | number
    outbound_byte_count?: IntFieldUpdateOperationsInput | number
    inbound_packet_count?: IntFieldUpdateOperationsInput | number
    outbound_packet_count?: IntFieldUpdateOperationsInput | number
  }

  export type flowsUncheckedUpdateManyWithoutFlowsInput = {
    id?: IntFieldUpdateOperationsInput | number
    device_port?: IntFieldUpdateOperationsInput | number
    counterparty_ip?: StringFieldUpdateOperationsInput | string
    counterparty_port?: IntFieldUpdateOperationsInput | number
    counterparty_hostname?: StringFieldUpdateOperationsInput | string
    counterparty_friendly_name?: StringFieldUpdateOperationsInput | string
    counterparty_country?: StringFieldUpdateOperationsInput | string
    counterparty_is_ad_tracking?: IntFieldUpdateOperationsInput | number
    counterparty_local_device_id?: StringFieldUpdateOperationsInput | string
    transport_layer_protocol?: StringFieldUpdateOperationsInput | string
    uses_weak_encryption?: IntFieldUpdateOperationsInput | number
    ts?: FloatFieldUpdateOperationsInput | number
    ts_mod_60?: FloatFieldUpdateOperationsInput | number
    ts_mod_600?: FloatFieldUpdateOperationsInput | number
    ts_mod_3600?: FloatFieldUpdateOperationsInput | number
    window_size?: FloatFieldUpdateOperationsInput | number
    inbound_byte_count?: IntFieldUpdateOperationsInput | number
    outbound_byte_count?: IntFieldUpdateOperationsInput | number
    inbound_packet_count?: IntFieldUpdateOperationsInput | number
    outbound_packet_count?: IntFieldUpdateOperationsInput | number
  }



  /**
   * Batch Payload for updateMany & deleteMany & createMany
   */

  export type BatchPayload = {
    count: number
  }

  /**
   * DMMF
   */
  export const dmmf: runtime.DMMF.Document;
}