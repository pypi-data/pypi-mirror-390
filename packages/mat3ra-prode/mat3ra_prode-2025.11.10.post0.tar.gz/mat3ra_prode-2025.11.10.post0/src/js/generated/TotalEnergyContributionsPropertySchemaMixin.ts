import type { InMemoryEntity } from "@mat3ra/code/dist/js/entity";
import type { TotalEnergyContributionsPropertySchema } from "@mat3ra/esse/dist/js/types";

export type TotalEnergyContributionsPropertySchemaMixin = Omit<
    TotalEnergyContributionsPropertySchema,
    "_id" | "slug" | "systemName" | "schemaVersion"
>;

export type TotalEnergyContributionsPropertyInMemoryEntity = InMemoryEntity &
    TotalEnergyContributionsPropertySchemaMixin;

export function totalEnergyContributionsPropertySchemaMixin(item: InMemoryEntity) {
    // @ts-expect-error
    const properties: InMemoryEntity & TotalEnergyContributionsPropertySchemaMixin = {
        get temperatureEntropy() {
            return this.prop<TotalEnergyContributionsPropertySchema["temperatureEntropy"]>(
                "temperatureEntropy",
            );
        },
        get harris_foulkes() {
            return this.prop<TotalEnergyContributionsPropertySchema["harris_foulkes"]>(
                "harris_foulkes",
            );
        },
        get smearing() {
            return this.prop<TotalEnergyContributionsPropertySchema["smearing"]>("smearing");
        },
        get one_electron() {
            return this.prop<TotalEnergyContributionsPropertySchema["one_electron"]>(
                "one_electron",
            );
        },
        get hartree() {
            return this.prop<TotalEnergyContributionsPropertySchema["hartree"]>("hartree");
        },
        get exchange() {
            return this.prop<TotalEnergyContributionsPropertySchema["exchange"]>("exchange");
        },
        get exchange_correlation() {
            return this.prop<TotalEnergyContributionsPropertySchema["exchange_correlation"]>(
                "exchange_correlation",
            );
        },
        get ewald() {
            return this.prop<TotalEnergyContributionsPropertySchema["ewald"]>("ewald");
        },
        get alphaZ() {
            return this.prop<TotalEnergyContributionsPropertySchema["alphaZ"]>("alphaZ");
        },
        get atomicEnergy() {
            return this.prop<TotalEnergyContributionsPropertySchema["atomicEnergy"]>(
                "atomicEnergy",
            );
        },
        get eigenvalues() {
            return this.prop<TotalEnergyContributionsPropertySchema["eigenvalues"]>("eigenvalues");
        },
        get PAWDoubleCounting2() {
            return this.prop<TotalEnergyContributionsPropertySchema["PAWDoubleCounting2"]>(
                "PAWDoubleCounting2",
            );
        },
        get PAWDoubleCounting3() {
            return this.prop<TotalEnergyContributionsPropertySchema["PAWDoubleCounting3"]>(
                "PAWDoubleCounting3",
            );
        },
        get hartreeFock() {
            return this.prop<TotalEnergyContributionsPropertySchema["hartreeFock"]>("hartreeFock");
        },
        get name() {
            return this.requiredProp<TotalEnergyContributionsPropertySchema["name"]>("name");
        },
        get units() {
            return this.prop<TotalEnergyContributionsPropertySchema["units"]>("units");
        },
    };

    Object.defineProperties(item, Object.getOwnPropertyDescriptors(properties));
}
