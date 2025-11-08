"""MCP server implementation for minimodal CUDA compilation and execution."""

import os
import tempfile
import json
from pathlib import Path
from typing import Any

import mcp.types as types
from mcp.server.lowlevel import Server

# Import existing minimodal functionality
from .cli import (
    find_gpu_by_name,
    list_available_gpus,
    get_gpu_architecture,
    MODAL_GPUS,
    GPU_ARCH_MAP,
)

try:
    from .modal_integration import compile_and_run_on_modal
    MODAL_AVAILABLE = True
except ImportError:
    MODAL_AVAILABLE = False
    compile_and_run_on_modal = None


def create_minimodal_mcp_server() -> Server:
    """Create and configure the minimodal MCP server."""
    
    app = Server("minimodal-cuda-compiler")
    
    @app.call_tool()
    async def compile_cuda(name: str, arguments: dict[str, Any]) -> list[types.TextContent]:
        """Compile and run a CUDA kernel file."""
        if name != "compile_cuda":
            raise ValueError(f"Unknown tool: {name}")
            
        required_args = ["cuda_file"]
        for arg in required_args:
            if arg not in arguments:
                raise ValueError(f"Missing required argument: {arg}")
        
        # Extract arguments
        cuda_file = arguments["cuda_file"]
        gpu = arguments.get("gpu", "A10G")
        include_dirs = arguments.get("include_dirs", [])
        exec_args = arguments.get("exec_args", "")
        arch = arguments.get("arch", None)
        output = arguments.get("output", None)
        keep_binary = arguments.get("keep_binary", False)
        nvcc_flags = arguments.get("nvcc_flags", "")
        
        # Validate inputs
        cuda_path = Path(cuda_file)
        if not cuda_path.exists():
            return [types.TextContent(
                type="text",
                text=f"Error: CUDA file not found: {cuda_file}"
            )]
        
        # Include directories validation
        validated_include_dirs = []
        for include_dir in include_dirs:
            inc_path = Path(include_dir)
            if not inc_path.exists() or not inc_path.is_dir():
                return [types.TextContent(
                    type="text",
                    text=f"Error: Include directory not found: {include_dir}"
                )]
            validated_include_dirs.append(str(inc_path))
        
        # Determine architecture
        if arch:
            target_arch = arch
        else:
            target_arch = get_gpu_architecture(gpu)
        
        # Check for local GPU if not using explicit architecture
        use_modal = False
        if not arch:
            gpu_id = find_gpu_by_name(gpu)
            if gpu_id is not None:
                os.environ["CUDA_VISIBLE_DEVICES"] = str(gpu_id)
                gpu_found = True
            else:
                # GPU not found locally - check if it's a Modal GPU
                normalized_gpu = gpu.strip().upper()
                if normalized_gpu in MODAL_GPUS and MODAL_AVAILABLE:
                    use_modal = True
                    gpu = normalized_gpu
                    gpu_found = False
                else:
                    # GPU not found and not a Modal GPU - return error
                    available_gpus = list_available_gpus()
                    error_msg = f"GPU '{gpu}' not found."
                    if available_gpus:
                        error_msg += "\nAvailable GPUs:\n"
                        for i, avail_gpu in enumerate(available_gpus):
                            error_msg += f"   [{i}] {avail_gpu}\n"
                        if MODAL_AVAILABLE:
                            error_msg += f"\n'{gpu}' is available on Modal. Try running again to use cloud GPU.\n"
                    else:
                        error_msg += "\nNo GPUs detected."
                        if MODAL_AVAILABLE and normalized_gpu in MODAL_GPUS:
                            error_msg += f"\n'{gpu}' is available on Modal. Run again to use cloud GPU."
                    error_msg += "\nUse --arch to compile for a specific architecture without GPU selection."
                    
                    return [types.TextContent(
                        type="text",
                        text=error_msg
                    )]
        else:
            gpu_found = True  # Using explicit architecture, assume GPU available
        
        result_text = f"🎯 Target GPU: {gpu}\n📐 Architecture: sm_{target_arch}\n"
        
        # Use Modal if appropriate
        if use_modal:
            if not MODAL_AVAILABLE:
                return [types.TextContent(
                    type="text",
                    text="❌ Modal not available. Install with: uv pip install modal"
                )]
            
            result_text += f"☁️  Running on Modal with GPU: {gpu}\n"
            
            try:
                modal_result = compile_and_run_on_modal(
                    cuda_file=str(cuda_path),
                    gpu=gpu,
                    arch=target_arch,
                    include_dirs=tuple(validated_include_dirs),
                    exec_args=exec_args,
                    nvcc_flags=nvcc_flags,
                )
                
                if not modal_result.get("success"):
                    error_text = f"❌ Failed: {modal_result.get('error', 'Unknown error')}\n"
                    if modal_result.get("compile_stderr"):
                        error_text += "\nCompilation errors:\n"
                        error_text += modal_result["compile_stderr"]
                    return [types.TextContent(type="text", text=error_text)]
                
                result_text += "✓ Execution completed successfully\n"
                if modal_result.get("run_stdout"):
                    result_text += f"\n{modal_result['run_stdout']}"
                if modal_result.get("run_stderr"):
                    result_text += f"\nSTDERR:\n{modal_result['run_stderr']}\n"
                
                return [types.TextContent(type="text", text=result_text)]
                
            except Exception as e:
                return [types.TextContent(
                    type="text",
                    text=f"❌ Modal execution failed: {e}"
                )]
        
        # Local execution
        import subprocess
        import sys
        
        # Verify GPU availability
        try:
            subprocess.run(["nvidia-smi"], capture_output=True, text=True, check=True)
            result_text += "✓ GPU detected\n"
        except (subprocess.CalledProcessError, FileNotFoundError):
            return [types.TextContent(
                type="text",
                text="❌ nvidia-smi not found or failed. Make sure CUDA drivers are installed."
            )]
        
        # Determine output path
        if output:
            output_path = Path(output)
        else:
            output_path = Path(tempfile.gettempdir()) / f"{cuda_path.stem}"
        
        # Compile
        result_text += f"\n📄 Compiling {cuda_path.name}...\n"
        
        nvcc_cmd = [
            "nvcc",
            f"-arch=sm_{target_arch}",
            "-o",
            str(output_path),
            str(cuda_path),
        ]
        
        # Add include directories
        for include_dir in validated_include_dirs:
            nvcc_cmd.extend(["-I", str(include_dir)])
        
        # Add extra nvcc flags
        if nvcc_flags:
            nvcc_cmd.extend(nvcc_flags.split())
        
        result_text += f"   Command: {' '.join(nvcc_cmd)}\n"
        
        try:
            compile_result = subprocess.run(
                nvcc_cmd,
                capture_output=True,
                text=True,
                check=True,
            )
            result_text += "✓ Compilation successful\n"
        except subprocess.CalledProcessError as e:
            error_text = "❌ Compilation failed:\n"
            if e.stdout:
                error_text += e.stdout + "\n"
            if e.stderr:
                error_text += e.stderr + "\n"
            return [types.TextContent(type="text", text=error_text)]
        except FileNotFoundError:
            return [types.TextContent(
                type="text",
                text="❌ nvcc not found. Make sure CUDA toolkit is installed and in PATH."
            )]
        
        # Run
        result_text += f"\n🚀 Running {output_path.name}...\n"
        
        run_cmd = [str(output_path)]
        if exec_args:
            run_cmd.extend(exec_args.split())
            result_text += f"   Arguments: {exec_args}\n"
        
        try:
            run_result = subprocess.run(
                run_cmd,
                capture_output=True,
                text=True,
            )
            
            # Add output section
            result_text += "\n" + "=" * 60 + "\n"
            result_text += "PROGRAM OUTPUT\n"
            result_text += "=" * 60 + "\n"
            
            if run_result.stdout:
                result_text += run_result.stdout + "\n"
            if run_result.stderr:
                result_text += "STDERR:\n"
                result_text += run_result.stderr + "\n"
            
            result_text += "=" * 60 + "\n"
            
            if run_result.returncode == 0:
                result_text += "\n✓ Execution completed successfully\n"
            else:
                result_text += (
                    f"\n⚠️  Execution completed with return code {run_result.returncode}\n"
                )
            
            # Cleanup
            if not keep_binary and not output:
                try:
                    output_path.unlink()
                except Exception:
                    pass
            elif keep_binary:
                result_text += f"\n💾 Binary saved at: {output_path}\n"
            
            return [types.TextContent(type="text", text=result_text)]
            
        except FileNotFoundError:
            return [types.TextContent(
                type="text",
                text=f"❌ Executable not found: {output_path}"
            )]
    
    @app.call_tool()
    async def list_gpus(name: str, arguments: dict[str, Any]) -> list[types.TextContent]:
        """List available GPUs."""
        if name != "list_gpus":
            raise ValueError(f"Unknown tool: {name}")
            
        import subprocess
        
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=index,name", "--format=csv,noheader"],
                capture_output=True,
                text=True,
                check=True,
            )
            
            gpu_list = "Available GPUs:\n"
            for line in result.stdout.strip().split("\n"):
                if line.strip():
                    gpu_list += f"   {line.strip()}\n"
            
            # Add Modal GPU options if available
            if MODAL_AVAILABLE:
                gpu_list += "\nModal Cloud GPUs:\n"
                for gpu in sorted(MODAL_GPUS):
                    arch = get_gpu_architecture(gpu)
                    gpu_list += f"   {gpu} (sm_{arch})\n"
            
            return [types.TextContent(type="text", text=gpu_list)]
            
        except (subprocess.CalledProcessError, FileNotFoundError):
            error_msg = "No GPUs detected. Make sure CUDA drivers are installed.\n"
            
            if MODAL_AVAILABLE:
                error_msg += "\nModal Cloud GPUs available:\n"
                for gpu in sorted(MODAL_GPUS):
                    arch = get_gpu_architecture(gpu)
                    error_msg += f"   {gpu} (sm_{arch})\n"
            
            return [types.TextContent(type="text", text=error_msg)]
    
    @app.call_tool()
    async def get_gpu_architecture(name: str, arguments: dict[str, Any]) -> list[types.TextContent]:
        """Get CUDA architecture for a GPU name."""
        if name != "get_gpu_architecture":
            raise ValueError(f"Unknown tool: {name}")
            
        if "gpu_name" not in arguments:
            return [types.TextContent(
                type="text",
                text="Error: Missing required argument 'gpu_name'"
            )]
        
        gpu_name = arguments["gpu_name"]
        arch = get_gpu_architecture(gpu_name)
        
        response = f"GPU: {gpu_name}\nArchitecture: sm_{arch}\n"
        
        # Add additional info if it's a known GPU
        normalized = gpu_name.strip().upper()
        if normalized in GPU_ARCH_MAP:
            response += f"Supported on Modal: {'Yes' if normalized in MODAL_GPUS else 'No'}\n"
        
        return [types.TextContent(type="text", text=response)]
    
    @app.list_tools()
    async def list_tools() -> list[types.Tool]:
        """List available MCP tools."""
        return [
            types.Tool(
                name="compile_cuda",
                title="Compile and Run CUDA Kernel",
                description="Compile and run a CUDA kernel file on local GPU or Modal cloud infrastructure",
                inputSchema={
                    "type": "object",
                    "required": ["cuda_file"],
                    "properties": {
                        "cuda_file": {
                            "type": "string",
                            "description": "Path to the CUDA source file (.cu)",
                        },
                        "gpu": {
                            "type": "string",
                            "description": "GPU name (e.g., A10G, H100, B200, A100) or architecture (e.g., 100a, 90)",
                            "default": "A10G",
                        },
                        "include_dirs": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Array of include directory paths",
                            "default": [],
                        },
                        "exec_args": {
                            "type": "string",
                            "description": "Arguments to pass to the compiled CUDA executable",
                            "default": "",
                        },
                        "arch": {
                            "type": "string",
                            "description": "Override architecture (e.g., 100a, 90) instead of inferring from GPU",
                            "default": None,
                        },
                        "output": {
                            "type": "string",
                            "description": "Output executable path. If not specified, uses temporary file",
                            "default": None,
                        },
                        "keep_binary": {
                            "type": "boolean",
                            "description": "Keep the compiled binary after execution",
                            "default": False,
                        },
                        "nvcc_flags": {
                            "type": "string",
                            "description": "Additional flags to pass to nvcc (e.g., '-O3 --ptxas-options=-v')",
                            "default": "",
                        }
                    }
                }
            ),
            types.Tool(
                name="list_gpus",
                title="List Available GPUs",
                description="List all available local GPUs and Modal cloud GPU options",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),
            types.Tool(
                name="get_gpu_architecture",
                title="Get GPU Architecture",
                description="Get CUDA architecture for a specific GPU name",
                inputSchema={
                    "type": "object",
                    "required": ["gpu_name"],
                    "properties": {
                        "gpu_name": {
                            "type": "string",
                            "description": "GPU name to lookup (e.g., A10G, H100, B200, A100)"
                        }
                    }
                }
            )
        ]
    
    return app


async def run_stdio_server():
    """Run the MCP server with stdio transport."""
    import mcp.server.stdio
    
    app = create_minimodal_mcp_server()
    async with mcp.server.stdio.stdio_server() as streams:
        await app.run(streams[0], streams[1], app.create_initialization_options())


async def run_sse_server(port: int = 8000):
    """Run the MCP server with SSE transport."""
    import uvicorn
    import mcp.server.sse
    from starlette.applications import Starlette
    from starlette.responses import Response
    from starlette.routing import Mount, Route
    from starlette.requests import Request
    
    app = create_minimodal_mcp_server()
    sse = mcp.server.sse.SseServerTransport("/messages/")
    
    async def handle_sse(request: Request):
        async with sse.connect_sse(request.scope, request.receive, request._send) as streams:
            await app.run(streams[0], streams[1], app.create_initialization_options())
        return Response()
    
    starlette_app = Starlette(
        debug=True,
        routes=[
            Route("/sse", endpoint=handle_sse, methods=["GET"]),
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )
    
    uvicorn.run(starlette_app, host="127.0.0.1", port=port)
