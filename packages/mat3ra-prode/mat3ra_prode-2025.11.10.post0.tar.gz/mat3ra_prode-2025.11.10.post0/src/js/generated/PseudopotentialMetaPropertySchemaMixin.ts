import type { InMemoryEntity } from "@mat3ra/code/dist/js/entity";
import type { FileDataItem } from "@mat3ra/esse/dist/js/types";

export type PseudopotentialMetaPropertySchemaMixin = Omit<
    FileDataItem,
    "_id" | "slug" | "systemName" | "schemaVersion"
>;

export type PseudopotentialMetaPropertyInMemoryEntity = InMemoryEntity &
    PseudopotentialMetaPropertySchemaMixin;

export function pseudopotentialMetaPropertySchemaMixin(item: InMemoryEntity) {
    // @ts-expect-error
    const properties: InMemoryEntity & PseudopotentialMetaPropertySchemaMixin = {
        get element() {
            return this.requiredProp<FileDataItem["element"]>("element");
        },
        get hash() {
            return this.requiredProp<FileDataItem["hash"]>("hash");
        },
        get type() {
            return this.requiredProp<FileDataItem["type"]>("type");
        },
        get source() {
            return this.requiredProp<FileDataItem["source"]>("source");
        },
        get version() {
            return this.prop<FileDataItem["version"]>("version");
        },
        get exchangeCorrelation() {
            return this.requiredProp<FileDataItem["exchangeCorrelation"]>("exchangeCorrelation");
        },
        get valenceConfiguration() {
            return this.prop<FileDataItem["valenceConfiguration"]>("valenceConfiguration");
        },
        get path() {
            return this.requiredProp<FileDataItem["path"]>("path");
        },
        get apps() {
            return this.requiredProp<FileDataItem["apps"]>("apps");
        },
        get filename() {
            return this.prop<FileDataItem["filename"]>("filename");
        },
        get name() {
            return this.requiredProp<FileDataItem["name"]>("name");
        },
        get cutoffs() {
            return this.prop<FileDataItem["cutoffs"]>("cutoffs");
        },
    };

    Object.defineProperties(item, Object.getOwnPropertyDescriptors(properties));
}
