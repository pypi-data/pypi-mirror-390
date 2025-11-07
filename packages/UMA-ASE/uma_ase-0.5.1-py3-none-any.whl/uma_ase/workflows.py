from __future__ import annotations

from argparse import Namespace
from collections import Counter
from contextlib import contextmanager, suppress
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, Optional, Tuple
import logging
import sys
import shutil
import inspect
import io

from ase.io import read, write
from ase.optimize import BFGS, BFGSLineSearch, FIRE, LBFGS, MDMin
from ase.vibrations import Vibrations
from ase.thermochemistry import IdealGasThermo
from ase.visualize import view
from ase import Atoms

try:
    from fairchem.core import pretrained_mlip, FAIRChemCalculator
except ModuleNotFoundError as exc:  # pragma: no cover - environment dependent
    pretrained_mlip = None
    FAIRChemCalculator = None
    FAIR_CHEM_IMPORT_ERROR = exc
else:  # pragma: no cover - environment dependent
    FAIR_CHEM_IMPORT_ERROR = None

from .utils import (
    Sum_of_atomic_energies,
    extract_xyz_metadata,
    get_predict_unit_with_local_fallback,
    rmsd_simple,
)


@dataclass(frozen=True)
class WorkflowPaths:
    """Collection of standard output artifacts emitted by a run."""

    trajectory: Path
    log: Path
    final_geometry: Path


@dataclass
class AtomContext:
    """Container bundling an ASE atoms object with metadata for downstream steps."""

    atoms: Atoms
    counts: Counter
    device: str


def capture_stdout(func, *args, **kwargs):
    """Capture stdout emitted by *func* and replay it to the original stream."""
    buffer = io.StringIO()
    original_stdout = sys.stdout
    try:
        sig = inspect.signature(func)
        if "log" in sig.parameters and "log" not in kwargs:
            kwargs["log"] = buffer
            result = func(*args, **kwargs)
        else:
            sys.stdout = buffer
            result = func(*args, **kwargs)
    finally:
        sys.stdout = original_stdout
    output = buffer.getvalue()
    if output:
        original_stdout.write(output)
        original_stdout.flush()
    return result, output


class LoggerWriter:
    """Adapter that lets ASE optimizers log through a standard logger."""

    def __init__(self, logger: logging.Logger):
        self._logger = logger

    def write(self, message: str) -> None:
        message = message.strip()
        if message:
            self._logger.info(message)

    def flush(self) -> None:  # pragma: no cover - interface requirement
        pass

    def close(self) -> None:  # pragma: no cover - interface requirement
        pass


class TorchUnavailable(RuntimeError):
    """Lightweight exception indicating torch is not present."""


OPTIMIZER_CLASSES = {
    "BFGS": BFGS,
    "LBFGS": LBFGS,
    "BFGS_LINESEARCH": BFGSLineSearch,
    "FIRE": FIRE,
    "MDMIN": MDMin,
}

RUN_LABELS = {
    "sp": "SP",
    "geoopt": "OPT",
    "freqs": "FREQS",
}


def build_output_paths(
    input_path: Path,
    run_sequence: Optional[Iterable[str]] = None,
    explicit_geoopt: bool = True,
) -> WorkflowPaths:
    """Generate canonical output filenames derived from the input geometry."""
    parent = input_path.parent
    stem = input_path.stem
    sequence = list(run_sequence) if run_sequence else ["geoopt"]
    normalized = [
        item.lower() if isinstance(item, str) else str(item).lower()
        for item in sequence
    ]
    if set(normalized) == {"freqs"}:
        labels = ["FREQS"]
    else:
        labels = []
        for item in normalized:
            label = RUN_LABELS.get(item, item.upper())
            if label not in labels:
                labels.append(label)
    log_suffix = "-".join(labels)
    log_name = f"{stem}-{log_suffix}.log"
    return WorkflowPaths(
        trajectory=parent / f"{stem}-{log_suffix}.traj",
        log=parent / log_name,
        final_geometry=parent / f"{stem}-geoopt-{log_suffix}.xyz",
    )


def remove_if_exists(paths: Iterable[Path]) -> None:
    """Delete pre-existing files or directories produced by earlier runs."""
    for path in paths:
        if path.is_dir():
            shutil.rmtree(path, ignore_errors=True)
        elif path.exists():
            path.unlink()


def _cleanup_vibration_cache(cache_dir: Path, target_dir: Path, logger: logging.Logger) -> None:
    """Move trajectory files to target dir and remove cache artifacts."""
    if not cache_dir.exists():
        return

    moved = 0
    for traj_file in cache_dir.glob("*.traj"):
        destination = target_dir / traj_file.name
        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            traj_file.replace(destination)
            moved += 1
        except OSError as exc:
            logger.warning("Unable to move %s to %s: %s", traj_file, destination, exc)

    removed = 0
    for cache_file in cache_dir.glob("cache*.json"):
        try:
            cache_file.unlink()
            removed += 1
        except OSError as exc:
            logger.warning("Unable to delete %s: %s", cache_file, exc)

    try:
        shutil.rmtree(cache_dir)
    except OSError as exc:
        logger.warning("Unable to remove cache directory %s: %s", cache_dir, exc)

    if moved:
        logger.info("Moved %d normal modes traj files to %s", moved, target_dir)
    if removed:
        logger.info("Removed %d temporary cache files", removed)


@contextmanager
def configure_logging(log_path: Path):
    """Context manager that emits log messages to stdout and a logfile."""
    logger = logging.getLogger("uma_workflow")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    formatter = logging.Formatter("%(message)s")
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    file_handler = logging.FileHandler(log_path, mode="w")
    file_handler.setFormatter(formatter)

    # Clear any pre-existing handlers to avoid duplicate logs.
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        handler.close()

    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)

    try:
        yield logger
    finally:
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)


def select_device(force_cpu: bool = False) -> str:
    """Return the preferred execution device based on torch availability."""
    if force_cpu:
        return "cpu"
    try:
        import torch
    except ModuleNotFoundError as exc:  # pragma: no cover - environment dependent
        raise TorchUnavailable("PyTorch is required to determine execution device.") from exc
    try:
        return "cuda" if torch.cuda.is_available() else "cpu"
    except Exception as exc:
        raise TorchUnavailable("Failed to query torch CUDA availability.") from exc


def log_header(logger: logging.Logger) -> None:
    """Print a static banner summarising the workflow."""
    try:
        from . import __version__
    except Exception:  # pragma: no cover
        __version__ = "unknown"

    banner = [
        "*****************************************************************************",
        f"*                        U M A - A S E   v{__version__:>8}                          *",
        "*        Universal Model for Atoms - Atomistic Simulation Environment       *",
        "*****************************************************************************",
    ]
    for line in banner:
        logger.info(line)


def log_arguments(args: Namespace, logger: logging.Logger, device: str) -> None:
    """Echo the parsed CLI arguments to aid reproducibility."""
    logger.info("Parsed & Catch Arguments:")
    logger.info("  input      : %s", args.input)
    logger.info("  chg        : %s", args.chg)
    logger.info("  spin       : %s", args.spin)
    logger.info("  iter       : %s", getattr(args, "iter", "-"))
    logger.info("  grad       : %s", getattr(args, "grad", "-"))
    logger.info("  optimizer  : %s", getattr(args, "optimizer", "-"))
    logger.info("  run_type   : %s", args.run_type)
    logger.info("  checkpoint : %s", args.mlff_chk)
    logger.info("  task       : %s", args.mlff_task)
    logger.info("  visualize  : %s", args.visualize)
    logger.info("  cpu_only   : %s", getattr(args, "cpu", False))
    logger.info("  temperature: %.4f K", getattr(args, "temp", 0.0))
    logger.info("  pressure   : %.2f Pa", getattr(args, "press", 0.0))
    logger.info("  device     : %s", device)


def summarise_structure(
    args: Namespace,
    atoms: Atoms,
    logger: logging.Logger,
    *,
    comment: Optional[str] = None,
) -> Counter:
    """Log structural information about the current Atoms object."""
    counts = Counter(atoms.get_chemical_symbols())
    log_header(logger)
    logger.info("*          Initial Geometry %s loaded", args.input)
    logger.info("*          Number of atoms: %s", len(atoms))
    logger.info("*          Formula: %s", atoms.get_chemical_formula())
    logger.info("*          Element counts: %s", dict(counts))
    logger.info("*          Charge: %s", args.chg)
    logger.info("*          Spin Multiplicity: %s", args.spin)
    if comment:
        logger.info("*          XYZ comment: %s", comment)
    logger.info("*")
    return counts


def log_geometry(logger: logging.Logger, atoms: Atoms, title: str) -> None:
    """Log atomic coordinates of *atoms* with a descriptive *title*."""
    logger.info(title)
    symbols = atoms.get_chemical_symbols()
    positions = atoms.get_positions()
    for symbol, (x_coord, y_coord, z_coord) in zip(symbols, positions):
        logger.info("  %3s %12.6f %12.6f %12.6f", symbol, x_coord, y_coord, z_coord)
    logger.info("")


def _setup_calculated_atoms(
    args: Namespace,
    logger: logging.Logger,
) -> Tuple[int, Optional[AtomContext]]:
    """Create an ASE atoms object wired with the requested UMA calculator."""
    if FAIR_CHEM_IMPORT_ERROR is not None:
        logger.error("UMA FairChem libraries unavailable: %s", FAIR_CHEM_IMPORT_ERROR)
        return 1, None

    try:
        device = select_device(force_cpu=getattr(args, "cpu", False))
    except TorchUnavailable as exc:
        logger.error(str(exc))
        return 1, None

    if device == "cpu" and not getattr(args, "cpu", False):
        logger.info("CUDA device unavailable; running on CPU.")

    input_path = Path(args.input)
    metadata = extract_xyz_metadata(input_path)

    chg_explicit = bool(getattr(args, "_chg_explicit", False))
    if metadata.charge is not None and not chg_explicit:
        args.chg = metadata.charge
        logger.info("Charge inferred from XYZ metadata: %s", args.chg)
    elif metadata.charge is not None and chg_explicit and metadata.charge != args.chg:
        logger.debug(
            "XYZ metadata charge %s ignored because CLI provided charge %s.",
            metadata.charge,
            args.chg,
        )

    spin_explicit = bool(getattr(args, "_spin_explicit", False))
    if metadata.spin is not None and not spin_explicit:
        args.spin = metadata.spin
        logger.info("Spin multiplicity inferred from XYZ metadata: %s", args.spin)
    elif metadata.spin is not None and spin_explicit and metadata.spin != args.spin:
        logger.debug(
            "XYZ metadata spin %s ignored because CLI provided spin %s.",
            metadata.spin,
            args.spin,
        )

    log_arguments(args, logger, device)

    atoms = read(args.input)
    atoms.info["charge"] = args.chg
    atoms.info["spin"] = args.spin

    xyz_comment = metadata.comment
    if xyz_comment:
        atoms.info.setdefault("uma_comment", xyz_comment)
    if metadata.url:
        atoms.info.setdefault("uma_comment_url", metadata.url)

    counts = summarise_structure(args, atoms, logger, comment=xyz_comment)

    try:
        predictor = get_predict_unit_with_local_fallback(
            args.mlff_chk,
            device=device,
            logger=logger,
        )
    except FileNotFoundError as exc:
        logger.error(str(exc))
        return 1, None
    except KeyError:
        logger.error(
            "UMA checkpoint '%s' not found. Please provide a valid identifier.",
            args.mlff_chk,
        )
        return 1, None
    except Exception as exc:
        logger.error("Failed to load UMA checkpoint '%s': %s", args.mlff_chk, exc)
        return 1, None

    try:
        atoms.calc = FAIRChemCalculator(predictor, task_name=args.mlff_task)
    except Exception as exc:
        logger.error("Failed to initialise UMA calculator for task '%s': %s", args.mlff_task, exc)
        return 1, None

    logger.info("*          UMA Checkpoint: %s", args.mlff_chk)
    logger.info("*          UMA model: %s", args.mlff_task)
    logger.info("*")

    return 0, AtomContext(atoms=atoms, counts=counts, device=device)


def prepare_atoms_for_vibrations(
    args: Namespace,
    logger: logging.Logger,
) -> Tuple[int, Optional[AtomContext]]:
    """Set up atoms for vibrational analysis without running an optimisation."""
    status, context = _setup_calculated_atoms(args, logger)
    if status != 0 or context is None:
        return status, None
    return 0, context

def _resolve_optimizer(name: str):
    """Map a user-supplied optimiser name to an ASE optimiser class."""
    key = name.replace("-", "_").upper()
    return OPTIMIZER_CLASSES.get(key)


def run_geometry_optimization(
    args: Namespace,
    paths: WorkflowPaths,
    logger: logging.Logger,
) -> Tuple[int, Optional[AtomContext]]:
    """Execute a geometry optimisation and capture derived metrics."""
    status, context = _setup_calculated_atoms(args, logger)
    if status != 0 or context is None:
        return status, None

    optimizer_cls = _resolve_optimizer(args.optimizer)
    if optimizer_cls is None:
        logger.error(
            "Unknown optimizer '%s'. Available options: %s",
            args.optimizer,
            ", ".join(sorted(OPTIMIZER_CLASSES)),
        )
        return 1, None

    logger.info("*          Optimizer: %s", optimizer_cls.__name__)
    logger.info("*")

    optimizer = optimizer_cls(
        context.atoms,
        trajectory=str(paths.trajectory),
        logfile=LoggerWriter(logger),
    )

    start_time = datetime.now()
    logger.info("*****************************************************************************",)
    logger.info("*                         Geometry optimization                             *",)
    logger.info("*****************************************************************************",)
    logger.info("*")
    logger.info("%s Running GeoOpt using device %s", start_time, context.device)
    logger.info("*")
    logger.info("Target fmax %s eV/A. Max number of iterations %s", args.grad, args.iter)
    logger.info("*")

    log_geometry(logger, context.atoms, "Initial geometry for GeoOpt (Å):")

    try:
        run_result = optimizer.run(fmax=args.grad, steps=args.iter)
    except Exception as exc:
        logger.error("Optimizer failed: %s", exc)
        return 1, None

    finish_time = datetime.now()
    converged: Optional[bool] = None
    if run_result is not None:
        with suppress(Exception):
            converged = bool(run_result)

    if converged is None:
        converged_attr = getattr(optimizer, "converged", None)
        if callable(converged_attr):
            gradient = None
            optimizable = getattr(optimizer, "optimizable", None)
            if optimizable is not None and hasattr(optimizable, "get_gradient"):
                with suppress(Exception):
                    gradient = optimizable.get_gradient()
            if gradient is None:
                atoms_obj = getattr(optimizer, "atoms", None)
                if atoms_obj is not None and hasattr(atoms_obj, "get_forces"):
                    with suppress(Exception):
                        gradient = atoms_obj.get_forces().ravel()
            if gradient is not None:
                with suppress(TypeError, AttributeError, AssertionError):
                    converged = converged_attr(gradient)
            else:
                with suppress(TypeError, AttributeError):
                    converged = converged_attr()
        elif isinstance(converged_attr, bool):
            converged = converged_attr

    if converged is None:
        converged = False

    if converged:
        logger.info("%s Optimization Finished", finish_time)
    else:
        logger.error(
            "%s GeoOpt stopped: maximum iterations reached without convergence.",
            finish_time,
        )
        return 1, None
    logger.info("")
    logger.info("*****************************************************************************",)
    logger.info("*                          Final GeoOpt Results                              *")
    logger.info("*****************************************************************************",)
    logger.info("*")
    log_geometry(logger, context.atoms, "Final geometry (Å):")
    logger.info("*")

    potential_energy = context.atoms.get_potential_energy()
    total_energy = context.atoms.get_total_energy()

    logger.info("Potential Energy: %s eV", potential_energy)
    logger.info("Total Energy:     %s eV", total_energy)
    logger.info("*")

    try:
        atomic_sum = Sum_of_atomic_energies(
            context.counts,
            args.mlff_chk,
            args.mlff_task,
            context.device,
            logger=logger,
        )
    except Exception as exc:
        logger.error("Failed to compute sum of atomic energies: %s", exc)
        return 1, None

    bonding_energy = total_energy - atomic_sum
    logger.info("*")
    logger.info("Sum of atomic energies: %s eV", atomic_sum)
    logger.info("Bonding Energy: %s eV", bonding_energy)
    logger.info("Bonding Energy: %s kcal.mol-1", bonding_energy*23.0609)
    logger.info("*")

    trajectory = read(filename=str(paths.trajectory), index=":")
    rmsd_value = rmsd_simple(trajectory[0], trajectory[-1])
    logger.info("RMSD between first (initial) and last(optimized) geometries: %.6f Å", rmsd_value)
    logger.info("*")

    write(str(paths.final_geometry), context.atoms)
    logger.info("Final geometry in %s", str(paths.final_geometry))
    logger.info("Check results in %s", str(paths.log))
    logger.info("GeoOpt movie in %s", str(paths.trajectory))
    logger.info("*")
    logger.info("End of GeoOpt")

    if args.visualize:
        view(trajectory)

    return 0, context


def run_single_point(
    args: Namespace,
    paths: WorkflowPaths,
    logger: logging.Logger,
) -> Tuple[int, Optional[AtomContext]]:
    """Compute single-point energies and bonding energy."""
    status, context = _setup_calculated_atoms(args, logger)
    if status != 0 or context is None:
        return status, None

    atoms = context.atoms
    logger.info("*****************************************************************************",)
    logger.info("*                      Single Point Energy Calculation                      *",)
    logger.info("*****************************************************************************",)
    logger.info("*")

    logger.info("*")
    logger.info("%s Single-point energy calculation", datetime.now())
    logger.info("*")

    log_geometry(logger, atoms, "Initial geometry for Single Point (Å):")
    logger.info("*")

    potential_energy = atoms.get_potential_energy()
    total_energy = atoms.get_total_energy()

    logger.info("Potential Energy: %s eV", potential_energy)
    logger.info("Total Energy:     %s eV", total_energy)
    logger.info(" ")

    try:
        atomic_sum = Sum_of_atomic_energies(
            context.counts,
            args.mlff_chk,
            args.mlff_task,
            context.device,
            logger=logger,
        )
    except Exception as exc:
        logger.error("Failed to compute sum of atomic energies: %s", exc)
        return 1, None

    bonding_energy = total_energy - atomic_sum
    logger.info("*")
    logger.info("Sum of atomic energies: %s eV", atomic_sum)
    logger.info("Bonding Energy: %s eV", bonding_energy)
    logger.info("Bonding Energy: %s kcal.mol-1", bonding_energy*23.0609)
    logger.info("*")
    logger.info("%s End of Single Point", datetime.now())

    return 0, context


def run_vibrational_analysis(
    context: AtomContext,
    logger: logging.Logger,
    base_path: Path,
    temperature: float,
    pressure: float,
) -> int:
    """Compute vibrational frequencies and thermochemistry, tidying cache files."""

    start_time = datetime.now()
    logger.info("*****************************************************************************",)
    logger.info("*                          Vibrational Analysis                             *",)
    logger.info("*****************************************************************************",)
    logger.info("*")
 
    logger.info(
        "%s Starting vibrational analysis on device %s (T=%.4f K, P=%.2f Pa)",
        start_time,
        context.device,
        temperature,
        pressure,
    )

    log_geometry(logger, context.atoms, "Geometry for Frequencies (Å):")
    logger.info("*")
    freq_root = base_path.parent / "freqs"
    freq_root.mkdir(parents=True, exist_ok=True)
    base_name = base_path.stem
    target_dir = freq_root / base_name
    target_dir.mkdir(parents=True, exist_ok=True)
    cache_dir = target_dir / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    vib_prefix = cache_dir / base_name
    vib = Vibrations(context.atoms, name=str(vib_prefix))
    vib.clean()

    try:
        vib.run()
    except Exception as exc:
        logger.error("Failed to compute vibrational modes: %s", exc)
        _cleanup_vibration_cache(cache_dir, target_dir, logger)
        return 1

    end_time = datetime.now()
    logger.info("%s Vibrational analysis completed. Normal modes stored under %s", end_time, target_dir)
    logger.info("*")

    try:
        vib_energies = vib.get_energies()
    except ValueError:
        logger.error("ValueError: Imaginary vibrational energies are present.")
        _cleanup_vibration_cache(cache_dir, target_dir, logger)
        return 1

    try:
        _, summary_output = capture_stdout(vib.summary)
        if summary_output:
            logger.info("Vibrational summary:\n%s", summary_output.rstrip())
        else:
            logger.info("Vibrational summary: <no output>")
    except Exception as exc:  # pragma: no cover - ASE behaviour varies
        logger.warning("Unable to print vibration summary: %s", exc)

    try:
        vib.write_mode()
    except Exception as exc:  # pragma: no cover - optional
        logger.warning("Unable to write vibrational modes: %s", exc)

    potential_energy = context.atoms.get_potential_energy()
    try:
        thermo = IdealGasThermo(
            vib_energies=vib_energies,
            potentialenergy=potential_energy,
            atoms=context.atoms,
            geometry="nonlinear",
            symmetrynumber=1,
            spin=0,
        )
    except ValueError:
        logger.error("ValueError: Imaginary vibrational energies prevent further Thermochemistry analysis")
        _cleanup_vibration_cache(cache_dir, target_dir, logger)
        return 1
    if hasattr(thermo, "summary"):
        try:
            _, thermo_output = capture_stdout(
                thermo.summary,
                temperature=temperature,
                pressure=pressure,
                verbose=True,
            )
            if thermo_output:
                logger.info("Thermochemistry summary (IdealGasThermo):\n%s", thermo_output.rstrip())
        except Exception as exc:  # pragma: no cover - optional
            logger.warning("IdealGasThermo.summary failed: %s", exc)
    else:
        property_specs = []
        recorded_lines = []
        for label, method_name, kwargs, unit in property_specs:
            method = getattr(thermo, method_name, None)
            if callable(method):
                try:
                    value, prop_output = capture_stdout(method, **kwargs)
                except Exception as exc:  # pragma: no cover - optional
                    logger.warning("Unable to evaluate %s: %s", label.lower(), exc)
                else:
                    if prop_output:
                        logger.info(prop_output.rstrip())
                    recorded_lines.append(f"  {label}: {value} {unit}")
        if recorded_lines:
            logger.info("Thermochemistry (IdealGasThermo):\n%s", "\n".join(recorded_lines))

    try:
        gibbs, gibbs_output = capture_stdout(
            thermo.get_gibbs_energy,
            temperature=temperature,
            pressure=pressure,
        )
        if gibbs_output:
            logger.info("IdealGasThermo main output:\n%s", gibbs_output.rstrip())
    except Exception as exc:
        logger.warning("Unable to compute Gibbs free energy: %s", exc)
        _cleanup_vibration_cache(cache_dir, target_dir, logger)
        return 1
    logger.info("*")
    logger.info("%s End of Vibrational Analysis", datetime.now())

    _cleanup_vibration_cache(cache_dir, target_dir, logger)
    return 0
