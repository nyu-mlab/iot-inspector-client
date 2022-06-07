'use strict';

Object.defineProperty(exports, '__esModule', { value: true });

const utils = require('@graphql-tools/utils');
const graphql = require('graphql');

/**
 * Deep merges multiple resolver definition objects into a single definition.
 * @param resolversDefinitions Resolver definitions to be merged
 * @param options Additional options
 *
 * ```js
 * const { mergeResolvers } = require('@graphql-tools/merge');
 * const clientResolver = require('./clientResolver');
 * const productResolver = require('./productResolver');
 *
 * const resolvers = mergeResolvers([
 *  clientResolver,
 *  productResolver,
 * ]);
 * ```
 *
 * If you don't want to manually create the array of resolver objects, you can
 * also use this function along with loadFiles:
 *
 * ```js
 * const path = require('path');
 * const { mergeResolvers } = require('@graphql-tools/merge');
 * const { loadFilesSync } = require('@graphql-tools/load-files');
 *
 * const resolversArray = loadFilesSync(path.join(__dirname, './resolvers'));
 *
 * const resolvers = mergeResolvers(resolversArray)
 * ```
 */
function mergeResolvers(resolversDefinitions, options) {
    if (!resolversDefinitions || (Array.isArray(resolversDefinitions) && resolversDefinitions.length === 0)) {
        return {};
    }
    if (!Array.isArray(resolversDefinitions)) {
        return resolversDefinitions;
    }
    if (resolversDefinitions.length === 1) {
        return resolversDefinitions[0] || {};
    }
    const resolvers = new Array();
    for (let resolversDefinition of resolversDefinitions) {
        if (Array.isArray(resolversDefinition)) {
            resolversDefinition = mergeResolvers(resolversDefinition);
        }
        if (typeof resolversDefinition === 'object' && resolversDefinition) {
            resolvers.push(resolversDefinition);
        }
    }
    const result = utils.mergeDeep(resolvers, true);
    if (options === null || options === void 0 ? void 0 : options.exclusions) {
        for (const exclusion of options.exclusions) {
            const [typeName, fieldName] = exclusion.split('.');
            if (!fieldName || fieldName === '*') {
                delete result[typeName];
            }
            else if (result[typeName]) {
                delete result[typeName][fieldName];
            }
        }
    }
    return result;
}

function mergeArguments(args1, args2, config) {
    const result = deduplicateArguments([...args2, ...args1].filter(utils.isSome));
    if (config && config.sort) {
        result.sort(utils.compareNodes);
    }
    return result;
}
function deduplicateArguments(args) {
    return args.reduce((acc, current) => {
        const dup = acc.find(arg => arg.name.value === current.name.value);
        if (!dup) {
            return acc.concat([current]);
        }
        return acc;
    }, []);
}

function directiveAlreadyExists(directivesArr, otherDirective) {
    return !!directivesArr.find(directive => directive.name.value === otherDirective.name.value);
}
function nameAlreadyExists(name, namesArr) {
    return namesArr.some(({ value }) => value === name.value);
}
function mergeArguments$1(a1, a2) {
    const result = [...a2];
    for (const argument of a1) {
        const existingIndex = result.findIndex(a => a.name.value === argument.name.value);
        if (existingIndex > -1) {
            const existingArg = result[existingIndex];
            if (existingArg.value.kind === 'ListValue') {
                const source = existingArg.value.values;
                const target = argument.value.values;
                // merge values of two lists
                existingArg.value.values = deduplicateLists(source, target, (targetVal, source) => {
                    const value = targetVal.value;
                    return !value || !source.some((sourceVal) => sourceVal.value === value);
                });
            }
            else {
                existingArg.value = argument.value;
            }
        }
        else {
            result.push(argument);
        }
    }
    return result;
}
function deduplicateDirectives(directives) {
    return directives
        .map((directive, i, all) => {
        const firstAt = all.findIndex(d => d.name.value === directive.name.value);
        if (firstAt !== i) {
            const dup = all[firstAt];
            directive.arguments = mergeArguments$1(directive.arguments, dup.arguments);
            return null;
        }
        return directive;
    })
        .filter(utils.isSome);
}
function mergeDirectives(d1 = [], d2 = [], config) {
    const reverseOrder = config && config.reverseDirectives;
    const asNext = reverseOrder ? d1 : d2;
    const asFirst = reverseOrder ? d2 : d1;
    const result = deduplicateDirectives([...asNext]);
    for (const directive of asFirst) {
        if (directiveAlreadyExists(result, directive)) {
            const existingDirectiveIndex = result.findIndex(d => d.name.value === directive.name.value);
            const existingDirective = result[existingDirectiveIndex];
            result[existingDirectiveIndex].arguments = mergeArguments$1(directive.arguments || [], existingDirective.arguments || []);
        }
        else {
            result.push(directive);
        }
    }
    return result;
}
function validateInputs(node, existingNode) {
    const printedNode = graphql.print({
        ...node,
        description: undefined,
    });
    const printedExistingNode = graphql.print({
        ...existingNode,
        description: undefined,
    });
    // eslint-disable-next-line
    const leaveInputs = new RegExp('(directive @w*d*)|( on .*$)', 'g');
    const sameArguments = printedNode.replace(leaveInputs, '') === printedExistingNode.replace(leaveInputs, '');
    if (!sameArguments) {
        throw new Error(`Unable to merge GraphQL directive "${node.name.value}". \nExisting directive:  \n\t${printedExistingNode} \nReceived directive: \n\t${printedNode}`);
    }
}
function mergeDirective(node, existingNode) {
    if (existingNode) {
        validateInputs(node, existingNode);
        return {
            ...node,
            locations: [
                ...existingNode.locations,
                ...node.locations.filter(name => !nameAlreadyExists(name, existingNode.locations)),
            ],
        };
    }
    return node;
}
function deduplicateLists(source, target, filterFn) {
    return source.concat(target.filter(val => filterFn(val, source)));
}

function mergeEnumValues(first, second, config) {
    if (config === null || config === void 0 ? void 0 : config.consistentEnumMerge) {
        const reversed = [];
        if (first) {
            reversed.push(...first);
        }
        first = second;
        second = reversed;
    }
    const enumValueMap = new Map();
    if (first) {
        for (const firstValue of first) {
            enumValueMap.set(firstValue.name.value, firstValue);
        }
    }
    if (second) {
        for (const secondValue of second) {
            const enumValue = secondValue.name.value;
            if (enumValueMap.has(enumValue)) {
                const firstValue = enumValueMap.get(enumValue);
                firstValue.description = secondValue.description || firstValue.description;
                firstValue.directives = mergeDirectives(secondValue.directives, firstValue.directives);
            }
            else {
                enumValueMap.set(enumValue, secondValue);
            }
        }
    }
    const result = [...enumValueMap.values()];
    if (config && config.sort) {
        result.sort(utils.compareNodes);
    }
    return result;
}

function mergeEnum(e1, e2, config) {
    if (e2) {
        return {
            name: e1.name,
            description: e1['description'] || e2['description'],
            kind: (config === null || config === void 0 ? void 0 : config.convertExtensions) || e1.kind === 'EnumTypeDefinition' || e2.kind === 'EnumTypeDefinition'
                ? 'EnumTypeDefinition'
                : 'EnumTypeExtension',
            loc: e1.loc,
            directives: mergeDirectives(e1.directives, e2.directives, config),
            values: mergeEnumValues(e1.values, e2.values, config),
        };
    }
    return (config === null || config === void 0 ? void 0 : config.convertExtensions)
        ? {
            ...e1,
            kind: graphql.Kind.ENUM_TYPE_DEFINITION,
        }
        : e1;
}

function isStringTypes(types) {
    return typeof types === 'string';
}
function isSourceTypes(types) {
    return types instanceof graphql.Source;
}
function extractType(type) {
    let visitedType = type;
    while (visitedType.kind === graphql.Kind.LIST_TYPE || visitedType.kind === 'NonNullType') {
        visitedType = visitedType.type;
    }
    return visitedType;
}
function isWrappingTypeNode(type) {
    return type.kind !== graphql.Kind.NAMED_TYPE;
}
function isListTypeNode(type) {
    return type.kind === graphql.Kind.LIST_TYPE;
}
function isNonNullTypeNode(type) {
    return type.kind === graphql.Kind.NON_NULL_TYPE;
}
function printTypeNode(type) {
    if (isListTypeNode(type)) {
        return `[${printTypeNode(type.type)}]`;
    }
    if (isNonNullTypeNode(type)) {
        return `${printTypeNode(type.type)}!`;
    }
    return type.name.value;
}
(function (CompareVal) {
    CompareVal[CompareVal["A_SMALLER_THAN_B"] = -1] = "A_SMALLER_THAN_B";
    CompareVal[CompareVal["A_EQUALS_B"] = 0] = "A_EQUALS_B";
    CompareVal[CompareVal["A_GREATER_THAN_B"] = 1] = "A_GREATER_THAN_B";
})(exports.CompareVal || (exports.CompareVal = {}));
function defaultStringComparator(a, b) {
    if (a == null && b == null) {
        return exports.CompareVal.A_EQUALS_B;
    }
    if (a == null) {
        return exports.CompareVal.A_SMALLER_THAN_B;
    }
    if (b == null) {
        return exports.CompareVal.A_GREATER_THAN_B;
    }
    if (a < b)
        return exports.CompareVal.A_SMALLER_THAN_B;
    if (a > b)
        return exports.CompareVal.A_GREATER_THAN_B;
    return exports.CompareVal.A_EQUALS_B;
}

function fieldAlreadyExists(fieldsArr, otherField, config) {
    const result = fieldsArr.find(field => field.name.value === otherField.name.value);
    if (result && !(config === null || config === void 0 ? void 0 : config.ignoreFieldConflicts)) {
        const t1 = extractType(result.type);
        const t2 = extractType(otherField.type);
        if (t1.name.value !== t2.name.value) {
            throw new Error(`Field "${otherField.name.value}" already defined with a different type. Declared as "${t1.name.value}", but you tried to override with "${t2.name.value}"`);
        }
    }
    return !!result;
}
function mergeFields(type, f1, f2, config) {
    const result = [];
    if (f2 != null) {
        result.push(...f2);
    }
    if (f1 != null) {
        for (const field of f1) {
            if (fieldAlreadyExists(result, field, config)) {
                const existing = result.find((f) => f.name.value === field.name.value);
                if (!(config === null || config === void 0 ? void 0 : config.ignoreFieldConflicts)) {
                    if (config === null || config === void 0 ? void 0 : config.throwOnConflict) {
                        preventConflicts(type, existing, field, false);
                    }
                    else {
                        preventConflicts(type, existing, field, true);
                    }
                    if (isNonNullTypeNode(field.type) && !isNonNullTypeNode(existing.type)) {
                        existing.type = field.type;
                    }
                }
                existing.arguments = mergeArguments(field['arguments'] || [], existing.arguments || [], config);
                existing.directives = mergeDirectives(field.directives, existing.directives, config);
                existing.description = field.description || existing.description;
            }
            else {
                result.push(field);
            }
        }
    }
    if (config && config.sort) {
        result.sort(utils.compareNodes);
    }
    if (config && config.exclusions) {
        const exclusions = config.exclusions;
        return result.filter(field => !exclusions.includes(`${type.name.value}.${field.name.value}`));
    }
    return result;
}
function preventConflicts(type, a, b, ignoreNullability = false) {
    const aType = printTypeNode(a.type);
    const bType = printTypeNode(b.type);
    if (aType !== bType && !safeChangeForFieldType(a.type, b.type, ignoreNullability)) {
        throw new Error(`Field '${type.name.value}.${a.name.value}' changed type from '${aType}' to '${bType}'`);
    }
}
function safeChangeForFieldType(oldType, newType, ignoreNullability = false) {
    // both are named
    if (!isWrappingTypeNode(oldType) && !isWrappingTypeNode(newType)) {
        return oldType.toString() === newType.toString();
    }
    // new is non-null
    if (isNonNullTypeNode(newType)) {
        const ofType = isNonNullTypeNode(oldType) ? oldType.type : oldType;
        return safeChangeForFieldType(ofType, newType.type);
    }
    // old is non-null
    if (isNonNullTypeNode(oldType)) {
        return safeChangeForFieldType(newType, oldType, ignoreNullability);
    }
    // old is list
    if (isListTypeNode(oldType)) {
        return ((isListTypeNode(newType) && safeChangeForFieldType(oldType.type, newType.type)) ||
            (isNonNullTypeNode(newType) && safeChangeForFieldType(oldType, newType['type'])));
    }
    return false;
}

function mergeInputType(node, existingNode, config) {
    if (existingNode) {
        try {
            return {
                name: node.name,
                description: node['description'] || existingNode['description'],
                kind: (config === null || config === void 0 ? void 0 : config.convertExtensions) ||
                    node.kind === 'InputObjectTypeDefinition' ||
                    existingNode.kind === 'InputObjectTypeDefinition'
                    ? 'InputObjectTypeDefinition'
                    : 'InputObjectTypeExtension',
                loc: node.loc,
                fields: mergeFields(node, node.fields, existingNode.fields, config),
                directives: mergeDirectives(node.directives, existingNode.directives, config),
            };
        }
        catch (e) {
            throw new Error(`Unable to merge GraphQL input type "${node.name.value}": ${e.message}`);
        }
    }
    return (config === null || config === void 0 ? void 0 : config.convertExtensions)
        ? {
            ...node,
            kind: graphql.Kind.INPUT_OBJECT_TYPE_DEFINITION,
        }
        : node;
}

function mergeInterface(node, existingNode, config) {
    if (existingNode) {
        try {
            return {
                name: node.name,
                description: node['description'] || existingNode['description'],
                kind: (config === null || config === void 0 ? void 0 : config.convertExtensions) ||
                    node.kind === 'InterfaceTypeDefinition' ||
                    existingNode.kind === 'InterfaceTypeDefinition'
                    ? 'InterfaceTypeDefinition'
                    : 'InterfaceTypeExtension',
                loc: node.loc,
                fields: mergeFields(node, node.fields, existingNode.fields, config),
                directives: mergeDirectives(node.directives, existingNode.directives, config),
                interfaces: node['interfaces']
                    ? mergeNamedTypeArray(node['interfaces'], existingNode['interfaces'], config)
                    : undefined,
            };
        }
        catch (e) {
            throw new Error(`Unable to merge GraphQL interface "${node.name.value}": ${e.message}`);
        }
    }
    return (config === null || config === void 0 ? void 0 : config.convertExtensions)
        ? {
            ...node,
            kind: graphql.Kind.INTERFACE_TYPE_DEFINITION,
        }
        : node;
}

function alreadyExists(arr, other) {
    return !!arr.find(i => i.name.value === other.name.value);
}
function mergeNamedTypeArray(first = [], second = [], config = {}) {
    const result = [...second, ...first.filter(d => !alreadyExists(second, d))];
    if (config && config.sort) {
        result.sort(utils.compareNodes);
    }
    return result;
}

function mergeType(node, existingNode, config) {
    if (existingNode) {
        try {
            return {
                name: node.name,
                description: node['description'] || existingNode['description'],
                kind: (config === null || config === void 0 ? void 0 : config.convertExtensions) ||
                    node.kind === 'ObjectTypeDefinition' ||
                    existingNode.kind === 'ObjectTypeDefinition'
                    ? 'ObjectTypeDefinition'
                    : 'ObjectTypeExtension',
                loc: node.loc,
                fields: mergeFields(node, node.fields, existingNode.fields, config),
                directives: mergeDirectives(node.directives, existingNode.directives, config),
                interfaces: mergeNamedTypeArray(node.interfaces, existingNode.interfaces, config),
            };
        }
        catch (e) {
            throw new Error(`Unable to merge GraphQL type "${node.name.value}": ${e.message}`);
        }
    }
    return (config === null || config === void 0 ? void 0 : config.convertExtensions)
        ? {
            ...node,
            kind: graphql.Kind.OBJECT_TYPE_DEFINITION,
        }
        : node;
}

function mergeScalar(node, existingNode, config) {
    if (existingNode) {
        return {
            name: node.name,
            description: node['description'] || existingNode['description'],
            kind: (config === null || config === void 0 ? void 0 : config.convertExtensions) ||
                node.kind === 'ScalarTypeDefinition' ||
                existingNode.kind === 'ScalarTypeDefinition'
                ? 'ScalarTypeDefinition'
                : 'ScalarTypeExtension',
            loc: node.loc,
            directives: mergeDirectives(node.directives, existingNode.directives, config),
        };
    }
    return (config === null || config === void 0 ? void 0 : config.convertExtensions)
        ? {
            ...node,
            kind: graphql.Kind.SCALAR_TYPE_DEFINITION,
        }
        : node;
}

function mergeUnion(first, second, config) {
    if (second) {
        return {
            name: first.name,
            description: first['description'] || second['description'],
            // ConstXNode has been introduced in v16 but it is not compatible with XNode so we do `as any` for backwards compatibility
            directives: mergeDirectives(first.directives, second.directives, config),
            kind: (config === null || config === void 0 ? void 0 : config.convertExtensions) || first.kind === 'UnionTypeDefinition' || second.kind === 'UnionTypeDefinition'
                ? graphql.Kind.UNION_TYPE_DEFINITION
                : graphql.Kind.UNION_TYPE_EXTENSION,
            loc: first.loc,
            types: mergeNamedTypeArray(first.types, second.types, config),
        };
    }
    return (config === null || config === void 0 ? void 0 : config.convertExtensions)
        ? {
            ...first,
            kind: graphql.Kind.UNION_TYPE_DEFINITION,
        }
        : first;
}

const DEFAULT_OPERATION_TYPE_NAME_MAP = {
    query: 'Query',
    mutation: 'Mutation',
    subscription: 'Subscription',
};
function mergeOperationTypes(opNodeList = [], existingOpNodeList = []) {
    const finalOpNodeList = [];
    for (const opNodeType in DEFAULT_OPERATION_TYPE_NAME_MAP) {
        const opNode = opNodeList.find(n => n.operation === opNodeType) || existingOpNodeList.find(n => n.operation === opNodeType);
        if (opNode) {
            finalOpNodeList.push(opNode);
        }
    }
    return finalOpNodeList;
}
function mergeSchemaDefs(node, existingNode, config) {
    if (existingNode) {
        return {
            kind: node.kind === graphql.Kind.SCHEMA_DEFINITION || existingNode.kind === graphql.Kind.SCHEMA_DEFINITION
                ? graphql.Kind.SCHEMA_DEFINITION
                : graphql.Kind.SCHEMA_EXTENSION,
            description: node['description'] || existingNode['description'],
            directives: mergeDirectives(node.directives, existingNode.directives, config),
            operationTypes: mergeOperationTypes(node.operationTypes, existingNode.operationTypes),
        };
    }
    return ((config === null || config === void 0 ? void 0 : config.convertExtensions)
        ? {
            ...node,
            kind: graphql.Kind.SCHEMA_DEFINITION,
        }
        : node);
}

const schemaDefSymbol = 'SCHEMA_DEF_SYMBOL';
function isNamedDefinitionNode(definitionNode) {
    return 'name' in definitionNode;
}
function mergeGraphQLNodes(nodes, config) {
    var _a, _b, _c;
    const mergedResultMap = {};
    for (const nodeDefinition of nodes) {
        if (isNamedDefinitionNode(nodeDefinition)) {
            const name = (_a = nodeDefinition.name) === null || _a === void 0 ? void 0 : _a.value;
            if (config === null || config === void 0 ? void 0 : config.commentDescriptions) {
                utils.collectComment(nodeDefinition);
            }
            if (name == null) {
                continue;
            }
            if (((_b = config === null || config === void 0 ? void 0 : config.exclusions) === null || _b === void 0 ? void 0 : _b.includes(name + '.*')) || ((_c = config === null || config === void 0 ? void 0 : config.exclusions) === null || _c === void 0 ? void 0 : _c.includes(name))) {
                delete mergedResultMap[name];
            }
            else {
                switch (nodeDefinition.kind) {
                    case graphql.Kind.OBJECT_TYPE_DEFINITION:
                    case graphql.Kind.OBJECT_TYPE_EXTENSION:
                        mergedResultMap[name] = mergeType(nodeDefinition, mergedResultMap[name], config);
                        break;
                    case graphql.Kind.ENUM_TYPE_DEFINITION:
                    case graphql.Kind.ENUM_TYPE_EXTENSION:
                        mergedResultMap[name] = mergeEnum(nodeDefinition, mergedResultMap[name], config);
                        break;
                    case graphql.Kind.UNION_TYPE_DEFINITION:
                    case graphql.Kind.UNION_TYPE_EXTENSION:
                        mergedResultMap[name] = mergeUnion(nodeDefinition, mergedResultMap[name], config);
                        break;
                    case graphql.Kind.SCALAR_TYPE_DEFINITION:
                    case graphql.Kind.SCALAR_TYPE_EXTENSION:
                        mergedResultMap[name] = mergeScalar(nodeDefinition, mergedResultMap[name], config);
                        break;
                    case graphql.Kind.INPUT_OBJECT_TYPE_DEFINITION:
                    case graphql.Kind.INPUT_OBJECT_TYPE_EXTENSION:
                        mergedResultMap[name] = mergeInputType(nodeDefinition, mergedResultMap[name], config);
                        break;
                    case graphql.Kind.INTERFACE_TYPE_DEFINITION:
                    case graphql.Kind.INTERFACE_TYPE_EXTENSION:
                        mergedResultMap[name] = mergeInterface(nodeDefinition, mergedResultMap[name], config);
                        break;
                    case graphql.Kind.DIRECTIVE_DEFINITION:
                        mergedResultMap[name] = mergeDirective(nodeDefinition, mergedResultMap[name]);
                        break;
                }
            }
        }
        else if (nodeDefinition.kind === graphql.Kind.SCHEMA_DEFINITION || nodeDefinition.kind === graphql.Kind.SCHEMA_EXTENSION) {
            mergedResultMap[schemaDefSymbol] = mergeSchemaDefs(nodeDefinition, mergedResultMap[schemaDefSymbol], config);
        }
    }
    return mergedResultMap;
}

function mergeTypeDefs(typeSource, config) {
    utils.resetComments();
    const doc = {
        kind: graphql.Kind.DOCUMENT,
        definitions: mergeGraphQLTypes(typeSource, {
            useSchemaDefinition: true,
            forceSchemaDefinition: false,
            throwOnConflict: false,
            commentDescriptions: false,
            ...config,
        }),
    };
    let result;
    if (config === null || config === void 0 ? void 0 : config.commentDescriptions) {
        result = utils.printWithComments(doc);
    }
    else {
        result = doc;
    }
    utils.resetComments();
    return result;
}
function visitTypeSources(typeSource, options, allNodes = [], visitedTypeSources = new Set()) {
    if (typeSource && !visitedTypeSources.has(typeSource)) {
        visitedTypeSources.add(typeSource);
        if (typeof typeSource === 'function') {
            visitTypeSources(typeSource(), options, allNodes, visitedTypeSources);
        }
        else if (Array.isArray(typeSource)) {
            for (const type of typeSource) {
                visitTypeSources(type, options, allNodes, visitedTypeSources);
            }
        }
        else if (graphql.isSchema(typeSource)) {
            const documentNode = utils.getDocumentNodeFromSchema(typeSource, options);
            visitTypeSources(documentNode.definitions, options, allNodes, visitedTypeSources);
        }
        else if (isStringTypes(typeSource) || isSourceTypes(typeSource)) {
            const documentNode = graphql.parse(typeSource, options);
            visitTypeSources(documentNode.definitions, options, allNodes, visitedTypeSources);
        }
        else if (typeof typeSource === 'object' && graphql.isDefinitionNode(typeSource)) {
            allNodes.push(typeSource);
        }
        else if (utils.isDocumentNode(typeSource)) {
            visitTypeSources(typeSource.definitions, options, allNodes, visitedTypeSources);
        }
        else {
            throw new Error(`typeDefs must contain only strings, documents, schemas, or functions, got ${typeof typeSource}`);
        }
    }
    return allNodes;
}
function mergeGraphQLTypes(typeSource, config) {
    var _a, _b, _c;
    utils.resetComments();
    const allNodes = visitTypeSources(typeSource, config);
    const mergedNodes = mergeGraphQLNodes(allNodes, config);
    if (config === null || config === void 0 ? void 0 : config.useSchemaDefinition) {
        // XXX: right now we don't handle multiple schema definitions
        const schemaDef = mergedNodes[schemaDefSymbol] || {
            kind: graphql.Kind.SCHEMA_DEFINITION,
            operationTypes: [],
        };
        const operationTypes = schemaDef.operationTypes;
        for (const opTypeDefNodeType in DEFAULT_OPERATION_TYPE_NAME_MAP) {
            const opTypeDefNode = operationTypes.find(operationType => operationType.operation === opTypeDefNodeType);
            if (!opTypeDefNode) {
                const possibleRootTypeName = DEFAULT_OPERATION_TYPE_NAME_MAP[opTypeDefNodeType];
                const existingPossibleRootType = mergedNodes[possibleRootTypeName];
                if (existingPossibleRootType != null && existingPossibleRootType.name != null) {
                    operationTypes.push({
                        kind: graphql.Kind.OPERATION_TYPE_DEFINITION,
                        type: {
                            kind: graphql.Kind.NAMED_TYPE,
                            name: existingPossibleRootType.name,
                        },
                        operation: opTypeDefNodeType,
                    });
                }
            }
        }
        if (((_a = schemaDef === null || schemaDef === void 0 ? void 0 : schemaDef.operationTypes) === null || _a === void 0 ? void 0 : _a.length) != null && schemaDef.operationTypes.length > 0) {
            mergedNodes[schemaDefSymbol] = schemaDef;
        }
    }
    if ((config === null || config === void 0 ? void 0 : config.forceSchemaDefinition) && !((_c = (_b = mergedNodes[schemaDefSymbol]) === null || _b === void 0 ? void 0 : _b.operationTypes) === null || _c === void 0 ? void 0 : _c.length)) {
        mergedNodes[schemaDefSymbol] = {
            kind: graphql.Kind.SCHEMA_DEFINITION,
            operationTypes: [
                {
                    kind: graphql.Kind.OPERATION_TYPE_DEFINITION,
                    operation: 'query',
                    type: {
                        kind: graphql.Kind.NAMED_TYPE,
                        name: {
                            kind: graphql.Kind.NAME,
                            value: 'Query',
                        },
                    },
                },
            ],
        };
    }
    const mergedNodeDefinitions = Object.values(mergedNodes);
    if (config === null || config === void 0 ? void 0 : config.sort) {
        const sortFn = typeof config.sort === 'function' ? config.sort : defaultStringComparator;
        mergedNodeDefinitions.sort((a, b) => { var _a, _b; return sortFn((_a = a.name) === null || _a === void 0 ? void 0 : _a.value, (_b = b.name) === null || _b === void 0 ? void 0 : _b.value); });
    }
    return mergedNodeDefinitions;
}

function travelSchemaPossibleExtensions(schema, hooks) {
    hooks.onSchema(schema);
    const typesMap = schema.getTypeMap();
    for (const [, type] of Object.entries(typesMap)) {
        const isPredefinedScalar = graphql.isScalarType(type) && graphql.isSpecifiedScalarType(type);
        const isIntrospection = graphql.isIntrospectionType(type);
        if (isPredefinedScalar || isIntrospection) {
            continue;
        }
        if (graphql.isObjectType(type)) {
            hooks.onObjectType(type);
            const fields = type.getFields();
            for (const [, field] of Object.entries(fields)) {
                hooks.onObjectField(type, field);
                const args = field.args || [];
                for (const arg of args) {
                    hooks.onObjectFieldArg(type, field, arg);
                }
            }
        }
        else if (graphql.isInterfaceType(type)) {
            hooks.onInterface(type);
            const fields = type.getFields();
            for (const [, field] of Object.entries(fields)) {
                hooks.onInterfaceField(type, field);
                const args = field.args || [];
                for (const arg of args) {
                    hooks.onInterfaceFieldArg(type, field, arg);
                }
            }
        }
        else if (graphql.isInputObjectType(type)) {
            hooks.onInputType(type);
            const fields = type.getFields();
            for (const [, field] of Object.entries(fields)) {
                hooks.onInputFieldType(type, field);
            }
        }
        else if (graphql.isUnionType(type)) {
            hooks.onUnion(type);
        }
        else if (graphql.isScalarType(type)) {
            hooks.onScalar(type);
        }
        else if (graphql.isEnumType(type)) {
            hooks.onEnum(type);
            for (const value of type.getValues()) {
                hooks.onEnumValue(type, value);
            }
        }
    }
}
function mergeExtensions(extensions) {
    return utils.mergeDeep(extensions);
}
function applyExtensionObject(obj, extensions) {
    if (!obj) {
        return;
    }
    obj.extensions = utils.mergeDeep([obj.extensions || {}, extensions || {}]);
}
function applyExtensions(schema, extensions) {
    applyExtensionObject(schema, extensions.schemaExtensions);
    for (const [typeName, data] of Object.entries(extensions.types || {})) {
        const type = schema.getType(typeName);
        if (type) {
            applyExtensionObject(type, data.extensions);
            if (data.type === 'object' || data.type === 'interface') {
                for (const [fieldName, fieldData] of Object.entries(data.fields)) {
                    const field = type.getFields()[fieldName];
                    if (field) {
                        applyExtensionObject(field, fieldData.extensions);
                        for (const [arg, argData] of Object.entries(fieldData.arguments)) {
                            applyExtensionObject(field.args.find(a => a.name === arg), argData);
                        }
                    }
                }
            }
            else if (data.type === 'input') {
                for (const [fieldName, fieldData] of Object.entries(data.fields)) {
                    const field = type.getFields()[fieldName];
                    applyExtensionObject(field, fieldData.extensions);
                }
            }
            else if (data.type === 'enum') {
                for (const [valueName, valueData] of Object.entries(data.values)) {
                    const value = type.getValue(valueName);
                    applyExtensionObject(value, valueData);
                }
            }
        }
    }
    return schema;
}
function extractExtensionsFromSchema(schema) {
    const result = {
        schemaExtensions: {},
        types: {},
    };
    travelSchemaPossibleExtensions(schema, {
        onSchema: schema => (result.schemaExtensions = schema.extensions || {}),
        onObjectType: type => (result.types[type.name] = { fields: {}, type: 'object', extensions: type.extensions || {} }),
        onObjectField: (type, field) => (result.types[type.name].fields[field.name] = {
            arguments: {},
            extensions: field.extensions || {},
        }),
        onObjectFieldArg: (type, field, arg) => (result.types[type.name].fields[field.name].arguments[arg.name] = arg.extensions || {}),
        onInterface: type => (result.types[type.name] = { fields: {}, type: 'interface', extensions: type.extensions || {} }),
        onInterfaceField: (type, field) => (result.types[type.name].fields[field.name] = {
            arguments: {},
            extensions: field.extensions || {},
        }),
        onInterfaceFieldArg: (type, field, arg) => (result.types[type.name].fields[field.name].arguments[arg.name] =
            arg.extensions || {}),
        onEnum: type => (result.types[type.name] = { values: {}, type: 'enum', extensions: type.extensions || {} }),
        onEnumValue: (type, value) => (result.types[type.name].values[value.name] = value.extensions || {}),
        onScalar: type => (result.types[type.name] = { type: 'scalar', extensions: type.extensions || {} }),
        onUnion: type => (result.types[type.name] = { type: 'union', extensions: type.extensions || {} }),
        onInputType: type => (result.types[type.name] = { fields: {}, type: 'input', extensions: type.extensions || {} }),
        onInputFieldType: (type, field) => (result.types[type.name].fields[field.name] = { extensions: field.extensions || {} }),
    });
    return result;
}

exports.applyExtensions = applyExtensions;
exports.defaultStringComparator = defaultStringComparator;
exports.extractExtensionsFromSchema = extractExtensionsFromSchema;
exports.extractType = extractType;
exports.isListTypeNode = isListTypeNode;
exports.isNamedDefinitionNode = isNamedDefinitionNode;
exports.isNonNullTypeNode = isNonNullTypeNode;
exports.isSourceTypes = isSourceTypes;
exports.isStringTypes = isStringTypes;
exports.isWrappingTypeNode = isWrappingTypeNode;
exports.mergeArguments = mergeArguments;
exports.mergeDirective = mergeDirective;
exports.mergeDirectives = mergeDirectives;
exports.mergeEnum = mergeEnum;
exports.mergeEnumValues = mergeEnumValues;
exports.mergeExtensions = mergeExtensions;
exports.mergeFields = mergeFields;
exports.mergeGraphQLNodes = mergeGraphQLNodes;
exports.mergeGraphQLTypes = mergeGraphQLTypes;
exports.mergeInputType = mergeInputType;
exports.mergeInterface = mergeInterface;
exports.mergeNamedTypeArray = mergeNamedTypeArray;
exports.mergeResolvers = mergeResolvers;
exports.mergeScalar = mergeScalar;
exports.mergeType = mergeType;
exports.mergeTypeDefs = mergeTypeDefs;
exports.mergeUnion = mergeUnion;
exports.printTypeNode = printTypeNode;
exports.schemaDefSymbol = schemaDefSymbol;
exports.travelSchemaPossibleExtensions = travelSchemaPossibleExtensions;
