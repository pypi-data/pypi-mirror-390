import Property from "./Property";
import { PropertyType } from "./settings";

export default class ProtoProperty<TSchema extends object = object> extends Property<TSchema> {
    static readonly propertyType = PropertyType.non_scalar;
}
