#!/usr/bin/env python3
"""
Auto-diagnosis engine for test failures.
Parses error messages, reads source files, and suggests fix hypotheses.

Usage:
  from diagnosis import DiagnosisEngine

  engine = DiagnosisEngine(project_root="/path/to/repo", depth="excerpt")
  diagnosis = engine.diagnose(
      error_message="ImportError: cannot import name 'ForecastingAgent'",
      error_type="ImportError",
      test_name="State & Coordinator Import"
  )

  # Output as Markdown
  print(diagnosis.to_markdown())

  # Output as JSON
  import json
  json.dump(diagnosis.to_dict(), open("diagnosis.json", "w"), indent=2)
"""

import re
import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict


@dataclass
class FixHypothesis:
    """A proposed fix with confidence and details"""

    title: str
    confidence: str  # HIGH, MEDIUM, LOW
    description: str
    file_path: str
    line_range: Optional[Tuple[int, int]] = None
    code_excerpt: Optional[str] = None
    action: str = ""

    def to_dict(self):
        return asdict(self)


@dataclass
class Diagnosis:
    """Complete diagnosis for a failed test"""

    test_name: str
    error_type: str
    error_message: str
    likely_files: List[str]
    suspected_problem: str
    fix_hypotheses: List[FixHypothesis]

    def to_dict(self):
        return {
            "test_name": self.test_name,
            "error_type": self.error_type,
            "error_message": self.error_message,
            "likely_files": self.likely_files,
            "suspected_problem": self.suspected_problem,
            "fix_hypotheses": [h.to_dict() for h in self.fix_hypotheses],
        }

    def to_markdown(self) -> str:
        """Format diagnosis as human-friendly Markdown"""
        lines = [
            "======================================================",
            f"DIAGNOSIS: {self.error_type} in {self.test_name}",
            "======================================================",
            "",
            "Likely Files:",
        ]

        for fpath in self.likely_files:
            lines.append(f"  * {fpath}")

        lines.extend([
            "",
            "Suspected Problem:",
            f"  {self.suspected_problem}",
            "",
        ])

        for i, hyp in enumerate(self.fix_hypotheses, 1):
            lines.extend([
                f"Fix Hypothesis {i} ({hyp.confidence} confidence):",
                f"  {hyp.title}",
                f"  Location: {hyp.file_path}" + (f":{hyp.line_range[0]}-{hyp.line_range[1]}" if hyp.line_range else ""),
                "",
            ])

            if hyp.code_excerpt:
                lines.extend([
                    f"  Code excerpt:",
                    "  -- " + hyp.file_path.split('/')[-1] + " " + "-" * 40,
                ])
                for line_text in hyp.code_excerpt.split('\n'):
                    if line_text.strip():
                        lines.append(f"  | {line_text}")
                lines.append("  --" + "-" * 50)
                lines.append("")

            if hyp.action:
                lines.extend([
                    f"  Action: {hyp.action}",
                    "",
                ])

        return "\n".join(lines)


class DiagnosisEngine:
    """
    Diagnoses test failures by parsing errors and reading source code.

    Supports three depth modes:
    - "paths": Only suggest file paths, don't read
    - "excerpt": Read 20-30 lines around problem area (default)
    - "full": Read entire file and analyze completely
    """

    def __init__(self, project_root: Path, depth: str = "excerpt"):
        self.project_root = Path(project_root)
        self.depth = depth

        if depth not in ("paths", "excerpt", "full"):
            raise ValueError(f"Invalid depth: {depth}. Must be 'paths', 'excerpt', or 'full'")

    def diagnose(
        self,
        error_message: str,
        error_type: str,
        test_name: str,
        test_module: str = "",
    ) -> Diagnosis:
        """
        Diagnose a test failure.

        Args:
            error_message: The error message from the exception
            error_type: The exception type (ImportError, AttributeError, etc.)
            test_name: Name of the failing test
            test_module: Module being tested (agents, forecasting, etc.)

        Returns:
            Diagnosis object with suspected files, problem, and fix hypotheses
        """

        # Route to appropriate diagnostic strategy
        if error_type == "ImportError":
            return self._diagnose_import_error(error_message, test_name, test_module)
        elif error_type == "AttributeError":
            return self._diagnose_attribute_error(error_message, test_name, test_module)
        elif error_type == "AssertionError":
            return self._diagnose_assertion_error(error_message, test_name, test_module)
        elif error_type == "TypeError":
            return self._diagnose_type_error(error_message, test_name, test_module)
        elif error_type in ("ValueError", "RuntimeError"):
            return self._diagnose_value_error(error_message, test_name, test_module)
        elif error_type == "ModuleNotFoundError":
            return self._diagnose_module_not_found(error_message, test_name, test_module)
        else:
            return self._diagnose_generic(error_message, error_type, test_name, test_module)

    def _diagnose_import_error(self, msg: str, test_name: str, module: str) -> Diagnosis:
        """Diagnose: cannot import name 'X' from 'Y'"""

        # Parse: "cannot import name 'ForecastingAgent' from 'ai_research_framework.agents'"
        match = re.search(r"cannot import name ['\"](\w+)['\"] from ['\"]([^'\"]+)['\"]", msg)
        if match:
            class_name = match.group(1)
            module_path = match.group(2)
        else:
            # Fallback
            class_name = "Unknown"
            module_path = module or "ai_research_framework"

        # Convert module path to file path
        file_path = self.project_root / module_path.replace(".", "/") / "__init__.py"
        agent_file = self.project_root / module_path.replace(".", "/") / f"{self._snake_case(class_name)}.py"

        likely_files = [str(file_path), str(agent_file)]

        # Read files if configured
        excerpts = {}
        if self.depth in ("excerpt", "full"):
            excerpts = self._read_import_excerpts(file_path, class_name)

        hypotheses = [
            FixHypothesis(
                title=f"Check {file_path.name} -- {class_name} missing from imports or __all__",
                confidence="HIGH",
                description=f"The class {class_name} may not be exported from {module_path}",
                file_path=str(file_path),
                line_range=(1, 30),
                code_excerpt=excerpts.get("init_file"),
                action=f"Add line to imports:\nfrom .{self._snake_case(class_name)} import {class_name}\n\nAdd to __all__:\n'{class_name}'",
            ),
            FixHypothesis(
                title=f"Check {agent_file.name} -- class definition may not exist",
                confidence="MEDIUM",
                description=f"The file {agent_file.name} may not define class {class_name}",
                file_path=str(agent_file),
                line_range=(1, 50),
                code_excerpt=excerpts.get("agent_file"),
                action=f"Verify file contains:\nclass {class_name}:\n    def __init__(self): ...\n    def run(self, state: dict) -> dict: ...",
            ),
            FixHypothesis(
                title="Python path issue or circular import",
                confidence="LOW",
                description="The module exists but isn't accessible due to path or circular dependency",
                file_path=str(self.project_root / "ai_research_framework" / "__init__.py"),
                action=f"Run: python -c \"import {module_path}; print(dir())\"\nCheck if {class_name} appears in output",
            ),
        ]

        return Diagnosis(
            test_name=test_name,
            error_type="ImportError",
            error_message=msg,
            likely_files=likely_files,
            suspected_problem=f"{class_name} class not exported from {module_path}",
            fix_hypotheses=hypotheses,
        )

    def _diagnose_attribute_error(self, msg: str, test_name: str, module: str) -> Diagnosis:
        """Diagnose: 'X' object has no attribute 'Y'"""

        # Parse: "'CompiledStateGraph' object has no attribute 'graph'"
        match = re.search(r"['\"](\w+)['\"] object has no attribute ['\"](\w+)['\"]", msg)
        if match:
            obj_type = match.group(1)
            attr_name = match.group(2)
        else:
            obj_type = "Object"
            attr_name = "attribute"

        # Common files to check
        coordinator_file = self.project_root / "ai_research_framework" / "core" / "coordinator.py"
        state_file = self.project_root / "ai_research_framework" / "state" / "research_state.py"

        likely_files = [str(coordinator_file), str(state_file)]

        excerpts = {}
        if self.depth in ("excerpt", "full"):
            excerpts = self._read_attribute_excerpts(coordinator_file, state_file, attr_name)

        hypotheses = [
            FixHypothesis(
                title=f"Check {obj_type} class definition -- {attr_name} may not exist",
                confidence="HIGH",
                description=f"{obj_type} is missing the {attr_name} attribute or method",
                file_path=str(coordinator_file),
                code_excerpt=excerpts.get("coordinator"),
                action=f"Search coordinator.py for class {obj_type}\nVerify it has attribute/method: {attr_name}",
            ),
            FixHypothesis(
                title=f"LangGraph API change -- {obj_type} may have different interface",
                confidence="MEDIUM",
                description=f"Recent LangGraph update may have changed {obj_type} API",
                file_path=str(coordinator_file),
                action=f"Check LangGraph version in requirements.txt\nConsult LangGraph docs for CompiledStateGraph interface",
            ),
            FixHypothesis(
                title="Object not initialized correctly",
                confidence="LOW",
                description=f"{obj_type} instance may not have been fully initialized",
                file_path=str(coordinator_file),
                action=f"Verify __init__ in {obj_type} sets {attr_name} attribute\nCheck if __init__ is being called",
            ),
        ]

        return Diagnosis(
            test_name=test_name,
            error_type="AttributeError",
            error_message=msg,
            likely_files=likely_files,
            suspected_problem=f"{obj_type} missing {attr_name} attribute",
            fix_hypotheses=hypotheses,
        )

    def _diagnose_assertion_error(self, msg: str, test_name: str, module: str) -> Diagnosis:
        """Diagnose: AssertionError with message"""

        likely_files = [
            str(self.project_root / "ai_research_framework" / "config.py"),
            str(self.project_root / "ai_research_framework" / "state" / "research_state.py"),
        ]

        hypotheses = [
            FixHypothesis(
                title="Config value mismatch",
                confidence="HIGH",
                description="RAM budget, model count, or config value is incorrect",
                file_path=str(likely_files[0]),
                action="Review config.py values:\nRAM_BUDGET_MB, FORECASTING_MODELS, LLM_MODEL\nMatch test expectations",
            ),
            FixHypothesis(
                title="Data model field validation failed",
                confidence="MEDIUM",
                description="A dataclass field validation or instantiation failed",
                file_path=str(likely_files[1]),
                action="Check ModelForecast, SynthesisOutput, ValidationReport dataclass definitions\nVerify field types and defaults",
            ),
            FixHypothesis(
                title="Logic error in routing or state transition",
                confidence="MEDIUM",
                description="Conditional routing function returned unexpected value",
                file_path=str(self.project_root / "ai_research_framework" / "core" / "coordinator.py"),
                action="Review _should_continue_after_* functions in coordinator.py\nCheck conditional logic and return values",
            ),
        ]

        return Diagnosis(
            test_name=test_name,
            error_type="AssertionError",
            error_message=msg,
            likely_files=likely_files,
            suspected_problem="Test assertion failed -- likely config or logic issue",
            fix_hypotheses=hypotheses,
        )

    def _diagnose_type_error(self, msg: str, test_name: str, module: str) -> Diagnosis:
        """Diagnose: TypeError from wrong argument types"""

        # Parse: "__init__() missing 1 required positional argument: 'x'"
        match = re.search(r"(\w+)\(\) (.+)", msg)

        likely_files = [
            str(self.project_root / "ai_research_framework" / "state" / "research_state.py"),
            str(self.project_root / "ai_research_framework" / "agents"),
        ]

        hypotheses = [
            FixHypothesis(
                title="Dataclass __init__ signature mismatch",
                confidence="HIGH",
                description="Calling dataclass with wrong arguments or missing required fields",
                file_path=str(likely_files[0]),
                action="Check ModelForecast, SynthesisOutput instantiation\nVerify all required @dataclass fields are provided",
            ),
            FixHypothesis(
                title="Agent __init__ signature changed",
                confidence="MEDIUM",
                description="Agent initialization parameters don't match function signature",
                file_path=str(likely_files[1]),
                action="Review agent __init__ methods in agents/ directory\nCheck if NielsenConfig, IndeksDanmarkConfig are still required",
            ),
            FixHypothesis(
                title="Graph invocation called with wrong arguments",
                confidence="LOW",
                description="Calling graph.invoke() with incorrect state type",
                file_path=str(self.project_root / "ai_research_framework" / "core" / "coordinator.py"),
                action="Check coordinator.build_research_graph() and graph.invoke() calls\nVerify state dict structure matches ResearchState",
            ),
        ]

        return Diagnosis(
            test_name=test_name,
            error_type="TypeError",
            error_message=msg,
            likely_files=likely_files,
            suspected_problem="Function called with wrong argument types or count",
            fix_hypotheses=hypotheses,
        )

    def _diagnose_value_error(self, msg: str, test_name: str, module: str) -> Diagnosis:
        """Diagnose: ValueError from invalid data"""

        likely_files = [
            str(self.project_root / "ai_research_framework" / "agents"),
            str(self.project_root / "ai_research_framework" / "config.py"),
        ]

        hypotheses = [
            FixHypothesis(
                title="Feature engineering computed invalid value",
                confidence="HIGH",
                description="lag_12, price_per_unit, or other computed feature has NaN, Inf, or invalid range",
                file_path=str(likely_files[0]),
                action="Review feature engineering logic in agents\nCheck for division by zero, NaN handling, edge cases",
            ),
            FixHypothesis(
                title="Metric calculation with edge case data",
                confidence="MEDIUM",
                description="MAPE, RMSE, MAE calculation failed on edge case (zero ground truth, empty array, etc.)",
                file_path=str(likely_files[0]),
                action="Check metric functions for edge case handling\nAdd guards for zero ground truth, empty predictions",
            ),
            FixHypothesis(
                title="Config value out of valid range",
                confidence="LOW",
                description="RAM budget, model count, or threshold value is invalid",
                file_path=str(likely_files[1]),
                action="Review config.py values\nEnsure RAM_BUDGET_MB > 0, model list not empty",
            ),
        ]

        return Diagnosis(
            test_name=test_name,
            error_type="ValueError",
            error_message=msg,
            likely_files=likely_files,
            suspected_problem="Invalid value in feature engineering, metrics, or config",
            fix_hypotheses=hypotheses,
        )

    def _diagnose_module_not_found(self, msg: str, test_name: str, module: str) -> Diagnosis:
        """Diagnose: ModuleNotFoundError"""

        # Parse: "No module named 'ai_research_framework.core'"
        match = re.search(r"No module named ['\"]([^'\"]+)['\"]", msg)
        if match:
            missing_module = match.group(1)
        else:
            missing_module = "unknown"

        likely_files = [
            str(self.project_root / missing_module.split(".")[0]),
        ]

        hypotheses = [
            FixHypothesis(
                title="Module directory or __init__.py missing",
                confidence="HIGH",
                description=f"Directory {missing_module.replace('.', '/')} doesn't exist or __init__.py missing",
                file_path=str(self.project_root / missing_module.replace(".", "/")),
                action=f"Verify directory exists: ls -la ai_research_framework/{missing_module.split('.')[-1]}/\nVerify __init__.py exists",
            ),
            FixHypothesis(
                title="Typo in module path",
                confidence="MEDIUM",
                description=f"Module path {missing_module} may have typo",
                file_path=str(self.project_root / "ai_research_framework"),
                action=f"Check coordinator.py and agent files for correct module path\nCompare to actual directory structure",
            ),
            FixHypothesis(
                title="PYTHONPATH not set correctly",
                confidence="LOW",
                description="Virtual environment may not have correct PYTHONPATH",
                file_path=str(self.project_root),
                action="Ensure virtualenv is activated: source .venv/bin/activate\nRun: python -c 'import sys; print(sys.path)'",
            ),
        ]

        return Diagnosis(
            test_name=test_name,
            error_type="ModuleNotFoundError",
            error_message=msg,
            likely_files=likely_files,
            suspected_problem=f"Module {missing_module} not found in package",
            fix_hypotheses=hypotheses,
        )

    def _diagnose_generic(self, msg: str, error_type: str, test_name: str, module: str) -> Diagnosis:
        """Fallback diagnosis for unknown error types"""

        likely_files = [
            str(self.project_root / "ai_research_framework"),
        ]

        hypotheses = [
            FixHypothesis(
                title="Check test execution context and imports",
                confidence="MEDIUM",
                description="Error may be related to test setup or imports",
                file_path=str(self.project_root / "tests"),
                action="Review test file for setup/teardown\nCheck test imports match coordinator imports",
            ),
            FixHypothesis(
                title="Check git status for uncommitted changes",
                confidence="MEDIUM",
                description="Recent uncommitted changes may have broken something",
                file_path=str(self.project_root),
                action="Run: git status\nRun: git diff to see recent changes",
            ),
            FixHypothesis(
                title="Check dependencies and versions",
                confidence="LOW",
                description="Dependency version mismatch or missing package",
                file_path=str(self.project_root / "requirements.txt"),
                action="Run: pip install -r requirements.txt\nRun: pip list | grep -i lang",
            ),
        ]

        return Diagnosis(
            test_name=test_name,
            error_type=error_type,
            error_message=msg,
            likely_files=likely_files,
            suspected_problem=f"Unknown {error_type} -- see error message for details",
            fix_hypotheses=hypotheses,
        )

    # ============================================================================
    # HELPER METHODS FOR READING SOURCE CODE
    # ============================================================================

    def _read_import_excerpts(self, init_file: Path, class_name: str) -> Dict[str, Optional[str]]:
        """Read relevant excerpts from __init__.py and agent file"""

        excerpts = {"init_file": None, "agent_file": None}

        if self.depth == "paths":
            return excerpts

        # Read __init__.py
        if init_file.exists():
            try:
                content = init_file.read_text()
                lines = content.split('\n')

                # Show first 30 lines (imports + __all__)
                excerpt_lines = []
                for i, line in enumerate(lines[:30], 1):
                    excerpt_lines.append(f"{i:3d}  {line}")

                excerpts["init_file"] = '\n'.join(excerpt_lines)
            except Exception:
                pass

        # Read agent file
        agent_file = init_file.parent / f"{self._snake_case(class_name)}.py"
        if agent_file.exists() and self.depth == "full":
            try:
                content = agent_file.read_text()
                lines = content.split('\n')

                # Show first 50 lines or class definition
                excerpt_lines = []
                for i, line in enumerate(lines[:50], 1):
                    excerpt_lines.append(f"{i:3d}  {line}")

                excerpts["agent_file"] = '\n'.join(excerpt_lines)
            except Exception:
                pass

        return excerpts

    def _read_attribute_excerpts(
        self,
        coordinator_file: Path,
        state_file: Path,
        attr_name: str,
    ) -> Dict[str, Optional[str]]:
        """Read coordinator.py snippet showing graph/invoke usage"""

        excerpts = {"coordinator": None}

        if self.depth == "paths":
            return excerpts

        if coordinator_file.exists():
            try:
                content = coordinator_file.read_text()
                lines = content.split('\n')

                # Find relevant section (first 100 lines, focusing on graph building)
                excerpt_lines = []
                for i, line in enumerate(lines[:100], 1):
                    excerpt_lines.append(f"{i:3d}  {line}")

                excerpts["coordinator"] = '\n'.join(excerpt_lines)
            except Exception:
                pass

        return excerpts

    @staticmethod
    def _snake_case(name: str) -> str:
        """Convert CamelCase to snake_case"""
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
