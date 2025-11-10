import type { InMemoryEntity } from "@mat3ra/code/dist/js/entity";
import type { FileContentPropertySchema } from "@mat3ra/esse/dist/js/types";

export type FileContentPropertySchemaMixin = Omit<
    FileContentPropertySchema,
    "_id" | "slug" | "systemName" | "schemaVersion"
>;

export type FileContentPropertyInMemoryEntity = InMemoryEntity & FileContentPropertySchemaMixin;

export function fileContentPropertySchemaMixin(item: InMemoryEntity) {
    // @ts-expect-error
    const properties: InMemoryEntity & FileContentPropertySchemaMixin = {
        get name() {
            return this.requiredProp<FileContentPropertySchema["name"]>("name");
        },
        get filetype() {
            return this.requiredProp<FileContentPropertySchema["filetype"]>("filetype");
        },
        get objectData() {
            return this.requiredProp<FileContentPropertySchema["objectData"]>("objectData");
        },
        get pathname() {
            return this.prop<FileContentPropertySchema["pathname"]>("pathname");
        },
        get basename() {
            return this.prop<FileContentPropertySchema["basename"]>("basename");
        },
    };

    Object.defineProperties(item, Object.getOwnPropertyDescriptors(properties));
}
