import { NamedInMemoryEntity } from "@mat3ra/code/dist/js/entity";
import type { AnyObject } from "@mat3ra/esse/dist/js/esse/types";
import type { PropertyHolderSchema } from "@mat3ra/esse/dist/js/types";

import { type PropertyName, PropertyType } from "./settings";

export type PropertySchemaJSON = PropertyHolderSchema["data"] & AnyObject;

export type PropertyRowValue = PropertySchemaJSON & {
    slug?: string;
    group?: string;
};

export default class Property<TSchema extends object = object> extends NamedInMemoryEntity {
    declare toJSON: (exclude?: string[]) => TSchema & AnyObject;

    declare _json: TSchema & AnyObject;

    declare name: `${PropertyName}`;

    readonly prettyName = Property.prettifyName(this.name);

    static readonly propertyType: PropertyType;

    static readonly propertyName: PropertyName;

    static readonly isRefined: boolean = false;

    static readonly isConvergence: boolean = false;

    static readonly isAbleToReturnMultipleResults: boolean = false;

    toRowValues(
        group: string | undefined,
        slug: string | undefined,
    ): (TSchema & AnyObject & { slug?: string; group?: string })[] {
        return [
            {
                ...this.toJSON(),
                slug,
                group,
            },
        ];
    }

    static prettifyName(name: string) {
        return (name.charAt(0).toUpperCase() + name.slice(1)).replace("_", " ");
    }
}
