import type { InMemoryEntity } from "@mat3ra/code/dist/js/entity";
import type { AnyObject } from "@mat3ra/esse/dist/js/esse/types";
import type { MetaPropertyHolderSchema } from "@mat3ra/esse/dist/js/types";

import {
    type MetaPropertyHolderSchemaMixin,
    metaPropertyHolderSchemaMixin,
} from "../../generated/MetaPropertyHolderSchemaMixin";
import type MetaProperty from "../../MetaProperty";
import PropertyFactory from "../../PropertyFactory";

export interface MetaPropertySchemaJSON extends MetaPropertyHolderSchema, AnyObject {}

export type MetaPropertyHolderMixin = {
    property: MetaProperty;
} & MetaPropertyHolderSchemaMixin;

export type MetaPropertyInMemoryEntity = InMemoryEntity & MetaPropertyHolderMixin;

export function metaPropertyHolderMixin(item: InMemoryEntity) {
    // @ts-expect-error - this is a workaround to allow the metaPropertyMixin to be used with any type of entity
    const properties: InMemoryEntity & MetaPropertyHolderMixin = {
        get property() {
            return PropertyFactory.createMetaProperty(this.data);
        },
    };

    Object.defineProperties(item, Object.getOwnPropertyDescriptors(properties));

    metaPropertyHolderSchemaMixin(item);
}
