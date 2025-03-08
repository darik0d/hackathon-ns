import ast
import random
import re
from typing import List, Dict, Any, Tuple

class BugGenerator:
    def __init__(self, severity_levels: Dict[str, float] = None):
        """
        Initialize the bug generator with configurable severity levels.
        
        Args:
            severity_levels: Dictionary mapping severity names to probabilities
                             (should sum to 1.0)
        """
        self.severity_levels = severity_levels or {
            "minor": 0.5,    # Syntax issues, style problems
            "moderate": 0.3, # Logic bugs that affect functionality but don't crash
            "severe": 0.2    # Bugs that cause crashes or security issues
        }
        
        # Register different types of bugs by severity
        self.bug_types = {
            "minor": [
                self._introduce_variable_name_typo,
                self._remove_comment,
                self._add_unused_variable,
            ],
            "moderate": [
                self._flip_boolean_condition,
                self._off_by_one_error,
                self._swap_function_arguments,
                self._modify_string_content,
            ],
            "severe": [
                self._remove_error_handling,
                self._introduce_null_pointer,
                self._add_memory_leak,
                self._introduce_security_vulnerability
            ]
        }
    
    def generate_bugs(self, code: str, num_bugs: int = 1) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Generate specified number of bugs in the provided code.
        
        Args:
            code: Source code to modify
            num_bugs: Number of bugs to introduce
            
        Returns:
            Tuple containing modified code and list of introduced bugs
        """
        modified_code = code
        introduced_bugs = []
        
        for _ in range(num_bugs):
            # Select severity based on configured probabilities
            severity = random.choices(
                list(self.severity_levels.keys()),
                weights=list(self.severity_levels.values())
            )[0]
            
            # Choose a bug type from the selected severity
            bug_function = random.choice(self.bug_types[severity])
            
            # Apply the bug
            modified_code, bug_info = bug_function(modified_code)
            bug_info["severity"] = severity
            introduced_bugs.append(bug_info)
        
        return modified_code, introduced_bugs
    
    def _introduce_variable_name_typo(self, code: str) -> Tuple[str, Dict[str, Any]]:
        """Introduce a typo in a variable name"""
        try:
            tree = ast.parse(code)
            variables = []
            
            # Find all variable names
            for node in ast.walk(tree):
                if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                    variables.append(node.id)
            
            if not variables:
                return code, {"type": "variable_typo", "success": False, "reason": "No variables found"}
            
            # Choose a random variable to modify
            var_to_modify = random.choice(variables)
            if len(var_to_modify) <= 1:
                return code, {"type": "variable_typo", "success": False, "reason": "Variable name too short"}
            
            # Create a typo by changing one character
            idx = random.randint(0, len(var_to_modify) - 1)
            typo_char = chr(ord(var_to_modify[idx]) + random.randint(1, 5))
            typo_name = var_to_modify[:idx] + typo_char + var_to_modify[idx+1:]
            
            # Replace some occurrences (not all to make it subtle)
            occurrences = [m.start() for m in re.finditer(r'\b' + var_to_modify + r'\b', code)]
            if occurrences:
                # Choose one occurrence to modify
                pos = random.choice(occurrences)
                modified_code = code[:pos] + typo_name + code[pos+len(var_to_modify):]
                return modified_code, {
                    "type": "variable_typo",
                    "original": var_to_modify,
                    "modified": typo_name,
                    "line_hint": code.count('\n', 0, pos) + 1,
                    "success": True
                }
            
            return code, {"type": "variable_typo", "success": False, "reason": "Failed to locate variable"}
            
        except SyntaxError:
            return code, {"type": "variable_typo", "success": False, "reason": "Syntax error in code"}
    
    def _flip_boolean_condition(self, code: str) -> Tuple[str, Dict[str, Any]]:
        """Flip a boolean condition (e.g., change == to !=, > to <, etc.)"""
        operators = ["==", "!=", ">", "<", ">=", "<=", "and", "or"]
        flips = {"==": "!=", "!=": "==", ">": "<", "<": ">", ">=": "<=", "<=": ">=", "and": "or", "or": "and"}
        
        # Find conditional statements
        for op in operators:
            pattern = re.escape(op)
            matches = list(re.finditer(pattern, code))
            if matches:
                # Choose a random occurrence to modify
                match = random.choice(matches)
                pos = match.start()
                line_num = code.count('\n', 0, pos) + 1
                
                # Check if it's within a comment
                line_start = code.rfind('\n', 0, pos) + 1
                line_end = code.find('\n', pos)
                if line_end == -1:
                    line_end = len(code)
                line = code[line_start:line_end]
                
                # Skip if in a comment
                if '#' in line and line.index('#') < pos - line_start:
                    continue
                
                flipped_op = flips[op]
                modified_code = code[:pos] + flipped_op + code[pos + len(op):]
                
                return modified_code, {
                    "type": "boolean_flip",
                    "original": op,
                    "modified": flipped_op,
                    "line": line_num,
                    "success": True
                }
        
        return code, {"type": "boolean_flip", "success": False, "reason": "No suitable conditions found"}
    
    def _off_by_one_error(self, code: str) -> Tuple[str, Dict[str, Any]]:
        """Introduce an off-by-one error in ranges or indices"""
        # Look for range or index access patterns
        patterns = [
            (r'range\(\s*(\d+)\s*,\s*(\d+)\s*\)', lambda m: f'range({m.group(1)}, {int(m.group(2))+1})'),
            (r'range\(\s*(\d+)\s*\)', lambda m: f'range({int(m.group(1))+1})'),
            (r'\[\s*(\d+)\s*:\s*(\d+)\s*\]', lambda m: f'[{m.group(1)}:{int(m.group(2))-1}]'),
            (r'\[\s*(\d+)\s*\]', lambda m: f'[{int(m.group(1))+1}]')
        ]
        
        for pattern, replacement_func in patterns:
            matches = list(re.finditer(pattern, code))
            if matches:
                match = random.choice(matches)
                pos = match.start()
                line_num = code.count('\n', 0, pos) + 1
                
                # Apply the replacement
                original = match.group(0)
                modified = replacement_func(match)
                modified_code = code[:pos] + modified + code[pos + len(original):]
                
                return modified_code, {
                    "type": "off_by_one",
                    "original": original,
                    "modified": modified,
                    "line": line_num,
                    "success": True
                }
        
        return code, {"type": "off_by_one", "success": False, "reason": "No suitable patterns found"}
    
    def _introduce_security_vulnerability(self, code: str) -> Tuple[str, Dict[str, Any]]:
        """Introduce a basic security vulnerability"""
        # Look for input validation patterns we could remove
        security_patterns = [
            # SQL injection vulnerability
            (r'(["\'])(\s*\+\s*[\w\.]+\s*\+\s*)(["\'])', r'\1\3'),  # Remove parameterization
            # Command injection
            (r'subprocess\.run\(\[([^]]+)\]', r'subprocess.run(\1'),  # Change list to string
            # Input validation
            (r'if\s+not\s+re\.match[^:]+:[^}]+}', ''),  # Remove validation check
        ]
        
        for pattern, replacement in security_patterns:
            matches = list(re.finditer(pattern, code))
            if matches:
                match = random.choice(matches)
                pos = match.start()
                length = match.end() - pos
                line_num = code.count('\n', 0, pos) + 1
                
                # Apply the replacement
                original = match.group(0)
                modified = re.sub(pattern, replacement, original)
                modified_code = code[:pos] + modified + code[pos + length:]
                
                return modified_code, {
                    "type": "security_vulnerability",
                    "original": original,
                    "modified": modified,
                    "line": line_num,
                    "success": True,
                    "details": "Removed input validation"
                }
        
        # If no specific security pattern found, add a hardcoded credential
        function_matches = list(re.finditer(r'def\s+\w+\s*\([^)]*\):', code))
        if function_matches:
            match = random.choice(function_matches)
            pos = match.end()
            line_num = code.count('\n', 0, pos) + 1
            
            indentation = "    "
            hardcoded_cred = f'\n{indentation}api_key = "S3CR3T_K3Y_123456789abcdef"\n'
            
            modified_code = code[:pos] + hardcoded_cred + code[pos:]
            
            return modified_code, {
                "type": "security_vulnerability",
                "subtype": "hardcoded_credentials",
                "line": line_num + 1,
                "success": True,
                "details": "Added hardcoded API key"
            }
        
        return code, {"type": "security_vulnerability", "success": False, "reason": "No suitable patterns found"}

    def _remove_comment(self, code: str) -> Tuple[str, Dict[str, Any]]:
        """Remove an important comment"""
        # Find meaningful comments (longer comments are likely more important)
        comment_matches = list(re.finditer(r'#[^\n]{15,}', code))
        if comment_matches:
            match = random.choice(comment_matches)
            pos = match.start()
            end_pos = match.end()
            line_num = code.count('\n', 0, pos) + 1
            
            original_comment = match.group(0)
            modified_code = code[:pos] + code[end_pos:]
            
            return modified_code, {
                "type": "removed_comment",
                "original": original_comment,
                "line": line_num,
                "success": True
            }
        
        return code, {"type": "removed_comment", "success": False, "reason": "No suitable comments found"}
    
    # Other bug introduction methods would be implemented similarly
    def _add_unused_variable(self, code: str) -> Tuple[str, Dict[str, Any]]:
        # placeholder implementation
        return code, {"type": "unused_variable", "success": False, "reason": "Not implemented"}
    
    def _swap_function_arguments(self, code: str) -> Tuple[str, Dict[str, Any]]:
        # placeholder implementation
        return code, {"type": "swapped_arguments", "success": False, "reason": "Not implemented"}
    
    def _modify_string_content(self, code: str) -> Tuple[str, Dict[str, Any]]:
        # placeholder implementation
        return code, {"type": "modified_string", "success": False, "reason": "Not implemented"}
    
    def _remove_error_handling(self, code: str) -> Tuple[str, Dict[str, Any]]:
        # placeholder implementation
        return code, {"type": "removed_error_handling", "success": False, "reason": "Not implemented"}
    
    def _introduce_null_pointer(self, code: str) -> Tuple[str, Dict[str, Any]]:
        # placeholder implementation
        return code, {"type": "null_pointer", "success": False, "reason": "Not implemented"}
    
    def _add_memory_leak(self, code: str) -> Tuple[str, Dict[str, Any]]:
        # placeholder implementation
        return code, {"type": "memory_leak", "success": False, "reason": "Not implemented"}
