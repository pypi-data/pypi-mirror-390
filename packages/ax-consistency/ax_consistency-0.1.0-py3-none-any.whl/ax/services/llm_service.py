import os
import json
from typing import Dict, Any, Optional, List
from pathlib import Path

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


class AIService:
    """AI service for cross-file consistency analysis"""
    
    def __init__(self):
        from .ai_config import AIConfig
        ai_config = AIConfig()
        if not ai_config.is_configured():
            raise Exception("AI not configured. Run 'ax setup' first.")
        
        config = ai_config.load_config()
        self.api_key = config.get("api_key")
        self.provider = config.get("provider", "openai")
        self.endpoint = config.get("endpoint")
        self.model_name = config.get("model")
    
    def analyze_file_consistency(self, file_path: Path, project_files: List[Path]) -> Dict[str, Any]:
        """
        Analyze a single file for consistency with the project
        
        Args:
            file_path: Path to the file being analyzed
            project_files: List of other files in project for context
            
        Returns:
            Analysis results with issues and fixes
        """
        if not self.api_key:
            return {"error": "No AI API key configured. Run 'ax setup' first."}
        
        # Read file content
        try:
            file_content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            return {"error": f"Could not read file: {str(e)}"}
        
        # Build project context from other files
        project_context = self._build_project_context(project_files, file_path)
        
        prompt = self._build_analysis_prompt(str(file_path), file_content, project_context)
        
        try:
            return self._call_ai_api(prompt)
        except Exception as e:
            return {"error": f"AI API call failed: {str(e)}"}
    
    def fix_file_issues(self, file_path: Path, project_files: List[Path]) -> Dict[str, Any]:
        """
        Fix issues in a single file using AI
        
        Args:
            file_path: Path to the file to fix
            project_files: List of other files in project for context
            
        Returns:
            Fix results with changes made
        """
        if not self.api_key:
            return {"error": "No AI API key configured. Run 'ax setup' first."}
        
        # First analyze to find issues
        analysis = self.analyze_file_consistency(file_path, project_files)
        if "error" in analysis:
            return analysis
        
        issues = analysis.get("issues", [])
        if not issues:
            return {"fixed": False, "message": "No issues found to fix"}
        
        # Read original content
        try:
            original_content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            return {"error": f"Could not read file: {str(e)}"}
        
        # Build fix prompt
        prompt = self._build_fix_prompt(str(file_path), original_content, issues)
        
        try:
            fix_result = self._call_ai_api(prompt)
            if "fixed_code" in fix_result:
                # Write fixed code back to file
                try:
                    file_path.write_text(fix_result["fixed_code"], encoding='utf-8')
                    return {
                        "fixed": True,
                        "changes": fix_result.get("changes", []),
                        "message": "File updated successfully"
                    }
                except Exception as e:
                    return {"error": f"Could not write fixed file: {str(e)}"}
            else:
                return {"fixed": False, "error": "AI did not provide fixed code"}
        except Exception as e:
            return {"error": f"AI API call failed: {str(e)}"}
    
    def _build_project_context(self, project_files: List[Path], current_file: Path) -> List[Dict]:
        """Build context from other project files"""
        context = []
        
        # Limit to 5 relevant files for context
        relevant_files = [f for f in project_files if f != current_file][:5]
        
        for file_path in relevant_files:
            try:
                content = file_path.read_text(encoding='utf-8')
                # Take first 500 chars as sample
                sample = content[:500] + "..." if len(content) > 500 else content
                context.append({
                    "path": str(file_path),
                    "sample": sample
                })
            except Exception:
                continue
        
        return context
    
    def _build_analysis_prompt(self, file_path: str, file_content: str, project_context: List[Dict]) -> str:
        """Build prompt for cross-file consistency analysis"""
        from pathlib import Path
        from ..core.language_detector import LanguageDetector, Language
        
        file_path_obj = Path(file_path)
        detected_lang = LanguageDetector.detect(file_path_obj)
        language_context = LanguageDetector.build_language_context(detected_lang)
        code_fence = "python" if detected_lang == Language.PYTHON else detected_lang.value
        
        context_info = []
        for ctx in project_context:
            context_info.append(f"File: {ctx.get('path', 'unknown')}\nSample code:\n{ctx.get('sample', '')}\n")
        
        context_str = "\n".join(context_info)
        
        prompt = f"""You are a code consistency analyzer. Analyze ONLY by comparing to the DOMINANT project pattern.

LANGUAGE: {detected_lang.value.upper()}
{language_context}

CURRENT FILE: {file_path}
```{code_fence}
{file_content}
```

PROJECT CONTEXT:
{context_str}

CRITICAL INSTRUCTIONS - READ CAREFULLY:

STEP 1: Count patterns in PROJECT CONTEXT ONLY (not current file):
1. Count snake_case functions vs camelCase functions
2. Count `is None` vs `== None` 
3. Count files with type hints vs without
4. Note coding style patterns (verbosity, error handling, etc.)

Example counting:
- If you see 8 snake_case functions and 2 camelCase → dominant is snake_case
- If you see 7 `is None` and 3 `== None` → dominant is `is None`

STEP 2: Compare current file to DOMINANT pattern ONLY:
- If current file uses camelCase but dominant is snake_case → report issue
- If current file uses snake_case but dominant is camelCase → report issue
- If current file uses `== None` but dominant is `is None` → report issue
- If current file uses `is None` but dominant is `== None` → report issue

STEP 3: Check logical consistency and code quality:
- Does code style match project? (verbose vs concise, explicit vs implicit)
- Does error handling match? (exceptions vs return values)
- Does it look like same author? (naming patterns, comment style)
- Are idioms consistent? (list comprehensions, loops, etc.)

STEP 4: Detect logical errors and code smells:
- Missing operators (+=, -=, ==, etc.)
- Incorrect logic (wrong conditions, unreachable code)
- Dead code (unused variables, functions)
- Unused imports
- Security issues (hardcoded secrets, SQL injection risks)
- Performance issues (inefficient loops, N+1 patterns)
- Missing error handling
- Code duplication
- Complex functions (too many branches)
- Magic numbers/strings
- Incomplete implementations (TODO, FIXME)

DO NOT:
- Report issues if current file already matches dominant pattern
- Mix up which pattern is dominant
- Change code that's already consistent

Respond with JSON ONLY (no markdown, no ```, no extra text):
{{
    "dominant_patterns": {{
        "naming": "snake_case",
        "none_check": "is None",
        "has_type_hints": false,
        "code_style": "concise with list comprehensions"
    }},
    "issues": [
        {{
            "line": 2,
            "severity": "warning",
            "message": "Function 'processString' uses camelCase but project dominant style is snake_case",
            "type": "naming_convention",
            "current_code": "processString",
            "suggested_fix": "process_string"
        }},
        {{
            "line": 5,
            "severity": "error",
            "message": "Logical error: Missing += operator, using = instead. This loses accumulated value",
            "type": "logical_error",
            "current_code": "total = total + value",
            "suggested_fix": "total += value"
        }},
        {{
            "line": 10,
            "severity": "warning",
            "message": "Security: Hardcoded API key found",
            "type": "security",
            "current_code": "API_KEY = 'sk-12345'",
            "suggested_fix": "API_KEY = os.getenv('API_KEY')"
        }},
        {{
            "line": 15,
            "severity": "info",
            "message": "Performance: Loop can be replaced with list comprehension for better performance",
            "type": "performance",
            "current_code": "for x in items:\\n    result.append(x * 2)",
            "suggested_fix": "result = [x * 2 for x in items]"
        }},
        {{
            "line": 20,
            "severity": "info",
            "message": "Dead code: Variable 'unused_var' is assigned but never used",
            "type": "dead_code",
            "current_code": "unused_var = 42",
            "suggested_fix": "Remove unused variable"
        }}
    ],
    "consistency_score": 0.65,
    "summary": "File uses camelCase (3 functions) but project uses snake_case (8/10 files)"
}}
"""
        return prompt
    
    def _build_fix_prompt(self, file_path: str, file_content: str, issues: List[Dict]) -> str:
        """Build prompt for fixing code issues"""
        
        issues_details = []
        for issue in issues:
            line = issue.get('line', 'N/A')
            msg = issue.get('message', '')
            current = issue.get('current_code', '')
            suggested = issue.get('suggested_fix', '')
            issues_details.append(f"Line {line}: {msg}")
            if current and suggested:
                issues_details.append(f"  Change '{current}' to '{suggested}'")
        
        issues_str = "\n".join(issues_details)
        
        prompt = f"""You are a code fixer. Fix issues based on DOMINANT project pattern. Preserve ALL functionality.

FILE: {file_path}
```python
{file_content}
```

ISSUES TO FIX (read the ENTIRE message for each issue):
{issues_str}

CRITICAL RULES - DO EXACTLY AS ISSUES SAY:
1. Read EACH issue message completely to understand the dominant pattern
2. If issue says "dominant style is snake_case" → convert to snake_case
3. If issue says "dominant style is camelCase" → convert to camelCase
4. If issue says "dominant style is 'is None'" → use `is None`
5. If issue says "dominant style is '== None'" → use `== None`
6. Preserve ALL logic, imports, and functionality
7. Output COMPLETE file with all code

EXAMPLE - Read issue messages carefully:
Issue: "uses camelCase but dominant is snake_case" → Change TO snake_case
Issue: "uses snake_case but dominant is camelCase" → Change TO camelCase
Issue: "uses == None but dominant is 'is None'" → Change TO is None
Issue: "uses is None but dominant is '== None'" → Change TO == None

DO NOT guess or assume - follow what each issue message explicitly says!

Respond with JSON ONLY (no markdown, no ```, no text):
{{
    "fixed_code": "def process_string(input_str):\\n    if input_str is None:\\n        return \\\"\\\"\\n    return input_str.strip()",
    "changes": [
        "Line 1: Renamed 'processString' to 'process_string' (dominant pattern)",
        "Line 2: Changed '== None' to 'is None' (dominant pattern)"
    ]
}}
"""
        return prompt
    

    
    def _parse_json_response(self, content: str) -> Dict[str, Any]:
        """Parse JSON from AI response, handling markdown wrapping"""
        try:
            content_clean = content.strip()
            
            if content_clean.startswith('```json'):
                content_clean = content_clean[7:]
            elif content_clean.startswith('```'):
                content_clean = content_clean[3:]
            
            if content_clean.endswith('```'):
                content_clean = content_clean[:-3]
            
            content_clean = content_clean.strip()
            
            return json.loads(content_clean)
        except json.JSONDecodeError as e:
            return {"error": "Invalid JSON response from AI", "raw_response": content[:500]}
    
    def _call_ai_api(self, prompt: str) -> Dict[str, Any]:
        """Call AI API based on configured provider"""
        if not HAS_REQUESTS:
            return {"error": "requests library not installed"}
        
        if not self.api_key:
            return {"error": "No API key provided"}
            
        if self.provider == "qwen":
            return self._call_qwen_api(prompt)
        elif self.provider == "openai":
            return self._call_openai_api(prompt)
        elif self.provider == "anthropic":
            return self._call_anthropic_api(prompt)
        elif self.provider == "gemini":
            return self._call_gemini_api(prompt)
        else:
            # Generic OpenAI-compatible API
            return self._call_openai_api(prompt)
    
    def _call_qwen_api(self, prompt: str) -> Dict[str, Any]:
        """Call Qwen/Alibaba Cloud API (OpenAI-compatible)"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
            "max_tokens": 2000
        }
        
        response = requests.post(self.endpoint, headers=headers, json=data)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            return {"error": f"HTTP {response.status_code}: {response.text}"}
        
        result = response.json()
        content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
        
        return self._parse_json_response(content)
    
    def _call_openai_api(self, prompt: str) -> Dict[str, Any]:
        """Call OpenAI or OpenAI-compatible API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
            "max_tokens": 2000
        }
        
        response = requests.post(f"{self.endpoint}/chat/completions", headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
        
        return self._parse_json_response(content)
    
    def _call_anthropic_api(self, prompt: str) -> Dict[str, Any]:
        """Call Anthropic Claude API"""
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        data = {
            "model": self.model_name,
            "max_tokens": 2000,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        response = requests.post(f"{self.endpoint}/messages", headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        content = result.get("content", [{}])[0].get("text", "")
        
        return self._parse_json_response(content)
    
    def _call_gemini_api(self, prompt: str) -> Dict[str, Any]:
        """Call Google Gemini API"""
        headers = {
            "Content-Type": "application/json"
        }
        
        # Add API key to URL for Gemini
        url = f"{self.endpoint}/models/{self.model_name}:generateContent?key={self.api_key}"
        
        data = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ]
        }
        
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        content = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
        
        return self._parse_json_response(content)
    

