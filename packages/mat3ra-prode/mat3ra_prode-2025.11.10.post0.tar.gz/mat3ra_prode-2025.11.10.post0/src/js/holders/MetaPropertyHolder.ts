import { InMemoryEntity } from "@mat3ra/code/dist/js/entity";
import type { Constructor } from "@mat3ra/code/dist/js/utils/types";
import type { MetaPropertyHolderSchema } from "@mat3ra/esse/dist/js/types";

import {
    type MetaPropertyHolderMixin,
    metaPropertyHolderMixin,
} from "./mixins/MetaPropertyHolderMixin";

type MetaPropertyBase = typeof InMemoryEntity & Constructor<MetaPropertyHolderMixin>;

export default class MetaPropertyHolder extends (InMemoryEntity as MetaPropertyBase) {
    // eslint-disable-next-line no-useless-constructor
    constructor(data: MetaPropertyHolderSchema) {
        super(data);
    }
}

metaPropertyHolderMixin(MetaPropertyHolder.prototype);
