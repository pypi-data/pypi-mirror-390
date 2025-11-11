"""Some notes:
- Run MD in ase following this tutorial: https://wiki.fysik.dtu.dk/ase/tutorials/md/md.html
- For MD run, control symmetry to avoid error: `broken symmetry`.
- Must set txt='calc.txt' in GPAW calculator for backward files.
- Defines some print functions that can attach to ASE's dynamics object
- param_yaml must contain
    - a dict `ase_calc` define calculator.
    - a dict `md` with ASE MD parameters.
"""

import argparse
from pathlib import Path

import yaml
from ase import units
from ase.io import read, write  # Trajectory
from ase.md.langevin import Langevin
from ase.md.melchionna import MelchionnaNPT
from ase.md.nose_hoover_chain import NoseHooverChainNVT  # , IsotropicMTKNPT
from ase.md.velocitydistribution import MaxwellBoltzmannDistribution, Stationary
from ase.md.verlet import VelocityVerlet
from ase.parallel import paropen, parprint


#####ANCHOR Helper functions
def get_cli_args():
    """Get the arguments from the command line"""
    parser = argparse.ArgumentParser(description="Optimize structure using GPAW")
    parser.add_argument("param", type=str, help="The YAML file contains parameters")
    args = parser.parse_args()
    configfile = args.param
    pdict = yaml.safe_load(open(configfile, "r"))
    return pdict


pdict = get_cli_args()

#####ANCHOR Define calculator
ase_calc = pdict.get("calc_args", {}).get("ase", {})
if ase_calc.get("py_file", None):
    with open(ase_calc["py_file"], "r") as f:
        code_lines = f.read()
elif ase_calc.get("py_script", None):
    code_lines = "\n".join(ase_calc["py_script"])
else:
    raise ValueError("Must define in the key `calc_args.ase` either `py_file` or `py_script`")

### Dynamically execute custom lines
exec(code_lines)

#####ANCHOR Define atoms
### atoms: read EXTXYZ file
struct_args = pdict["structure"]
extxyz_file = struct_args["from_extxyz"]
atoms = read(extxyz_file, format="extxyz", index="-1")
input_pbc = struct_args.get("pbc", False)
if input_pbc:
    atoms.pbc = input_pbc

### set calculator
atoms.calc = calc  # noqa: F821


#####ANCHOR MD simulation
### MD parameters
md_args = {
    "ensemble": "NVE",
    "dt": 1,
    "temp": 300,
    "thermostat": "langevin",
    "barostat": "parrinello_rahman",
}
input_md_args = pdict.get("md", {})
md_args.update(input_md_args)

thermostat = md_args["thermostat"]
support_thermostats = ["langevin", "nose_hoover", "nose_hoover_chain"]
if thermostat not in support_thermostats:
    raise ValueError(f"Unsupported thermostat '{thermostat}'. Choices: {support_thermostats}")
barostat = md_args["barostat"]
support_barostats = ["parrinello_rahman", "iso_nose_hoover_chain", "aniso_nose_hoover_chain"]
if barostat not in support_barostats:
    raise ValueError(f"Unsupported barostat {barostat}. Choices: {support_barostats}")

dt = md_args["dt"] * units.fs
temp = md_args["temp"]
ensemble = md_args["ensemble"]

### Set the momenta corresponding to T=300K
MaxwellBoltzmannDistribution(atoms, temperature_K=temp, force_temp=True)
Stationary(atoms)  # Set zero total momentum to avoid drifting

### DYN object
if ensemble == "NVE":
    dyn = VelocityVerlet(atoms, timestep=dt)

elif ensemble == "NVT":
    if thermostat == "langevin":
        friction = md_args.get("langevin_friction", 0.002) / units.fs
        dyn = Langevin(atoms, timestep=dt, temperature_K=temp, friction=friction)
    elif thermostat == "nose_hoover":
        tdamp = md_args.get("tdamp", 100)  # damping time for Nose-Hoover thermostat
        dyn = MelchionnaNPT(
            atoms,
            timestep=dt,
            temperature_K=temp,
            ttime=tdamp * dt,
            pfactor=None,  # none for NVT
        )
    elif thermostat == "nose_hoover_chain":
        tdamp = thermostat.get("tdamp", 100)  # damping time for nose_hoover_chain
        dyn = NoseHooverChainNVT(
            atoms,
            timestep=dt,
            temperature_K=temp,
            tdamp=tdamp * dt,
            tchain=3,
        )

elif ensemble == "NPT":
    stress = md_args.get("press", None)  # external stress for NPT, in GPa
    if stress is not None:
        stress_in_eVA3 = stress / units.GPa  # to eV/Angstrom^3
    else:
        stress_in_eVA3 = None

    if barostat == "parrinello_rahman":
        tdamp = md_args.get("tdamp", 100)
        pfactor = md_args.get(
            "pfactor", 2e6
        )  # pressure scaling factor for parrinello_rahman barostat
        mask = md_args.get("mask", None)
        if mask is None:
            mask = atoms.pbc
        dyn = MelchionnaNPT(
            atoms,
            timestep=dt,
            temperature_K=temp,
            externalstress=stress_in_eVA3,  # stress in eV/Angstrom^3
            ttime=tdamp * dt,
            pfactor=pfactor,
            mask=mask,
        )
    elif barostat in ["iso_nose_hoover_chain", "aniso_nose_hoover_chain"]:
        from ase.md.nose_hoover_chain import MTKNPT, IsotropicMTKNPT

        tdamp = thermostat.get("tdamp", 100)
        pdamp = barostat.get("pdamp", 1000)
        if barostat == "iso_nose_hoover_chain":
            dyn = IsotropicMTKNPT(
                atoms,
                timestep=dt,
                temperature_K=temp,
                pressure_au=stress_in_eVA3,  # stress in eV/Angstrom^3
                tdamp=tdamp * dt,
                pdamp=pdamp * dt,
                tchain=3,
                pchain=3,
            )
        elif barostat == "aniso_nose_hoover_chain":
            mask = barostat.get("mask", None)
            if mask is None:
                mask = atoms.pbc
            if any(x == 0 for x in mask):
                raise NotImplementedError(
                    "'aniso_nose_hoover_chain' is not implemented yet. Consider using 'parrinello_rahman' instead."
                )

            dyn = MTKNPT(
                atoms,
                timestep=dt,
                temperature_K=temp,
                pressure_au=stress_in_eVA3,  # stress in eV/Angstrom^3
                tdamp=tdamp * dt,
                pdamp=pdamp * dt,
                tchain=3,
                pchain=3,
            )

    else:
        raise NotImplementedError("{barostat_name} is not supported")
else:
    raise ValueError(f"Unsupported ensemble {ensemble}. Choices: NVE, NVT, NPT")


### tailor properties
def print_dynamic(atoms=atoms, filename="calc_dyn_properties.txt"):
    """Function to print the potential, kinetic and total energy.
    Note: Stress printed in this file in GPa, but save in EXTXYZ in eV/Angstrom^3.
    """
    ### Extract properties
    step = dyn.nsteps
    epot = atoms.get_potential_energy() / len(atoms)
    ekin = atoms.get_kinetic_energy() / len(atoms)
    temp = atoms.get_temperature()
    stress = atoms.get_stress() / units.GPa  # 6_vector in Voigt notation
    cellpar = atoms.cell.cellpar()
    ### Write the header line
    if not Path(filename).exists():
        with paropen(filename, "w") as f:
            f.write("step temperature epot ekin pxx pyy pzz lx ly lz\n")
    ### Append the data to the file
    with paropen(filename, "a") as f:
        f.write(
            f"{step} {temp:.1f} {epot:.8f} {ekin:.8f} {stress[0]:.8f} {stress[1]:.8f} {stress[2]:.8f} {cellpar[0]:.7f} {cellpar[1]:.7f} {cellpar[2]:.7f}\n"
        )


### Traj in eXYZ format
def write_dyn_extxyz(atoms=atoms, filename="traj_md.extxyz"):
    # write("test_Cu.exyz", a, format="extxyz", append=True)
    _ = (
        atoms.get_potential_energy()
    )  # `force_consistent=True` cause error if combine multi-calculators
    _ = atoms.get_forces()
    _ = atoms.get_stress()
    atoms.info["pbc"] = atoms.get_pbc()
    write(filename, atoms, format="extxyz", append=True)


### Save ASE trajectory
# traj = Trajectory("CONF.asetraj", "w", atoms, properties=["energy", "forces", "stress"])
# dyn.attach(traj.write, interval=traj_freq)

parprint(f"INFO: Start MD with ensemble {ensemble}: {dyn.__class__.__name__}")
Path("calc_dyn_properties.txt").unlink(missing_ok=True)
Path("traj_md.extxyz").unlink(missing_ok=True)
### run MD
equil_steps = md_args.get("equil_steps", 0)
if equil_steps > 0:
    dyn.run(equil_steps)
    parprint(f"INFO: Finish {dyn.nsteps} steps of equilibration run.")

num_frames = md_args.get("num_frames", 1)
traj_freq = md_args.get("traj_freq", 1)
nsteps = num_frames * traj_freq

dyn.attach(print_dynamic, interval=traj_freq)
dyn.attach(write_dyn_extxyz, interval=traj_freq)

dyn.run(nsteps)

parprint(
    f"INFO: Finish {dyn.nsteps} steps of product run, to collect {num_frames} frames with {traj_freq} steps interval."
)
