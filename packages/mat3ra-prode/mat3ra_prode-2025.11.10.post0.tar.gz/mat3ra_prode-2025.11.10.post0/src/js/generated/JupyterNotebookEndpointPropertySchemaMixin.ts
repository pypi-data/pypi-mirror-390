import type { InMemoryEntity } from "@mat3ra/code/dist/js/entity";
import type { JupyterNotebookEndpointPropertySchema } from "@mat3ra/esse/dist/js/types";

export type JupyterNotebookEndpointPropertySchemaMixin = Omit<
    JupyterNotebookEndpointPropertySchema,
    "_id" | "slug" | "systemName" | "schemaVersion"
>;

export type JupyterNotebookEndpointPropertyInMemoryEntity = InMemoryEntity &
    JupyterNotebookEndpointPropertySchemaMixin;

export function jupyterNotebookEndpointPropertySchemaMixin(item: InMemoryEntity) {
    // @ts-expect-error
    const properties: InMemoryEntity & JupyterNotebookEndpointPropertySchemaMixin = {
        get name() {
            return this.requiredProp<JupyterNotebookEndpointPropertySchema["name"]>("name");
        },
        get host() {
            return this.requiredProp<JupyterNotebookEndpointPropertySchema["host"]>("host");
        },
        get port() {
            return this.requiredProp<JupyterNotebookEndpointPropertySchema["port"]>("port");
        },
        get token() {
            return this.requiredProp<JupyterNotebookEndpointPropertySchema["token"]>("token");
        },
    };

    Object.defineProperties(item, Object.getOwnPropertyDescriptors(properties));
}
