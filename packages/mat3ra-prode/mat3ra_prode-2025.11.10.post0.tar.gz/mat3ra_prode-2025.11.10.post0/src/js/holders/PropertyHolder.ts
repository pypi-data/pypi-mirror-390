import { InMemoryEntity } from "@mat3ra/code/dist/js/entity";
import type { Constructor } from "@mat3ra/code/dist/js/utils/types";
import type { PropertyHolderSchema } from "@mat3ra/esse/dist/js/types";

import type { PropertyHolderMixin } from "./mixins/PropertyHolderMixin";
import { propertyHolderMixin } from "./mixins/PropertyHolderMixin";

type PropertyHolderBase = typeof InMemoryEntity & Constructor<PropertyHolderMixin>;

export default class PropertyHolder extends (InMemoryEntity as PropertyHolderBase) {
    // eslint-disable-next-line no-useless-constructor
    constructor(data: PropertyHolderSchema) {
        super(data);
    }
}

propertyHolderMixin(PropertyHolder.prototype);
