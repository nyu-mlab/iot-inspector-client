'use strict';

Object.defineProperty(exports, '__esModule', { value: true });

function _interopDefault (ex) { return (ex && (typeof ex === 'object') && 'default' in ex) ? ex['default'] : ex; }

const graphql = require('graphql');
const stringify = _interopDefault(require('fast-json-stable-stringify'));
const utils = require('@graphql-tools/utils');
const schema = require('@graphql-tools/schema');

function isRef(maybeRef) {
    return !!(maybeRef && typeof maybeRef === 'object' && '$ref' in maybeRef);
}
function assertIsRef(maybeRef, message) {
    if (!isRef(maybeRef)) {
        throw new Error(message || `Expected ${maybeRef} to be a valid Ref.`);
    }
}
function isRecord(obj) {
    return typeof obj === 'object' && obj !== null;
}

function uuidv4() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
        const r = (Math.random() * 16) | 0;
        // eslint-disable-next-line eqeqeq
        const v = c == 'x' ? r : (r & 0x3) | 0x8;
        return v.toString(16);
    });
}
const randomListLength = () => {
    // Mocking has always returned list of length 2 by default
    // return 1 + Math.round(Math.random() * 10)
    return 2;
};
const takeRandom = (arr) => arr[Math.floor(Math.random() * arr.length)];
function makeRef(typeName, key) {
    return { $ref: { key, typeName } };
}
function isObject(thing) {
    return thing === Object(thing) && !Array.isArray(thing);
}
function copyOwnPropsIfNotPresent(target, source) {
    for (const prop of Object.getOwnPropertyNames(source)) {
        if (!Object.getOwnPropertyDescriptor(target, prop)) {
            const propertyDescriptor = Object.getOwnPropertyDescriptor(source, prop);
            Object.defineProperty(target, prop, propertyDescriptor == null ? {} : propertyDescriptor);
        }
    }
}
function copyOwnProps(target, ...sources) {
    for (const source of sources) {
        let chain = source;
        while (chain != null) {
            copyOwnPropsIfNotPresent(target, chain);
            chain = Object.getPrototypeOf(chain);
        }
    }
    return target;
}
const isRootType = (type, schema) => {
    const rootTypeNames = utils.getRootTypeNames(schema);
    return rootTypeNames.has(type.name);
};

/**
 * @internal
 */
function isMockList(obj) {
    if (typeof (obj === null || obj === void 0 ? void 0 : obj.len) === 'number' || (Array.isArray(obj === null || obj === void 0 ? void 0 : obj.len) && typeof (obj === null || obj === void 0 ? void 0 : obj.len[0]) === 'number')) {
        if (typeof obj.wrappedFunction === 'undefined' || typeof obj.wrappedFunction === 'function') {
            return true;
        }
    }
    return false;
}
/**
 * This is an object you can return from your mock resolvers which calls the
 * provided `mockFunction` once for each list item.
 */
class MockList {
    /**
     * @param length Either the exact length of items to return or an inclusive
     * range of possible lengths.
     * @param mockFunction The function to call for each item in the list to
     * resolve it. It can return another MockList or a value.
     */
    constructor(length, mockFunction) {
        this.len = length;
        if (typeof mockFunction !== 'undefined') {
            if (typeof mockFunction !== 'function') {
                throw new Error('Second argument to MockList must be a function or undefined');
            }
            this.wrappedFunction = mockFunction;
        }
    }
    /**
     * @internal
     */
    mock() {
        let arr;
        if (Array.isArray(this.len)) {
            arr = new Array(this.randint(this.len[0], this.len[1]));
        }
        else {
            arr = new Array(this.len);
        }
        for (let i = 0; i < arr.length; i++) {
            if (typeof this.wrappedFunction === 'function') {
                const res = this.wrappedFunction();
                if (isMockList(res)) {
                    arr[i] = res.mock();
                }
                else {
                    arr[i] = res;
                }
            }
            else {
                arr[i] = undefined;
            }
        }
        return arr;
    }
    randint(low, high) {
        return Math.floor(Math.random() * (high - low + 1) + low);
    }
}
function deepResolveMockList(mockList) {
    return mockList.mock().map(v => {
        if (isMockList(v))
            return deepResolveMockList(v);
        return v;
    });
}

const defaultMocks = {
    Int: () => Math.round(Math.random() * 200) - 100,
    Float: () => Math.random() * 200 - 100,
    String: () => 'Hello World',
    Boolean: () => Math.random() > 0.5,
    ID: () => uuidv4(),
};
const defaultKeyFieldNames = ['id', '_id'];
class MockStore {
    constructor({ schema, mocks, typePolicies, }) {
        this.store = {};
        this.schema = schema;
        this.mocks = { ...defaultMocks, ...mocks };
        this.typePolicies = typePolicies || {};
    }
    has(typeName, key) {
        return !!this.store[typeName] && !!this.store[typeName][key];
    }
    get(_typeName, _key, _fieldName, _fieldArgs) {
        if (typeof _typeName !== 'string') {
            if (_key === undefined) {
                if (isRef(_typeName)) {
                    throw new Error("Can't provide a ref as first argument and no other argument");
                }
                // get({...})
                return this.getImpl(_typeName);
            }
            else {
                assertIsRef(_typeName);
                const { $ref } = _typeName;
                // arguments shift
                _fieldArgs = _fieldName;
                _fieldName = _key;
                _key = $ref.key;
                _typeName = $ref.typeName;
            }
        }
        const args = {
            typeName: _typeName,
        };
        if (isRecord(_key) || _key === undefined) {
            // get('User', { name: 'Alex'})
            args.defaultValue = _key;
            return this.getImpl(args);
        }
        args.key = _key;
        if (Array.isArray(_fieldName) && _fieldName.length === 1) {
            _fieldName = _fieldName[0];
        }
        if (typeof _fieldName !== 'string' && !Array.isArray(_fieldName)) {
            // get('User', 'me', { name: 'Alex'})
            args.defaultValue = _fieldName;
            return this.getImpl(args);
        }
        if (Array.isArray(_fieldName)) {
            // get('User', 'me', ['father', 'name'])
            const ref = this.get(_typeName, _key, _fieldName[0], _fieldArgs);
            assertIsRef(ref);
            return this.get(ref.$ref.typeName, ref.$ref.key, _fieldName.slice(1, _fieldName.length));
        }
        // get('User', 'me', 'name'...);
        args.fieldName = _fieldName;
        args.fieldArgs = _fieldArgs;
        return this.getImpl(args);
    }
    set(_typeName, _key, _fieldName, _value) {
        if (typeof _typeName !== 'string') {
            if (_key === undefined) {
                if (isRef(_typeName)) {
                    throw new Error("Can't provide a ref as first argument and no other argument");
                }
                // set({...})
                return this.setImpl(_typeName);
            }
            else {
                assertIsRef(_typeName);
                const { $ref } = _typeName;
                // arguments shift
                _value = _fieldName;
                _fieldName = _key;
                _key = $ref.key;
                _typeName = $ref.typeName;
            }
        }
        assertIsDefined(_key, 'key was not provided');
        const args = {
            typeName: _typeName,
            key: _key,
        };
        if (typeof _fieldName !== 'string') {
            // set('User', 1, { name: 'Foo' })
            if (!isRecord(_fieldName))
                throw new Error('Expected value to be a record');
            args.value = _fieldName;
            return this.setImpl(args);
        }
        args.fieldName = _fieldName;
        args.value = _value;
        return this.setImpl(args);
    }
    reset() {
        this.store = {};
    }
    filter(key, predicate) {
        const entity = this.store[key];
        return Object.values(entity).filter(predicate);
    }
    find(key, predicate) {
        const entity = this.store[key];
        return Object.values(entity).find(predicate);
    }
    getImpl(args) {
        const { typeName, key, fieldName, fieldArgs, defaultValue } = args;
        if (!fieldName) {
            if (defaultValue !== undefined && !isRecord(defaultValue)) {
                throw new Error('`defaultValue` should be an object');
            }
            let valuesToInsert = defaultValue || {};
            if (key) {
                valuesToInsert = { ...valuesToInsert, ...makeRef(typeName, key) };
            }
            return this.insert(typeName, valuesToInsert, true);
        }
        assertIsDefined(key, 'key argument should be given when fieldName is given');
        const fieldNameInStore = getFieldNameInStore(fieldName, fieldArgs);
        if (this.store[typeName] === undefined ||
            this.store[typeName][key] === undefined ||
            this.store[typeName][key][fieldNameInStore] === undefined) {
            let value;
            if (defaultValue !== undefined) {
                value = defaultValue;
            }
            else if (this.isKeyField(typeName, fieldName)) {
                value = key;
            }
            else {
                value = this.generateFieldValue(typeName, fieldName, (otherFieldName, otherValue) => {
                    // if we get a key field in the mix we don't care
                    if (this.isKeyField(typeName, otherFieldName))
                        return;
                    this.set({ typeName, key, fieldName: otherFieldName, value: otherValue, noOverride: true });
                });
            }
            this.set({ typeName, key, fieldName, fieldArgs, value, noOverride: true });
        }
        return this.store[typeName][key][fieldNameInStore];
    }
    setImpl(args) {
        const { typeName, key, fieldName, fieldArgs, noOverride } = args;
        let { value } = args;
        if (isMockList(value)) {
            value = deepResolveMockList(value);
        }
        if (this.store[typeName] === undefined) {
            this.store[typeName] = {};
        }
        if (this.store[typeName][key] === undefined) {
            this.store[typeName][key] = {};
        }
        if (!fieldName) {
            if (!isRecord(value)) {
                throw new Error('When no `fieldName` is provided, `value` should be a record.');
            }
            for (const fieldName in value) {
                this.setImpl({
                    typeName,
                    key,
                    fieldName,
                    value: value[fieldName],
                    noOverride,
                });
            }
            return;
        }
        const fieldNameInStore = getFieldNameInStore(fieldName, fieldArgs);
        if (this.isKeyField(typeName, fieldName) && value !== key) {
            throw new Error(`Field ${fieldName} is a key field of ${typeName} and you are trying to set it to ${value} while the key is ${key}`);
        }
        // if already set and we don't override
        if (this.store[typeName][key][fieldNameInStore] !== undefined && noOverride) {
            return;
        }
        const fieldType = this.getFieldType(typeName, fieldName);
        const currentValue = this.store[typeName][key][fieldNameInStore];
        let valueToStore;
        try {
            valueToStore = this.normalizeValueToStore(fieldType, value, currentValue, (typeName, values) => this.insert(typeName, values, noOverride));
        }
        catch (e) {
            throw new Error(`Value to set in ${typeName}.${fieldName} in not normalizable: ${e.message}`);
        }
        this.store[typeName][key] = {
            ...this.store[typeName][key],
            [fieldNameInStore]: valueToStore,
        };
    }
    normalizeValueToStore(fieldType, value, currentValue, onInsertType) {
        const fieldTypeName = fieldType.toString();
        if (value === null) {
            if (!graphql.isNullableType(fieldType)) {
                throw new Error(`should not be null because ${fieldTypeName} is not nullable. Received null.`);
            }
            return null;
        }
        const nullableFieldType = graphql.getNullableType(fieldType);
        if (value === undefined)
            return this.generateValueFromType(nullableFieldType);
        // deal with nesting insert
        if (graphql.isCompositeType(nullableFieldType)) {
            if (!isRecord(value))
                throw new Error(`should be an object or null or undefined. Received ${value}`);
            let joinedTypeName;
            if (graphql.isAbstractType(nullableFieldType)) {
                if (isRef(value)) {
                    joinedTypeName = value.$ref.typeName;
                }
                else {
                    if (typeof value['__typename'] !== 'string') {
                        throw new Error(`should contain a '__typename' because ${nullableFieldType.name} an abstract type`);
                    }
                    joinedTypeName = value['__typename'];
                }
            }
            else {
                joinedTypeName = nullableFieldType.name;
            }
            return onInsertType(joinedTypeName, isRef(currentValue) ? { ...currentValue, ...value } : value);
        }
        if (graphql.isListType(nullableFieldType)) {
            if (!Array.isArray(value))
                throw new Error(`should be an array or null or undefined. Received ${value}`);
            return value.map((v, index) => {
                return this.normalizeValueToStore(nullableFieldType.ofType, v, typeof currentValue === 'object' && currentValue != null && currentValue[index] ? currentValue : undefined, onInsertType);
            });
        }
        return value;
    }
    insert(typeName, values, noOverride) {
        const keyFieldName = this.getKeyFieldName(typeName);
        let key;
        // when we generate a key for the type, we might produce
        // other associated values with it
        // We keep track of them and we'll insert them, with propririty
        // for the ones that we areasked to insert
        const otherValues = {};
        if (isRef(values)) {
            key = values.$ref.key;
        }
        else if (keyFieldName && keyFieldName in values) {
            key = values[keyFieldName];
        }
        else {
            key = this.generateKeyForType(typeName, (otherFieldName, otherFieldValue) => {
                otherValues[otherFieldName] = otherFieldValue;
            });
        }
        const toInsert = { ...otherValues, ...values };
        for (const fieldName in toInsert) {
            if (fieldName === '$ref')
                continue;
            if (fieldName === '__typename')
                continue;
            this.set({
                typeName,
                key,
                fieldName,
                value: toInsert[fieldName],
                noOverride,
            });
        }
        if (this.store[typeName] === undefined) {
            this.store[typeName] = {};
        }
        if (this.store[typeName][key] === undefined) {
            this.store[typeName][key] = {};
        }
        return makeRef(typeName, key);
    }
    generateFieldValue(typeName, fieldName, onOtherFieldsGenerated) {
        const mockedValue = this.generateFieldValueFromMocks(typeName, fieldName, onOtherFieldsGenerated);
        if (mockedValue !== undefined)
            return mockedValue;
        const fieldType = this.getFieldType(typeName, fieldName);
        return this.generateValueFromType(fieldType);
    }
    generateFieldValueFromMocks(typeName, fieldName, onOtherFieldsGenerated) {
        let value;
        const mock = this.mocks ? this.mocks[typeName] : undefined;
        if (mock) {
            if (typeof mock === 'function') {
                const values = mock();
                if (typeof values !== 'object' || values == null) {
                    throw new Error(`Value returned by the mock for ${typeName} is not an object`);
                }
                for (const otherFieldName in values) {
                    if (otherFieldName === fieldName)
                        continue;
                    if (typeof values[otherFieldName] === 'function')
                        continue;
                    onOtherFieldsGenerated && onOtherFieldsGenerated(otherFieldName, values[otherFieldName]);
                }
                value = values[fieldName];
                if (typeof value === 'function')
                    value = value();
            }
            else if (typeof mock === 'object' && mock != null && typeof mock[fieldName] === 'function') {
                value = mock[fieldName]();
            }
        }
        if (value !== undefined)
            return value;
        const type = this.getType(typeName);
        // GraphQL 14 Compatibility
        const interfaces = 'getInterfaces' in type ? type.getInterfaces() : [];
        if (interfaces.length > 0) {
            for (const interface_ of interfaces) {
                if (value)
                    break;
                value = this.generateFieldValueFromMocks(interface_.name, fieldName, onOtherFieldsGenerated);
            }
        }
        return value;
    }
    generateKeyForType(typeName, onOtherFieldsGenerated) {
        const keyFieldName = this.getKeyFieldName(typeName);
        if (!keyFieldName)
            return uuidv4();
        return this.generateFieldValue(typeName, keyFieldName, onOtherFieldsGenerated);
    }
    generateValueFromType(fieldType) {
        const nullableType = graphql.getNullableType(fieldType);
        if (graphql.isScalarType(nullableType)) {
            const mockFn = this.mocks[nullableType.name];
            if (typeof mockFn !== 'function')
                throw new Error(`No mock defined for type "${nullableType.name}"`);
            return mockFn();
        }
        else if (graphql.isEnumType(nullableType)) {
            const mockFn = this.mocks[nullableType.name];
            if (typeof mockFn === 'function')
                return mockFn();
            const values = nullableType.getValues().map(v => v.value);
            return takeRandom(values);
        }
        else if (graphql.isObjectType(nullableType)) {
            // this will create a new random ref
            return this.insert(nullableType.name, {});
        }
        else if (graphql.isListType(nullableType)) {
            return [...new Array(randomListLength())].map(() => this.generateValueFromType(nullableType.ofType));
        }
        else if (graphql.isAbstractType(nullableType)) {
            const mock = this.mocks[nullableType.name];
            let typeName;
            let values = {};
            if (!mock) {
                typeName = takeRandom(this.schema.getPossibleTypes(nullableType).map(t => t.name));
            }
            else if (typeof mock === 'function') {
                const mockRes = mock();
                if (mockRes === null)
                    return null;
                if (!isRecord(mockRes)) {
                    throw new Error(`Value returned by the mock for ${nullableType.name} is not an object or null`);
                }
                values = mockRes;
                if (typeof values['__typename'] !== 'string') {
                    throw new Error(`Please return a __typename in "${nullableType.name}"`);
                }
                typeName = values['__typename'];
            }
            else if (typeof mock === 'object' && mock != null && typeof mock['__typename'] === 'function') {
                const mockRes = mock['__typename']();
                if (typeof mockRes !== 'string')
                    throw new Error(`'__typename' returned by the mock for abstract type ${nullableType.name} is not a string`);
                typeName = mockRes;
            }
            else {
                throw new Error(`Please return a __typename in "${nullableType.name}"`);
            }
            const toInsert = {};
            for (const fieldName in values) {
                if (fieldName === '__typename')
                    continue;
                const fieldValue = values[fieldName];
                toInsert[fieldName] = typeof fieldValue === 'function' ? fieldValue() : fieldValue;
            }
            return this.insert(typeName, toInsert);
        }
        else {
            throw new Error(`${nullableType} not implemented`);
        }
    }
    getFieldType(typeName, fieldName) {
        if (fieldName === '__typename') {
            return graphql.GraphQLString;
        }
        const type = this.getType(typeName);
        const field = type.getFields()[fieldName];
        if (!field) {
            throw new Error(`${fieldName} does not exist on type ${typeName}`);
        }
        return field.type;
    }
    getType(typeName) {
        const type = this.schema.getType(typeName);
        if (!type || !(graphql.isObjectType(type) || graphql.isInterfaceType(type))) {
            throw new Error(`${typeName} does not exist on schema or is not an object or interface`);
        }
        return type;
    }
    isKeyField(typeName, fieldName) {
        return this.getKeyFieldName(typeName) === fieldName;
    }
    getKeyFieldName(typeName) {
        var _a;
        const typePolicyKeyField = (_a = this.typePolicies[typeName]) === null || _a === void 0 ? void 0 : _a.keyFieldName;
        if (typePolicyKeyField !== undefined) {
            if (typePolicyKeyField === false)
                return null;
            return typePolicyKeyField;
        }
        // How about common key field names?
        const gqlType = this.getType(typeName);
        for (const fieldName in gqlType.getFields()) {
            if (defaultKeyFieldNames.includes(fieldName)) {
                return fieldName;
            }
        }
        return null;
    }
}
const getFieldNameInStore = (fieldName, fieldArgs) => {
    if (!fieldArgs)
        return fieldName;
    if (typeof fieldArgs === 'string') {
        return `${fieldName}:${fieldArgs}`;
    }
    // empty args
    if (Object.keys(fieldArgs).length === 0) {
        return fieldName;
    }
    return `${fieldName}:${stringify(fieldArgs)}`;
};
function assertIsDefined(value, message) {
    if (value !== undefined && value !== null) {
        return;
    }
    throw new Error(process.env['NODE_ENV'] === 'production' ? 'Invariant failed:' : `Invariant failed: ${message || ''}`);
}
/**
 * Will create `MockStore` for the given `schema`.
 *
 * A `MockStore` will generate mock values for the given schem when queried.
 *
 * It will stores generated mocks, so that, provided with same arguments
 * the returned values will be the same.
 *
 * Its API also allows to modify the stored values.
 *
 * Basic example:
 * ```ts
 * store.get('User', 1, 'name');
 * // > "Hello World"
 * store.set('User', 1, 'name', 'Alexandre');
 * store.get('User', 1, 'name');
 * // > "Alexandre"
 * ```
 *
 * The storage key will correspond to the "key field"
 * of the type. Field with name `id` or `_id` will be
 * by default considered as the key field for the type.
 * However, use `typePolicies` to precise the field to use
 * as key.
 */
function createMockStore(options) {
    return new MockStore(options);
}

// todo: add option to preserve resolver
/**
 * Given a `schema` and a `MockStore`, returns an executable schema that
 * will use the provided `MockStore` to execute queries.
 *
 * ```ts
 * const schema = buildSchema(`
 *  type User {
 *    id: ID!
 *    name: String!
 *  }
 *  type Query {
 *    me: User!
 *  }
 * `)
 *
 * const store = createMockStore({ schema });
 * const mockedSchema = addMocksToSchema({ schema, store });
 * ```
 *
 *
 * If a `resolvers` parameter is passed, the query execution will use
 * the provided `resolvers` if, one exists, instead of the default mock
 * resolver.
 *
 *
 * ```ts
 * const schema = buildSchema(`
 *   type User {
 *     id: ID!
 *     name: String!
 *   }
 *   type Query {
 *     me: User!
 *   }
 *   type Mutation {
 *     setMyName(newName: String!): User!
 *   }
 * `)
 *
 * const store = createMockStore({ schema });
 * const mockedSchema = addMocksToSchema({
 *   schema,
 *   store,
 *   resolvers: {
 *     Mutation: {
 *       setMyName: (_, { newName }) => {
 *          const ref = store.get('Query', 'ROOT', 'viewer');
 *          store.set(ref, 'name', newName);
 *          return ref;
 *       }
 *     }
 *   }
 *  });
 * ```
 *
 *
 * `Query` and `Mutation` type will use `key` `'ROOT'`.
 */
function addMocksToSchema({ schema: schema$1, store: maybeStore, mocks, typePolicies, resolvers: resolversOrFnResolvers, preserveResolvers = false, }) {
    if (!schema$1) {
        throw new Error('Must provide schema to mock');
    }
    if (!graphql.isSchema(schema$1)) {
        throw new Error('Value at "schema" must be of type GraphQLSchema');
    }
    if (mocks && !isObject(mocks)) {
        throw new Error('mocks must be of type Object');
    }
    const store = maybeStore ||
        createMockStore({
            schema: schema$1,
            mocks,
            typePolicies,
        });
    const resolvers = typeof resolversOrFnResolvers === 'function'
        ? resolversOrFnResolvers(store)
        : resolversOrFnResolvers;
    const mockResolver = (source, args, contex, info) => {
        const defaultResolvedValue = graphql.defaultFieldResolver(source, args, contex, info);
        // priority to default resolved value
        if (defaultResolvedValue !== undefined)
            return defaultResolvedValue;
        if (isRef(source)) {
            return store.get({
                typeName: source.$ref.typeName,
                key: source.$ref.key,
                fieldName: info.fieldName,
                fieldArgs: args,
            });
        }
        // we have to handle the root mutation, root query and root subscription types
        // differently, because no resolver is called at the root
        if (isRootType(info.parentType, info.schema)) {
            return store.get({
                typeName: info.parentType.name,
                key: 'ROOT',
                fieldName: info.fieldName,
                fieldArgs: args,
            });
        }
        if (defaultResolvedValue === undefined) {
            // any is used here because generateFieldValue is a private method at time of writing
            return store.generateFieldValue(info.parentType.name, info.fieldName);
        }
        return undefined;
    };
    const typeResolver = data => {
        if (isRef(data)) {
            return data.$ref.typeName;
        }
    };
    const mockSubscriber = () => ({
        [Symbol.asyncIterator]() {
            return {
                async next() {
                    return {
                        done: true,
                        value: {},
                    };
                },
            };
        },
    });
    const schemaWithMocks = utils.mapSchema(schema$1, {
        [utils.MapperKind.OBJECT_FIELD]: fieldConfig => {
            const newFieldConfig = {
                ...fieldConfig,
            };
            const oldResolver = fieldConfig.resolve;
            if (!preserveResolvers || !oldResolver) {
                newFieldConfig.resolve = mockResolver;
            }
            else {
                newFieldConfig.resolve = async (rootObject, args, context, info) => {
                    const [mockedValue, resolvedValue] = await Promise.all([
                        mockResolver(rootObject, args, context, info),
                        oldResolver(rootObject, args, context, info),
                    ]);
                    // In case we couldn't mock
                    if (mockedValue instanceof Error) {
                        // only if value was not resolved, populate the error.
                        if (undefined === resolvedValue) {
                            throw mockedValue;
                        }
                        return resolvedValue;
                    }
                    if (resolvedValue instanceof Date && mockedValue instanceof Date) {
                        return undefined !== resolvedValue ? resolvedValue : mockedValue;
                    }
                    if (isObject(mockedValue) && isObject(resolvedValue)) {
                        // Object.assign() won't do here, as we need to all properties, including
                        // the non-enumerable ones and defined using Object.defineProperty
                        const emptyObject = Object.create(Object.getPrototypeOf(resolvedValue));
                        return copyOwnProps(emptyObject, resolvedValue, mockedValue);
                    }
                    return undefined !== resolvedValue ? resolvedValue : mockedValue;
                };
            }
            const fieldSubscriber = fieldConfig.subscribe;
            if (!preserveResolvers || !fieldSubscriber) {
                newFieldConfig.subscribe = mockSubscriber;
            }
            else {
                newFieldConfig.subscribe = async (rootObject, args, context, info) => {
                    const [mockAsyncIterable, oldAsyncIterable] = await Promise.all([
                        mockSubscriber(),
                        fieldSubscriber(rootObject, args, context, info),
                    ]);
                    return oldAsyncIterable || mockAsyncIterable;
                };
            }
            return newFieldConfig;
        },
        [utils.MapperKind.ABSTRACT_TYPE]: type => {
            if (preserveResolvers && type.resolveType != null && type.resolveType.length) {
                return;
            }
            if (graphql.isUnionType(type)) {
                return new graphql.GraphQLUnionType({
                    ...type.toConfig(),
                    resolveType: typeResolver,
                });
            }
            else {
                return new graphql.GraphQLInterfaceType({
                    ...type.toConfig(),
                    resolveType: typeResolver,
                });
            }
        },
    });
    return resolvers ? schema.addResolversToSchema(schemaWithMocks, resolvers) : schemaWithMocks;
}

/**
 * A convenience wrapper on top of addMocksToSchema. It adds your mock resolvers
 * to your schema and returns a client that will correctly execute your query with
 * variables. Note: when executing queries from the returned server, context and
 * root will both equal `{}`.
 * @param schema The schema to which to add mocks. This can also be a set of type
 * definitions instead.
 * @param mocks The mocks to add to the schema.
 * @param preserveResolvers Set to `true` to prevent existing resolvers from being
 * overwritten to provide mock data. This can be used to mock some parts of the
 * server and not others.
 */
function mockServer(schema$1, mocks, preserveResolvers = false) {
    const mockedSchema = addMocksToSchema({
        schema: graphql.isSchema(schema$1)
            ? schema$1
            : schema.makeExecutableSchema({
                typeDefs: schema$1,
            }),
        mocks,
        preserveResolvers,
    });
    return {
        query: (query, vars) => graphql.graphql({
            schema: mockedSchema,
            source: query,
            rootValue: {},
            contextValue: {},
            variableValues: vars,
        }),
    };
}

/**
 * Produces a resolver that'll mock a [Relay-style cursor pagination](https://relay.dev/graphql/connections.htm).
 *
 * ```ts
 * const schemaWithMocks = addMocksToSchema({
 *   schema,
 *   resolvers: (store) => ({
 *     User: {
 *       friends: relayStylePaginationMock(store),
 *     }
 *   }),
 * })
 * ```
 * @param store the MockStore
 */
const relayStylePaginationMock = (store, { cursorFn = node => `${node.$ref.key}`, applyOnNodes, allNodesFn, } = {}) => {
    return (parent, args, context, info) => {
        const source = isRootType(info.parentType, info.schema) ? makeRef(info.parentType.name, 'ROOT') : parent;
        const allNodesFn_ = allNodesFn !== null && allNodesFn !== void 0 ? allNodesFn : defaultAllNodesFn(store);
        let allNodes = allNodesFn_(source, args, context, info);
        if (applyOnNodes) {
            allNodes = applyOnNodes(allNodes, args);
        }
        const allEdges = allNodes.map(node => ({
            node,
            cursor: cursorFn(node),
        }));
        let start, end;
        const { first, after, last, before } = args;
        if (typeof first === 'number') {
            // forward pagination
            if (last || before) {
                throw new Error("if `first` is provided, `last` or `before` can't be provided");
            }
            const afterIndex = after ? allEdges.findIndex(e => e.cursor === after) : -1;
            start = afterIndex + 1;
            end = afterIndex + 1 + first;
        }
        else if (typeof last === 'number') {
            // backward pagination
            if (first || after) {
                throw new Error("if `last` is provided, `first` or `after` can't be provided");
            }
            const foundBeforeIndex = before ? allEdges.findIndex(e => e.cursor === before) : -1;
            const beforeIndex = foundBeforeIndex !== -1 ? foundBeforeIndex : allNodes.length;
            start = allEdges.length - (allEdges.length - beforeIndex) - last;
            // negative index on Array.slice indicate offset from end of sequence => we don't want
            if (start < 0)
                start = 0;
            end = beforeIndex;
        }
        else {
            throw new Error('A `first` or a `last` arguments should be provided');
        }
        const edges = allEdges.slice(start, end);
        const pageInfo = {
            startCursor: edges.length > 0 ? edges[0].cursor : '',
            endCursor: edges.length > 0 ? edges[edges.length - 1].cursor : '',
            hasNextPage: end < allEdges.length - 1,
            hasPreviousPage: start > 0,
        };
        return {
            edges,
            pageInfo,
            totalCount: allEdges.length,
        };
    };
};
const defaultAllNodesFn = (store) => (parent, _, __, info) => store.get(parent, [info.fieldName, 'edges']).map(e => store.get(e, 'node'));

exports.MockList = MockList;
exports.MockStore = MockStore;
exports.addMocksToSchema = addMocksToSchema;
exports.assertIsRef = assertIsRef;
exports.createMockStore = createMockStore;
exports.deepResolveMockList = deepResolveMockList;
exports.defaultMocks = defaultMocks;
exports.isMockList = isMockList;
exports.isRecord = isRecord;
exports.isRef = isRef;
exports.mockServer = mockServer;
exports.relayStylePaginationMock = relayStylePaginationMock;
