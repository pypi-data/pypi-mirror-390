"""Modal integration for minimodal."""

import modal
import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple, List


def compile_and_run_on_modal(
    cuda_file: str,
    gpu: str,
    arch: str,
    include_dirs: Tuple[str, ...],
    exec_args: str,
    nvcc_flags: str,
) -> dict:
    """Compile and run CUDA kernel on Modal."""
    
    cuda_path = Path(cuda_file)
    
    # Build image
    flavor = "devel"
    operating_sys = "ubuntu24.04"
    cuda_version = "13.0.0"
    tag = f"{cuda_version}-{flavor}-{operating_sys}"
    
    image = (
        modal.Image.from_registry(f"nvcr.io/nvidia/cuda:{tag}", add_python="3.12")
        .entrypoint([])
        .apt_install("build-essential")
    )
    
    # Add CUDA file
    cuda_file_abs = cuda_path.resolve()
    image = image.add_local_file(str(cuda_file_abs), remote_path=f"/workspace/{cuda_path.name}")
    
    # Add include directories and collect their names
    include_dir_names = []
    for include_dir in include_dirs:
        include_path = Path(include_dir).resolve()
        if include_path.is_dir():
            dir_name = include_path.name
            image = image.add_local_dir(str(include_path), remote_path=f"/workspace/{dir_name}")
            include_dir_names.append(dir_name)
    
    # Create app
    app = modal.App("minimodal-cuda-kernel", image=image)
    
    # Capture variables for closure
    cuda_filename = cuda_path.name
    extra_flags_str = nvcc_flags if nvcc_flags else ""
    
    # Define the function inline with serialized=True
    # The function only uses standard library, so it can be serialized safely
    @app.function(
        gpu=gpu,
        timeout=600,
        image=image,
        serialized=True,
    )
    def compile_and_run_cuda_modal(
        cuda_filename: str,
        target_arch: str,
        include_dirs: List[str],
        extra_flags: str,
        exec_args_str: str,
    ):
        """Compile and run CUDA kernel on Modal - this function runs on Modal."""
        # Verify GPU
        print("Verifying GPU availability...")
        gpu_check = subprocess.run(["nvidia-smi"], capture_output=True, text=True)
        if gpu_check.returncode == 0:
            print("✓ GPU detected:")
            print(gpu_check.stdout.split("\n")[0:5])
        
        # Resolve file path
        cuda_path = Path("/workspace") / cuda_filename
        if not cuda_path.exists():
            return {
                "error": f"CUDA file not found: {cuda_filename}",
                "success": False,
            }
        
        # Compile
        print(f"\n📄 Compiling {cuda_path.name}...")
        print(f"   Architecture: sm_{target_arch}")
        
        output_name = cuda_path.stem
        nvcc_cmd = [
            "nvcc",
            f"-arch=sm_{target_arch}",
            "-o", f"/tmp/{output_name}",
            str(cuda_path),
        ]
        
        # Add include directories
        for include_dir_name in include_dirs:
            nvcc_cmd.extend(["-I", f"/workspace/{include_dir_name}"])
        
        if extra_flags:
            nvcc_cmd.extend(extra_flags.split())
        
        print(f"   Command: {' '.join(nvcc_cmd)}")
        
        compile_result = subprocess.run(nvcc_cmd, capture_output=True, text=True)
        
        if compile_result.returncode != 0:
            return {
                "error": "Compilation failed",
                "success": False,
                "compile_stdout": compile_result.stdout,
                "compile_stderr": compile_result.stderr,
            }
        
        print("✓ Compilation successful")
        
        # Run
        print(f"\n🚀 Running {output_name}...")
        run_cmd = [f"/tmp/{output_name}"]
        if exec_args_str:
            run_cmd.extend(exec_args_str.split())
            print(f"   Arguments: {exec_args_str}")
        
        run_result = subprocess.run(
            run_cmd,
            capture_output=True,
            text=True,
        )
        
        # Print output
        print("\n" + "="*60)
        print("PROGRAM OUTPUT")
        print("="*60)
        if run_result.stdout:
            print(run_result.stdout)
        if run_result.stderr:
            print("STDERR:", file=sys.stderr)
            print(run_result.stderr, file=sys.stderr)
        print("="*60)
        
        return {
            "success": True,
            "compile_stdout": compile_result.stdout,
            "compile_stderr": compile_result.stderr,
            "run_stdout": run_result.stdout,
            "run_stderr": run_result.stderr,
            "return_code": run_result.returncode,
        }
    
    # Use Modal's run() context manager to execute the function
    # This creates a synchronous execution context
    with modal.enable_output():
        with app.run():
            result = compile_and_run_cuda_modal.remote(
                cuda_filename, arch, include_dir_names, extra_flags_str, exec_args
            )
    
    return result

