#!/usr/bin/env python3
"""
Recon Wake - MCP Server for Wake Testing Framework

A FastMCP-based server providing:
- Dynamic test evaluation
- Contract discovery and indexing
- Solidity compilation and pytypes generation
- Server status monitoring

Usage:
    uvx recon-wake
    # or
    python3 -m recon_wake
"""

import asyncio
import shutil
import sys
import time
import warnings
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Optional

# Suppress deprecation warnings from third-party libraries
warnings.filterwarnings("ignore", category=DeprecationWarning, module="eth_keys")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="pydantic")
warnings.filterwarnings("ignore", message=".*pkg_resources.*")
warnings.filterwarnings("ignore", message=".*collections.abc.ByteString.*")
warnings.filterwarnings("ignore", message=".*@model_validator.*")

from fastmcp import FastMCP


@dataclass
class TestResult:
    """Result of a test execution"""

    success: bool
    output: str
    error: Optional[str] = None
    execution_time: Optional[float] = None
    gas_used: Optional[int] = None


@dataclass
class ContractInfo:
    """Information about an available contract"""

    name: str
    path: str
    module_path: str
    type: str  # "contract", "interface", "library", "mock"


class WakeTestServer:
    """Production-ready Wake Test Server"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.pytypes_root = project_root / "pytypes"
        self.contracts_cache: Optional[list[ContractInfo]] = None
        self.is_initialized = False
        self.contracts_dir = project_root / "src" / "recon_wake"
        self.package_mocks_dir = Path(__file__).parent / "contracts"

    async def _inject_mocks(self) -> None:
        """Copy injected mock contracts to project src/recon_wake"""
        if not self.package_mocks_dir.exists():
            return
        
        # Create target directory
        self.contracts_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy all .sol files
        for sol_file in self.package_mocks_dir.glob("*.sol"):
            target = self.contracts_dir / sol_file.name
            shutil.copy2(sol_file, target)

    async def _cleanup_mocks(self) -> None:
        """Remove injected mock contracts after compilation"""
        if self.contracts_dir.exists():
            shutil.rmtree(self.contracts_dir)

    async def _cleanup_unwanted_folders(self) -> None:
        """Remove unwanted folders from project root (scripts, tests)"""
        unwanted_dirs = [
            self.project_root / "scripts",
            self.project_root / "tests",
        ]
        for unwanted_dir in unwanted_dirs:
            if unwanted_dir.exists():
                shutil.rmtree(unwanted_dir)

    async def initialize(self) -> dict[str, Any]:
        """
        Initialize the server:
        1. Inject mock contracts
        2. Compile Solidity contracts
        3. Generate pytypes
        4. Index available contracts
        5. Cleanup mocks
        """
        try:
            # Inject mocks
            await self._inject_mocks()
            
            # Compile contracts
            compile_result = await self._compile_contracts()
            if not compile_result["success"]:
                await self._cleanup_mocks()
                return compile_result

            # Check pytypes
            if not self.pytypes_root.exists():
                await self._cleanup_mocks()
                return {
                    "success": False,
                    "error": "Pytypes not found after compilation. Run 'wake up' manually.",
                }

            # Index contracts
            self.contracts_cache = await self._index_contracts()
            self.is_initialized = True
            
            # Cleanup mocks and unwanted folders
            await self._cleanup_mocks()
            await self._cleanup_unwanted_folders()

            return {
                "success": True,
                "contracts_found": len(self.contracts_cache),
                "pytypes_path": str(self.pytypes_root),
            }

        except Exception as e:
            await self._cleanup_mocks()
            return {"success": False, "error": str(e)}

    async def _compile_contracts(self) -> dict[str, Any]:
        """Compile Solidity contracts using wake up"""
        try:
            # Use wake's compilation system
            process = await asyncio.create_subprocess_exec(
                "wake",
                "up",
                cwd=self.project_root,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                return {"success": True, "output": stdout.decode()}
            else:
                return {
                    "success": False,
                    "error": f"Compilation failed: {stderr.decode()}",
                }

        except Exception as e:
            return {"success": False, "error": f"Compilation error: {e!s}"}

    async def _index_contracts(self) -> list[ContractInfo]:
        """Index all available contracts from pytypes"""
        contracts = []

        if not self.pytypes_root.exists():
            return contracts

        # Index all Python files in pytypes
        for py_file in self.pytypes_root.rglob("*.py"):
            if py_file.name == "__init__.py":
                continue

            # Get relative path and module path
            rel_path = py_file.relative_to(self.pytypes_root)
            module_path = str(rel_path.with_suffix("")).replace("/", ".")

            # Determine contract type
            contract_type = "contract"
            name = py_file.stem
            if "Mock" in name or "mock" in str(py_file):
                contract_type = "mock"
            elif name.startswith("I") and name[1].isupper():
                contract_type = "interface"

            contracts.append(
                ContractInfo(
                    name=name, path=str(rel_path), module_path=module_path, type=contract_type
                )
            )

        return sorted(contracts, key=lambda x: x.name)

    async def run_solidity_test(self, code: str) -> TestResult:
        """
        Run Solidity contract tests using Wake testing framework
        
        Execute Python code that deploys and tests Solidity contracts using Wake's
        testing capabilities. All contracts from pytypes are auto-imported.

        Args:
            code: Python code using Wake testing framework (from wake.testing import *)

        Returns:
            TestResult with execution details, stdout/stderr output, and timing
        """
        start_time = time.time()
        
        stdout_capture = StringIO()
        stderr_capture = StringIO()

        try:
            if not self.is_initialized:
                await self.initialize()

            if str(self.pytypes_root.parent) not in sys.path:
                sys.path.insert(0, str(self.pytypes_root.parent))

            namespace = {
                "__name__": "__main__",
            }

            exec("from wake.testing import *", namespace)

            for contract in self.contracts_cache or []:
                try:
                    module_path = f"pytypes.{contract.module_path}"
                    module = __import__(module_path, fromlist=[contract.name])
                    contract_class = getattr(module, contract.name)
                    namespace[contract.name] = contract_class
                except Exception:
                    pass

            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                exec(code, namespace)

            execution_time = time.time() - start_time
            output = stdout_capture.getvalue()
            if stderr_capture.getvalue():
                output += "\n" + stderr_capture.getvalue()

            return TestResult(
                success=True,
                output=output if output else "Test executed successfully",
                execution_time=execution_time,
            )

        except SyntaxError as e:
            return TestResult(
                success=False, output="", error=f"Syntax error: {e!s}", execution_time=0.0
            )
        except Exception as e:
            execution_time = time.time() - start_time
            stderr_output = stderr_capture.getvalue()
            return TestResult(
                success=False,
                output=stderr_output,
                error=f"Execution error: {e!s}",
                execution_time=execution_time,
            )

    async def get_available_contracts(
        self, filter_type: Optional[str] = None, search: Optional[str] = None
    ) -> list[dict[str, Any]]:
        """
        Get list of available contracts

        Args:
            filter_type: Filter by type (contract, mock, interface, library)
            search: Search string for contract names

        Returns:
            List of contract names and types only
        """
        if not self.is_initialized or self.contracts_cache is None:
            await self.initialize()

        contracts = self.contracts_cache or []

        # Apply filters
        if filter_type:
            contracts = [c for c in contracts if c.type == filter_type]

        if search:
            search_lower = search.lower()
            contracts = [
                c for c in contracts if search_lower in c.name.lower() or search_lower in c.path
            ]

        return [{"name": c.name, "type": c.type} for c in contracts]

    async def get_contract_functions(self, contract_name: str) -> Optional[dict[str, Any]]:
        """Get list of functions/methods for a specific contract"""
        if not self.is_initialized or self.contracts_cache is None:
            await self.initialize()

        # Find the contract
        contract_info = None
        for contract in self.contracts_cache or []:
            if contract.name == contract_name:
                contract_info = contract
                break

        if not contract_info:
            return None

        # Ensure pytypes is importable
        if str(self.pytypes_root.parent) not in sys.path:
            sys.path.insert(0, str(self.pytypes_root.parent))

        try:
            # Import the contract class
            module_path = f"pytypes.{contract_info.module_path}"
            module = __import__(module_path, fromlist=[contract_name])
            contract_class = getattr(module, contract_name)

            # Extract functions
            functions = []
            for attr_name in dir(contract_class):
                if attr_name.startswith("_"):
                    continue

                attr = getattr(contract_class, attr_name)
                if callable(attr):
                    # Try to get function signature
                    try:
                        import inspect
                        sig = inspect.signature(attr)
                        functions.append({
                            "name": attr_name,
                            "signature": str(sig),
                            "doc": inspect.getdoc(attr) or ""
                        })
                    except:
                        functions.append({
                            "name": attr_name,
                            "signature": "()",
                            "doc": ""
                        })

            return {
                "contract": contract_name,
                "functions": sorted(functions, key=lambda x: x["name"]),
                "total_functions": len(functions)
            }

        except Exception as e:
            return {"error": f"Failed to load contract: {e!s}"}

    async def compile_contracts(self) -> dict[str, Any]:
        """Compile all Solidity contracts"""
        return await self._compile_contracts()

    async def get_server_status(self) -> dict[str, Any]:
        """Get current server status"""
        return {
            "initialized": self.is_initialized,
            "project_root": str(self.project_root),
            "pytypes_exists": self.pytypes_root.exists(),
            "contracts_indexed": len(self.contracts_cache) if self.contracts_cache else 0,
        }


# Create FastMCP server
mcp = FastMCP("recon-wake")


# Global server instance
_server: Optional[WakeTestServer] = None
_initialization_task: Optional[asyncio.Task] = None


def get_server() -> WakeTestServer:
    """Get or create the global server instance"""
    global _server
    if _server is None:
        project_root = Path.cwd()
        _server = WakeTestServer(project_root)
    return _server


async def ensure_initialized():
    """Ensure server is initialized (idempotent)"""
    global _initialization_task
    server = get_server()
    
    if server.is_initialized:
        return
    
    # If initialization is already in progress, wait for it
    if _initialization_task and not _initialization_task.done():
        await _initialization_task
        return
    
    # Start initialization
    _initialization_task = asyncio.create_task(server.initialize())
    await _initialization_task


@mcp.tool()
async def run_solidity_test(code: str, timeout: int = 60) -> dict[str, Any]:
    """
    Run Solidity contract tests using Wake testing framework
    
    IMPORTANT: This executes Python code that deploys and tests Solidity smart contracts
    using the Wake testing framework. All compiled contracts are automatically imported
    and available in the namespace (ReconERC20Mock, Auth, SizeMetaVault, etc.).
    
    Use @chain.connect() decorator and deploy contracts with .deploy(), call functions,
    make assertions, and print results. All stdout/stderr is captured and returned.

    Args:
        code: Python test code using Wake framework (from wake.testing import *)
        timeout: Timeout in seconds (default: 60)

    Returns:
        Test execution result with success status, output, and timing
        
    Example:
        ```python
        from wake.testing import *
        
        @chain.connect()
        def test_example():
            deployer = chain.accounts[0]
            token = ReconERC20Mock.deploy("Token", "TKN", from_=deployer)
            print(f"Deployed at: {token.address}")
        
        test_example()
        ```
    """
    server = get_server()
    await ensure_initialized()

    result = await server.run_solidity_test(code)
    return asdict(result)


@mcp.tool()
async def get_contracts(filter_type: str = None, search: str = None) -> list[dict[str, Any]]:
    """
    Get list of available contracts from pytypes

    Args:
        filter_type: Filter by type (contract, mock, interface, library)
        search: Search string for contract names

    Returns:
        List of contracts with name and type only (contracts are auto-imported in eval)
    """
    server = get_server()
    await ensure_initialized()

    return await server.get_available_contracts(filter_type, search)


@mcp.tool()
async def get_contract_functions(contract_name: str) -> dict[str, Any]:
    """
    Get list of functions/methods available in a contract

    Args:
        contract_name: Name of the contract

    Returns:
        List of functions with signatures and documentation
    """
    server = get_server()
    await ensure_initialized()

    result = await server.get_contract_functions(contract_name)
    if result is None:
        return {"error": f"Contract '{contract_name}' not found"}
    return result


@mcp.tool()
async def compile() -> dict[str, Any]:
    """
    Compile Solidity contracts and regenerate pytypes

    Returns:
        Compilation result with success status and output
    """
    server = get_server()
    result = await server.compile_contracts()

    # Re-index after compilation
    if result["success"]:
        server.contracts_cache = await server._index_contracts()
        server.is_initialized = True

    return result


@mcp.tool()
async def server_status() -> dict[str, Any]:
    """
    Get current server status and configuration

    Returns:
        Server status including initialization state and indexed contracts
    """
    server = get_server()
    return await server.get_server_status()


def main():
    """Main entry point for the MCP server"""
    # Initialize on startup
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(ensure_initialized())
    
    # Run the FastMCP server
    mcp.run()


if __name__ == "__main__":
    main()
