'use strict';

Object.defineProperty(exports, '__esModule', { value: true });

const graphql = require('graphql');
const utils = require('@graphql-tools/utils');
const merge = require('@graphql-tools/merge');

function assertResolversPresent(schema, resolverValidationOptions = {}) {
    const { requireResolversForArgs, requireResolversForNonScalar, requireResolversForAllFields } = resolverValidationOptions;
    if (requireResolversForAllFields && (requireResolversForArgs || requireResolversForNonScalar)) {
        throw new TypeError('requireResolversForAllFields takes precedence over the more specific assertions. ' +
            'Please configure either requireResolversForAllFields or requireResolversForArgs / ' +
            'requireResolversForNonScalar, but not a combination of them.');
    }
    utils.forEachField(schema, (field, typeName, fieldName) => {
        // requires a resolver for *every* field.
        if (requireResolversForAllFields) {
            expectResolver('requireResolversForAllFields', requireResolversForAllFields, field, typeName, fieldName);
        }
        // requires a resolver on every field that has arguments
        if (requireResolversForArgs && field.args.length > 0) {
            expectResolver('requireResolversForArgs', requireResolversForArgs, field, typeName, fieldName);
        }
        // requires a resolver on every field that returns a non-scalar type
        if (requireResolversForNonScalar !== 'ignore' && !graphql.isScalarType(graphql.getNamedType(field.type))) {
            expectResolver('requireResolversForNonScalar', requireResolversForNonScalar, field, typeName, fieldName);
        }
    });
}
function expectResolver(validator, behavior, field, typeName, fieldName) {
    if (!field.resolve) {
        const message = `Resolver missing for "${typeName}.${fieldName}".
To disable this validator, use:
  resolverValidationOptions: {
    ${validator}: 'ignore'
  }`;
        if (behavior === 'error') {
            throw new Error(message);
        }
        if (behavior === 'warn') {
            console.warn(message);
        }
        return;
    }
    if (typeof field.resolve !== 'function') {
        throw new Error(`Resolver "${typeName}.${fieldName}" must be a function`);
    }
}

function chainResolvers(resolvers) {
    return (root, args, ctx, info) => resolvers.reduce((prev, curResolver) => {
        if (curResolver != null) {
            return curResolver(prev, args, ctx, info);
        }
        return graphql.defaultFieldResolver(prev, args, ctx, info);
    }, root);
}

// If we have any union or interface types throw if no there is no resolveType resolver
function checkForResolveTypeResolver(schema, requireResolversForResolveType) {
    utils.mapSchema(schema, {
        [utils.MapperKind.ABSTRACT_TYPE]: type => {
            if (!type.resolveType) {
                const message = `Type "${type.name}" is missing a "__resolveType" resolver. Pass 'ignore' into ` +
                    '"resolverValidationOptions.requireResolversForResolveType" to disable this error.';
                if (requireResolversForResolveType === 'error') {
                    throw new Error(message);
                }
                if (requireResolversForResolveType === 'warn') {
                    console.warn(message);
                }
            }
            return undefined;
        },
    });
}

function extendResolversFromInterfaces(schema, resolvers) {
    const extendedResolvers = {};
    const typeMap = schema.getTypeMap();
    for (const typeName in typeMap) {
        const type = typeMap[typeName];
        if ('getInterfaces' in type) {
            extendedResolvers[typeName] = {};
            for (const iFace of type.getInterfaces()) {
                if (resolvers[iFace.name]) {
                    for (const fieldName in resolvers[iFace.name]) {
                        if (fieldName === '__isTypeOf' || !fieldName.startsWith('__')) {
                            extendedResolvers[typeName][fieldName] = resolvers[iFace.name][fieldName];
                        }
                    }
                }
            }
            const typeResolvers = resolvers[typeName];
            extendedResolvers[typeName] = {
                ...extendedResolvers[typeName],
                ...typeResolvers,
            };
        }
        else {
            const typeResolvers = resolvers[typeName];
            if (typeResolvers != null) {
                extendedResolvers[typeName] = typeResolvers;
            }
        }
    }
    return extendedResolvers;
}

function addResolversToSchema(schemaOrOptions, legacyInputResolvers, legacyInputValidationOptions) {
    const options = graphql.isSchema(schemaOrOptions)
        ? {
            schema: schemaOrOptions,
            resolvers: legacyInputResolvers !== null && legacyInputResolvers !== void 0 ? legacyInputResolvers : {},
            resolverValidationOptions: legacyInputValidationOptions,
        }
        : schemaOrOptions;
    let { schema, resolvers: inputResolvers, defaultFieldResolver, resolverValidationOptions = {}, inheritResolversFromInterfaces = false, updateResolversInPlace = false, } = options;
    const { requireResolversToMatchSchema = 'error', requireResolversForResolveType } = resolverValidationOptions;
    const resolvers = inheritResolversFromInterfaces
        ? extendResolversFromInterfaces(schema, inputResolvers)
        : inputResolvers;
    for (const typeName in resolvers) {
        const resolverValue = resolvers[typeName];
        const resolverType = typeof resolverValue;
        if (resolverType !== 'object') {
            throw new Error(`"${typeName}" defined in resolvers, but has invalid value "${resolverValue}". The resolver's value must be of type object.`);
        }
        const type = schema.getType(typeName);
        if (type == null) {
            if (requireResolversToMatchSchema === 'ignore') {
                continue;
            }
            throw new Error(`"${typeName}" defined in resolvers, but not in schema`);
        }
        else if (graphql.isSpecifiedScalarType(type)) {
            // allow -- without recommending -- overriding of specified scalar types
            for (const fieldName in resolverValue) {
                if (fieldName.startsWith('__')) {
                    type[fieldName.substring(2)] = resolverValue[fieldName];
                }
                else {
                    type[fieldName] = resolverValue[fieldName];
                }
            }
        }
        else if (graphql.isEnumType(type)) {
            const values = type.getValues();
            for (const fieldName in resolverValue) {
                if (!fieldName.startsWith('__') &&
                    !values.some(value => value.name === fieldName) &&
                    requireResolversToMatchSchema &&
                    requireResolversToMatchSchema !== 'ignore') {
                    throw new Error(`${type.name}.${fieldName} was defined in resolvers, but not present within ${type.name}`);
                }
            }
        }
        else if (graphql.isUnionType(type)) {
            for (const fieldName in resolverValue) {
                if (!fieldName.startsWith('__') &&
                    requireResolversToMatchSchema &&
                    requireResolversToMatchSchema !== 'ignore') {
                    throw new Error(`${type.name}.${fieldName} was defined in resolvers, but ${type.name} is not an object or interface type`);
                }
            }
        }
        else if (graphql.isObjectType(type) || graphql.isInterfaceType(type)) {
            for (const fieldName in resolverValue) {
                if (!fieldName.startsWith('__')) {
                    const fields = type.getFields();
                    const field = fields[fieldName];
                    if (field == null) {
                        // Field present in resolver but not in schema
                        if (requireResolversToMatchSchema && requireResolversToMatchSchema !== 'ignore') {
                            throw new Error(`${typeName}.${fieldName} defined in resolvers, but not in schema`);
                        }
                    }
                    else {
                        // Field present in both the resolver and schema
                        const fieldResolve = resolverValue[fieldName];
                        if (typeof fieldResolve !== 'function' && typeof fieldResolve !== 'object') {
                            throw new Error(`Resolver ${typeName}.${fieldName} must be object or function`);
                        }
                    }
                }
            }
        }
    }
    schema = updateResolversInPlace
        ? addResolversToExistingSchema(schema, resolvers, defaultFieldResolver)
        : createNewSchemaWithResolvers(schema, resolvers, defaultFieldResolver);
    if (requireResolversForResolveType && requireResolversForResolveType !== 'ignore') {
        checkForResolveTypeResolver(schema, requireResolversForResolveType);
    }
    return schema;
}
function addResolversToExistingSchema(schema, resolvers, defaultFieldResolver) {
    var _a, _b, _c, _d, _e, _f, _g, _h, _j, _k, _l, _m;
    const typeMap = schema.getTypeMap();
    for (const typeName in resolvers) {
        const type = schema.getType(typeName);
        const resolverValue = resolvers[typeName];
        if (graphql.isScalarType(type)) {
            for (const fieldName in resolverValue) {
                if (fieldName.startsWith('__')) {
                    type[fieldName.substring(2)] = resolverValue[fieldName];
                }
                else if (fieldName === 'astNode' && type.astNode != null) {
                    type.astNode = {
                        ...type.astNode,
                        description: (_b = (_a = resolverValue === null || resolverValue === void 0 ? void 0 : resolverValue.astNode) === null || _a === void 0 ? void 0 : _a.description) !== null && _b !== void 0 ? _b : type.astNode.description,
                        directives: ((_c = type.astNode.directives) !== null && _c !== void 0 ? _c : []).concat((_e = (_d = resolverValue === null || resolverValue === void 0 ? void 0 : resolverValue.astNode) === null || _d === void 0 ? void 0 : _d.directives) !== null && _e !== void 0 ? _e : []),
                    };
                }
                else if (fieldName === 'extensionASTNodes' && type.extensionASTNodes != null) {
                    type.extensionASTNodes = type.extensionASTNodes.concat((_f = resolverValue === null || resolverValue === void 0 ? void 0 : resolverValue.extensionASTNodes) !== null && _f !== void 0 ? _f : []);
                }
                else if (fieldName === 'extensions' &&
                    type.extensions != null &&
                    resolverValue.extensions != null) {
                    type.extensions = Object.assign(Object.create(null), type.extensions, resolverValue.extensions);
                }
                else {
                    type[fieldName] = resolverValue[fieldName];
                }
            }
        }
        else if (graphql.isEnumType(type)) {
            const config = type.toConfig();
            const enumValueConfigMap = config.values;
            for (const fieldName in resolverValue) {
                if (fieldName.startsWith('__')) {
                    config[fieldName.substring(2)] = resolverValue[fieldName];
                }
                else if (fieldName === 'astNode' && config.astNode != null) {
                    config.astNode = {
                        ...config.astNode,
                        description: (_h = (_g = resolverValue === null || resolverValue === void 0 ? void 0 : resolverValue.astNode) === null || _g === void 0 ? void 0 : _g.description) !== null && _h !== void 0 ? _h : config.astNode.description,
                        directives: ((_j = config.astNode.directives) !== null && _j !== void 0 ? _j : []).concat((_l = (_k = resolverValue === null || resolverValue === void 0 ? void 0 : resolverValue.astNode) === null || _k === void 0 ? void 0 : _k.directives) !== null && _l !== void 0 ? _l : []),
                    };
                }
                else if (fieldName === 'extensionASTNodes' && config.extensionASTNodes != null) {
                    config.extensionASTNodes = config.extensionASTNodes.concat((_m = resolverValue === null || resolverValue === void 0 ? void 0 : resolverValue.extensionASTNodes) !== null && _m !== void 0 ? _m : []);
                }
                else if (fieldName === 'extensions' &&
                    type.extensions != null &&
                    resolverValue.extensions != null) {
                    type.extensions = Object.assign(Object.create(null), type.extensions, resolverValue.extensions);
                }
                else if (enumValueConfigMap[fieldName]) {
                    enumValueConfigMap[fieldName].value = resolverValue[fieldName];
                }
            }
            typeMap[typeName] = new graphql.GraphQLEnumType(config);
        }
        else if (graphql.isUnionType(type)) {
            for (const fieldName in resolverValue) {
                if (fieldName.startsWith('__')) {
                    type[fieldName.substring(2)] = resolverValue[fieldName];
                }
            }
        }
        else if (graphql.isObjectType(type) || graphql.isInterfaceType(type)) {
            for (const fieldName in resolverValue) {
                if (fieldName.startsWith('__')) {
                    // this is for isTypeOf and resolveType and all the other stuff.
                    type[fieldName.substring(2)] = resolverValue[fieldName];
                    continue;
                }
                const fields = type.getFields();
                const field = fields[fieldName];
                if (field != null) {
                    const fieldResolve = resolverValue[fieldName];
                    if (typeof fieldResolve === 'function') {
                        // for convenience. Allows shorter syntax in resolver definition file
                        field.resolve = fieldResolve.bind(resolverValue);
                    }
                    else {
                        setFieldProperties(field, fieldResolve);
                    }
                }
            }
        }
    }
    // serialize all default values prior to healing fields with new scalar/enum types.
    utils.forEachDefaultValue(schema, utils.serializeInputValue);
    // schema may have new scalar/enum types that require healing
    utils.healSchema(schema);
    // reparse all default values with new parsing functions.
    utils.forEachDefaultValue(schema, utils.parseInputValue);
    if (defaultFieldResolver != null) {
        utils.forEachField(schema, field => {
            if (!field.resolve) {
                field.resolve = defaultFieldResolver;
            }
        });
    }
    return schema;
}
function createNewSchemaWithResolvers(schema, resolvers, defaultFieldResolver) {
    schema = utils.mapSchema(schema, {
        [utils.MapperKind.SCALAR_TYPE]: type => {
            var _a, _b, _c, _d, _e, _f;
            const config = type.toConfig();
            const resolverValue = resolvers[type.name];
            if (!graphql.isSpecifiedScalarType(type) && resolverValue != null) {
                for (const fieldName in resolverValue) {
                    if (fieldName.startsWith('__')) {
                        config[fieldName.substring(2)] = resolverValue[fieldName];
                    }
                    else if (fieldName === 'astNode' && config.astNode != null) {
                        config.astNode = {
                            ...config.astNode,
                            description: (_b = (_a = resolverValue === null || resolverValue === void 0 ? void 0 : resolverValue.astNode) === null || _a === void 0 ? void 0 : _a.description) !== null && _b !== void 0 ? _b : config.astNode.description,
                            directives: ((_c = config.astNode.directives) !== null && _c !== void 0 ? _c : []).concat((_e = (_d = resolverValue === null || resolverValue === void 0 ? void 0 : resolverValue.astNode) === null || _d === void 0 ? void 0 : _d.directives) !== null && _e !== void 0 ? _e : []),
                        };
                    }
                    else if (fieldName === 'extensionASTNodes' && config.extensionASTNodes != null) {
                        config.extensionASTNodes = config.extensionASTNodes.concat((_f = resolverValue === null || resolverValue === void 0 ? void 0 : resolverValue.extensionASTNodes) !== null && _f !== void 0 ? _f : []);
                    }
                    else if (fieldName === 'extensions' &&
                        config.extensions != null &&
                        resolverValue.extensions != null) {
                        config.extensions = Object.assign(Object.create(null), type.extensions, resolverValue.extensions);
                    }
                    else {
                        config[fieldName] = resolverValue[fieldName];
                    }
                }
                return new graphql.GraphQLScalarType(config);
            }
        },
        [utils.MapperKind.ENUM_TYPE]: type => {
            var _a, _b, _c, _d, _e, _f;
            const resolverValue = resolvers[type.name];
            const config = type.toConfig();
            const enumValueConfigMap = config.values;
            if (resolverValue != null) {
                for (const fieldName in resolverValue) {
                    if (fieldName.startsWith('__')) {
                        config[fieldName.substring(2)] = resolverValue[fieldName];
                    }
                    else if (fieldName === 'astNode' && config.astNode != null) {
                        config.astNode = {
                            ...config.astNode,
                            description: (_b = (_a = resolverValue === null || resolverValue === void 0 ? void 0 : resolverValue.astNode) === null || _a === void 0 ? void 0 : _a.description) !== null && _b !== void 0 ? _b : config.astNode.description,
                            directives: ((_c = config.astNode.directives) !== null && _c !== void 0 ? _c : []).concat((_e = (_d = resolverValue === null || resolverValue === void 0 ? void 0 : resolverValue.astNode) === null || _d === void 0 ? void 0 : _d.directives) !== null && _e !== void 0 ? _e : []),
                        };
                    }
                    else if (fieldName === 'extensionASTNodes' && config.extensionASTNodes != null) {
                        config.extensionASTNodes = config.extensionASTNodes.concat((_f = resolverValue === null || resolverValue === void 0 ? void 0 : resolverValue.extensionASTNodes) !== null && _f !== void 0 ? _f : []);
                    }
                    else if (fieldName === 'extensions' &&
                        config.extensions != null &&
                        resolverValue.extensions != null) {
                        config.extensions = Object.assign(Object.create(null), type.extensions, resolverValue.extensions);
                    }
                    else if (enumValueConfigMap[fieldName]) {
                        enumValueConfigMap[fieldName].value = resolverValue[fieldName];
                    }
                }
                return new graphql.GraphQLEnumType(config);
            }
        },
        [utils.MapperKind.UNION_TYPE]: type => {
            const resolverValue = resolvers[type.name];
            if (resolverValue != null) {
                const config = type.toConfig();
                if (resolverValue['__resolveType']) {
                    config.resolveType = resolverValue['__resolveType'];
                }
                return new graphql.GraphQLUnionType(config);
            }
        },
        [utils.MapperKind.OBJECT_TYPE]: type => {
            const resolverValue = resolvers[type.name];
            if (resolverValue != null) {
                const config = type.toConfig();
                if (resolverValue['__isTypeOf']) {
                    config.isTypeOf = resolverValue['__isTypeOf'];
                }
                return new graphql.GraphQLObjectType(config);
            }
        },
        [utils.MapperKind.INTERFACE_TYPE]: type => {
            const resolverValue = resolvers[type.name];
            if (resolverValue != null) {
                const config = type.toConfig();
                if (resolverValue['__resolveType']) {
                    config.resolveType = resolverValue['__resolveType'];
                }
                return new graphql.GraphQLInterfaceType(config);
            }
        },
        [utils.MapperKind.COMPOSITE_FIELD]: (fieldConfig, fieldName, typeName) => {
            const resolverValue = resolvers[typeName];
            if (resolverValue != null) {
                const fieldResolve = resolverValue[fieldName];
                if (fieldResolve != null) {
                    const newFieldConfig = { ...fieldConfig };
                    if (typeof fieldResolve === 'function') {
                        // for convenience. Allows shorter syntax in resolver definition file
                        newFieldConfig.resolve = fieldResolve.bind(resolverValue);
                    }
                    else {
                        setFieldProperties(newFieldConfig, fieldResolve);
                    }
                    return newFieldConfig;
                }
            }
        },
    });
    if (defaultFieldResolver != null) {
        schema = utils.mapSchema(schema, {
            [utils.MapperKind.OBJECT_FIELD]: fieldConfig => ({
                ...fieldConfig,
                resolve: fieldConfig.resolve != null ? fieldConfig.resolve : defaultFieldResolver,
            }),
        });
    }
    return schema;
}
function setFieldProperties(field, propertiesObj) {
    for (const propertyName in propertiesObj) {
        field[propertyName] = propertiesObj[propertyName];
    }
}

/**
 * Builds a schema from the provided type definitions and resolvers.
 *
 * The type definitions are written using Schema Definition Language (SDL). They
 * can be provided as a string, a `DocumentNode`, a function, or an array of any
 * of these. If a function is provided, it will be passed no arguments and
 * should return an array of strings or `DocumentNode`s.
 *
 * Note: You can use `graphql-tag` to not only parse a string into a
 * `DocumentNode` but also to provide additional syntax highlighting in your
 * editor (with the appropriate editor plugin).
 *
 * ```js
 * const typeDefs = gql`
 *   type Query {
 *     posts: [Post]
 *     author(id: Int!): Author
 *   }
 * `;
 * ```
 *
 * The `resolvers` object should be a map of type names to nested object, which
 * themselves map the type's fields to their appropriate resolvers.
 * See the [Resolvers](/docs/resolvers) section of the documentation for more details.
 *
 * ```js
 * const resolvers = {
 *   Query: {
 *     posts: (obj, args, ctx, info) => getAllPosts(),
 *     author: (obj, args, ctx, info) => getAuthorById(args.id)
 *   }
 * };
 * ```
 *
 * Once you've defined both the `typeDefs` and `resolvers`, you can create your
 * schema:
 *
 * ```js
 * const schema = makeExecutableSchema({
 *   typeDefs,
 *   resolvers,
 * })
 * ```
 */
function makeExecutableSchema({ typeDefs, resolvers = {}, resolverValidationOptions = {}, parseOptions = {}, inheritResolversFromInterfaces = false, pruningOptions, updateResolversInPlace = false, schemaExtensions, }) {
    // Validate and clean up arguments
    if (typeof resolverValidationOptions !== 'object') {
        throw new Error('Expected `resolverValidationOptions` to be an object');
    }
    if (!typeDefs) {
        throw new Error('Must provide typeDefs');
    }
    let schema;
    if (graphql.isSchema(typeDefs)) {
        schema = typeDefs;
    }
    else if (parseOptions === null || parseOptions === void 0 ? void 0 : parseOptions.commentDescriptions) {
        const mergedTypeDefs = merge.mergeTypeDefs(typeDefs, {
            ...parseOptions,
            commentDescriptions: true,
        });
        schema = graphql.buildSchema(mergedTypeDefs, parseOptions);
    }
    else {
        const mergedTypeDefs = merge.mergeTypeDefs(typeDefs, parseOptions);
        schema = graphql.buildASTSchema(mergedTypeDefs, parseOptions);
    }
    if (pruningOptions) {
        schema = utils.pruneSchema(schema);
    }
    // We allow passing in an array of resolver maps, in which case we merge them
    schema = addResolversToSchema({
        schema,
        resolvers: merge.mergeResolvers(resolvers),
        resolverValidationOptions,
        inheritResolversFromInterfaces,
        updateResolversInPlace,
    });
    if (Object.keys(resolverValidationOptions).length > 0) {
        assertResolversPresent(schema, resolverValidationOptions);
    }
    if (schemaExtensions) {
        schemaExtensions = merge.mergeExtensions(utils.asArray(schemaExtensions));
        merge.applyExtensions(schema, schemaExtensions);
    }
    return schema;
}

/**
 * Synchronously merges multiple schemas, typeDefinitions and/or resolvers into a single schema.
 * @param config Configuration object
 */
function mergeSchemas(config) {
    const extractedTypeDefs = utils.asArray(config.typeDefs || []);
    const extractedResolvers = utils.asArray(config.resolvers || []);
    const extractedSchemaExtensions = utils.asArray(config.schemaExtensions || []);
    const schemas = config.schemas || [];
    for (const schema of schemas) {
        extractedTypeDefs.push(schema);
        extractedResolvers.push(utils.getResolversFromSchema(schema));
        extractedSchemaExtensions.push(merge.extractExtensionsFromSchema(schema));
    }
    return makeExecutableSchema({
        parseOptions: config,
        ...config,
        typeDefs: extractedTypeDefs,
        resolvers: extractedResolvers,
        schemaExtensions: extractedSchemaExtensions,
    });
}

exports.addResolversToSchema = addResolversToSchema;
exports.assertResolversPresent = assertResolversPresent;
exports.chainResolvers = chainResolvers;
exports.checkForResolveTypeResolver = checkForResolveTypeResolver;
exports.extendResolversFromInterfaces = extendResolversFromInterfaces;
exports.makeExecutableSchema = makeExecutableSchema;
exports.mergeSchemas = mergeSchemas;
