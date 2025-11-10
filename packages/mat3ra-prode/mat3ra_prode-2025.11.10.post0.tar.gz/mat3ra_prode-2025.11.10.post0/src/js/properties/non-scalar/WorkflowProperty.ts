import type { Constructor } from "@mat3ra/code/dist/js/utils/types";
import type { WorkflowPropertySchema } from "@mat3ra/esse/dist/js/types";

import {
    WorkflowPropertySchemaMixin,
    workflowPropertySchemaMixin,
} from "../../generated/WorkflowPropertySchemaMixin";
import Property from "../../Property";
import { PropertyName, PropertyType } from "../../settings";

type Schema = WorkflowPropertySchema;

type Base = typeof Property<Schema> & Constructor<WorkflowPropertySchemaMixin>;

export default class WorkflowProperty extends (Property as Base) implements Schema {
    static readonly propertyName = PropertyName.workflow_pyml_predict;

    static readonly propertyType = PropertyType.non_scalar;

    constructor(config: Omit<Schema, "name">) {
        super({ ...config, name: WorkflowProperty.propertyName });
    }
}

workflowPropertySchemaMixin(WorkflowProperty.prototype);
