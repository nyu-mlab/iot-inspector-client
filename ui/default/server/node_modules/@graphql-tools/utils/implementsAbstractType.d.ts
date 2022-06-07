import { GraphQLType, GraphQLSchema } from 'graphql';
import { Maybe } from './types';
export declare function implementsAbstractType(schema: GraphQLSchema, typeA: Maybe<GraphQLType>, typeB: Maybe<GraphQLType>): boolean;
