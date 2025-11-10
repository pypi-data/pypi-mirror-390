export enum ExternalSource {
    materials_project = "MaterialsProject",
    icsd = "ICSD",
}

export enum PropertyType {
    // by data type
    scalar = "scalar",
    non_scalar = "non-scalar",
    // non-scalar subtypes
    tensor = "tensor",
    object = "object",
}

export enum PropertyName {
    pressure = "pressure",
    total_force = "total_force",
    total_energy = "total_energy",
    surface_energy = "surface_energy",
    convergence_electronic = "convergence_electronic",
    convergence_ionic = "convergence_ionic",
    fermi_energy = "fermi_energy",
    zero_point_energy = "zero_point_energy",
    total_energy_contributions = "total_energy_contributions",
    atomic_forces = "atomic_forces",
    atomic_constraints = "atomic_constraints",
    stress_tensor = "stress_tensor",
    density_of_states = "density_of_states",
    band_structure = "band_structure",
    band_gaps = "band_gaps",
    phonon_dispersions = "phonon_dispersions",
    phonon_dos = "phonon_dos",
    final_structure = "final_structure",
    is_relaxed = "is_relaxed",
    workflow_pyml_predict = "workflow:pyml_predict",
    file_content = "file_content",
    magnetic_moments = "magnetic_moments",
    reaction_energy_barrier = "reaction_energy_barrier",
    reaction_energy_profile = "reaction_energy_profile",
    potential_profile = "potential_profile",
    charge_density_profile = "charge_density_profile",
    jupyter_notebook_endpoint = "jupyter_notebook_endpoint",
    average_potential_profile = "average_potential_profile",
    valence_band_offset = "valence_band_offset",
    ionization_potential = "ionization_potential",
    pseudopotential = "pseudopotential",
    boundary_conditions = "boundary_conditions",
    dielectric_tensor = "dielectric_tensor",
    hubbard_u = "hubbard_u",
    hubbard_v_nn = "hubbard_v_nn",
    hubbard_v = "hubbard_v",
}
