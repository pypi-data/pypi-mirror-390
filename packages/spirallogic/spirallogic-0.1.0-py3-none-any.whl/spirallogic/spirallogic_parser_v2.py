#!/usr/bin/env python3
"""
REAL SPIROLOGIC SYNTAX PARSER
Full implementation of mystical programming language syntax

Usage:
    from spirallogic_parser_v2 import SpiralLogicParser
    parser = SpiralLogicParser()
    ritual_data = parser.parse(spirallogic_code)
"""

import re
import json
import textwrap
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

@dataclass
class ParseError:
    line: int
    column: int
    message: str
    code: str

class SpiralLogicParser:
    """Complete Spirologic syntax parser with mystical energy"""
    
    def __init__(self):
        self.tokens = []
        self.position = 0
        self.current_line = 1
        self.current_column = 1
        
        # Spirologic keywords and operators
        self.keywords = {
            'ritual', 'spirit', 'voice', 'consent', 'memory', 'archive',
            'if', 'else', 'and', 'or', 'not', 'true', 'false'
        }
        
        self.ritual_verbs = {
            'ritual.engage', 'ritual.complete', 'ritual.pause', 'ritual.abort',
            'spirit.summon', 'spirit.channel', 'spirit.invoke', 'spirit.release',
            'voice.speak', 'voice.whisper', 'voice.channel', 'voice.manifest',
            'consent.request', 'consent.grant', 'consent.revoke', 'consent.check',
            'memory.store', 'memory.recall', 'memory.release', 'memory.search',
            'archive.access', 'archive.store', 'archive.query', 'archive.seal'
        }
    
    def parse(self, code: str) -> Dict[str, Any]:
        """Parse Spirologic code into executable ritual structure"""
        try:
            self.code = code
            # Tokenize
            self.tokens = self._tokenize(code)
            self.position = 0
            self.current_line = 1
            self.current_column = 1
            
            # Parse ritual structure
            ritual = self._parse_ritual()
            
            return {
                "success": True,
                "ritual": ritual,
                "syntax": "spirallogic_v2"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "line": self.current_line,
                "column": self.current_column,
                "syntax": "spirallogic_v2"
            }
    
    def _tokenize(self, code: str) -> List[Dict[str, Any]]:
        """Convert Spirologic code into tokens"""
        tokens = []
        
        # Token patterns
        patterns = [
            ('COMMENT', r'#.*'),
            ('RITUAL_VERB', r'(?:ritual|spirit|voice|consent|memory|archive)\.[a-zA-Z_][a-zA-Z0-9_]*'),
            ('SPIRIT_REF', r'@[a-zA-Z_][a-zA-Z0-9_]*'),
            ('STRING', r'"([^"\\]|\\.)*"'),
            ('STRING_SINGLE', r"'([^'\\]|\\.)*'"),
            ('NUMBER', r'\d+\.?\d*'),
            ('PIPE', r'\|'),
            ('COLON', r':'),
            ('COMMA', r','),
            ('SEMICOLON', r';'),
            ('LBRACKET', r'\['),
            ('RBRACKET', r'\]'),
            ('LBRACE', r'\{'),
            ('RBRACE', r'\}'),
            ('LPAREN', r'\('),
            ('RPAREN', r'\)'),
            ('ARROW', r'->'),
            ('EQUALS', r'='),
            ('IF', r'\bif\b'),
            ('ELSE', r'\belse\b'),
            ('AND', r'\band\b'),
            ('OR', r'\bor\b'),
            ('NOT', r'\bnot\b'),
            ('TRUE', r'\btrue\b'),
            ('FALSE', r'\bfalse\b'),
            ('IDENTIFIER', r'[a-zA-Z_][a-zA-Z0-9_]*'),
            ('NEWLINE', r'\n'),
            ('WHITESPACE', r'[ \t]+'),
        ]
        
        # Compile patterns
        pattern_re = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in patterns)
        
        line_num = 1
        line_start = 0
        
        for match in re.finditer(pattern_re, code):
            token_type = match.lastgroup
            token_value = match.group()
            
            if token_type == 'NEWLINE':
                line_num += 1
                line_start = match.end()
                continue
            elif token_type == 'WHITESPACE' or token_type == 'COMMENT':
                continue
            
            column = match.start() - line_start + 1
            
            tokens.append({
                'type': token_type,
                'value': token_value,
                'line': line_num,
                'column': column,
                'start': match.start(),
                'end': match.end()
            })
        
        return tokens
    
    def _current_token(self) -> Optional[Dict[str, Any]]:
        """Get current token"""
        if self.position < len(self.tokens):
            return self.tokens[self.position]
        return None
    
    def _advance(self) -> Optional[Dict[str, Any]]:
        """Move to next token"""
        token = self._current_token()
        if token:
            self.current_line = token['line']
            self.current_column = token['column']
            self.position += 1
        return token
    
    def _peek(self, offset: int = 1) -> Optional[Dict[str, Any]]:
        """Look ahead at token"""
        pos = self.position + offset - 1
        if pos < len(self.tokens):
            return self.tokens[pos]
        return None
    
    def _expect(self, token_type: str) -> Dict[str, Any]:
        """Expect specific token type"""
        token = self._advance()
        if not token or token['type'] != token_type:
            expected = token_type
            actual = token['type'] if token else 'EOF'
            raise SyntaxError(f"Expected {expected}, got {actual} at line {self.current_line}")
        return token
    
    def _parse_ritual(self) -> Dict[str, Any]:
        """Parse complete ritual structure"""
        ritual = {
            "intent": "unknown",
            "spirit": None,
            "voice": None,
            "phase": "active",
            "steps": []
        }
        
        # Parse ritual statements
        while self._current_token():
            stmt = self._parse_statement()
            if stmt:
                # Handle ritual metadata
                if stmt.get('type') == 'ritual.engage':
                    ritual['intent'] = stmt.get('intent', 'unknown')
                    ritual['spirit'] = stmt.get('spirit')
                    ritual['voice'] = stmt.get('voice')
                    ritual['phase'] = stmt.get('phase', 'active')
                
                # Add to steps
                ritual['steps'].append(stmt)
        
        return ritual
    
    def _parse_statement(self) -> Optional[Dict[str, Any]]:
        """Parse a single Spirologic statement"""
        token = self._current_token()
        if not token:
            return None
        
        if token['type'] == 'RITUAL_VERB':
            return self._parse_ritual_verb()
        elif token['type'] == 'IF':
            return self._parse_conditional()
        else:
            # Skip unknown tokens
            self._advance()
            return None
    
    def _parse_ritual_verb(self) -> Dict[str, Any]:
        """Parse ritual verb with parameters and optional execution blocks"""
        verb_token = self._advance()
        verb = verb_token['value']

        stmt = {
            'type': verb,
            'line': verb_token['line'],
            'column': verb_token['column']
        }

        # Optional primary argument (quoted string)
        if self._current_token() and self._current_token()['type'] in ['STRING', 'STRING_SINGLE']:
            arg_token = self._advance()
            arg_value = arg_token['value'][1:-1]  # Strip quotes

            if verb == 'ritual.engage':
                stmt['intent'] = arg_value
            elif verb in ['voice.speak', 'voice.whisper', 'voice.manifest']:
                stmt['message'] = arg_value
            elif verb in ['memory.store', 'archive.store']:
                stmt['data'] = arg_value
            elif verb in ['memory.recall', 'archive.query']:
                stmt['query'] = arg_value
            elif verb == 'consent.request':
                stmt['message'] = arg_value
            else:
                stmt['argument'] = arg_value

        # Optional metadata block
        if self._current_token() and self._current_token()['type'] == 'LBRACE':
            metadata_block = self._collect_brace_block_text(raw=True)
            metadata_clean = self._clean_block_text(metadata_block)
            stmt['metadata_raw'] = metadata_block
            stmt['metadata'] = self._parse_metadata_block(metadata_clean)

        # Parse parameters after pipe (legacy syntax)
        if self._current_token() and self._current_token()['type'] == 'PIPE':
            self._advance()
            params = self._parse_parameters()
            stmt.update(params)

        # Additional execution sections (execute, complete, guard, etc.)
        while self._current_token() and self._current_token()['type'] == 'IDENTIFIER':
            section_token = self._current_token()
            section_name = section_token['value']
            if section_name not in {'execute', 'complete', 'guard', 'after', 'before'}:
                break
            self._advance()
            if not self._current_token() or self._current_token()['type'] != 'LBRACE':
                break
            block_text = self._collect_brace_block_text(raw=True)
            stmt[section_name] = self._clean_block_text(block_text)

        return stmt

    def _collect_brace_block_text(self, raw: bool = False) -> str:
        opening = self._expect('LBRACE')
        block_start = opening['end']
        depth = 1
        end_index = block_start

        while depth > 0:
            token = self._advance()
            if not token:
                raise SyntaxError('Unterminated brace block in ritual definition')
            if token['type'] == 'LBRACE':
                depth += 1
            elif token['type'] == 'RBRACE':
                depth -= 1
                if depth == 0:
                    end_index = token['start']
                    break

        raw_text = self.code[block_start:end_index]
        return raw_text if raw else self._clean_block_text(raw_text)

    def _clean_block_text(self, text: str) -> str:
        if text is None:
            return ''
        cleaned = textwrap.dedent(text)
        return cleaned.strip()


    def _parse_metadata_block(self, block_text: str) -> Dict[str, Any]:
        metadata: Dict[str, Any] = {}
        if not block_text:
            return metadata

        for line in block_text.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith('//') or stripped.startswith('#'):
                continue
            if '//' in stripped:
                stripped = stripped.split('//', 1)[0].strip()
            if stripped.endswith(','):
                stripped = stripped[:-1].strip()

            match = re.match(r'([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(.+)', stripped)
            if not match:
                continue

            key, value_expr = match.groups()
            value_expr = value_expr.strip()

            if key == 'consent':
                scope = self._extract_scope_from_consent(value_expr)
                metadata['consent'] = value_expr
                if scope:
                    metadata.setdefault('consent_scopes', []).append(scope)
            else:
                metadata[key] = self._interpret_metadata_value(value_expr)

        return metadata

    def _interpret_metadata_value(self, value: str) -> Any:
        value = value.strip()
        lowered = value.lower()
        if lowered in {'true', 'false'}:
            return lowered == 'true'

        number_candidate = value.replace('_', '')
        try:
            if '.' in number_candidate and number_candidate.replace('.', '', 1).isdigit():
                return float(number_candidate)
            if number_candidate.isdigit():
                return int(number_candidate)
        except ValueError:
            pass

        if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
            return value[1:-1]

        if value.startswith('[') and value.endswith(']'):
            inner = value[1:-1]
            if not inner.strip():
                return []
            try:
                sanitized = value.replace("'", '"')
                return json.loads(sanitized)
            except json.JSONDecodeError:
                items = []
                for item in inner.split(','):
                    token = item.strip()
                    if not token:
                        continue
                    if (token.startswith('"') and token.endswith('"')) or (token.startswith("'") and token.endswith("'")):
                        items.append(token[1:-1])
                    else:
                        items.append(token)
                return items

        return value

    def _extract_scope_from_consent(self, expression: str) -> Optional[str]:
        match = re.search(r"user\.permits\(\s*[\"\']([^\"\']+)[\"\']", expression)
        if match:
            return match.group(1)
        return None


    def _parse_parameters(self) -> Dict[str, Any]:
        """Parse parameter list: key: value, key2: value2"""
        params = {}
        
        while self._current_token():
            # Check for parameter name
            if self._current_token()['type'] != 'IDENTIFIER':
                break
            
            key_token = self._advance()
            key = key_token['value']
            
            # Expect colon
            if not self._current_token() or self._current_token()['type'] != 'COLON':
                break
            self._advance()  # consume colon
            
            # Parse value
            value = self._parse_value()
            params[key] = value
            
            # Check for comma (continue) or end
            if self._current_token() and self._current_token()['type'] == 'COMMA':
                self._advance()  # consume comma
            else:
                break
        
        return params
    
    def _parse_value(self) -> Any:
        """Parse parameter value"""
        token = self._current_token()
        if not token:
            return None
        
        if token['type'] in ['STRING', 'STRING_SINGLE']:
            self._advance()
            return token['value'][1:-1]  # Strip quotes
        elif token['type'] == 'NUMBER':
            self._advance()
            value = token['value']
            return float(value) if '.' in value else int(value)
        elif token['type'] == 'TRUE':
            self._advance()
            return True
        elif token['type'] == 'FALSE':
            self._advance()
            return False
        elif token['type'] == 'SPIRIT_REF':
            self._advance()
            return token['value']  # Keep @ prefix
        elif token['type'] == 'LBRACKET':
            return self._parse_list()
        elif token['type'] == 'IDENTIFIER':
            self._advance()
            return token['value']
        else:
            self._advance()
            return token['value']
    
    def _parse_list(self) -> List[Any]:
        """Parse list: [item1, item2, item3]"""
        self._expect('LBRACKET')
        items = []
        
        while self._current_token() and self._current_token()['type'] != 'RBRACKET':
            item = self._parse_value()
            items.append(item)
            
            if self._current_token() and self._current_token()['type'] == 'COMMA':
                self._advance()  # consume comma
            elif self._current_token() and self._current_token()['type'] == 'RBRACKET':
                break
            else:
                break
        
        self._expect('RBRACKET')
        return items
    
    def _parse_conditional(self) -> Dict[str, Any]:
        """Parse if/else conditional"""
        if_token = self._advance()
        
        stmt = {
            'type': 'conditional',
            'line': if_token['line'],
            'column': if_token['column']
        }
        
        # Parse condition
        condition = self._parse_condition()
        stmt['condition'] = condition
        
        # Parse arrow
        if self._current_token() and self._current_token()['type'] == 'ARROW':
            self._advance()
        
        # Parse then statement
        then_stmt = self._parse_statement()
        stmt['then'] = then_stmt
        
        # Parse optional else
        if self._current_token() and self._current_token()['type'] == 'ELSE':
            self._advance()
            if self._current_token() and self._current_token()['type'] == 'ARROW':
                self._advance()
            else_stmt = self._parse_statement()
            stmt['else'] = else_stmt
        
        return stmt
    
    def _parse_condition(self) -> Dict[str, Any]:
        """Parse conditional expression"""
        # Simple condition parsing for now
        left = self._parse_condition_term()
        
        while self._current_token() and self._current_token()['type'] in ['AND', 'OR']:
            op_token = self._advance()
            right = self._parse_condition_term()
            left = {
                'type': 'binary_op',
                'operator': op_token['value'],
                'left': left,
                'right': right
            }
        
        return left
    
    def _parse_condition_term(self) -> Dict[str, Any]:
        """Parse single condition term"""
        token = self._current_token()
        
        if token['type'] == 'NOT':
            self._advance()
            operand = self._parse_condition_term()
            return {
                'type': 'unary_op',
                'operator': 'not',
                'operand': operand
            }
        elif token['type'] == 'RITUAL_VERB':
            # consent.granted, memory.available, etc.
            verb_token = self._advance()
            
            # Handle optional parameters
            params = {}
            if self._current_token() and self._current_token()['type'] == 'LBRACKET':
                scope_list = self._parse_list()
                params['scopes'] = scope_list
            
            return {
                'type': 'condition_check',
                'verb': verb_token['value'],
                'params': params
            }
        else:
            # Simple identifier or value
            value = self._parse_value()
            return {
                'type': 'value',
                'value': value
            }

# Enhanced runtime integration function
def convert_to_runtime_format(parsed_ritual: Dict[str, Any]) -> Dict[str, Any]:
    """Convert parsed Spirologic to runtime-compatible format"""
    if not parsed_ritual.get('success'):
        return parsed_ritual
    
    ritual = parsed_ritual['ritual']
    runtime_steps = []
    
    for step in ritual['steps']:
        step_type = step.get('type')
        runtime_step = {'type': step_type}
        
        # Convert Spirologic steps to runtime format
        if step_type == 'ritual.engage':
            # This is metadata, not a step
            continue
        elif step_type == 'consent.request':
            runtime_step = {
                'type': 'consent.request',
                'scopes': step.get('scopes', ['memory']),
                'message': step.get('message', 'Permission requested')
            }
        elif step_type in ['voice.speak', 'voice.whisper', 'voice.manifest']:
            runtime_step = {
                'type': 'voice.speak',
                'message': step.get('message', ''),
                'voice': step.get('voice', ritual.get('voice', '@healer')),
                'wait_for_response': step.get('wait_for_response', False)
            }
        elif step_type in ['memory.store', 'archive.store']:
            runtime_step = {
                'type': 'memory.store',
                'data': step.get('data', ''),
                'type_': step.get('type', 'narrative'),
                'tags': step.get('tags', [])
            }
        elif step_type in ['memory.recall', 'archive.query']:
            runtime_step = {
                'type': 'memory.recall',
                'query': step.get('query', ''),
                'max_results': step.get('max_results', 5)
            }
        elif step_type and step_type.startswith('ritual.'):
            runtime_step = {
                'type': step_type,
                'metadata': step.get('metadata', {}),
                'metadata_raw': step.get('metadata_raw'),
                'execute': step.get('execute'),
                'complete': step.get('complete'),
                'guard': step.get('guard'),
                'after': step.get('after'),
                'before': step.get('before'),
                'consent_scopes': step.get('metadata', {}).get('consent_scopes', [])
            }
        elif step_type == 'conditional':
            # Handle conditionals
            runtime_step = {
                'type': 'conditional',
                'condition': step.get('condition'),
                'then': convert_step_to_runtime(step.get('then', {})),
                'else': convert_step_to_runtime(step.get('else', {})) if step.get('else') else None
            }
        else:
            # Pass through unknown steps
            runtime_step = step
        
        runtime_steps.append(runtime_step)
    
    return {
        'intent': ritual.get('intent', 'unknown'),
        'voice': ritual.get('voice', '@healer'),
        'phase': ritual.get('phase', 'active'),
        'steps': runtime_steps
    }

def convert_step_to_runtime(step: Dict[str, Any]) -> Dict[str, Any]:
    """Convert single step to runtime format"""
    if not step:
        return {}
    
    # Use same conversion logic as above
    step_type = step.get('type')
    if step_type == 'consent.request':
        return {
            'type': 'consent.request',
            'scopes': step.get('scopes', ['memory']),
            'message': step.get('message', 'Permission requested')
        }
    elif step_type in ['voice.speak', 'voice.whisper', 'voice.manifest']:
        return {
            'type': 'voice.speak',
            'message': step.get('message', ''),
            'voice': step.get('voice', '@healer')
        }
    elif step_type in ['memory.store', 'archive.store']:
        return {
            'type': 'memory.store',
            'data': step.get('data', ''),
            'type_': step.get('memory_type', 'narrative')
        }
    elif step_type and step_type.startswith('ritual.'):
        return {
            'type': step_type,
            'metadata': step.get('metadata', {}),
            'metadata_raw': step.get('metadata_raw'),
            'execute': step.get('execute'),
            'complete': step.get('complete'),
            'guard': step.get('guard'),
            'after': step.get('after'),
            'before': step.get('before'),
            'consent_scopes': step.get('metadata', {}).get('consent_scopes', [])
        }
    else:
        return step

# Test the parser
if __name__ == "__main__":
    test_code = '''
    ritual.engage "customer_support" | spirit: @business_helper, phase: active
    consent.request [database_access, customer_data] | "Access customer records?"
    voice.speak "How can I help you today?" | wait_for_response: true
    memory.store "session_started" | type: narrative, tags: ["support", "customer"]
    
    if consent.granted [database_access] -> memory.recall "customer_history" | max_results: 10
    else -> voice.speak "I can help with general questions" | voice: @public_helper
    '''
    
    parser = SpiralLogicParser()
    result = parser.parse(test_code)
    
    if result['success']:
        print("âœ… SPIROLOGIC PARSING SUCCESS!")
        print(json.dumps(result['ritual'], indent=2))
        
        print("\nðŸ”„ RUNTIME CONVERSION:")
        runtime_format = convert_to_runtime_format(result)
        print(json.dumps(runtime_format, indent=2))
    else:
        print("âŒ PARSING FAILED:")
        print(f"Error: {result['error']}")
        print(f"Line: {result['line']}, Column: {result['column']}")




