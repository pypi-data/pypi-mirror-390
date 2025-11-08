"""Command-line interface for minimodal."""

import click
import subprocess
import sys
import os
import tempfile
from pathlib import Path
from typing import Optional

try:
    from .modal_integration import compile_and_run_on_modal
    MODAL_AVAILABLE = True
except ImportError:
    MODAL_AVAILABLE = False
    compile_and_run_on_modal = None

# GPU name to architecture mapping (matches Modal GPU naming convention)
GPU_ARCH_MAP = {
    "H100": "90",
    "H800": "90",
    "A100": "80",
    "A800": "80",
    "A10G": "86",
    "B200": "100a",
    "B100": "100a",
    "RTX4090": "89",
    "RTX3090": "86",
    "RTX3080": "86",
    "V100": "70",
    "T4": "75",
}

# Modal-supported GPUs (these can run on Modal cloud)
MODAL_GPUS = {"H100", "H800", "A100", "A800", "A10G", "B200", "B100", "V100", "T4"}


def find_gpu_by_name(gpu_name: str) -> Optional[int]:
    """Find GPU device ID by name using nvidia-smi.
    
    Matches GPU names case-insensitively and handles partial matches.
    For example, "A10G" will match "NVIDIA A10G" or "A10G".
    """
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=index,name", "--format=csv,noheader"],
            capture_output=True,
            text=True,
            check=True,
        )
        
        # Normalize the input GPU name for matching
        normalized_search = gpu_name.strip().upper()
        
        for line in result.stdout.strip().split("\n"):
            if not line.strip():
                continue
            parts = line.split(",", 1)
            if len(parts) == 2:
                gpu_id = int(parts[0].strip())
                name = parts[1].strip()
                normalized_name = name.upper()
                
                # Check if search term appears in GPU name
                # This handles cases like "A10G" matching "NVIDIA A10G" or "RTX 3090" matching "NVIDIA GeForce RTX 3090"
                if normalized_search in normalized_name:
                    return gpu_id
        
        return None
    except (subprocess.CalledProcessError, FileNotFoundError, ValueError):
        return None


def list_available_gpus() -> list[str]:
    """List all available GPU names."""
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
            capture_output=True,
            text=True,
            check=True,
        )
        return [line.strip() for line in result.stdout.strip().split("\n") if line.strip()]
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []


def get_gpu_architecture(gpu_name: str) -> str:
    """Get CUDA architecture string for a GPU name.
    
    Supports Modal GPU naming convention (A10G, H100, B200, etc.)
    and also accepts raw architecture strings (e.g., "100a", "90").
    """
    # Normalize input
    normalized = gpu_name.strip().upper()
    
    # Try exact match first (e.g., "A10G" -> "86")
    if normalized in GPU_ARCH_MAP:
        return GPU_ARCH_MAP[normalized]
    
    # Try partial match (e.g., "RTX3090" matches "RTX3090" in map)
    for gpu, arch in GPU_ARCH_MAP.items():
        if gpu.upper() in normalized or normalized in gpu.upper():
            return arch
    
    # Default to the provided name (might be raw arch like "100a" or "90")
    return gpu_name


@click.command()
@click.argument("cuda_file", type=click.Path(exists=True))
@click.option(
    "--gpu",
    "-g",
    default="A10G",
    help="GPU name using Modal convention (e.g., A10G, H100, B200, A100) or architecture (e.g., 100a, 90). Default: A10G",
)
@click.option(
    "--include-dir",
    "-I",
    "include_dirs",
    multiple=True,
    type=click.Path(exists=True, dir_okay=True, file_okay=False),
    help="Include directory. Can be specified multiple times.",
)
@click.option(
    "--exec-args",
    default="",
    help="Arguments to pass to the compiled CUDA executable.",
)
@click.option(
    "--arch",
    help="Override architecture (e.g., 100a, 90). If not specified, inferred from --gpu.",
)
@click.option(
    "--output",
    "-o",
    help="Output executable path. If not specified, uses temporary file.",
)
@click.option(
    "--keep-binary",
    is_flag=True,
    help="Keep the compiled binary after execution.",
)
@click.option(
    "--nvcc-flags",
    default="",
    help="Additional flags to pass to nvcc (e.g., '-O3 --ptxas-options=-v').",
)
def main(
    cuda_file: str,
    gpu: str,
    include_dirs: tuple,
    exec_args: str,
    arch: Optional[str],
    output: Optional[str],
    keep_binary: bool,
    nvcc_flags: str,
):
    """
    Compile and run a CUDA kernel file on a local GPU or Modal cloud GPU.
    
    If the specified GPU is not found locally but is available on Modal (A10G, H100, B200, etc.),
    it will automatically run on Modal cloud infrastructure.
    
    Examples:
    
        minimodal v1.cu                          # Uses local A10G or Modal A10G
    
        minimodal v1.cu --gpu B200 -I ./includes # Uses Modal B200 if not found locally
    
        minimodal v1.cu --gpu A100 --exec-args "--N 2097152 --warmup 5"
    
        minimodal kernel.cu --gpu H100 -I ./includes -I ./headers --nvcc-flags "-O3"
    """
    cuda_path = Path(cuda_file)
    
    # Determine architecture
    if arch:
        target_arch = arch
    else:
        target_arch = get_gpu_architecture(gpu)
    
    click.echo(f"🎯 Target GPU: {gpu}")
    click.echo(f"📐 Architecture: sm_{target_arch}")
    
    # Find GPU device ID (skip if --arch is specified, as user is explicitly setting architecture)
    use_modal = False
    if not arch:
        gpu_id = find_gpu_by_name(gpu)
        if gpu_id is not None:
            click.echo(f"🔍 Found GPU {gpu} at device {gpu_id}")
            os.environ["CUDA_VISIBLE_DEVICES"] = str(gpu_id)
        else:
            # GPU not found locally - check if it's a Modal GPU
            normalized_gpu = gpu.strip().upper()
            if normalized_gpu in MODAL_GPUS and MODAL_AVAILABLE:
                click.echo(f"🔍 GPU '{gpu}' not found locally. Using Modal cloud GPU...")
                use_modal = True
                # Use normalized GPU name for Modal (e.g., "A10G" instead of "a10g")
                gpu = normalized_gpu
            else:
                # GPU not found and not a Modal GPU - exit with error
                available_gpus = list_available_gpus()
                if available_gpus:
                    click.echo(f"❌ GPU '{gpu}' not found. Available GPUs:", err=True)
                    for i, avail_gpu in enumerate(available_gpus):
                        click.echo(f"   [{i}] {avail_gpu}", err=True)
                    if MODAL_AVAILABLE:
                        click.echo(f"\n💡 Tip: '{gpu}' is available on Modal. Install modal and run again to use cloud GPU.", err=True)
                    click.echo(f"\n💡 Tip: Use one of the available GPUs above or specify an architecture directly with --arch sm_{target_arch}", err=True)
                else:
                    click.echo(f"❌ GPU '{gpu}' not found and no GPUs detected.", err=True)
                    if MODAL_AVAILABLE and normalized_gpu in MODAL_GPUS:
                        click.echo(f"\n💡 Tip: '{gpu}' is available on Modal. Run again to use cloud GPU.", err=True)
                click.echo("\n⚠️  Exiting: GPU not found. Use --arch to compile for a specific architecture without GPU selection.", err=True)
                sys.exit(1)
    
    # Use Modal if GPU not found locally
    if use_modal:
        if not MODAL_AVAILABLE:
            click.echo("❌ Modal not available. Install with: uv pip install modal", err=True)
            sys.exit(1)
        
        click.echo(f"\n☁️  Running on Modal with GPU: {gpu}")
        
        try:
            result = compile_and_run_on_modal(
                cuda_file=str(cuda_path),
                gpu=gpu,
                arch=target_arch,
                include_dirs=include_dirs,
                exec_args=exec_args,
                nvcc_flags=nvcc_flags,
            )
            
            if not result.get("success"):
                click.echo(f"\n❌ Failed: {result.get('error', 'Unknown error')}", err=True)
                if result.get("compile_stderr"):
                    click.echo("\nCompilation errors:", err=True)
                    click.echo(result["compile_stderr"], err=True)
                sys.exit(1)
            
            click.echo("\n✓ Execution completed successfully")
            sys.exit(result.get("return_code", 0))
            
        except Exception as e:
            click.echo(f"\n❌ Modal execution failed: {e}", err=True)
            sys.exit(1)
    
    # Verify GPU availability
    try:
        gpu_check = subprocess.run(
            ["nvidia-smi"],
            capture_output=True,
            text=True,
            check=True,
        )
        if gpu_check.returncode == 0:
            click.echo("✓ GPU detected")
    except (subprocess.CalledProcessError, FileNotFoundError):
        click.echo("❌ nvidia-smi not found or failed. Make sure CUDA drivers are installed.", err=True)
        sys.exit(1)
    
    # Determine output path
    if output:
        output_path = Path(output)
    else:
        output_path = Path(tempfile.gettempdir()) / f"{cuda_path.stem}"
    
    # Compile
    click.echo(f"\n📄 Compiling {cuda_path.name}...")
    
    nvcc_cmd = [
        "nvcc",
        f"-arch=sm_{target_arch}",
        "-o",
        str(output_path),
        str(cuda_path),
    ]
    
    # Add include directories
    for include_dir in include_dirs:
        nvcc_cmd.extend(["-I", str(include_dir)])
    
    # Add extra nvcc flags
    if nvcc_flags:
        nvcc_cmd.extend(nvcc_flags.split())
    
    click.echo(f"   Command: {' '.join(nvcc_cmd)}")
    
    try:
        compile_result = subprocess.run(
            nvcc_cmd,
            capture_output=True,
            text=True,
            check=True,
        )
        click.echo("✓ Compilation successful")
    except subprocess.CalledProcessError as e:
        click.echo("❌ Compilation failed:", err=True)
        if e.stdout:
            click.echo(e.stdout, err=True)
        if e.stderr:
            click.echo(e.stderr, err=True)
        sys.exit(1)
    except FileNotFoundError:
        click.echo("❌ nvcc not found. Make sure CUDA toolkit is installed and in PATH.", err=True)
        sys.exit(1)
    
    # Run
    click.echo(f"\n🚀 Running {output_path.name}...")
    
    run_cmd = [str(output_path)]
    if exec_args:
        run_cmd.extend(exec_args.split())
        click.echo(f"   Arguments: {exec_args}")
    
    try:
        run_result = subprocess.run(
            run_cmd,
            capture_output=True,
            text=True,
        )
        
        # Print output
        click.echo("\n" + "=" * 60)
        click.echo("PROGRAM OUTPUT")
        click.echo("=" * 60)
        
        if run_result.stdout:
            click.echo(run_result.stdout)
        if run_result.stderr:
            click.echo("STDERR:", err=True)
            click.echo(run_result.stderr, err=True)
        
        click.echo("=" * 60)
        
        if run_result.returncode == 0:
            click.echo("\n✓ Execution completed successfully")
        else:
            click.echo(
                f"\n⚠️  Execution completed with return code {run_result.returncode}",
                err=True,
            )
        
        # Cleanup
        if not keep_binary and not output:
            try:
                output_path.unlink()
            except Exception:
                pass
        elif keep_binary:
            click.echo(f"\n💾 Binary saved at: {output_path}")
        
        sys.exit(run_result.returncode)
        
    except FileNotFoundError:
        click.echo(f"❌ Executable not found: {output_path}", err=True)
        sys.exit(1)
    except KeyboardInterrupt:
        click.echo("\n\n⚠️  Interrupted by user", err=True)
        if not keep_binary and not output:
            try:
                output_path.unlink()
            except Exception:
                pass
        sys.exit(130)


if __name__ == "__main__":
    main()

