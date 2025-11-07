"""Flask service exposing UMA-ASE workflows for web clients."""

from __future__ import annotations

import tempfile
from datetime import datetime
from importlib import resources
from pathlib import Path
from collections import Counter
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional
import threading
import uuid

from flask import Flask, Response, abort, jsonify, request, send_file
from werkzeug.utils import secure_filename

from ase.io import read, write

from .cli import main as cli_main
from .workflows import build_output_paths, select_device, TorchUnavailable
from .utils import extract_xyz_metadata

STATIC_HTML = "UMA-ASE.html"
app = Flask(__name__)
app.config.setdefault("UMA_RESULTS_DIR", Path.home() / ".uma_ase" / "results")


@dataclass
class JobRecord:
    job_id: str
    job_dir: Path
    charge: int
    spin: int
    grad: float
    iterations: int
    run_types: List[str]
    status: str = "running"
    message: Optional[str] = None
    log_path: Optional[Path] = None
    traj_path: Optional[Path] = None
    opt_path: Optional[Path] = None
    log_url: Optional[str] = None
    traj_url: Optional[str] = None
    opt_url: Optional[str] = None


JOBS: Dict[str, JobRecord] = {}
JOB_LOCK = threading.Lock()


def _get_job(job_id: str) -> JobRecord:
    with JOB_LOCK:
        record = JOBS.get(job_id)
    if record is None:
        abort(404)
    return record


def _build_cli_args(
    input_path: Path,
    run_types: Iterable[str],
    charge: str,
    spin: str,
    optimizer: str,
    grad: str,
    iterations: str,
    temperature: str,
    pressure: str,
    mlff_checkpoint: str | None,
    mlff_task: str | None,
) -> List[str]:
    args: List[str] = [
        "-input",
        str(input_path),
        "-chg",
        charge,
        "-spin",
        spin,
        "-optimizer",
        optimizer,
        "-grad",
        grad,
        "-iter",
        iterations,
        "-temp",
        temperature,
        "-press",
        pressure,
    ]
    if run_types:
        args.extend(["-run-type", *run_types])
    if mlff_checkpoint:
        args.extend(["-mlff-chk", mlff_checkpoint])
    if mlff_task:
        args.extend(["-mlff-task", mlff_task])
    return args


def _collect_log(temp_dir: Path) -> str:
    logs = sorted(temp_dir.glob("*.log"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not logs:
        return "No log file generated."
    return logs[0].read_text(encoding="utf-8", errors="replace")


@app.route("/")
def index() -> Response:
    """Serve the single-page frontend bundled with the package."""
    html_path = resources.files("uma_ase").joinpath("static", STATIC_HTML)
    return Response(html_path.read_bytes(), mimetype="text/html")


@app.route("/assets/<path:asset>")
def serve_static_asset(asset: str):
    """Serve packaged static assets (e.g. logo.svg) referenced from the frontend."""
    candidate = resources.files("uma_ase").joinpath("static", asset)
    if not candidate.is_file():
        abort(404)
    with resources.as_file(candidate) as fs_path:
        return send_file(fs_path)


@app.route("/assets/")
def serve_static_root():
    """Provide a no-op response for tools that probe the asset root (e.g. JSmol)."""
    return Response(status=204)


@app.route("/api/uma-ase/run", methods=["POST"])
def run_job():
    geometry = request.files.get("geometry")
    if geometry is None or geometry.filename == "":
        return jsonify({"status": "error", "message": "Geometry file is required."}), 400

    try:
        charge_val = int(request.form.get("charge", "0"))
    except (TypeError, ValueError):
        return jsonify({"status": "error", "message": "Charge must be an integer."}), 400

    try:
        spin_val = int(request.form.get("spin", "1"))
    except (TypeError, ValueError):
        return jsonify({"status": "error", "message": "Spin multiplicity must be an integer."}), 400

    try:
        grad_val = float(request.form.get("grad", "0.01"))
    except (TypeError, ValueError):
        return jsonify({"status": "error", "message": "Grad must be a number."}), 400
    if grad_val <= 0:
        return jsonify({"status": "error", "message": "Grad must be positive."}), 400

    try:
        iter_val = int(request.form.get("iter", "250"))
    except (TypeError, ValueError):
        return jsonify({"status": "error", "message": "Max iterations must be an integer."}), 400
    if iter_val <= 0:
        return jsonify({"status": "error", "message": "Max iterations must be positive."}), 400

    optimizer = request.form.get("optimizer", "LBFGS")
    temperature = request.form.get("temperature", "298.15")
    pressure = request.form.get("pressure", "101325.0")
    run_types_raw = request.form.get("run_type", "sp").split()
    run_types = [item.lower() for item in run_types_raw] or ["sp"]
    mlff_checkpoint_raw = request.form.get("mlff_checkpoint", "uma-s-1p1")
    mlff_checkpoint = mlff_checkpoint_raw.strip() or "uma-s-1p1"
    mlff_task_raw = request.form.get("mlff_task", "omol")
    mlff_task = mlff_task_raw.strip() or "omol"

    results_root = Path(app.config["UMA_RESULTS_DIR"])
    results_root.mkdir(parents=True, exist_ok=True)

    job_id = f"{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6]}"
    job_dir = results_root / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    filename = secure_filename(geometry.filename) or "input.xyz"
    input_path = job_dir / filename
    geometry.save(input_path)

    record = JobRecord(
        job_id=job_id,
        job_dir=job_dir,
        charge=charge_val,
        spin=spin_val,
        grad=grad_val,
        iterations=iter_val,
        run_types=run_types,
    )

    with JOB_LOCK:
        JOBS[job_id] = record

    worker = threading.Thread(
        target=_execute_job,
        args=(
            record,
            filename,
            optimizer,
            temperature,
            pressure,
            mlff_checkpoint,
            mlff_task,
        ),
        daemon=True,
    )
    worker.start()

    return jsonify({"job_id": job_id})


def _execute_job(
    record: JobRecord,
    filename: str,
    optimizer: str,
    temperature: str,
    pressure: str,
    mlff_checkpoint: Optional[str],
    mlff_task: Optional[str],
):
    job_dir = record.job_dir
    input_path = job_dir / filename
    run_sequence = record.run_types or ["sp"]

    try:
        paths = build_output_paths(input_path, run_sequence)
        record.log_path = paths.log
        record.traj_path = paths.trajectory
        record.opt_path = paths.final_geometry

        argv = _build_cli_args(
            input_path,
            record.run_types,
            str(record.charge),
            str(record.spin),
            optimizer,
            str(record.grad),
            str(record.iterations),
            temperature,
            pressure,
            mlff_checkpoint,
            mlff_task,
        )

        status = cli_main(argv)

        error_message: Optional[str] = None
        if status != 0:
            error_message = f"UMA-ASE exited with status {status}."
        else:
            if record.opt_path and record.opt_path.exists():
                try:
                    atoms_opt = read(str(record.opt_path))
                    formula_opt = atoms_opt.get_chemical_formula()
                    comment = " ".join(
                        part
                        for part in [
                            formula_opt,
                            f"charge={record.charge}",
                            f"spin={record.spin}",
                        ]
                        if part
                    )
                    write(str(record.opt_path), atoms_opt, format="xyz", comment=comment)
                except Exception as exc:
                    error_message = f"Optimized geometry rewrite failed: {exc}"

        with JOB_LOCK:
            if error_message:
                record.status = "error"
                record.message = error_message
            else:
                record.status = "completed"

            if record.log_path and record.log_path.exists():
                record.log_url = f"/api/uma-ase/job/{record.job_id}/log"
            if record.traj_path and record.traj_path.exists():
                record.traj_url = f"/api/uma-ase/job/{record.job_id}/trajectory"
            if record.opt_path and record.opt_path.exists():
                record.opt_url = f"/api/uma-ase/job/{record.job_id}/optimized"

    except Exception as exc:
        with JOB_LOCK:
            record.status = "error"
            record.message = str(exc)


def _send_job_file(path: Optional[Path], mimetype: str = "text/plain"):
    if path is None or not path.exists():
        abort(404)
    return send_file(
        path,
        mimetype=mimetype,
        as_attachment=True,
        download_name=path.name,
    )


@app.route("/api/uma-ase/job/<job_id>", methods=["GET"])
def job_status(job_id: str):
    record = _get_job(job_id)
    log_text = ""
    if record.log_path and record.log_path.exists():
        try:
            log_text = record.log_path.read_text(encoding="utf-8")
        except OSError:
            log_text = ""
    return jsonify(
        {
            "status": record.status,
            "message": record.message,
            "log": log_text,
            "log_download": record.log_url,
            "traj_download": record.traj_url,
            "opt_download": record.opt_url,
        }
    )


@app.route("/api/uma-ase/job/<job_id>/log", methods=["GET"])
def download_job_log(job_id: str):
    record = _get_job(job_id)
    return _send_job_file(record.log_path, "text/plain")


@app.route("/api/uma-ase/job/<job_id>/trajectory", methods=["GET"])
def download_job_trajectory(job_id: str):
    record = _get_job(job_id)
    return _send_job_file(record.traj_path, "application/octet-stream")


@app.route("/api/uma-ase/job/<job_id>/optimized", methods=["GET"])
def download_job_optimized(job_id: str):
    record = _get_job(job_id)
    return _send_job_file(record.opt_path, "text/plain")


@app.route("/api/uma-ase/preview", methods=["POST"])
def preview_structure():
    geometry = request.files.get("geometry")
    if geometry is None or geometry.filename == "":
        return jsonify({"status": "error", "message": "Geometry file is required."}), 400

    charge_raw = request.form.get("charge")
    spin_raw = request.form.get("spin")
    spin_val = 1

    with tempfile.TemporaryDirectory(prefix="uma_preview_") as temp_dir_str:
        temp_dir = Path(temp_dir_str)
        filename = secure_filename(geometry.filename) or "input.xyz"
        input_path = temp_dir / filename
        geometry.save(input_path)

        metadata = extract_xyz_metadata(input_path)

        if charge_raw is None or charge_raw.strip() == "":
            charge_val = metadata.charge if metadata.charge is not None else 0
        else:
            try:
                charge_val = int(charge_raw)
            except (TypeError, ValueError):
                return jsonify({"status": "error", "message": "Charge must be an integer."}), 400

        if spin_raw is None or spin_raw.strip() == "":
            if metadata.spin is not None and metadata.spin > 0:
                spin_val = metadata.spin
            else:
                spin_val = 1
        else:
            try:
                spin_val = int(spin_raw)
            except (TypeError, ValueError):
                return jsonify({"status": "error", "message": "Spin multiplicity must be an integer."}), 400
            if spin_val <= 0:
                return jsonify({"status": "error", "message": "Spin multiplicity must be positive."}), 400

        try:
            atoms = read(str(input_path))
        except Exception as exc:  # pragma: no cover - depends on external IO
            return jsonify({"status": "error", "message": f"Unable to read geometry: {exc}"}), 400

        atoms.info["charge"] = charge_val
        atoms.info["spin"] = spin_val
        xyz_comment = metadata.comment
        if xyz_comment:
            atoms.info.setdefault("uma_comment", xyz_comment)
        if metadata.url:
            atoms.info.setdefault("uma_comment_url", metadata.url)

        counts = Counter(atoms.get_chemical_symbols())
        num_atoms = len(atoms)
        formula = atoms.get_chemical_formula()
        element_counts = dict(counts)

        # Decide device availability using fairchem rules
        try:
            device = select_device()
        except TorchUnavailable:
            device = "cpu"

    summary_lines = [
        f"Number of atoms: {num_atoms}",
        f"Formula: {formula}",
        f"Element counts: {element_counts}",
        f"Device: {device}",
    ]
    summary_lines.insert(0, f"Spin multiplicity: {spin_val}")
    summary_lines.insert(0, f"Charge: {charge_val}")
    if xyz_comment:
        summary_lines.insert(0, f"Comment: {xyz_comment}")
    if metadata.url:
        summary_lines.insert(0, f"Source URL: {metadata.url}")

    return jsonify(
        {
            "status": "ok",
            "initial_geometry": filename,
            "num_atoms": num_atoms,
            "formula": formula,
            "element_counts": element_counts,
            "charge": charge_val,
            "spin": spin_val,
            "device": device,
            "comment": xyz_comment,
            "lines": summary_lines,
        }
    )
def create_app() -> Flask:
    """Factory for embedding in external WSGI servers."""
    return app


def main() -> None:
    """Run the development server."""
    app.run(debug=True, port=8000)


if __name__ == "__main__":  # pragma: no cover
    main()
