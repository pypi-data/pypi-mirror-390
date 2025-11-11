#!/usr/bin/env python3
"""
SpiralLogic Runtime Engine
AI-native programming language for ethical interaction systems

Usage:
    from spirallogic_runtime import SpiralLogic
    
    sl = SpiralLogic()
    result = sl.execute(ritual_program_string)
"""

import json
import time
import hashlib
import traceback
from datetime import datetime
from dataclasses import dataclass, asdict
from types import SimpleNamespace
from typing import Dict, List, Optional, Any, Callable
import builtins
import threading
import uuid
import sqlite3
import os

@dataclass
class ConsentRequest:
    """Consent request structure"""
    scopes: List[str]
    message: str
    timeout_ms: int = 30000
    request_id: str = None
    
    def __post_init__(self):
        if not self.request_id:
            self.request_id = str(uuid.uuid4())

@dataclass
class RitualContext:
    """Execution context for a ritual"""
    ritual_id: str
    intent: str
    voice: str
    phase: str
    user_id: str
    session_id: str
    consent_granted: Dict[str, bool]
    memory_store: Dict[str, Any]
    artifacts: Dict[str, Any]
    crisis_active: bool = False
    
class ConsentManager:
    """Manages consent requests and permissions"""
    
    def __init__(self, consent_callback: Optional[Callable] = None):
        self.granted_scopes = set()
        self.consent_callback = consent_callback or self._default_consent_callback
        self.pending_requests = {}
        
    def _default_consent_callback(self, request: ConsentRequest) -> bool:
        """Default consent handler - always grant for testing"""
        print(f"CONSENT REQUEST: {request.message}")
        print(f"Scopes: {', '.join(request.scopes)}")
        response = input("Grant consent? (y/n): ").lower().strip()
        return response in ['y', 'yes']
    
    def request(self, scopes: List[str], message: str, timeout_ms: int = 30000) -> bool:
        """Request consent for specified scopes"""
        request = ConsentRequest(scopes, message, timeout_ms)
        
        try:
            granted = self.consent_callback(request)
            if granted:
                self.granted_scopes.update(scopes)
                return True
            return False
        except Exception as e:
            print(f"Consent error: {e}")
            return False
    
    def check(self, scope: str) -> bool:
        """Check if consent is granted for scope"""
        return scope in self.granted_scopes
    
    def revoke(self, scopes: List[str]):
        """Revoke consent for scopes"""
        for scope in scopes:
            self.granted_scopes.discard(scope)

class MemoryVault:
    """Chronicle Split memory management"""
    
    def __init__(self, db_path: str = "spirallogic_memory.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize memory database"""
        os.makedirs(os.path.dirname(self.db_path) if os.path.dirname(self.db_path) else ".", exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            # User narrative storage (encrypted)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS narrative_memory (
                    id TEXT PRIMARY KEY,
                    timestamp REAL,
                    data TEXT,
                    tags TEXT,
                    encrypted BOOLEAN DEFAULT 1
                )
            """)
            
            # System artifacts (technical logs)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS artifact_memory (
                    id TEXT PRIMARY KEY,
                    timestamp REAL,
                    data TEXT,
                    type TEXT,
                    ritual_id TEXT
                )
            """)
    
    def store_narrative(self, data: str, tags: List[str] = None) -> str:
        """Store user narrative data"""
        memory_id = str(uuid.uuid4())
        tags_json = json.dumps(tags or [])
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO narrative_memory (id, timestamp, data, tags)
                VALUES (?, ?, ?, ?)
            """, (memory_id, time.time(), data, tags_json))
        
        return memory_id
    
    def store_artifact(self, data: Any, artifact_type: str, ritual_id: str) -> str:
        """Store system artifact"""
        artifact_id = str(uuid.uuid4())
        data_json = json.dumps(data) if not isinstance(data, str) else data
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO artifact_memory (id, timestamp, data, type, ritual_id)
                VALUES (?, ?, ?, ?, ?)
            """, (artifact_id, time.time(), data_json, artifact_type, ritual_id))
        
        return artifact_id
    
    def recall_narrative(self, query: str, max_results: int = 5) -> List[Dict]:
        """Recall narrative memories"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT id, timestamp, data, tags FROM narrative_memory
                WHERE data LIKE ? OR tags LIKE ?
                ORDER BY timestamp DESC LIMIT ?
            """, (f"%{query}%", f"%{query}%", max_results))
            
            return [{"id": row[0], "timestamp": row[1], "data": row[2], "tags": json.loads(row[3])} 
                    for row in cursor.fetchall()]
    
    def release(self, memory_type: str, query: str) -> int:
        """Release/delete memories"""
        table = "narrative_memory" if memory_type == "narrative" else "artifact_memory"
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(f"""
                DELETE FROM {table} WHERE data LIKE ?
            """, (f"%{query}%",))
            return cursor.rowcount

class CrisisMonitor:
    """Crisis detection and response system"""
    
    def __init__(self):
        self.crisis_keywords = [
            "overwhelmed", "can't handle", "too much", "give up",
            "hurt myself", "end it all", "no point", "worthless",
            "suicide", "kill myself", "want to die"
        ]
        self.active = False
        self.crisis_callbacks = []
    
    def detect(self, text: str) -> bool:
        """Detect crisis indicators in text"""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.crisis_keywords)
    
    def trigger_response(self, context: RitualContext, trigger_text: str) -> Dict[str, Any]:
        """Trigger crisis response"""
        self.active = True
        context.crisis_active = True
        
        response = {
            "mode": "anchor_mode",
            "message": "I notice you might be feeling overwhelmed right now. You're safe here. Let's take a breath together.",
            "actions": ["pause_ritual", "activate_witness_voice", "offer_resources"],
            "timestamp": datetime.now().isoformat(),
            "trigger": trigger_text
        }
        
        # Call registered crisis callbacks
        for callback in self.crisis_callbacks:
            try:
                callback(context, response)
            except Exception as e:
                print(f"Crisis callback error: {e}")
        
        return response

class AttestationLogger:
    """Cryptographic logging of all operations"""
    
    def __init__(self, log_path: str = "spirallogic_attestations.log"):
        self.log_path = log_path
        self.chain_hash = "GENESIS"
    
    def log(self, event: str, data: Dict[str, Any], ritual_id: str):
        """Log event with cryptographic attestation"""
        entry = {
            "timestamp": time.time(),
            "event": event,
            "ritual_id": ritual_id,
            "data": data,
            "previous_hash": self.chain_hash
        }
        
        # Create hash for chain integrity
        hash_input = json.dumps(entry, sort_keys=True)
        entry_hash = hashlib.sha256(hash_input.encode()).hexdigest()
        entry["hash"] = entry_hash
        self.chain_hash = entry_hash
        
        # Write to log file
        os.makedirs(os.path.dirname(self.log_path) if os.path.dirname(self.log_path) else ".", exist_ok=True)
        with open(self.log_path, "a") as f:
            f.write(json.dumps(entry) + "\n")

class SpiralLogicParser:
    """Parser for SpiralLogic ritual syntax"""
    
    def __init__(self):
        # Import the new parser
        try:
            from .spirallogic_parser_v2 import SpiralLogicParser as V2Parser, convert_to_runtime_format
            self.v2_parser = V2Parser()
            self.convert_to_runtime = convert_to_runtime_format
            self.v2_available = True
        except ImportError:
            self.v2_available = False
    
    def parse_ritual(self, ritual_code: str) -> Dict[str, Any]:
        """Parse SpiralLogic ritual into executable structure"""
        try:
            # Try V2 parser first (real Spirologic syntax)
            if self.v2_available and not ritual_code.strip().startswith('{'):
                result = self.v2_parser.parse(ritual_code)
                if result['success']:
                    return self.convert_to_runtime(result)
                else:
                    print(f"V2 Parser failed: {result.get('error')}")
                    # Fall back to JSON
            
            # Fallback to JSON parsing
            if ritual_code.strip().startswith('{'):
                return json.loads(ritual_code)
            
            # Legacy simple parsing for demonstration
            ritual = {
                "intent": self._extract_value(ritual_code, "intent"),
                "voice": self._extract_value(ritual_code, "voice"),
                "phase": self._extract_value(ritual_code, "phase", "active"),
                "steps": self._parse_steps(ritual_code)
            }
            
            return ritual
        except Exception as e:
            raise SyntaxError(f"Failed to parse ritual: {e}")
    
    def _extract_value(self, code: str, key: str, default: str = None) -> str:
        """Extract value for key from ritual code"""
        lines = code.split('\n')
        for line in lines:
            if f"{key}:" in line:
                return line.split(':', 1)[1].strip().strip('"\'')
        return default
    
    def _parse_steps(self, code: str) -> List[Dict[str, Any]]:
        """Parse ritual steps"""
        # Simplified step parsing
        steps = []
        
        if "consent.request" in code:
            steps.append({
                "type": "consent.request",
                "scopes": ["memory"],  # Default scope
                "message": "I need to store this conversation"
            })
        
        if "voice.speak" in code:
            steps.append({
                "type": "voice.speak",
                "message": "How can I help you today?",
                "wait_for_response": True
            })
        
        if "memory.store" in code:
            steps.append({
                "type": "memory.store",
                "type_": "narrative",
                "data": "user_input"
            })
        
        return steps


class PythonExecutionSandbox:
    """Minimal sandbox for executing consent-wrapped Python blocks."""

    SAFE_BUILTINS = [
        'abs', 'all', 'any', 'bool', 'dict', 'enumerate', 'float', 'int',
        'len', 'list', 'map', 'max', 'min', 'pow', 'range', 'round',
        'set', 'sorted', 'str', 'sum', 'tuple', 'zip', 'print',
        'Exception', '__import__'
    ]

    def __init__(self) -> None:
        self.safe_builtins = {
            name: getattr(builtins, name)
            for name in self.SAFE_BUILTINS
            if hasattr(builtins, name)
        }

    def create_environment(
        self,
        *,
        runtime: Optional['SpiralLogic'] = None,
        context: Optional[RitualContext] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        env_globals: Dict[str, Any] = {
            '__builtins__': dict(self.safe_builtins),
            'metadata': metadata or {},
            'ritual_context': context,
            'json': json,
            'time': time,
            'datetime': datetime,
            'uuid': uuid,
            'hashlib': hashlib,
            'SimpleNamespace': SimpleNamespace,
        }

        try:
            import requests  # type: ignore
            env_globals['requests'] = requests
        except ImportError:
            pass

        try:
            import sqlite3 as sqlite_module  # type: ignore
            env_globals['sqlite3'] = sqlite_module
        except ImportError:
            pass

        if runtime is not None:
            env_globals['runtime'] = runtime

        return env_globals

    def execute_block(
        self,
        code: str,
        env_globals: Dict[str, Any],
        env_locals: Dict[str, Any],
        *,
        block_name: str = 'execute',
    ) -> None:
        if not code or not code.strip():
            return
        compiled = compile(code, f'<spirallogic:{block_name}>', 'exec')
        exec(compiled, env_globals, env_locals)  # nosec B102


class ExecutionBridge:
    """Helper exposed inside consent-wrapped execution blocks."""

    def __init__(self, runtime: 'SpiralLogic', context: RitualContext, metadata: Dict[str, Any]):
        self._runtime = runtime
        self._context = context
        self.metadata = metadata

    @property
    def consent(self) -> Dict[str, bool]:
        return self._context.consent_granted

    def require_scope(self, scope: str, message: Optional[str] = None) -> bool:
        return self._runtime._ensure_scopes([scope], message or f'Requires scope: {scope}', self._context)

    def remember(self, data: Any, memory_type: str = 'narrative', tags: Optional[List[str]] = None) -> Dict[str, Any]:
        step = {
            'type': 'memory.store',
            'data': data,
            'type_': memory_type,
        }
        if tags:
            step['tags'] = tags
        return self._runtime._execute_memory_store(step, self._context)

    def log(self, message: str, **details: Any) -> None:
        payload = {
            'message': message,
            'details': self._runtime._safe_json_value(details) if details else {}
        }
        self._runtime.attestation_logger.log('execution_note', payload, self._context.ritual_id)


class SpiralLogic:
    """Main SpiralLogic runtime engine"""
    
    def __init__(self, consent_callback: Optional[Callable] = None, memory_db: str = None):
        self.consent_manager = ConsentManager(consent_callback)
        self.memory_vault = MemoryVault(memory_db or "spirallogic_memory.db")
        self.crisis_monitor = CrisisMonitor()
        self.attestation_logger = AttestationLogger()
        self.parser = SpiralLogicParser()
        self.execution_sandbox = PythonExecutionSandbox()
        
        # Voice management
        self.available_voices = {
            "@healer": {"name": "Healer", "specialization": "emotional_support"},
            "@witness": {"name": "Witness", "specialization": "crisis_response"},
            "@sage": {"name": "Sage", "specialization": "wisdom_guidance"},
            "@strategist": {"name": "Strategist", "specialization": "planning"}
        }
        self.active_voice = None
    
    def execute(self, ritual_code: str, user_id: str = "default", session_id: str = None) -> Dict[str, Any]:
        """Execute a SpiralLogic ritual program"""
        ritual_id = str(uuid.uuid4())
        session_id = session_id or str(uuid.uuid4())
        
        try:
            # Parse ritual
            ritual = self.parser.parse_ritual(ritual_code)
            
            # Create execution context
            context = RitualContext(
                ritual_id=ritual_id,
                intent=ritual.get("intent", "unknown"),
                voice=ritual.get("voice", "@healer"),
                phase=ritual.get("phase", "active"),
                user_id=user_id,
                session_id=session_id,
                consent_granted={},
                memory_store={},
                artifacts={},
                crisis_active=False
            )
            
            # Log ritual start
            self.attestation_logger.log("ritual_start", {
                "intent": context.intent,
                "voice": context.voice,
                "phase": context.phase
            }, ritual_id)
            
            # Execute steps
            results = []
            for step in ritual.get("steps", []):
                step_result = self._execute_step(step, context)
                results.append(step_result)
                
                # Check for crisis after each step
                if step_result.get("crisis_detected"):
                    crisis_response = self.crisis_monitor.trigger_response(context, 
                                                                         step_result.get("trigger_text", ""))
                    results.append({"type": "crisis_response", "data": crisis_response})
                    break
            
            # Prepare final result
            final_result = {
                "ritual_id": ritual_id,
                "success": True,
                "results": results,
                "context": {
                    "voice": context.voice,
                    "intent": context.intent,
                    "consent_granted": context.consent_granted,
                    "crisis_active": context.crisis_active
                },
                "artifacts": context.artifacts
            }
            
            # Log completion
            self.attestation_logger.log("ritual_complete", {
                "success": True,
                "steps_executed": len(results)
            }, ritual_id)
            
            return final_result
            
        except Exception as e:
            error_result = {
                "ritual_id": ritual_id,
                "success": False,
                "error": str(e),
                "context": {}
            }
            
            self.attestation_logger.log("ritual_error", {
                "error": str(e)
            }, ritual_id)
            
            return error_result
    
    def _execute_step(self, step: Dict[str, Any], context: RitualContext) -> Dict[str, Any]:
        """Execute a single ritual step"""
        step_type = step.get("type")
        
        if step_type == "consent.request":
            return self._execute_consent_request(step, context)
        elif step_type == "voice.speak":
            return self._execute_voice_speak(step, context)
        elif step_type == "memory.store":
            return self._execute_memory_store(step, context)
        elif step_type == "memory.recall":
            return self._execute_memory_recall(step, context)
        elif step_type == "crisis.detect":
            return self._execute_crisis_detect(step, context)
        elif step_type and step_type.startswith("ritual."):
            return self._execute_ritual_action(step, context)
        else:
            return {"type": step_type, "success": False, "error": f"Unknown step type: {step_type}"}
    
    def _execute_consent_request(self, step: Dict[str, Any], context: RitualContext) -> Dict[str, Any]:
        """Execute consent request step"""
        scopes = step.get("scopes", [])
        message = step.get("message", "Permission requested")
        
        granted = self.consent_manager.request(scopes, message)
        
        if granted:
            context.consent_granted.update({scope: True for scope in scopes})
        
        return {
            "type": "consent.request",
            "success": granted,
            "scopes": scopes,
            "message": message
        }
    
    def _execute_voice_speak(self, step: Dict[str, Any], context: RitualContext) -> Dict[str, Any]:
        """Execute voice speak step"""
        message = step.get("message", "")
        voice = step.get("voice", context.voice)
        
        # Activate voice if needed
        if voice != self.active_voice:
            self.active_voice = voice
        
        # Crisis detection on voice output
        crisis_detected = self.crisis_monitor.detect(message)
        
        return {
            "type": "voice.speak",
            "success": True,
            "voice": voice,
            "message": message,
            "crisis_detected": crisis_detected,
            "trigger_text": message if crisis_detected else None
        }
    
    def _execute_memory_store(self, step: Dict[str, Any], context: RitualContext) -> Dict[str, Any]:
        """Execute memory store step"""
        if not context.consent_granted.get("memory", False):
            return {
                "type": "memory.store",
                "success": False,
                "error": "Memory consent not granted"
            }
        
        data = step.get("data", "")
        memory_type = step.get("type_", "narrative")
        
        if memory_type == "narrative":
            memory_id = self.memory_vault.store_narrative(data)
        else:
            memory_id = self.memory_vault.store_artifact(data, memory_type, context.ritual_id)
        
        return {
            "type": "memory.store",
            "success": True,
            "memory_id": memory_id,
            "memory_type": memory_type
        }
    
    def _execute_memory_recall(self, step: Dict[str, Any], context: RitualContext) -> Dict[str, Any]:
        """Execute memory recall step"""
        query = step.get("query", "")
        max_results = step.get("max_results", 5)
        
        memories = self.memory_vault.recall_narrative(query, max_results)
        
        return {
            "type": "memory.recall",
            "success": True,
            "query": query,
            "memories": memories
        }
    
    def _execute_crisis_detect(self, step: Dict[str, Any], context: RitualContext) -> Dict[str, Any]:
        """Execute crisis detection step"""
        text = step.get("text", "")
        
        crisis_detected = self.crisis_monitor.detect(text)
        
        return {
            "type": "crisis.detect",
            "success": True,
            "crisis_detected": crisis_detected,
            "trigger_text": text if crisis_detected else None
        }

    def _execute_ritual_action(self, step: Dict[str, Any], context: RitualContext) -> Dict[str, Any]:
        """Execute consent-wrapped ritual actions that run embedded Python code."""
        metadata = step.get('metadata', {}) or {}
        step_type = step.get('type', 'ritual.action')

        consent_scopes = step.get('consent_scopes') or metadata.get('consent_scopes') or []
        if not consent_scopes:
            consent_scopes = self._default_scopes_for_step(step_type)

        if consent_scopes:
            consent_message = metadata.get('intent') or metadata.get('message') or f"{step_type} requires consent"
            if not self._ensure_scopes(consent_scopes, consent_message, context):
                return {
                    'type': step_type,
                    'success': False,
                    'error': 'Consent denied',
                    'requested_scopes': consent_scopes,
                }

        env_globals = self.execution_sandbox.create_environment(
            runtime=self,
            context=context,
            metadata=metadata,
        )
        env_locals: Dict[str, Any] = {}
        bridge = ExecutionBridge(self, context, metadata)
        env_globals['bridge'] = bridge
        env_globals['context'] = SimpleNamespace(ritual=context, metadata=metadata, bridge=bridge)

        result_payload: Dict[str, Any] = {
            'type': step_type,
            'metadata': metadata,
            'requested_scopes': consent_scopes,
        }

        try:
            self.execution_sandbox.execute_block(step.get('execute', ''), env_globals, env_locals, block_name='execute')
            if step.get('complete'):
                self.execution_sandbox.execute_block(step['complete'], env_globals, env_locals, block_name='complete')
            success = True
            error = None
        except Exception as exc:
            success = False
            error = str(exc)
            result_payload['traceback'] = traceback.format_exc()

        result_payload['success'] = success
        if error:
            result_payload['error'] = error

        locals_summary = self._summarize_execution_locals(env_locals)
        if locals_summary:
            result_payload['locals'] = locals_summary

        self.attestation_logger.log(
            'ritual_action',
            {
                'step_type': step_type,
                'success': success,
                'metadata': self._safe_json_value(metadata),
                'locals': locals_summary,
            },
            context.ritual_id,
        )

        return result_payload

    def _ensure_scopes(self, scopes: List[str], message: str, context: RitualContext) -> bool:
        """Ensure required consent scopes are approved before continuing."""
        needed = [scope for scope in scopes if not context.consent_granted.get(scope) and not self.consent_manager.check(scope)]
        if not needed:
            return True

        granted = self.consent_manager.request(needed, message)
        if granted:
            for scope in needed:
                context.consent_granted[scope] = True
        return granted

    def _default_scopes_for_step(self, step_type: str) -> List[str]:
        """Map ritual verbs to default consent scopes."""
        mapping = {
            'ritual.api_request': ['external_api'],
            'ritual.file_access': ['file_system'],
            'ritual.file_write': ['file_system'],
            'ritual.database_query': ['database_access'],
            'ritual.database_insert': ['database_access'],
            'ritual.database_connection': ['database_access'],
        }
        return mapping.get(step_type, [])

    def _summarize_execution_locals(self, env_locals: Dict[str, Any]) -> Dict[str, Any]:
        """Produce a JSON-safe snapshot of local variables."""
        summary: Dict[str, Any] = {}
        for key, value in env_locals.items():
            if key.startswith('_'):
                continue
            summary[key] = self._safe_json_value(value)
        return summary

    def _safe_json_value(self, value: Any, depth: int = 0) -> Any:
        """Best-effort conversion of arbitrary objects into JSON-friendly data."""
        if depth > 3:
            return repr(value)
        if isinstance(value, (str, int, float, bool)) or value is None:
            return value
        if isinstance(value, list):
            return [self._safe_json_value(item, depth + 1) for item in value[:10]]
        if isinstance(value, tuple):
            return [self._safe_json_value(item, depth + 1) for item in list(value)[:10]]
        if isinstance(value, dict):
            items = list(value.items())[:10]
            return {str(k): self._safe_json_value(v, depth + 1) for k, v in items}
        if isinstance(value, set):
            return [self._safe_json_value(item, depth + 1) for item in list(value)[:10]]
        return repr(value)

# Example usage and testing
if __name__ == "__main__":
    # Test ritual program
    test_ritual = """
    {
        "intent": "emotional_support",
        "voice": "@healer",
        "phase": "active",
        "steps": [
            {
                "type": "consent.request",
                "scopes": ["memory"],
                "message": "Can I remember our conversation to help you better?"
            },
            {
                "type": "voice.speak",
                "message": "I'm here to listen. How are you feeling right now?"
            },
            {
                "type": "memory.store",
                "data": "User requested emotional support",
                "type_": "narrative"
            }
        ]
    }
    """
    
    # Initialize SpiralLogic runtime
    sl = SpiralLogic()
    
    # Execute test ritual
    result = sl.execute(test_ritual)
    
    print("SpiralLogic Test Result:")
    print(json.dumps(result, indent=2))



