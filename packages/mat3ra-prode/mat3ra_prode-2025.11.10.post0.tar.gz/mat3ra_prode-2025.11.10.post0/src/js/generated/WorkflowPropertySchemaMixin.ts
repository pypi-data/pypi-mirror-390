import type { InMemoryEntity } from "@mat3ra/code/dist/js/entity";
import type { WorkflowPropertySchema } from "@mat3ra/esse/dist/js/types";

export type WorkflowPropertySchemaMixin = Omit<
    WorkflowPropertySchema,
    "_id" | "slug" | "systemName" | "schemaVersion"
>;

export type WorkflowPropertyInMemoryEntity = InMemoryEntity & WorkflowPropertySchemaMixin;

export function workflowPropertySchemaMixin(item: InMemoryEntity) {
    // @ts-expect-error
    const properties: InMemoryEntity & WorkflowPropertySchemaMixin = {
        get name() {
            return this.requiredProp<WorkflowPropertySchema["name"]>("name");
        },
        get subworkflows() {
            return this.requiredProp<WorkflowPropertySchema["subworkflows"]>("subworkflows");
        },
        get units() {
            return this.requiredProp<WorkflowPropertySchema["units"]>("units");
        },
        get properties() {
            return this.prop<WorkflowPropertySchema["properties"]>("properties");
        },
        get isUsingDataset() {
            return this.prop<WorkflowPropertySchema["isUsingDataset"]>("isUsingDataset");
        },
        get workflows() {
            return this.prop<WorkflowPropertySchema["workflows"]>("workflows");
        },
        get isDefault() {
            return this.prop<WorkflowPropertySchema["isDefault"]>("isDefault");
        },
        get metadata() {
            return this.prop<WorkflowPropertySchema["metadata"]>("metadata");
        },
    };

    Object.defineProperties(item, Object.getOwnPropertyDescriptors(properties));
}
