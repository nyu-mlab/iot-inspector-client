
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
 * Model device_info
 * 
 */
export type device_info = {
  device_id: string
  device_name: string
  vendor_name: string
  tag_list: string
  is_inspected: number
  is_blocked: number
}

/**
 * Model state_kv
 * 
 */
export type state_kv = {
  state_key: string
  state_value_json: string
}

/**
 * Model user_configs
 * 
 */
export type user_configs = {
  id: number
  is_consent: number
  is_auto_inspect_device: number
  is_contribute_to_research: number
}


/**
 * ##  Prisma Client ʲˢ
 * 
 * Type-safe database client for TypeScript & Node.js
 * @example
 * ```
 * const prisma = new PrismaClient()
 * // Fetch zero or more Device_infos
 * const device_infos = await prisma.device_info.findMany()
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
   * // Fetch zero or more Device_infos
   * const device_infos = await prisma.device_info.findMany()
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
   * `prisma.device_info`: Exposes CRUD operations for the **device_info** model.
    * Example usage:
    * ```ts
    * // Fetch zero or more Device_infos
    * const device_infos = await prisma.device_info.findMany()
    * ```
    */
  get device_info(): Prisma.device_infoDelegate<GlobalReject>;

  /**
   * `prisma.state_kv`: Exposes CRUD operations for the **state_kv** model.
    * Example usage:
    * ```ts
    * // Fetch zero or more State_kvs
    * const state_kvs = await prisma.state_kv.findMany()
    * ```
    */
  get state_kv(): Prisma.state_kvDelegate<GlobalReject>;

  /**
   * `prisma.user_configs`: Exposes CRUD operations for the **user_configs** model.
    * Example usage:
    * ```ts
    * // Fetch zero or more User_configs
    * const user_configs = await prisma.user_configs.findMany()
    * ```
    */
  get user_configs(): Prisma.user_configsDelegate<GlobalReject>;
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
   * Query Engine version: da41d2bb3406da22087b849f0e911199ba4fbf11
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
    device_info: 'device_info',
    state_kv: 'state_kv',
    user_configs: 'user_configs'
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
   * Models
   */

  /**
   * Model device_info
   */


  export type AggregateDevice_info = {
    _count: Device_infoCountAggregateOutputType | null
    _avg: Device_infoAvgAggregateOutputType | null
    _sum: Device_infoSumAggregateOutputType | null
    _min: Device_infoMinAggregateOutputType | null
    _max: Device_infoMaxAggregateOutputType | null
  }

  export type Device_infoAvgAggregateOutputType = {
    is_inspected: number | null
    is_blocked: number | null
  }

  export type Device_infoSumAggregateOutputType = {
    is_inspected: number | null
    is_blocked: number | null
  }

  export type Device_infoMinAggregateOutputType = {
    device_id: string | null
    device_name: string | null
    vendor_name: string | null
    tag_list: string | null
    is_inspected: number | null
    is_blocked: number | null
  }

  export type Device_infoMaxAggregateOutputType = {
    device_id: string | null
    device_name: string | null
    vendor_name: string | null
    tag_list: string | null
    is_inspected: number | null
    is_blocked: number | null
  }

  export type Device_infoCountAggregateOutputType = {
    device_id: number
    device_name: number
    vendor_name: number
    tag_list: number
    is_inspected: number
    is_blocked: number
    _all: number
  }


  export type Device_infoAvgAggregateInputType = {
    is_inspected?: true
    is_blocked?: true
  }

  export type Device_infoSumAggregateInputType = {
    is_inspected?: true
    is_blocked?: true
  }

  export type Device_infoMinAggregateInputType = {
    device_id?: true
    device_name?: true
    vendor_name?: true
    tag_list?: true
    is_inspected?: true
    is_blocked?: true
  }

  export type Device_infoMaxAggregateInputType = {
    device_id?: true
    device_name?: true
    vendor_name?: true
    tag_list?: true
    is_inspected?: true
    is_blocked?: true
  }

  export type Device_infoCountAggregateInputType = {
    device_id?: true
    device_name?: true
    vendor_name?: true
    tag_list?: true
    is_inspected?: true
    is_blocked?: true
    _all?: true
  }

  export type Device_infoAggregateArgs = {
    /**
     * Filter which device_info to aggregate.
     * 
    **/
    where?: device_infoWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of device_infos to fetch.
     * 
    **/
    orderBy?: Enumerable<device_infoOrderByWithRelationInput>
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the start position
     * 
    **/
    cursor?: device_infoWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` device_infos from the position of the cursor.
     * 
    **/
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` device_infos.
     * 
    **/
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Count returned device_infos
    **/
    _count?: true | Device_infoCountAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to average
    **/
    _avg?: Device_infoAvgAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to sum
    **/
    _sum?: Device_infoSumAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to find the minimum value
    **/
    _min?: Device_infoMinAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to find the maximum value
    **/
    _max?: Device_infoMaxAggregateInputType
  }

  export type GetDevice_infoAggregateType<T extends Device_infoAggregateArgs> = {
        [P in keyof T & keyof AggregateDevice_info]: P extends '_count' | 'count'
      ? T[P] extends true
        ? number
        : GetScalarType<T[P], AggregateDevice_info[P]>
      : GetScalarType<T[P], AggregateDevice_info[P]>
  }




  export type Device_infoGroupByArgs = {
    where?: device_infoWhereInput
    orderBy?: Enumerable<device_infoOrderByWithAggregationInput>
    by: Array<Device_infoScalarFieldEnum>
    having?: device_infoScalarWhereWithAggregatesInput
    take?: number
    skip?: number
    _count?: Device_infoCountAggregateInputType | true
    _avg?: Device_infoAvgAggregateInputType
    _sum?: Device_infoSumAggregateInputType
    _min?: Device_infoMinAggregateInputType
    _max?: Device_infoMaxAggregateInputType
  }


  export type Device_infoGroupByOutputType = {
    device_id: string
    device_name: string
    vendor_name: string
    tag_list: string
    is_inspected: number
    is_blocked: number
    _count: Device_infoCountAggregateOutputType | null
    _avg: Device_infoAvgAggregateOutputType | null
    _sum: Device_infoSumAggregateOutputType | null
    _min: Device_infoMinAggregateOutputType | null
    _max: Device_infoMaxAggregateOutputType | null
  }

  type GetDevice_infoGroupByPayload<T extends Device_infoGroupByArgs> = PrismaPromise<
    Array<
      PickArray<Device_infoGroupByOutputType, T['by']> &
        {
          [P in ((keyof T) & (keyof Device_infoGroupByOutputType))]: P extends '_count'
            ? T[P] extends boolean
              ? number
              : GetScalarType<T[P], Device_infoGroupByOutputType[P]>
            : GetScalarType<T[P], Device_infoGroupByOutputType[P]>
        }
      >
    >


  export type device_infoSelect = {
    device_id?: boolean
    device_name?: boolean
    vendor_name?: boolean
    tag_list?: boolean
    is_inspected?: boolean
    is_blocked?: boolean
  }

  export type device_infoGetPayload<
    S extends boolean | null | undefined | device_infoArgs,
    U = keyof S
      > = S extends true
        ? device_info
    : S extends undefined
    ? never
    : S extends device_infoArgs | device_infoFindManyArgs
    ?'include' extends U
    ? device_info 
    : 'select' extends U
    ? {
    [P in TrueKeys<S['select']>]:
    P extends keyof device_info ? device_info[P] : never
  } 
    : device_info
  : device_info


  type device_infoCountArgs = Merge<
    Omit<device_infoFindManyArgs, 'select' | 'include'> & {
      select?: Device_infoCountAggregateInputType | true
    }
  >

  export interface device_infoDelegate<GlobalRejectSettings> {
    /**
     * Find zero or one Device_info that matches the filter.
     * @param {device_infoFindUniqueArgs} args - Arguments to find a Device_info
     * @example
     * // Get one Device_info
     * const device_info = await prisma.device_info.findUnique({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
    **/
    findUnique<T extends device_infoFindUniqueArgs,  LocalRejectSettings = T["rejectOnNotFound"] extends RejectOnNotFound ? T['rejectOnNotFound'] : undefined>(
      args: SelectSubset<T, device_infoFindUniqueArgs>
    ): HasReject<GlobalRejectSettings, LocalRejectSettings, 'findUnique', 'device_info'> extends True ? CheckSelect<T, Prisma__device_infoClient<device_info>, Prisma__device_infoClient<device_infoGetPayload<T>>> : CheckSelect<T, Prisma__device_infoClient<device_info | null >, Prisma__device_infoClient<device_infoGetPayload<T> | null >>

    /**
     * Find the first Device_info that matches the filter.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {device_infoFindFirstArgs} args - Arguments to find a Device_info
     * @example
     * // Get one Device_info
     * const device_info = await prisma.device_info.findFirst({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
    **/
    findFirst<T extends device_infoFindFirstArgs,  LocalRejectSettings = T["rejectOnNotFound"] extends RejectOnNotFound ? T['rejectOnNotFound'] : undefined>(
      args?: SelectSubset<T, device_infoFindFirstArgs>
    ): HasReject<GlobalRejectSettings, LocalRejectSettings, 'findFirst', 'device_info'> extends True ? CheckSelect<T, Prisma__device_infoClient<device_info>, Prisma__device_infoClient<device_infoGetPayload<T>>> : CheckSelect<T, Prisma__device_infoClient<device_info | null >, Prisma__device_infoClient<device_infoGetPayload<T> | null >>

    /**
     * Find zero or more Device_infos that matches the filter.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {device_infoFindManyArgs=} args - Arguments to filter and select certain fields only.
     * @example
     * // Get all Device_infos
     * const device_infos = await prisma.device_info.findMany()
     * 
     * // Get first 10 Device_infos
     * const device_infos = await prisma.device_info.findMany({ take: 10 })
     * 
     * // Only select the `device_id`
     * const device_infoWithDevice_idOnly = await prisma.device_info.findMany({ select: { device_id: true } })
     * 
    **/
    findMany<T extends device_infoFindManyArgs>(
      args?: SelectSubset<T, device_infoFindManyArgs>
    ): CheckSelect<T, PrismaPromise<Array<device_info>>, PrismaPromise<Array<device_infoGetPayload<T>>>>

    /**
     * Create a Device_info.
     * @param {device_infoCreateArgs} args - Arguments to create a Device_info.
     * @example
     * // Create one Device_info
     * const Device_info = await prisma.device_info.create({
     *   data: {
     *     // ... data to create a Device_info
     *   }
     * })
     * 
    **/
    create<T extends device_infoCreateArgs>(
      args: SelectSubset<T, device_infoCreateArgs>
    ): CheckSelect<T, Prisma__device_infoClient<device_info>, Prisma__device_infoClient<device_infoGetPayload<T>>>

    /**
     * Delete a Device_info.
     * @param {device_infoDeleteArgs} args - Arguments to delete one Device_info.
     * @example
     * // Delete one Device_info
     * const Device_info = await prisma.device_info.delete({
     *   where: {
     *     // ... filter to delete one Device_info
     *   }
     * })
     * 
    **/
    delete<T extends device_infoDeleteArgs>(
      args: SelectSubset<T, device_infoDeleteArgs>
    ): CheckSelect<T, Prisma__device_infoClient<device_info>, Prisma__device_infoClient<device_infoGetPayload<T>>>

    /**
     * Update one Device_info.
     * @param {device_infoUpdateArgs} args - Arguments to update one Device_info.
     * @example
     * // Update one Device_info
     * const device_info = await prisma.device_info.update({
     *   where: {
     *     // ... provide filter here
     *   },
     *   data: {
     *     // ... provide data here
     *   }
     * })
     * 
    **/
    update<T extends device_infoUpdateArgs>(
      args: SelectSubset<T, device_infoUpdateArgs>
    ): CheckSelect<T, Prisma__device_infoClient<device_info>, Prisma__device_infoClient<device_infoGetPayload<T>>>

    /**
     * Delete zero or more Device_infos.
     * @param {device_infoDeleteManyArgs} args - Arguments to filter Device_infos to delete.
     * @example
     * // Delete a few Device_infos
     * const { count } = await prisma.device_info.deleteMany({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     * 
    **/
    deleteMany<T extends device_infoDeleteManyArgs>(
      args?: SelectSubset<T, device_infoDeleteManyArgs>
    ): PrismaPromise<BatchPayload>

    /**
     * Update zero or more Device_infos.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {device_infoUpdateManyArgs} args - Arguments to update one or more rows.
     * @example
     * // Update many Device_infos
     * const device_info = await prisma.device_info.updateMany({
     *   where: {
     *     // ... provide filter here
     *   },
     *   data: {
     *     // ... provide data here
     *   }
     * })
     * 
    **/
    updateMany<T extends device_infoUpdateManyArgs>(
      args: SelectSubset<T, device_infoUpdateManyArgs>
    ): PrismaPromise<BatchPayload>

    /**
     * Create or update one Device_info.
     * @param {device_infoUpsertArgs} args - Arguments to update or create a Device_info.
     * @example
     * // Update or create a Device_info
     * const device_info = await prisma.device_info.upsert({
     *   create: {
     *     // ... data to create a Device_info
     *   },
     *   update: {
     *     // ... in case it already exists, update
     *   },
     *   where: {
     *     // ... the filter for the Device_info we want to update
     *   }
     * })
    **/
    upsert<T extends device_infoUpsertArgs>(
      args: SelectSubset<T, device_infoUpsertArgs>
    ): CheckSelect<T, Prisma__device_infoClient<device_info>, Prisma__device_infoClient<device_infoGetPayload<T>>>

    /**
     * Count the number of Device_infos.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {device_infoCountArgs} args - Arguments to filter Device_infos to count.
     * @example
     * // Count the number of Device_infos
     * const count = await prisma.device_info.count({
     *   where: {
     *     // ... the filter for the Device_infos we want to count
     *   }
     * })
    **/
    count<T extends device_infoCountArgs>(
      args?: Subset<T, device_infoCountArgs>,
    ): PrismaPromise<
      T extends _Record<'select', any>
        ? T['select'] extends true
          ? number
          : GetScalarType<T['select'], Device_infoCountAggregateOutputType>
        : number
    >

    /**
     * Allows you to perform aggregations operations on a Device_info.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {Device_infoAggregateArgs} args - Select which aggregations you would like to apply and on what fields.
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
    aggregate<T extends Device_infoAggregateArgs>(args: Subset<T, Device_infoAggregateArgs>): PrismaPromise<GetDevice_infoAggregateType<T>>

    /**
     * Group by Device_info.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {Device_infoGroupByArgs} args - Group by arguments.
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
      T extends Device_infoGroupByArgs,
      HasSelectOrTake extends Or<
        Extends<'skip', Keys<T>>,
        Extends<'take', Keys<T>>
      >,
      OrderByArg extends True extends HasSelectOrTake
        ? { orderBy: Device_infoGroupByArgs['orderBy'] }
        : { orderBy?: Device_infoGroupByArgs['orderBy'] },
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
    >(args: SubsetIntersection<T, Device_infoGroupByArgs, OrderByArg> & InputErrors): {} extends InputErrors ? GetDevice_infoGroupByPayload<T> : PrismaPromise<InputErrors>
  }

  /**
   * The delegate class that acts as a "Promise-like" for device_info.
   * Why is this prefixed with `Prisma__`?
   * Because we want to prevent naming conflicts as mentioned in
   * https://github.com/prisma/prisma-client-js/issues/707
   */
  export class Prisma__device_infoClient<T> implements PrismaPromise<T> {
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
   * device_info findUnique
   */
  export type device_infoFindUniqueArgs = {
    /**
     * Select specific fields to fetch from the device_info
     * 
    **/
    select?: device_infoSelect | null
    /**
     * Throw an Error if a device_info can't be found
     * 
    **/
    rejectOnNotFound?: RejectOnNotFound
    /**
     * Filter, which device_info to fetch.
     * 
    **/
    where: device_infoWhereUniqueInput
  }


  /**
   * device_info findFirst
   */
  export type device_infoFindFirstArgs = {
    /**
     * Select specific fields to fetch from the device_info
     * 
    **/
    select?: device_infoSelect | null
    /**
     * Throw an Error if a device_info can't be found
     * 
    **/
    rejectOnNotFound?: RejectOnNotFound
    /**
     * Filter, which device_info to fetch.
     * 
    **/
    where?: device_infoWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of device_infos to fetch.
     * 
    **/
    orderBy?: Enumerable<device_infoOrderByWithRelationInput>
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for searching for device_infos.
     * 
    **/
    cursor?: device_infoWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` device_infos from the position of the cursor.
     * 
    **/
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` device_infos.
     * 
    **/
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/distinct Distinct Docs}
     * 
     * Filter by unique combinations of device_infos.
     * 
    **/
    distinct?: Enumerable<Device_infoScalarFieldEnum>
  }


  /**
   * device_info findMany
   */
  export type device_infoFindManyArgs = {
    /**
     * Select specific fields to fetch from the device_info
     * 
    **/
    select?: device_infoSelect | null
    /**
     * Filter, which device_infos to fetch.
     * 
    **/
    where?: device_infoWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of device_infos to fetch.
     * 
    **/
    orderBy?: Enumerable<device_infoOrderByWithRelationInput>
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for listing device_infos.
     * 
    **/
    cursor?: device_infoWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` device_infos from the position of the cursor.
     * 
    **/
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` device_infos.
     * 
    **/
    skip?: number
    distinct?: Enumerable<Device_infoScalarFieldEnum>
  }


  /**
   * device_info create
   */
  export type device_infoCreateArgs = {
    /**
     * Select specific fields to fetch from the device_info
     * 
    **/
    select?: device_infoSelect | null
    /**
     * The data needed to create a device_info.
     * 
    **/
    data: XOR<device_infoCreateInput, device_infoUncheckedCreateInput>
  }


  /**
   * device_info update
   */
  export type device_infoUpdateArgs = {
    /**
     * Select specific fields to fetch from the device_info
     * 
    **/
    select?: device_infoSelect | null
    /**
     * The data needed to update a device_info.
     * 
    **/
    data: XOR<device_infoUpdateInput, device_infoUncheckedUpdateInput>
    /**
     * Choose, which device_info to update.
     * 
    **/
    where: device_infoWhereUniqueInput
  }


  /**
   * device_info updateMany
   */
  export type device_infoUpdateManyArgs = {
    /**
     * The data used to update device_infos.
     * 
    **/
    data: XOR<device_infoUpdateManyMutationInput, device_infoUncheckedUpdateManyInput>
    /**
     * Filter which device_infos to update
     * 
    **/
    where?: device_infoWhereInput
  }


  /**
   * device_info upsert
   */
  export type device_infoUpsertArgs = {
    /**
     * Select specific fields to fetch from the device_info
     * 
    **/
    select?: device_infoSelect | null
    /**
     * The filter to search for the device_info to update in case it exists.
     * 
    **/
    where: device_infoWhereUniqueInput
    /**
     * In case the device_info found by the `where` argument doesn't exist, create a new device_info with this data.
     * 
    **/
    create: XOR<device_infoCreateInput, device_infoUncheckedCreateInput>
    /**
     * In case the device_info was found with the provided `where` argument, update it with this data.
     * 
    **/
    update: XOR<device_infoUpdateInput, device_infoUncheckedUpdateInput>
  }


  /**
   * device_info delete
   */
  export type device_infoDeleteArgs = {
    /**
     * Select specific fields to fetch from the device_info
     * 
    **/
    select?: device_infoSelect | null
    /**
     * Filter which device_info to delete.
     * 
    **/
    where: device_infoWhereUniqueInput
  }


  /**
   * device_info deleteMany
   */
  export type device_infoDeleteManyArgs = {
    /**
     * Filter which device_infos to delete
     * 
    **/
    where?: device_infoWhereInput
  }


  /**
   * device_info without action
   */
  export type device_infoArgs = {
    /**
     * Select specific fields to fetch from the device_info
     * 
    **/
    select?: device_infoSelect | null
  }



  /**
   * Model state_kv
   */


  export type AggregateState_kv = {
    _count: State_kvCountAggregateOutputType | null
    _min: State_kvMinAggregateOutputType | null
    _max: State_kvMaxAggregateOutputType | null
  }

  export type State_kvMinAggregateOutputType = {
    state_key: string | null
    state_value_json: string | null
  }

  export type State_kvMaxAggregateOutputType = {
    state_key: string | null
    state_value_json: string | null
  }

  export type State_kvCountAggregateOutputType = {
    state_key: number
    state_value_json: number
    _all: number
  }


  export type State_kvMinAggregateInputType = {
    state_key?: true
    state_value_json?: true
  }

  export type State_kvMaxAggregateInputType = {
    state_key?: true
    state_value_json?: true
  }

  export type State_kvCountAggregateInputType = {
    state_key?: true
    state_value_json?: true
    _all?: true
  }

  export type State_kvAggregateArgs = {
    /**
     * Filter which state_kv to aggregate.
     * 
    **/
    where?: state_kvWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of state_kvs to fetch.
     * 
    **/
    orderBy?: Enumerable<state_kvOrderByWithRelationInput>
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the start position
     * 
    **/
    cursor?: state_kvWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` state_kvs from the position of the cursor.
     * 
    **/
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` state_kvs.
     * 
    **/
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Count returned state_kvs
    **/
    _count?: true | State_kvCountAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to find the minimum value
    **/
    _min?: State_kvMinAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to find the maximum value
    **/
    _max?: State_kvMaxAggregateInputType
  }

  export type GetState_kvAggregateType<T extends State_kvAggregateArgs> = {
        [P in keyof T & keyof AggregateState_kv]: P extends '_count' | 'count'
      ? T[P] extends true
        ? number
        : GetScalarType<T[P], AggregateState_kv[P]>
      : GetScalarType<T[P], AggregateState_kv[P]>
  }




  export type State_kvGroupByArgs = {
    where?: state_kvWhereInput
    orderBy?: Enumerable<state_kvOrderByWithAggregationInput>
    by: Array<State_kvScalarFieldEnum>
    having?: state_kvScalarWhereWithAggregatesInput
    take?: number
    skip?: number
    _count?: State_kvCountAggregateInputType | true
    _min?: State_kvMinAggregateInputType
    _max?: State_kvMaxAggregateInputType
  }


  export type State_kvGroupByOutputType = {
    state_key: string
    state_value_json: string
    _count: State_kvCountAggregateOutputType | null
    _min: State_kvMinAggregateOutputType | null
    _max: State_kvMaxAggregateOutputType | null
  }

  type GetState_kvGroupByPayload<T extends State_kvGroupByArgs> = PrismaPromise<
    Array<
      PickArray<State_kvGroupByOutputType, T['by']> &
        {
          [P in ((keyof T) & (keyof State_kvGroupByOutputType))]: P extends '_count'
            ? T[P] extends boolean
              ? number
              : GetScalarType<T[P], State_kvGroupByOutputType[P]>
            : GetScalarType<T[P], State_kvGroupByOutputType[P]>
        }
      >
    >


  export type state_kvSelect = {
    state_key?: boolean
    state_value_json?: boolean
  }

  export type state_kvGetPayload<
    S extends boolean | null | undefined | state_kvArgs,
    U = keyof S
      > = S extends true
        ? state_kv
    : S extends undefined
    ? never
    : S extends state_kvArgs | state_kvFindManyArgs
    ?'include' extends U
    ? state_kv 
    : 'select' extends U
    ? {
    [P in TrueKeys<S['select']>]:
    P extends keyof state_kv ? state_kv[P] : never
  } 
    : state_kv
  : state_kv


  type state_kvCountArgs = Merge<
    Omit<state_kvFindManyArgs, 'select' | 'include'> & {
      select?: State_kvCountAggregateInputType | true
    }
  >

  export interface state_kvDelegate<GlobalRejectSettings> {
    /**
     * Find zero or one State_kv that matches the filter.
     * @param {state_kvFindUniqueArgs} args - Arguments to find a State_kv
     * @example
     * // Get one State_kv
     * const state_kv = await prisma.state_kv.findUnique({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
    **/
    findUnique<T extends state_kvFindUniqueArgs,  LocalRejectSettings = T["rejectOnNotFound"] extends RejectOnNotFound ? T['rejectOnNotFound'] : undefined>(
      args: SelectSubset<T, state_kvFindUniqueArgs>
    ): HasReject<GlobalRejectSettings, LocalRejectSettings, 'findUnique', 'state_kv'> extends True ? CheckSelect<T, Prisma__state_kvClient<state_kv>, Prisma__state_kvClient<state_kvGetPayload<T>>> : CheckSelect<T, Prisma__state_kvClient<state_kv | null >, Prisma__state_kvClient<state_kvGetPayload<T> | null >>

    /**
     * Find the first State_kv that matches the filter.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {state_kvFindFirstArgs} args - Arguments to find a State_kv
     * @example
     * // Get one State_kv
     * const state_kv = await prisma.state_kv.findFirst({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
    **/
    findFirst<T extends state_kvFindFirstArgs,  LocalRejectSettings = T["rejectOnNotFound"] extends RejectOnNotFound ? T['rejectOnNotFound'] : undefined>(
      args?: SelectSubset<T, state_kvFindFirstArgs>
    ): HasReject<GlobalRejectSettings, LocalRejectSettings, 'findFirst', 'state_kv'> extends True ? CheckSelect<T, Prisma__state_kvClient<state_kv>, Prisma__state_kvClient<state_kvGetPayload<T>>> : CheckSelect<T, Prisma__state_kvClient<state_kv | null >, Prisma__state_kvClient<state_kvGetPayload<T> | null >>

    /**
     * Find zero or more State_kvs that matches the filter.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {state_kvFindManyArgs=} args - Arguments to filter and select certain fields only.
     * @example
     * // Get all State_kvs
     * const state_kvs = await prisma.state_kv.findMany()
     * 
     * // Get first 10 State_kvs
     * const state_kvs = await prisma.state_kv.findMany({ take: 10 })
     * 
     * // Only select the `state_key`
     * const state_kvWithState_keyOnly = await prisma.state_kv.findMany({ select: { state_key: true } })
     * 
    **/
    findMany<T extends state_kvFindManyArgs>(
      args?: SelectSubset<T, state_kvFindManyArgs>
    ): CheckSelect<T, PrismaPromise<Array<state_kv>>, PrismaPromise<Array<state_kvGetPayload<T>>>>

    /**
     * Create a State_kv.
     * @param {state_kvCreateArgs} args - Arguments to create a State_kv.
     * @example
     * // Create one State_kv
     * const State_kv = await prisma.state_kv.create({
     *   data: {
     *     // ... data to create a State_kv
     *   }
     * })
     * 
    **/
    create<T extends state_kvCreateArgs>(
      args: SelectSubset<T, state_kvCreateArgs>
    ): CheckSelect<T, Prisma__state_kvClient<state_kv>, Prisma__state_kvClient<state_kvGetPayload<T>>>

    /**
     * Delete a State_kv.
     * @param {state_kvDeleteArgs} args - Arguments to delete one State_kv.
     * @example
     * // Delete one State_kv
     * const State_kv = await prisma.state_kv.delete({
     *   where: {
     *     // ... filter to delete one State_kv
     *   }
     * })
     * 
    **/
    delete<T extends state_kvDeleteArgs>(
      args: SelectSubset<T, state_kvDeleteArgs>
    ): CheckSelect<T, Prisma__state_kvClient<state_kv>, Prisma__state_kvClient<state_kvGetPayload<T>>>

    /**
     * Update one State_kv.
     * @param {state_kvUpdateArgs} args - Arguments to update one State_kv.
     * @example
     * // Update one State_kv
     * const state_kv = await prisma.state_kv.update({
     *   where: {
     *     // ... provide filter here
     *   },
     *   data: {
     *     // ... provide data here
     *   }
     * })
     * 
    **/
    update<T extends state_kvUpdateArgs>(
      args: SelectSubset<T, state_kvUpdateArgs>
    ): CheckSelect<T, Prisma__state_kvClient<state_kv>, Prisma__state_kvClient<state_kvGetPayload<T>>>

    /**
     * Delete zero or more State_kvs.
     * @param {state_kvDeleteManyArgs} args - Arguments to filter State_kvs to delete.
     * @example
     * // Delete a few State_kvs
     * const { count } = await prisma.state_kv.deleteMany({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     * 
    **/
    deleteMany<T extends state_kvDeleteManyArgs>(
      args?: SelectSubset<T, state_kvDeleteManyArgs>
    ): PrismaPromise<BatchPayload>

    /**
     * Update zero or more State_kvs.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {state_kvUpdateManyArgs} args - Arguments to update one or more rows.
     * @example
     * // Update many State_kvs
     * const state_kv = await prisma.state_kv.updateMany({
     *   where: {
     *     // ... provide filter here
     *   },
     *   data: {
     *     // ... provide data here
     *   }
     * })
     * 
    **/
    updateMany<T extends state_kvUpdateManyArgs>(
      args: SelectSubset<T, state_kvUpdateManyArgs>
    ): PrismaPromise<BatchPayload>

    /**
     * Create or update one State_kv.
     * @param {state_kvUpsertArgs} args - Arguments to update or create a State_kv.
     * @example
     * // Update or create a State_kv
     * const state_kv = await prisma.state_kv.upsert({
     *   create: {
     *     // ... data to create a State_kv
     *   },
     *   update: {
     *     // ... in case it already exists, update
     *   },
     *   where: {
     *     // ... the filter for the State_kv we want to update
     *   }
     * })
    **/
    upsert<T extends state_kvUpsertArgs>(
      args: SelectSubset<T, state_kvUpsertArgs>
    ): CheckSelect<T, Prisma__state_kvClient<state_kv>, Prisma__state_kvClient<state_kvGetPayload<T>>>

    /**
     * Count the number of State_kvs.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {state_kvCountArgs} args - Arguments to filter State_kvs to count.
     * @example
     * // Count the number of State_kvs
     * const count = await prisma.state_kv.count({
     *   where: {
     *     // ... the filter for the State_kvs we want to count
     *   }
     * })
    **/
    count<T extends state_kvCountArgs>(
      args?: Subset<T, state_kvCountArgs>,
    ): PrismaPromise<
      T extends _Record<'select', any>
        ? T['select'] extends true
          ? number
          : GetScalarType<T['select'], State_kvCountAggregateOutputType>
        : number
    >

    /**
     * Allows you to perform aggregations operations on a State_kv.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {State_kvAggregateArgs} args - Select which aggregations you would like to apply and on what fields.
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
    aggregate<T extends State_kvAggregateArgs>(args: Subset<T, State_kvAggregateArgs>): PrismaPromise<GetState_kvAggregateType<T>>

    /**
     * Group by State_kv.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {State_kvGroupByArgs} args - Group by arguments.
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
      T extends State_kvGroupByArgs,
      HasSelectOrTake extends Or<
        Extends<'skip', Keys<T>>,
        Extends<'take', Keys<T>>
      >,
      OrderByArg extends True extends HasSelectOrTake
        ? { orderBy: State_kvGroupByArgs['orderBy'] }
        : { orderBy?: State_kvGroupByArgs['orderBy'] },
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
    >(args: SubsetIntersection<T, State_kvGroupByArgs, OrderByArg> & InputErrors): {} extends InputErrors ? GetState_kvGroupByPayload<T> : PrismaPromise<InputErrors>
  }

  /**
   * The delegate class that acts as a "Promise-like" for state_kv.
   * Why is this prefixed with `Prisma__`?
   * Because we want to prevent naming conflicts as mentioned in
   * https://github.com/prisma/prisma-client-js/issues/707
   */
  export class Prisma__state_kvClient<T> implements PrismaPromise<T> {
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
   * state_kv findUnique
   */
  export type state_kvFindUniqueArgs = {
    /**
     * Select specific fields to fetch from the state_kv
     * 
    **/
    select?: state_kvSelect | null
    /**
     * Throw an Error if a state_kv can't be found
     * 
    **/
    rejectOnNotFound?: RejectOnNotFound
    /**
     * Filter, which state_kv to fetch.
     * 
    **/
    where: state_kvWhereUniqueInput
  }


  /**
   * state_kv findFirst
   */
  export type state_kvFindFirstArgs = {
    /**
     * Select specific fields to fetch from the state_kv
     * 
    **/
    select?: state_kvSelect | null
    /**
     * Throw an Error if a state_kv can't be found
     * 
    **/
    rejectOnNotFound?: RejectOnNotFound
    /**
     * Filter, which state_kv to fetch.
     * 
    **/
    where?: state_kvWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of state_kvs to fetch.
     * 
    **/
    orderBy?: Enumerable<state_kvOrderByWithRelationInput>
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for searching for state_kvs.
     * 
    **/
    cursor?: state_kvWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` state_kvs from the position of the cursor.
     * 
    **/
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` state_kvs.
     * 
    **/
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/distinct Distinct Docs}
     * 
     * Filter by unique combinations of state_kvs.
     * 
    **/
    distinct?: Enumerable<State_kvScalarFieldEnum>
  }


  /**
   * state_kv findMany
   */
  export type state_kvFindManyArgs = {
    /**
     * Select specific fields to fetch from the state_kv
     * 
    **/
    select?: state_kvSelect | null
    /**
     * Filter, which state_kvs to fetch.
     * 
    **/
    where?: state_kvWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of state_kvs to fetch.
     * 
    **/
    orderBy?: Enumerable<state_kvOrderByWithRelationInput>
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for listing state_kvs.
     * 
    **/
    cursor?: state_kvWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` state_kvs from the position of the cursor.
     * 
    **/
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` state_kvs.
     * 
    **/
    skip?: number
    distinct?: Enumerable<State_kvScalarFieldEnum>
  }


  /**
   * state_kv create
   */
  export type state_kvCreateArgs = {
    /**
     * Select specific fields to fetch from the state_kv
     * 
    **/
    select?: state_kvSelect | null
    /**
     * The data needed to create a state_kv.
     * 
    **/
    data: XOR<state_kvCreateInput, state_kvUncheckedCreateInput>
  }


  /**
   * state_kv update
   */
  export type state_kvUpdateArgs = {
    /**
     * Select specific fields to fetch from the state_kv
     * 
    **/
    select?: state_kvSelect | null
    /**
     * The data needed to update a state_kv.
     * 
    **/
    data: XOR<state_kvUpdateInput, state_kvUncheckedUpdateInput>
    /**
     * Choose, which state_kv to update.
     * 
    **/
    where: state_kvWhereUniqueInput
  }


  /**
   * state_kv updateMany
   */
  export type state_kvUpdateManyArgs = {
    /**
     * The data used to update state_kvs.
     * 
    **/
    data: XOR<state_kvUpdateManyMutationInput, state_kvUncheckedUpdateManyInput>
    /**
     * Filter which state_kvs to update
     * 
    **/
    where?: state_kvWhereInput
  }


  /**
   * state_kv upsert
   */
  export type state_kvUpsertArgs = {
    /**
     * Select specific fields to fetch from the state_kv
     * 
    **/
    select?: state_kvSelect | null
    /**
     * The filter to search for the state_kv to update in case it exists.
     * 
    **/
    where: state_kvWhereUniqueInput
    /**
     * In case the state_kv found by the `where` argument doesn't exist, create a new state_kv with this data.
     * 
    **/
    create: XOR<state_kvCreateInput, state_kvUncheckedCreateInput>
    /**
     * In case the state_kv was found with the provided `where` argument, update it with this data.
     * 
    **/
    update: XOR<state_kvUpdateInput, state_kvUncheckedUpdateInput>
  }


  /**
   * state_kv delete
   */
  export type state_kvDeleteArgs = {
    /**
     * Select specific fields to fetch from the state_kv
     * 
    **/
    select?: state_kvSelect | null
    /**
     * Filter which state_kv to delete.
     * 
    **/
    where: state_kvWhereUniqueInput
  }


  /**
   * state_kv deleteMany
   */
  export type state_kvDeleteManyArgs = {
    /**
     * Filter which state_kvs to delete
     * 
    **/
    where?: state_kvWhereInput
  }


  /**
   * state_kv without action
   */
  export type state_kvArgs = {
    /**
     * Select specific fields to fetch from the state_kv
     * 
    **/
    select?: state_kvSelect | null
  }



  /**
   * Model user_configs
   */


  export type AggregateUser_configs = {
    _count: User_configsCountAggregateOutputType | null
    _avg: User_configsAvgAggregateOutputType | null
    _sum: User_configsSumAggregateOutputType | null
    _min: User_configsMinAggregateOutputType | null
    _max: User_configsMaxAggregateOutputType | null
  }

  export type User_configsAvgAggregateOutputType = {
    id: number | null
    is_consent: number | null
    is_auto_inspect_device: number | null
    is_contribute_to_research: number | null
  }

  export type User_configsSumAggregateOutputType = {
    id: number | null
    is_consent: number | null
    is_auto_inspect_device: number | null
    is_contribute_to_research: number | null
  }

  export type User_configsMinAggregateOutputType = {
    id: number | null
    is_consent: number | null
    is_auto_inspect_device: number | null
    is_contribute_to_research: number | null
  }

  export type User_configsMaxAggregateOutputType = {
    id: number | null
    is_consent: number | null
    is_auto_inspect_device: number | null
    is_contribute_to_research: number | null
  }

  export type User_configsCountAggregateOutputType = {
    id: number
    is_consent: number
    is_auto_inspect_device: number
    is_contribute_to_research: number
    _all: number
  }


  export type User_configsAvgAggregateInputType = {
    id?: true
    is_consent?: true
    is_auto_inspect_device?: true
    is_contribute_to_research?: true
  }

  export type User_configsSumAggregateInputType = {
    id?: true
    is_consent?: true
    is_auto_inspect_device?: true
    is_contribute_to_research?: true
  }

  export type User_configsMinAggregateInputType = {
    id?: true
    is_consent?: true
    is_auto_inspect_device?: true
    is_contribute_to_research?: true
  }

  export type User_configsMaxAggregateInputType = {
    id?: true
    is_consent?: true
    is_auto_inspect_device?: true
    is_contribute_to_research?: true
  }

  export type User_configsCountAggregateInputType = {
    id?: true
    is_consent?: true
    is_auto_inspect_device?: true
    is_contribute_to_research?: true
    _all?: true
  }

  export type User_configsAggregateArgs = {
    /**
     * Filter which user_configs to aggregate.
     * 
    **/
    where?: user_configsWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of user_configs to fetch.
     * 
    **/
    orderBy?: Enumerable<user_configsOrderByWithRelationInput>
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the start position
     * 
    **/
    cursor?: user_configsWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` user_configs from the position of the cursor.
     * 
    **/
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` user_configs.
     * 
    **/
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Count returned user_configs
    **/
    _count?: true | User_configsCountAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to average
    **/
    _avg?: User_configsAvgAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to sum
    **/
    _sum?: User_configsSumAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to find the minimum value
    **/
    _min?: User_configsMinAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to find the maximum value
    **/
    _max?: User_configsMaxAggregateInputType
  }

  export type GetUser_configsAggregateType<T extends User_configsAggregateArgs> = {
        [P in keyof T & keyof AggregateUser_configs]: P extends '_count' | 'count'
      ? T[P] extends true
        ? number
        : GetScalarType<T[P], AggregateUser_configs[P]>
      : GetScalarType<T[P], AggregateUser_configs[P]>
  }




  export type User_configsGroupByArgs = {
    where?: user_configsWhereInput
    orderBy?: Enumerable<user_configsOrderByWithAggregationInput>
    by: Array<User_configsScalarFieldEnum>
    having?: user_configsScalarWhereWithAggregatesInput
    take?: number
    skip?: number
    _count?: User_configsCountAggregateInputType | true
    _avg?: User_configsAvgAggregateInputType
    _sum?: User_configsSumAggregateInputType
    _min?: User_configsMinAggregateInputType
    _max?: User_configsMaxAggregateInputType
  }


  export type User_configsGroupByOutputType = {
    id: number
    is_consent: number
    is_auto_inspect_device: number
    is_contribute_to_research: number
    _count: User_configsCountAggregateOutputType | null
    _avg: User_configsAvgAggregateOutputType | null
    _sum: User_configsSumAggregateOutputType | null
    _min: User_configsMinAggregateOutputType | null
    _max: User_configsMaxAggregateOutputType | null
  }

  type GetUser_configsGroupByPayload<T extends User_configsGroupByArgs> = PrismaPromise<
    Array<
      PickArray<User_configsGroupByOutputType, T['by']> &
        {
          [P in ((keyof T) & (keyof User_configsGroupByOutputType))]: P extends '_count'
            ? T[P] extends boolean
              ? number
              : GetScalarType<T[P], User_configsGroupByOutputType[P]>
            : GetScalarType<T[P], User_configsGroupByOutputType[P]>
        }
      >
    >


  export type user_configsSelect = {
    id?: boolean
    is_consent?: boolean
    is_auto_inspect_device?: boolean
    is_contribute_to_research?: boolean
  }

  export type user_configsGetPayload<
    S extends boolean | null | undefined | user_configsArgs,
    U = keyof S
      > = S extends true
        ? user_configs
    : S extends undefined
    ? never
    : S extends user_configsArgs | user_configsFindManyArgs
    ?'include' extends U
    ? user_configs 
    : 'select' extends U
    ? {
    [P in TrueKeys<S['select']>]:
    P extends keyof user_configs ? user_configs[P] : never
  } 
    : user_configs
  : user_configs


  type user_configsCountArgs = Merge<
    Omit<user_configsFindManyArgs, 'select' | 'include'> & {
      select?: User_configsCountAggregateInputType | true
    }
  >

  export interface user_configsDelegate<GlobalRejectSettings> {
    /**
     * Find zero or one User_configs that matches the filter.
     * @param {user_configsFindUniqueArgs} args - Arguments to find a User_configs
     * @example
     * // Get one User_configs
     * const user_configs = await prisma.user_configs.findUnique({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
    **/
    findUnique<T extends user_configsFindUniqueArgs,  LocalRejectSettings = T["rejectOnNotFound"] extends RejectOnNotFound ? T['rejectOnNotFound'] : undefined>(
      args: SelectSubset<T, user_configsFindUniqueArgs>
    ): HasReject<GlobalRejectSettings, LocalRejectSettings, 'findUnique', 'user_configs'> extends True ? CheckSelect<T, Prisma__user_configsClient<user_configs>, Prisma__user_configsClient<user_configsGetPayload<T>>> : CheckSelect<T, Prisma__user_configsClient<user_configs | null >, Prisma__user_configsClient<user_configsGetPayload<T> | null >>

    /**
     * Find the first User_configs that matches the filter.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {user_configsFindFirstArgs} args - Arguments to find a User_configs
     * @example
     * // Get one User_configs
     * const user_configs = await prisma.user_configs.findFirst({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
    **/
    findFirst<T extends user_configsFindFirstArgs,  LocalRejectSettings = T["rejectOnNotFound"] extends RejectOnNotFound ? T['rejectOnNotFound'] : undefined>(
      args?: SelectSubset<T, user_configsFindFirstArgs>
    ): HasReject<GlobalRejectSettings, LocalRejectSettings, 'findFirst', 'user_configs'> extends True ? CheckSelect<T, Prisma__user_configsClient<user_configs>, Prisma__user_configsClient<user_configsGetPayload<T>>> : CheckSelect<T, Prisma__user_configsClient<user_configs | null >, Prisma__user_configsClient<user_configsGetPayload<T> | null >>

    /**
     * Find zero or more User_configs that matches the filter.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {user_configsFindManyArgs=} args - Arguments to filter and select certain fields only.
     * @example
     * // Get all User_configs
     * const user_configs = await prisma.user_configs.findMany()
     * 
     * // Get first 10 User_configs
     * const user_configs = await prisma.user_configs.findMany({ take: 10 })
     * 
     * // Only select the `id`
     * const user_configsWithIdOnly = await prisma.user_configs.findMany({ select: { id: true } })
     * 
    **/
    findMany<T extends user_configsFindManyArgs>(
      args?: SelectSubset<T, user_configsFindManyArgs>
    ): CheckSelect<T, PrismaPromise<Array<user_configs>>, PrismaPromise<Array<user_configsGetPayload<T>>>>

    /**
     * Create a User_configs.
     * @param {user_configsCreateArgs} args - Arguments to create a User_configs.
     * @example
     * // Create one User_configs
     * const User_configs = await prisma.user_configs.create({
     *   data: {
     *     // ... data to create a User_configs
     *   }
     * })
     * 
    **/
    create<T extends user_configsCreateArgs>(
      args: SelectSubset<T, user_configsCreateArgs>
    ): CheckSelect<T, Prisma__user_configsClient<user_configs>, Prisma__user_configsClient<user_configsGetPayload<T>>>

    /**
     * Delete a User_configs.
     * @param {user_configsDeleteArgs} args - Arguments to delete one User_configs.
     * @example
     * // Delete one User_configs
     * const User_configs = await prisma.user_configs.delete({
     *   where: {
     *     // ... filter to delete one User_configs
     *   }
     * })
     * 
    **/
    delete<T extends user_configsDeleteArgs>(
      args: SelectSubset<T, user_configsDeleteArgs>
    ): CheckSelect<T, Prisma__user_configsClient<user_configs>, Prisma__user_configsClient<user_configsGetPayload<T>>>

    /**
     * Update one User_configs.
     * @param {user_configsUpdateArgs} args - Arguments to update one User_configs.
     * @example
     * // Update one User_configs
     * const user_configs = await prisma.user_configs.update({
     *   where: {
     *     // ... provide filter here
     *   },
     *   data: {
     *     // ... provide data here
     *   }
     * })
     * 
    **/
    update<T extends user_configsUpdateArgs>(
      args: SelectSubset<T, user_configsUpdateArgs>
    ): CheckSelect<T, Prisma__user_configsClient<user_configs>, Prisma__user_configsClient<user_configsGetPayload<T>>>

    /**
     * Delete zero or more User_configs.
     * @param {user_configsDeleteManyArgs} args - Arguments to filter User_configs to delete.
     * @example
     * // Delete a few User_configs
     * const { count } = await prisma.user_configs.deleteMany({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     * 
    **/
    deleteMany<T extends user_configsDeleteManyArgs>(
      args?: SelectSubset<T, user_configsDeleteManyArgs>
    ): PrismaPromise<BatchPayload>

    /**
     * Update zero or more User_configs.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {user_configsUpdateManyArgs} args - Arguments to update one or more rows.
     * @example
     * // Update many User_configs
     * const user_configs = await prisma.user_configs.updateMany({
     *   where: {
     *     // ... provide filter here
     *   },
     *   data: {
     *     // ... provide data here
     *   }
     * })
     * 
    **/
    updateMany<T extends user_configsUpdateManyArgs>(
      args: SelectSubset<T, user_configsUpdateManyArgs>
    ): PrismaPromise<BatchPayload>

    /**
     * Create or update one User_configs.
     * @param {user_configsUpsertArgs} args - Arguments to update or create a User_configs.
     * @example
     * // Update or create a User_configs
     * const user_configs = await prisma.user_configs.upsert({
     *   create: {
     *     // ... data to create a User_configs
     *   },
     *   update: {
     *     // ... in case it already exists, update
     *   },
     *   where: {
     *     // ... the filter for the User_configs we want to update
     *   }
     * })
    **/
    upsert<T extends user_configsUpsertArgs>(
      args: SelectSubset<T, user_configsUpsertArgs>
    ): CheckSelect<T, Prisma__user_configsClient<user_configs>, Prisma__user_configsClient<user_configsGetPayload<T>>>

    /**
     * Count the number of User_configs.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {user_configsCountArgs} args - Arguments to filter User_configs to count.
     * @example
     * // Count the number of User_configs
     * const count = await prisma.user_configs.count({
     *   where: {
     *     // ... the filter for the User_configs we want to count
     *   }
     * })
    **/
    count<T extends user_configsCountArgs>(
      args?: Subset<T, user_configsCountArgs>,
    ): PrismaPromise<
      T extends _Record<'select', any>
        ? T['select'] extends true
          ? number
          : GetScalarType<T['select'], User_configsCountAggregateOutputType>
        : number
    >

    /**
     * Allows you to perform aggregations operations on a User_configs.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {User_configsAggregateArgs} args - Select which aggregations you would like to apply and on what fields.
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
    aggregate<T extends User_configsAggregateArgs>(args: Subset<T, User_configsAggregateArgs>): PrismaPromise<GetUser_configsAggregateType<T>>

    /**
     * Group by User_configs.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {User_configsGroupByArgs} args - Group by arguments.
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
      T extends User_configsGroupByArgs,
      HasSelectOrTake extends Or<
        Extends<'skip', Keys<T>>,
        Extends<'take', Keys<T>>
      >,
      OrderByArg extends True extends HasSelectOrTake
        ? { orderBy: User_configsGroupByArgs['orderBy'] }
        : { orderBy?: User_configsGroupByArgs['orderBy'] },
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
    >(args: SubsetIntersection<T, User_configsGroupByArgs, OrderByArg> & InputErrors): {} extends InputErrors ? GetUser_configsGroupByPayload<T> : PrismaPromise<InputErrors>
  }

  /**
   * The delegate class that acts as a "Promise-like" for user_configs.
   * Why is this prefixed with `Prisma__`?
   * Because we want to prevent naming conflicts as mentioned in
   * https://github.com/prisma/prisma-client-js/issues/707
   */
  export class Prisma__user_configsClient<T> implements PrismaPromise<T> {
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
   * user_configs findUnique
   */
  export type user_configsFindUniqueArgs = {
    /**
     * Select specific fields to fetch from the user_configs
     * 
    **/
    select?: user_configsSelect | null
    /**
     * Throw an Error if a user_configs can't be found
     * 
    **/
    rejectOnNotFound?: RejectOnNotFound
    /**
     * Filter, which user_configs to fetch.
     * 
    **/
    where: user_configsWhereUniqueInput
  }


  /**
   * user_configs findFirst
   */
  export type user_configsFindFirstArgs = {
    /**
     * Select specific fields to fetch from the user_configs
     * 
    **/
    select?: user_configsSelect | null
    /**
     * Throw an Error if a user_configs can't be found
     * 
    **/
    rejectOnNotFound?: RejectOnNotFound
    /**
     * Filter, which user_configs to fetch.
     * 
    **/
    where?: user_configsWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of user_configs to fetch.
     * 
    **/
    orderBy?: Enumerable<user_configsOrderByWithRelationInput>
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for searching for user_configs.
     * 
    **/
    cursor?: user_configsWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` user_configs from the position of the cursor.
     * 
    **/
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` user_configs.
     * 
    **/
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/distinct Distinct Docs}
     * 
     * Filter by unique combinations of user_configs.
     * 
    **/
    distinct?: Enumerable<User_configsScalarFieldEnum>
  }


  /**
   * user_configs findMany
   */
  export type user_configsFindManyArgs = {
    /**
     * Select specific fields to fetch from the user_configs
     * 
    **/
    select?: user_configsSelect | null
    /**
     * Filter, which user_configs to fetch.
     * 
    **/
    where?: user_configsWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of user_configs to fetch.
     * 
    **/
    orderBy?: Enumerable<user_configsOrderByWithRelationInput>
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for listing user_configs.
     * 
    **/
    cursor?: user_configsWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` user_configs from the position of the cursor.
     * 
    **/
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` user_configs.
     * 
    **/
    skip?: number
    distinct?: Enumerable<User_configsScalarFieldEnum>
  }


  /**
   * user_configs create
   */
  export type user_configsCreateArgs = {
    /**
     * Select specific fields to fetch from the user_configs
     * 
    **/
    select?: user_configsSelect | null
    /**
     * The data needed to create a user_configs.
     * 
    **/
    data: XOR<user_configsCreateInput, user_configsUncheckedCreateInput>
  }


  /**
   * user_configs update
   */
  export type user_configsUpdateArgs = {
    /**
     * Select specific fields to fetch from the user_configs
     * 
    **/
    select?: user_configsSelect | null
    /**
     * The data needed to update a user_configs.
     * 
    **/
    data: XOR<user_configsUpdateInput, user_configsUncheckedUpdateInput>
    /**
     * Choose, which user_configs to update.
     * 
    **/
    where: user_configsWhereUniqueInput
  }


  /**
   * user_configs updateMany
   */
  export type user_configsUpdateManyArgs = {
    /**
     * The data used to update user_configs.
     * 
    **/
    data: XOR<user_configsUpdateManyMutationInput, user_configsUncheckedUpdateManyInput>
    /**
     * Filter which user_configs to update
     * 
    **/
    where?: user_configsWhereInput
  }


  /**
   * user_configs upsert
   */
  export type user_configsUpsertArgs = {
    /**
     * Select specific fields to fetch from the user_configs
     * 
    **/
    select?: user_configsSelect | null
    /**
     * The filter to search for the user_configs to update in case it exists.
     * 
    **/
    where: user_configsWhereUniqueInput
    /**
     * In case the user_configs found by the `where` argument doesn't exist, create a new user_configs with this data.
     * 
    **/
    create: XOR<user_configsCreateInput, user_configsUncheckedCreateInput>
    /**
     * In case the user_configs was found with the provided `where` argument, update it with this data.
     * 
    **/
    update: XOR<user_configsUpdateInput, user_configsUncheckedUpdateInput>
  }


  /**
   * user_configs delete
   */
  export type user_configsDeleteArgs = {
    /**
     * Select specific fields to fetch from the user_configs
     * 
    **/
    select?: user_configsSelect | null
    /**
     * Filter which user_configs to delete.
     * 
    **/
    where: user_configsWhereUniqueInput
  }


  /**
   * user_configs deleteMany
   */
  export type user_configsDeleteManyArgs = {
    /**
     * Filter which user_configs to delete
     * 
    **/
    where?: user_configsWhereInput
  }


  /**
   * user_configs without action
   */
  export type user_configsArgs = {
    /**
     * Select specific fields to fetch from the user_configs
     * 
    **/
    select?: user_configsSelect | null
  }



  /**
   * Enums
   */

  // Based on
  // https://github.com/microsoft/TypeScript/issues/3192#issuecomment-261720275

  export const Device_infoScalarFieldEnum: {
    device_id: 'device_id',
    device_name: 'device_name',
    vendor_name: 'vendor_name',
    tag_list: 'tag_list',
    is_inspected: 'is_inspected',
    is_blocked: 'is_blocked'
  };

  export type Device_infoScalarFieldEnum = (typeof Device_infoScalarFieldEnum)[keyof typeof Device_infoScalarFieldEnum]


  export const State_kvScalarFieldEnum: {
    state_key: 'state_key',
    state_value_json: 'state_value_json'
  };

  export type State_kvScalarFieldEnum = (typeof State_kvScalarFieldEnum)[keyof typeof State_kvScalarFieldEnum]


  export const User_configsScalarFieldEnum: {
    id: 'id',
    is_consent: 'is_consent',
    is_auto_inspect_device: 'is_auto_inspect_device',
    is_contribute_to_research: 'is_contribute_to_research'
  };

  export type User_configsScalarFieldEnum = (typeof User_configsScalarFieldEnum)[keyof typeof User_configsScalarFieldEnum]


  export const SortOrder: {
    asc: 'asc',
    desc: 'desc'
  };

  export type SortOrder = (typeof SortOrder)[keyof typeof SortOrder]


  /**
   * Deep Input Types
   */


  export type device_infoWhereInput = {
    AND?: Enumerable<device_infoWhereInput>
    OR?: Enumerable<device_infoWhereInput>
    NOT?: Enumerable<device_infoWhereInput>
    device_id?: StringFilter | string
    device_name?: StringFilter | string
    vendor_name?: StringFilter | string
    tag_list?: StringFilter | string
    is_inspected?: IntFilter | number
    is_blocked?: IntFilter | number
  }

  export type device_infoOrderByWithRelationInput = {
    device_id?: SortOrder
    device_name?: SortOrder
    vendor_name?: SortOrder
    tag_list?: SortOrder
    is_inspected?: SortOrder
    is_blocked?: SortOrder
  }

  export type device_infoWhereUniqueInput = {
    device_id?: string
  }

  export type device_infoOrderByWithAggregationInput = {
    device_id?: SortOrder
    device_name?: SortOrder
    vendor_name?: SortOrder
    tag_list?: SortOrder
    is_inspected?: SortOrder
    is_blocked?: SortOrder
    _count?: device_infoCountOrderByAggregateInput
    _avg?: device_infoAvgOrderByAggregateInput
    _max?: device_infoMaxOrderByAggregateInput
    _min?: device_infoMinOrderByAggregateInput
    _sum?: device_infoSumOrderByAggregateInput
  }

  export type device_infoScalarWhereWithAggregatesInput = {
    AND?: Enumerable<device_infoScalarWhereWithAggregatesInput>
    OR?: Enumerable<device_infoScalarWhereWithAggregatesInput>
    NOT?: Enumerable<device_infoScalarWhereWithAggregatesInput>
    device_id?: StringWithAggregatesFilter | string
    device_name?: StringWithAggregatesFilter | string
    vendor_name?: StringWithAggregatesFilter | string
    tag_list?: StringWithAggregatesFilter | string
    is_inspected?: IntWithAggregatesFilter | number
    is_blocked?: IntWithAggregatesFilter | number
  }

  export type state_kvWhereInput = {
    AND?: Enumerable<state_kvWhereInput>
    OR?: Enumerable<state_kvWhereInput>
    NOT?: Enumerable<state_kvWhereInput>
    state_key?: StringFilter | string
    state_value_json?: StringFilter | string
  }

  export type state_kvOrderByWithRelationInput = {
    state_key?: SortOrder
    state_value_json?: SortOrder
  }

  export type state_kvWhereUniqueInput = {
    state_key?: string
  }

  export type state_kvOrderByWithAggregationInput = {
    state_key?: SortOrder
    state_value_json?: SortOrder
    _count?: state_kvCountOrderByAggregateInput
    _max?: state_kvMaxOrderByAggregateInput
    _min?: state_kvMinOrderByAggregateInput
  }

  export type state_kvScalarWhereWithAggregatesInput = {
    AND?: Enumerable<state_kvScalarWhereWithAggregatesInput>
    OR?: Enumerable<state_kvScalarWhereWithAggregatesInput>
    NOT?: Enumerable<state_kvScalarWhereWithAggregatesInput>
    state_key?: StringWithAggregatesFilter | string
    state_value_json?: StringWithAggregatesFilter | string
  }

  export type user_configsWhereInput = {
    AND?: Enumerable<user_configsWhereInput>
    OR?: Enumerable<user_configsWhereInput>
    NOT?: Enumerable<user_configsWhereInput>
    id?: IntFilter | number
    is_consent?: IntFilter | number
    is_auto_inspect_device?: IntFilter | number
    is_contribute_to_research?: IntFilter | number
  }

  export type user_configsOrderByWithRelationInput = {
    id?: SortOrder
    is_consent?: SortOrder
    is_auto_inspect_device?: SortOrder
    is_contribute_to_research?: SortOrder
  }

  export type user_configsWhereUniqueInput = {
    id?: number
  }

  export type user_configsOrderByWithAggregationInput = {
    id?: SortOrder
    is_consent?: SortOrder
    is_auto_inspect_device?: SortOrder
    is_contribute_to_research?: SortOrder
    _count?: user_configsCountOrderByAggregateInput
    _avg?: user_configsAvgOrderByAggregateInput
    _max?: user_configsMaxOrderByAggregateInput
    _min?: user_configsMinOrderByAggregateInput
    _sum?: user_configsSumOrderByAggregateInput
  }

  export type user_configsScalarWhereWithAggregatesInput = {
    AND?: Enumerable<user_configsScalarWhereWithAggregatesInput>
    OR?: Enumerable<user_configsScalarWhereWithAggregatesInput>
    NOT?: Enumerable<user_configsScalarWhereWithAggregatesInput>
    id?: IntWithAggregatesFilter | number
    is_consent?: IntWithAggregatesFilter | number
    is_auto_inspect_device?: IntWithAggregatesFilter | number
    is_contribute_to_research?: IntWithAggregatesFilter | number
  }

  export type device_infoCreateInput = {
    device_id: string
    device_name?: string
    vendor_name?: string
    tag_list?: string
    is_inspected?: number
    is_blocked?: number
  }

  export type device_infoUncheckedCreateInput = {
    device_id: string
    device_name?: string
    vendor_name?: string
    tag_list?: string
    is_inspected?: number
    is_blocked?: number
  }

  export type device_infoUpdateInput = {
    device_id?: StringFieldUpdateOperationsInput | string
    device_name?: StringFieldUpdateOperationsInput | string
    vendor_name?: StringFieldUpdateOperationsInput | string
    tag_list?: StringFieldUpdateOperationsInput | string
    is_inspected?: IntFieldUpdateOperationsInput | number
    is_blocked?: IntFieldUpdateOperationsInput | number
  }

  export type device_infoUncheckedUpdateInput = {
    device_id?: StringFieldUpdateOperationsInput | string
    device_name?: StringFieldUpdateOperationsInput | string
    vendor_name?: StringFieldUpdateOperationsInput | string
    tag_list?: StringFieldUpdateOperationsInput | string
    is_inspected?: IntFieldUpdateOperationsInput | number
    is_blocked?: IntFieldUpdateOperationsInput | number
  }

  export type device_infoUpdateManyMutationInput = {
    device_id?: StringFieldUpdateOperationsInput | string
    device_name?: StringFieldUpdateOperationsInput | string
    vendor_name?: StringFieldUpdateOperationsInput | string
    tag_list?: StringFieldUpdateOperationsInput | string
    is_inspected?: IntFieldUpdateOperationsInput | number
    is_blocked?: IntFieldUpdateOperationsInput | number
  }

  export type device_infoUncheckedUpdateManyInput = {
    device_id?: StringFieldUpdateOperationsInput | string
    device_name?: StringFieldUpdateOperationsInput | string
    vendor_name?: StringFieldUpdateOperationsInput | string
    tag_list?: StringFieldUpdateOperationsInput | string
    is_inspected?: IntFieldUpdateOperationsInput | number
    is_blocked?: IntFieldUpdateOperationsInput | number
  }

  export type state_kvCreateInput = {
    state_key: string
    state_value_json: string
  }

  export type state_kvUncheckedCreateInput = {
    state_key: string
    state_value_json: string
  }

  export type state_kvUpdateInput = {
    state_key?: StringFieldUpdateOperationsInput | string
    state_value_json?: StringFieldUpdateOperationsInput | string
  }

  export type state_kvUncheckedUpdateInput = {
    state_key?: StringFieldUpdateOperationsInput | string
    state_value_json?: StringFieldUpdateOperationsInput | string
  }

  export type state_kvUpdateManyMutationInput = {
    state_key?: StringFieldUpdateOperationsInput | string
    state_value_json?: StringFieldUpdateOperationsInput | string
  }

  export type state_kvUncheckedUpdateManyInput = {
    state_key?: StringFieldUpdateOperationsInput | string
    state_value_json?: StringFieldUpdateOperationsInput | string
  }

  export type user_configsCreateInput = {
    id: number
    is_consent?: number
    is_auto_inspect_device?: number
    is_contribute_to_research?: number
  }

  export type user_configsUncheckedCreateInput = {
    id: number
    is_consent?: number
    is_auto_inspect_device?: number
    is_contribute_to_research?: number
  }

  export type user_configsUpdateInput = {
    id?: IntFieldUpdateOperationsInput | number
    is_consent?: IntFieldUpdateOperationsInput | number
    is_auto_inspect_device?: IntFieldUpdateOperationsInput | number
    is_contribute_to_research?: IntFieldUpdateOperationsInput | number
  }

  export type user_configsUncheckedUpdateInput = {
    id?: IntFieldUpdateOperationsInput | number
    is_consent?: IntFieldUpdateOperationsInput | number
    is_auto_inspect_device?: IntFieldUpdateOperationsInput | number
    is_contribute_to_research?: IntFieldUpdateOperationsInput | number
  }

  export type user_configsUpdateManyMutationInput = {
    id?: IntFieldUpdateOperationsInput | number
    is_consent?: IntFieldUpdateOperationsInput | number
    is_auto_inspect_device?: IntFieldUpdateOperationsInput | number
    is_contribute_to_research?: IntFieldUpdateOperationsInput | number
  }

  export type user_configsUncheckedUpdateManyInput = {
    id?: IntFieldUpdateOperationsInput | number
    is_consent?: IntFieldUpdateOperationsInput | number
    is_auto_inspect_device?: IntFieldUpdateOperationsInput | number
    is_contribute_to_research?: IntFieldUpdateOperationsInput | number
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

  export type device_infoCountOrderByAggregateInput = {
    device_id?: SortOrder
    device_name?: SortOrder
    vendor_name?: SortOrder
    tag_list?: SortOrder
    is_inspected?: SortOrder
    is_blocked?: SortOrder
  }

  export type device_infoAvgOrderByAggregateInput = {
    is_inspected?: SortOrder
    is_blocked?: SortOrder
  }

  export type device_infoMaxOrderByAggregateInput = {
    device_id?: SortOrder
    device_name?: SortOrder
    vendor_name?: SortOrder
    tag_list?: SortOrder
    is_inspected?: SortOrder
    is_blocked?: SortOrder
  }

  export type device_infoMinOrderByAggregateInput = {
    device_id?: SortOrder
    device_name?: SortOrder
    vendor_name?: SortOrder
    tag_list?: SortOrder
    is_inspected?: SortOrder
    is_blocked?: SortOrder
  }

  export type device_infoSumOrderByAggregateInput = {
    is_inspected?: SortOrder
    is_blocked?: SortOrder
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

  export type state_kvCountOrderByAggregateInput = {
    state_key?: SortOrder
    state_value_json?: SortOrder
  }

  export type state_kvMaxOrderByAggregateInput = {
    state_key?: SortOrder
    state_value_json?: SortOrder
  }

  export type state_kvMinOrderByAggregateInput = {
    state_key?: SortOrder
    state_value_json?: SortOrder
  }

  export type user_configsCountOrderByAggregateInput = {
    id?: SortOrder
    is_consent?: SortOrder
    is_auto_inspect_device?: SortOrder
    is_contribute_to_research?: SortOrder
  }

  export type user_configsAvgOrderByAggregateInput = {
    id?: SortOrder
    is_consent?: SortOrder
    is_auto_inspect_device?: SortOrder
    is_contribute_to_research?: SortOrder
  }

  export type user_configsMaxOrderByAggregateInput = {
    id?: SortOrder
    is_consent?: SortOrder
    is_auto_inspect_device?: SortOrder
    is_contribute_to_research?: SortOrder
  }

  export type user_configsMinOrderByAggregateInput = {
    id?: SortOrder
    is_consent?: SortOrder
    is_auto_inspect_device?: SortOrder
    is_contribute_to_research?: SortOrder
  }

  export type user_configsSumOrderByAggregateInput = {
    id?: SortOrder
    is_consent?: SortOrder
    is_auto_inspect_device?: SortOrder
    is_contribute_to_research?: SortOrder
  }

  export type StringFieldUpdateOperationsInput = {
    set?: string
  }

  export type IntFieldUpdateOperationsInput = {
    set?: number
    increment?: number
    decrement?: number
    multiply?: number
    divide?: number
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