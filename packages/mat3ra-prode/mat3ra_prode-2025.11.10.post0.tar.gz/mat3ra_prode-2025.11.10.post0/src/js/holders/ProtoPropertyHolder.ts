import { InMemoryEntity } from "@mat3ra/code/dist/js/entity";
import type { Constructor } from "@mat3ra/code/dist/js/utils/types";
import type { ProtoPropertyHolderSchema } from "@mat3ra/esse/dist/js/types";

import type { ProtoPropertyHolderMixin } from "./mixins/ProtoPropertyHolderMixin";
import { protoPropertyHolderMixin } from "./mixins/ProtoPropertyHolderMixin";

type ProtoPropertyBase = typeof InMemoryEntity & Constructor<ProtoPropertyHolderMixin>;

export default class ProtoPropertyHolder extends (InMemoryEntity as ProtoPropertyBase) {
    // eslint-disable-next-line no-useless-constructor
    constructor(data: ProtoPropertyHolderSchema) {
        super(data);
    }
}

protoPropertyHolderMixin(ProtoPropertyHolder.prototype);
