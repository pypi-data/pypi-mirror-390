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
import glob
import json
import os
import re
import shutil
import subprocess
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


class CertoraVerifier:
    """Certora formal verification integration"""

    def __init__(self, project_root: Path):
        self.project_root = project_root

    def _format_value(self, value):
        """Convert hex to decimal."""
        if isinstance(value, str) and value.startswith('0x'):
            try:
                return int(value, 16)
            except:
                return value
        return value

    def _parse_state_changes(self, ctpp_content: str) -> list[dict[str, Any]]:
        """Parse Store operations to extract state changes."""
        state_changes = []
        lines = ctpp_content.split('\n')
        
        for i, line in enumerate(lines):
            # Look for Store operations (state changes)
            store_match = re.search(r'\[Store,.*?\]\s+Store at\s+(\w+)\.(\w+)(?:\[([^\]]+)\])?\s+↪\s+(.+)', line)
            if store_match:
                contract = store_match.group(1)
                variable = store_match.group(2)
                key = store_match.group(3) if store_match.group(3) else None
                new_value = store_match.group(4).strip()
                
                # Try to find the previous value (Load before this Store)
                old_value = None
                for j in range(max(0, i-10), i):
                    if key:
                        load_match = re.search(rf'\[Load,.*?\]\s+Load from\s+{contract}\.{variable}\[{re.escape(key)}\]\s+↪\s+(.+)', lines[j])
                    else:
                        load_match = re.search(rf'\[Load,.*?\]\s+Load from\s+{contract}\.{variable}\s+↪\s+(.+)', lines[j])
                    
                    if load_match:
                        old_value = load_match.group(1).strip()
                        break
                
                change = {
                    'contract': contract,
                    'variable': variable,
                    'old_value': old_value,
                    'new_value': new_value
                }
                
                if key:
                    change['key'] = key
                
                state_changes.append(change)
        
        return state_changes

    def _parse_ctpp_file(self, ctpp_path: str) -> dict[str, Any]:
        """Parse ctpp file to extract call traces, variables, return values, and environment context."""
        try:
            with open(ctpp_path, 'r') as f:
                content = f.read()
            
            result = {
                'call_trace': [],
                'call_trace_with_inputs': [],
                'call_trace_with_env': [],  # NEW: CVL-level calls with environments
                'variables': {},
                'calldata_mapping': {},
                'state_changes': [],
                'return_values': {},  # NEW: Function return values
                'initial_state': {},  # NEW: Initial/havoc state
                'full_assertion': ''  # NEW: Full assertion text
            }
            
            # Parse state changes
            result['state_changes'] = self._parse_state_changes(content)
            
            # Parse CVL-level calls with environments (LabelInstance)
            lines = content.split('\n')
            for i, line in enumerate(lines):
                # Look for LabelInstance lines that show CVL-level calls
                label_match = re.search(r'\[LabelInstance,.*?\]\s+(.+)', line)
                if label_match:
                    label_text = label_match.group(1).strip()
                    
                    # Extract full assertion text
                    if label_text.startswith('assert '):
                        result['full_assertion'] = label_text
                    
                    # Extract CVL-level function calls (e.g., "Counter.deposit(e1, amount1)")
                    if re.search(r'\w+\.\w+\([^)]*\)', label_text) and not label_text.startswith('require '):
                        # Check if next line is External/Internal call
                        if i + 1 < len(lines) and ('[External,' in lines[i+1] or '[Internal,' in lines[i+1]):
                            result['call_trace_with_env'].append(label_text)
                            
                            # Look for return value (Load after Return)
                            for j in range(i+1, min(i+20, len(lines))):
                                return_match = re.search(r'\[Return,.*?\] Return', lines[j])
                                if return_match:
                                    # Check next few lines for Load that shows return value
                                    for k in range(j-5, j):
                                        if k >= 0:
                                            load_match = re.search(r'\[Load,.*?\].*?↪\s+(.+)', lines[k])
                                            if load_match:
                                                return_val = load_match.group(1).strip()
                                                result['return_values'][label_text] = return_val
                                                break
                                    break
                                elif '[External,' in lines[j] or '[Internal,' in lines[j]:
                                    break
                
                # Look for initial state (HAVOC status)
                havoc_match = re.search(r'status.*HAVOC', line, re.IGNORECASE)
                if havoc_match and i > 0:
                    # Look back for the storage variable
                    for k in range(max(0, i-5), i):
                        state_match = re.search(r'\[StorageStateValueInstance,.*?\]\s+(.+?):\s+(.+)', lines[k])
                        if state_match:
                            var_name = state_match.group(1).strip()
                            value = state_match.group(2).strip()
                            if '(changed)' not in value:
                                result['initial_state'][var_name] = value + ' (havoced)'
                            break
            
            lines = content.split('\n')
            in_cvl_model = False
            current_canon_var = None
            current_var_info = {}
            
            # First pass: extract calldata buffer mappings
            for line in lines:
                calldata_match = re.search(r'tacCalldatabufCANON1@(\d+):bv256\s+-->\s+(.+)', line)
                if calldata_match:
                    arg_index = int(calldata_match.group(1))
                    value = calldata_match.group(2).strip()
                    result['calldata_mapping'][arg_index] = value
            
            # Second pass: extract variables and call traces
            for i, line in enumerate(lines):
                if '-------- CVL model begin ------------' in line:
                    in_cvl_model = True
                    continue
                elif '-------- CVL model end --------------' in line:
                    in_cvl_model = False
                    if current_canon_var and current_var_info:
                        if 'display' in current_var_info and 'value' in current_var_info:
                            result['variables'][current_var_info['display']] = current_var_info['value']
                    continue
                
                if in_cvl_model:
                    if '~~>' in line and 'cvl' not in line:
                        if current_canon_var and current_var_info:
                            if 'display' in current_var_info and 'value' in current_var_info:
                                result['variables'][current_var_info['display']] = current_var_info['value']
                        
                        match = re.search(r'(CANON\S+)\s+~~>\s+(.+)', line)
                        if match:
                            current_canon_var = match.group(1).strip()
                            value = match.group(2).strip()
                            current_var_info = {'value': value}
                    
                    elif 'cvl.display' in line:
                        match = re.search(r'cvl\.display\s+:\s+(.+)', line)
                        if match:
                            display_name = match.group(1).strip()
                            current_var_info['display'] = display_name
                
                # Extract function calls with arguments
                if ('[External,' in line or '[Internal,' in line) and ')' in line:
                    result['call_trace'].append(line.strip())
                    
                    func_match = re.search(r'\]\s+(\w+)\.(\w+)\(', line)
                    if func_match:
                        contract = func_match.group(1)
                        func_name = func_match.group(2)
                        
                        call_info = {
                            'contract': contract,
                            'function': func_name,
                            'arguments': []
                        }
                        
                        # Check next few lines for call data movement
                        for j in range(i+1, min(i+5, len(lines))):
                            if 'call data movement' in lines[j]:
                                calldata_ref_match = re.search(r'tacCalldatabufCANON1@(\d+):bv256', lines[j])
                                if calldata_ref_match:
                                    arg_index = int(calldata_ref_match.group(1))
                                    if arg_index in result['calldata_mapping']:
                                        arg_value = result['calldata_mapping'][arg_index]
                                    else:
                                        arg_value = None
                                        for search_line in lines:
                                            search_match = re.search(rf'tacCalldatabufCANON1@{arg_index}:bv256\s+-->\s+(.+)', search_line)
                                            if search_match:
                                                arg_value = search_match.group(1).strip()
                                                result['calldata_mapping'][arg_index] = arg_value
                                                break
                                    
                                    if arg_value:
                                        var_name = None
                                        for cvl_var, cvl_val in result['variables'].items():
                                            if str(cvl_val).strip() == str(arg_value).strip():
                                                var_name = cvl_var
                                                break
                                        
                                        call_info['arguments'].append({
                                            'index': arg_index,
                                            'value': arg_value,
                                            'variable': var_name if var_name else f'arg{arg_index}'
                                        })
                                break
                            elif '[External,' in lines[j] or '[Internal,' in lines[j]:
                                break
                        
                        result['call_trace_with_inputs'].append(call_info)
            
            return result
        except Exception:
            return None

    def _parse_archive(self, archive_dir: str) -> dict[str, Any]:
        """Parse the complete extracted job archive and return structured results."""
        result = {
            'rules': [],
            'summary': {}
        }
        
        # Cloud archives have an extra TarName directory level
        # Check if TarName directory exists
        base_dir = archive_dir
        if os.path.exists(f"{archive_dir}/TarName"):
            base_dir = f"{archive_dir}/TarName"
        
        # Parse output.json for rule statuses
        output_json_path = f"{base_dir}/Reports/output.json"
        try:
            with open(output_json_path, 'r') as f:
                data = json.load(f)
                rule_statuses = data.get('rules', {})
                result['summary']['rule_statuses'] = rule_statuses
        except:
            rule_statuses = {}
        
        # Parse rule_output JSON files for detailed error messages
        rule_outputs = {}
        treeview_dir = f"{base_dir}/Reports/treeView"
        if os.path.exists(treeview_dir):
            for filename in os.listdir(treeview_dir):
                if filename.startswith('rule_output_') and filename.endswith('.json'):
                    try:
                        with open(f"{treeview_dir}/{filename}", 'r') as f:
                            rule_data = json.load(f)
                            # Extract rule name from treeViewPath (format: "ruleName-assertion message")
                            tree_path = rule_data.get('treeViewPath', '')
                            if '-' in tree_path:
                                rule_name = tree_path.split('-', 1)[0]
                                rule_outputs[rule_name] = rule_data
                    except:
                        pass
        
        # Parse ctpp files for counterexamples
        ctpp_dir = f"{base_dir}/Reports"
        
        for rule_name, status in rule_statuses.items():
            rule_data = {
                'name': rule_name,
                'status': status,
                'violated': status == 'FAIL',
                'details': {}
            }
            
            # Add detailed error information from rule_output JSON
            if rule_name in rule_outputs:
                output_data = rule_outputs[rule_name]
                rule_data['details']['assert_message'] = output_data.get('assertMessage', '')
                rule_data['details']['jump_to_definition'] = output_data.get('jumpToDefinition', {})
            
            # Add ctpp details if available
            ctpp_file = f"{ctpp_dir}/ctpp_{rule_name}.txt"
            if os.path.exists(ctpp_file):
                ctpp_data = self._parse_ctpp_file(ctpp_file)
                if ctpp_data:
                    rule_data['details']['call_trace'] = ctpp_data.get('call_trace', [])
                    rule_data['details']['call_trace_with_inputs'] = ctpp_data.get('call_trace_with_inputs', [])
                    rule_data['details']['call_trace_with_env'] = ctpp_data.get('call_trace_with_env', [])
                    rule_data['details']['variables'] = ctpp_data.get('variables', {})
                    rule_data['details']['state_changes'] = ctpp_data.get('state_changes', [])
                    rule_data['details']['return_values'] = ctpp_data.get('return_values', {})
                    rule_data['details']['initial_state'] = ctpp_data.get('initial_state', {})
                    # Override truncated assertion with full version if available
                    full_assertion = ctpp_data.get('full_assertion', '')
                    if full_assertion and full_assertion.startswith('assert '):
                        rule_data['details']['assert_message'] = full_assertion.replace('assert ', '')
            
            result['rules'].append(rule_data)
        
        # Add summary statistics
        result['summary']['total_rules'] = len(result['rules'])
        result['summary']['passed'] = sum(1 for r in result['rules'] if not r['violated'])
        result['summary']['failed'] = sum(1 for r in result['rules'] if r['violated'])
        
        return result

    def _generate_clean_output(self, data: dict[str, Any]) -> dict[str, Any]:
        """Convert summary data to clean MCP-friendly format."""
        output = {
            'status': 'success',
            'summary': data.get('summary', {}),
            'rules': []
        }
        
        for rule in data.get('rules', []):
            rule_output = {
                'name': rule['name'],
                'status': rule['status'],
                'violated': rule.get('violated', False)
            }
            
            if rule['violated'] and 'details' in rule:
                details = rule['details']
                
                # CRITICAL FOR LLM: Add assertion message (why it failed)
                assert_message = details.get('assert_message', '')
                
                # Extract variables
                variables = {}
                for k, v in details.get('variables', {}).items():
                    if not k.startswith('e.') and not k.startswith('CANON'):
                        variables[k] = {
                            'value': v,
                            'decimal': self._format_value(v)
                        }
                
                # PRIORITY: Use CVL-level calls with environments if available
                call_trace_with_env = details.get('call_trace_with_env', [])
                return_values = details.get('return_values', {})
                
                if call_trace_with_env:
                    # Use enhanced trace with environments and return values
                    call_trace = []
                    for cvl_call in call_trace_with_env:
                        # cvl_call is like "Counter.deposit(e1, amount1)" or "balance1 = Counter.balances(user1)"
                        call_str = cvl_call
                        
                        # Add return value if available
                        if cvl_call in return_values:
                            ret_val = return_values[cvl_call]
                            try:
                                ret_dec = self._format_value(ret_val)
                                call_str += f" => {ret_dec}"
                            except:
                                call_str += f" => {ret_val}"
                        
                        # Extract environment details if present (e.g., "e1", "e2")
                        env_match = re.search(r'\(([^,)]+),', cvl_call)
                        if env_match:
                            env_name = env_match.group(1).strip()
                            # Find env.msg.sender in variables
                            sender_key = f"{env_name}.msg.sender"
                            if sender_key in details.get('variables', {}):
                                sender_val = details['variables'][sender_key]
                                try:
                                    sender_dec = self._format_value(sender_val)
                                    call_str += f" [msg.sender={sender_dec}]"
                                except:
                                    pass
                        
                        call_trace.append(call_str)
                else:
                    # Fallback to old method if CVL trace not available
                    call_trace = []
                    call_trace_data = details.get('call_trace_with_inputs', [])
                    
                    for call in call_trace_data:
                        call_str = f"{call['contract']}.{call['function']}"
                        
                        if call.get('arguments'):
                            args = []
                            for arg in call['arguments']:
                                value_hex = arg['value']
                                value_dec = self._format_value(value_hex)
                                
                                # Find variable name
                                var_name = None
                                for k, v in details.get('variables', {}).items():
                                    if v == value_hex and not k.startswith('e.') and not k.startswith('CANON'):
                                        var_name = k
                                        break
                                
                                if var_name:
                                    args.append(f"{var_name}={value_dec}")
                                else:
                                    args.append(str(value_dec))
                            
                            call_str += f"({', '.join(args)})"
                        else:
                            call_str += "()"
                        
                        call_trace.append(call_str)
                
                counterexample = {
                    'variables': variables,
                    'execution_trace': call_trace
                }
                
                # CRITICAL FOR LLM: Add assertion message and location
                if assert_message:
                    counterexample['assertion_failed'] = assert_message
                
                jump_def = details.get('jump_to_definition', {})
                if jump_def:
                    counterexample['rule_location'] = {
                        'file': jump_def.get('file', ''),
                        'line_start': jump_def.get('start', {}).get('line', 0),
                        'line_end': jump_def.get('end', {}).get('line', 0)
                    }
                
                # CRITICAL FOR LLM: Add initial state (HAVOC/symbolic values)
                initial_state = details.get('initial_state', {})
                if initial_state:
                    formatted_initial = []
                    for storage_key, status in initial_state.items():
                        if status == 'HAVOC':
                            formatted_initial.append(f"{storage_key}: havoc (symbolic)")
                    
                    if formatted_initial:
                        counterexample['initial_state'] = formatted_initial
                
                # CRITICAL FOR LLM: Add state changes (before/after values)
                state_changes = details.get('state_changes', [])
                if state_changes:
                    formatted_changes = []
                    for change in state_changes:
                        change_str = f"{change['contract']}.{change['variable']}"
                        if 'key' in change:
                            change_str += f"[{change['key']}]"
                        
                        old_val = change.get('old_value', 'unknown')
                        new_val = change.get('new_value', 'unknown')
                        
                        # Try to format values as decimals
                        try:
                            old_dec = self._format_value(old_val)
                            new_dec = self._format_value(new_val)
                            change_str += f": {old_dec} => {new_dec}"
                        except:
                            change_str += f": {old_val} => {new_val}"
                        
                        formatted_changes.append(change_str)
                    
                    counterexample['state_changes'] = formatted_changes
                
                rule_output['counterexample'] = counterexample
            
            output['rules'].append(rule_output)
        
        return output

    async def verify_contract(
        self, 
        cvl_spec: str, 
        contract_file: str, 
        contract_name: str
    ) -> dict[str, Any]:
        """
        Run Certora formal verification on a contract with CVL specification.
        
        Args:
            cvl_spec: CVL specification text
            contract_file: Path to Solidity contract file
            contract_name: Name of the contract to verify
            
        Returns:
            Verification results with counterexamples if violations found
        """
        start_time = time.time()
        
        # Create temporary CVL file
        temp_cvl = self.project_root / f".certora_temp_{int(time.time())}.spec"
        try:
            with open(temp_cvl, 'w') as f:
                f.write(cvl_spec)
            
            # Run certoraRun (using subprocess.run for simpler handling)
            cmd = [
                'certoraRun',
                contract_file,
                '--verify', f'{contract_name}:{temp_cvl}',
                '--wait_for_results', 'all'
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=self.project_root,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            output = stdout.decode() + stderr.decode()
            
            # Check for compilation or CVL errors
            if 'Error in spec file' in output or 'Error: Compilation failed' in output:
                error_lines = []
                for line in output.split('\n'):
                    if 'Error' in line or 'error' in line:
                        error_lines.append(line.strip())
                
                return {
                    'status': 'error',
                    'message': 'CVL or compilation error',
                    'details': '\n'.join(error_lines[:10]) if error_lines else 'Unknown error'
                }
            
            # First, try to find local emv archive directory
            emv_dirs = glob.glob(str(self.project_root / 'emv-*-certora-*'))
            if emv_dirs:
                # Filter by creation time and get the most recent
                emv_dirs = [d for d in emv_dirs if os.path.isdir(d) and os.path.getmtime(d) >= start_time]
                if emv_dirs:
                    archive_dir = sorted(emv_dirs, key=lambda x: os.path.getmtime(x), reverse=True)[0]
                    
                    # Parse the archive directly
                    data = self._parse_archive(archive_dir)
                    
                    # Generate clean output
                    result = self._generate_clean_output(data)
                    result['execution_time'] = time.time() - start_time
                    return result
            
            # If no local archive, check for cloud run URL
            result_url_match = re.search(r'report url:\s*(https://prover\.certora\.com/output/([^/]+)/([^/?]+)(\?anonymousKey=([^\s]+))?)', output)
            if result_url_match:
                full_url = result_url_match.group(1)
                job_id = result_url_match.group(3)
                anon_key = result_url_match.group(5)
                
                # Download and extract the cloud archive
                archive_url = f"https://prover.certora.com/v1/domain/jobs/{job_id}/f/outputs"
                if anon_key:
                    archive_url += f"?anonymousKey={anon_key}"
                
                timestamp = int(time.time())
                archive_file = self.project_root / f".certora_job_{timestamp}.tar.gz"
                extract_dir = self.project_root / f".certora_job_{timestamp}"
                
                try:
                    # Download the archive
                    download_result = subprocess.run(
                        ['curl', '-fsS', '-L', '--retry', '2', '--max-time', '60', '-o', str(archive_file), archive_url],
                        capture_output=True,
                        text=True,
                        cwd=self.project_root
                    )
                    
                    if download_result.returncode == 0 and os.path.exists(str(archive_file)):
                        # Extract the archive
                        os.makedirs(str(extract_dir), exist_ok=True)
                        extract_result = subprocess.run(
                            ['tar', '-xzf', str(archive_file), '-C', str(extract_dir)],
                            capture_output=True,
                            text=True
                        )
                        
                        if extract_result.returncode == 0:
                            # Parse the extracted archive
                            data = self._parse_archive(str(extract_dir))
                            
                            # Generate clean output
                            result = self._generate_clean_output(data)
                            result['execution_time'] = time.time() - start_time
                            result['report_url'] = result_url_match.group(0)
                            
                            # Cleanup archive file
                            if os.path.exists(str(archive_file)):
                                os.unlink(str(archive_file))
                            
                            return result
                        else:
                            return {
                                'status': 'error',
                                'message': 'Failed to extract cloud archive',
                                'details': extract_result.stderr,
                                'report_url': result_url_match.group(0)
                            }
                    else:
                        return {
                            'status': 'error',
                            'message': 'Failed to download cloud archive',
                            'details': download_result.stderr if download_result.returncode != 0 else 'Archive file not found after download',
                            'report_url': result_url_match.group(0)
                        }
                        
                except Exception as e:
                    # Cleanup on error
                    if os.path.exists(str(archive_file)):
                        os.unlink(str(archive_file))
                    return {
                        'status': 'error',
                        'message': f'Failed to download/extract cloud archive: {e}',
                        'report_url': result_url_match.group(0) if result_url_match else None
                    }
            
            return {
                'status': 'error',
                'message': 'No verification archive found',
                'output': output[-1000:] if len(output) > 1000 else output
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
        finally:
            # Cleanup temp file
            if temp_cvl.exists():
                temp_cvl.unlink()


class WakeTestServer:
    """Production-ready Wake Test Server"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.pytypes_root = project_root / "pytypes"
        self.contracts_cache: Optional[list[ContractInfo]] = None
        self.is_initialized = False
        self.contracts_dir = project_root / "src" / "recon_wake"
        self.package_mocks_dir = Path(__file__).parent / "contracts"
        self.certora = CertoraVerifier(project_root)

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


@mcp.tool()
async def certora_verify(
    cvl_spec: str,
    contract_file: str,
    contract_name: str
) -> dict[str, Any]:
    """
    Run Certora formal verification on a Solidity contract
    
    Verifies smart contract properties using CVL (Certora Verification Language).
    Returns detailed counterexamples with execution traces if violations are found.
    
    Args:
        cvl_spec: CVL specification defining properties to verify (methods, rules, invariants)
        contract_file: Path to the Solidity contract file (e.g., "src/Counter.sol")
        contract_name: Name of the contract to verify (e.g., "Counter")
    
    Returns:
        Verification results with:
        - status: "success" or "error"
        - summary: Statistics about verified/violated rules
        - rules: List of rules with their status
        - counterexample: Execution trace and variable values for violated rules
        - execution_time: Time taken for verification
    
    Example CVL:
        ```
        methods {
            function deposit(uint256) external;
            function withdraw(uint256) external;
            function totalDeposits() external returns (uint256) envfree;
        }
        
        rule depositIncreasesTotal(uint256 amount) {
            uint256 before = totalDeposits();
            env e;
            deposit(e, amount);
            uint256 after = totalDeposits();
            assert after == before + amount;
        }
        ```
    """
    server = get_server()
    result = await server.certora.verify_contract(cvl_spec, contract_file, contract_name)
    return result


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
