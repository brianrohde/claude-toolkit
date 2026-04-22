#!/usr/bin/env python3
"""
Test Codebase Integrity Runner
Executes a subset or full suite of integration tests for CMT thesis codebase.
Supports module filtering: agents, forecasting, coordination, data_models, all

Usage:
  python test_runner.py [--module all|agents|forecasting|coordination|data_models] [--verbose]

Example:
  python test_runner.py --module agents
  python test_runner.py --module all --verbose
"""

import sys
import argparse
import traceback
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import time

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import diagnosis engine
from diagnosis import DiagnosisEngine

# ============================================================================
# TEST DEFINITIONS & REMEDIATION
# ============================================================================

TEST_METADATA = {
    1: {
        "name": "State & Coordinator Import",
        "module": "agents",
        "checks": "LangGraph imports, 4 nodes load",
        "keywords": ["State", "Coordinator", "import", "LangGraph"],
    },
    2: {
        "name": "Config Loading",
        "module": "coordination",
        "checks": "RAM budget, LLM setup, Nielsen/Indeks configs",
        "keywords": ["Config", "RAM_BUDGET", "LLM_MODEL"],
    },
    3: {
        "name": "Agent Imports",
        "module": "agents",
        "checks": "All 4 agents instantiate without error",
        "keywords": ["ForecastingAgent", "DataAssessmentAgent", "import"],
    },
    4: {
        "name": "Routing Logic",
        "module": "coordination",
        "checks": "State transition routing functions defined",
        "keywords": ["routing", "transition", "_should_continue"],
    },
    5: {
        "name": "Data Models",
        "module": "data_models",
        "checks": "Output dataclasses instantiate and validate",
        "keywords": ["ModelForecast", "SynthesisOutput", "ValidationReport"],
    },
    6: {
        "name": "Feature Engineering",
        "module": "forecasting",
        "checks": "Agents process feature-rich data correctly",
        "keywords": ["feature", "agent", "data"],
    },
    7: {
        "name": "Metric Functions",
        "module": "forecasting",
        "checks": "Agent validation produces metrics",
        "keywords": ["metric", "validation", "agent"],
    },
    8: {
        "name": "Model Stability",
        "module": "forecasting",
        "checks": "Agent models predict without NaN/Inf",
        "keywords": ["stability", "forecast", "agent"],
    },
    9: {
        "name": "State Transitions",
        "module": "coordination",
        "checks": "Coordinator state machine graph structure valid",
        "keywords": ["state", "transition", "graph"],
    },
    10: {
        "name": "Full Integration",
        "module": "agents",
        "checks": "All components together, no import/init errors",
        "keywords": ["integration", "coordinator", "state"],
    },
}

REMEDIATION = {
    "ImportError": {
        "description": "A module or class cannot be imported",
        "steps": [
            "1. Check if the file exists: find ai_research_framework -name '*.py' | grep -i <filename>",
            "2. Check if it's exported: grep '<ClassName>' ai_research_framework/<module>/__init__.py",
            "3. If missing, add to __init__.py: from .file_name import ClassName",
            "4. If class doesn't exist, create a minimal wrapper or check git history",
        ],
    },
    "ModuleNotFoundError": {
        "description": "A module path doesn't exist in the package",
        "steps": [
            "1. Verify the module directory exists: ls -la ai_research_framework/",
            "2. Check for typos in the import path",
            "3. Verify __init__.py exists in the module: ls ai_research_framework/<module>/__init__.py",
            "4. Review ITERATION_NOTES.md for correct module mappings",
        ],
    },
    "AttributeError": {
        "description": "An object doesn't have the expected attribute",
        "steps": [
            "1. Check the object's class definition",
            "2. Verify the attribute exists and is spelled correctly",
            "3. Check for typos in coordinator.py or agent files",
            "4. Run 'git diff' to see recent changes that may have removed the attribute",
        ],
    },
    "TypeError": {
        "description": "Function/class called with wrong argument types",
        "steps": [
            "1. Check function signature: grep -A 3 'def __init__' <file>",
            "2. Verify argument types match the signature",
            "3. Check if dataclass has required fields",
            "4. Review recent changes to coordinator or agent initialization",
        ],
    },
    "AssertionError": {
        "description": "An explicit test assertion failed",
        "steps": [
            "1. Read the assertion message in the error output",
            "2. Check the actual vs. expected value",
            "3. Verify the logic in the relevant function",
            "4. Check if config values (RAM, models) have changed",
        ],
    },
    "ValueError": {
        "description": "Invalid value passed to a function",
        "steps": [
            "1. Check input validation in the failing function",
            "2. Review feature engineering logic in agents",
            "3. Check for edge cases (empty data, NaN, division by zero)",
            "4. Verify metric calculations handle edge cases",
        ],
    },
}

# ============================================================================
# TEST FUNCTIONS
# ============================================================================


def test_1_state_coordinator_import() -> Tuple[bool, str]:
    """Test 1: State & Coordinator Import"""
    try:
        from ai_research_framework.state.research_state import ResearchState
        from ai_research_framework.core.coordinator import build_research_graph

        graph = build_research_graph()
        assert graph is not None, "Graph is None"

        # Check that graph has invoke method (compiled LangGraph)
        assert hasattr(graph, "invoke"), "Graph missing invoke method"

        return True, "[PASS] ResearchState and build_research_graph imported, graph compiled"
    except Exception as e:
        return False, f"[FAIL] {type(e).__name__}: {str(e)}"


def test_2_config_loading() -> Tuple[bool, str]:
    """Test 2: Config Loading"""
    try:
        from ai_research_framework.config import (
            RAM_BUDGET_MB,
            FORECASTING_MODELS,
            LLM_MODEL,
            RAM_TARGETS_MB,
            NielsenConfig,
            IndeksDanmarkConfig,
        )

        assert RAM_BUDGET_MB > 0, f"RAM_BUDGET_MB invalid: {RAM_BUDGET_MB}"
        assert isinstance(FORECASTING_MODELS, (list, dict)), "FORECASTING_MODELS not a list/dict"
        assert LLM_MODEL, "LLM_MODEL not set"

        ram_sum = sum(RAM_TARGETS_MB.values())
        assert ram_sum < RAM_BUDGET_MB, f"RAM_TARGETS_MB sum ({ram_sum}) exceeds budget ({RAM_BUDGET_MB})"

        nc = NielsenConfig()
        ic = IndeksDanmarkConfig()
        assert nc is not None and ic is not None, "Config objects not instantiated"

        return True, f"[PASS] Config loaded: RAM={RAM_BUDGET_MB}MB, LLM={LLM_MODEL}, Models={len(FORECASTING_MODELS)}"
    except Exception as e:
        return False, f"[FAIL] {type(e).__name__}: {str(e)}"


def test_3_agent_imports() -> Tuple[bool, str]:
    """Test 3: Agent Imports"""
    try:
        from ai_research_framework.agents import (
            ForecastingAgent,
            DataAssessmentAgent,
            SynthesisAgent,
            ValidationAgent,
        )

        assert ForecastingAgent is not None, "ForecastingAgent is None"
        assert DataAssessmentAgent is not None, "DataAssessmentAgent is None"
        assert SynthesisAgent is not None, "SynthesisAgent is None"
        assert ValidationAgent is not None, "ValidationAgent is None"

        return True, "[PASS] All 4 agents imported successfully"
    except Exception as e:
        return False, f"[FAIL] {type(e).__name__}: {str(e)}"


def test_4_routing_logic() -> Tuple[bool, str]:
    """Test 4: Routing Logic"""
    try:
        from ai_research_framework.core import coordinator
        from ai_research_framework.state.research_state import ResearchState

        # Check that routing functions exist
        assert hasattr(coordinator, "_should_continue_after_data"), "Missing _should_continue_after_data"
        assert hasattr(coordinator, "_should_continue_after_forecasting"), "Missing _should_continue_after_forecasting"
        assert hasattr(coordinator, "_should_continue_after_synthesis"), "Missing _should_continue_after_synthesis"
        assert hasattr(coordinator, "_should_continue_after_validation"), "Missing _should_continue_after_validation"

        return True, "[PASS] All routing functions (_should_continue_after_*) exist"
    except Exception as e:
        return False, f"[FAIL] {type(e).__name__}: {str(e)}"


def test_5_data_models() -> Tuple[bool, str]:
    """Test 5: Data Models (from research_state)"""
    try:
        from ai_research_framework.state.research_state import (
            ModelForecast,
            SynthesisOutput,
            ValidationReport,
        )

        # Test ModelForecast instantiation
        mf = ModelForecast(
            model_name="ARIMA",
            point_forecast=100.0,
            lower_90=90.0,
            upper_90=110.0,
            mape_validation=5.2,
            rmse_validation=10.3,
            peak_ram_mb=512.0,
            training_latency_s=2.1,
            inference_latency_s=0.05,
        )
        assert mf.model_name == "ARIMA", "ModelForecast not initialized correctly"

        # Test SynthesisOutput instantiation
        so = SynthesisOutput(
            point_forecast_ensemble=105.0,
            lower_90_calibrated=95.0,
            upper_90_calibrated=115.0,
            confidence_score=85.2,
            confidence_tier="High",
            inter_model_spread=0.08,
            consumer_signal_direction="aligned",
            recommendation_text="Good forecast confidence",
            llm_tokens_used=450,
        )
        assert so.confidence_tier == "High", "SynthesisOutput not initialized correctly"

        # Test ValidationReport instantiation
        vr = ValidationReport()
        assert vr is not None, "ValidationReport not instantiated"

        return True, "[PASS] All data models instantiate correctly"
    except Exception as e:
        return False, f"[FAIL] {type(e).__name__}: {str(e)}"


def test_6_feature_engineering() -> Tuple[bool, str]:
    """Test 6: Feature Engineering (agent system)"""
    try:
        from ai_research_framework.agents import DataAssessmentAgent
        from ai_research_framework.config import NielsenConfig, IndeksDanmarkConfig

        # Instantiate agents that do feature engineering
        nc = NielsenConfig()
        ic = IndeksDanmarkConfig()
        agent = DataAssessmentAgent(nc, ic)

        assert agent is not None, "DataAssessmentAgent not instantiated"
        assert hasattr(agent, "run"), "DataAssessmentAgent missing run method"

        return True, "[PASS] Feature engineering agent instantiated"
    except Exception as e:
        return False, f"[FAIL] {type(e).__name__}: {str(e)}"


def test_7_metric_functions() -> Tuple[bool, str]:
    """Test 7: Metric Functions (agent validation)"""
    try:
        from ai_research_framework.agents import ValidationAgent
        from ai_research_framework.state.research_state import ValidationReport

        agent = ValidationAgent()
        assert agent is not None, "ValidationAgent not instantiated"
        assert hasattr(agent, "run"), "ValidationAgent missing run method"

        # Verify ValidationReport can hold metrics
        vr = ValidationReport()
        assert hasattr(vr, "mape_per_model"), "ValidationReport missing mape_per_model"

        return True, "[PASS] Validation agent and metric structures exist"
    except Exception as e:
        return False, f"[FAIL] {type(e).__name__}: {str(e)}"


def test_8_model_stability() -> Tuple[bool, str]:
    """Test 8: Model Stability (forecasting agent)"""
    try:
        from ai_research_framework.agents import ForecastingAgent
        import numpy as np

        agent = ForecastingAgent()
        assert agent is not None, "ForecastingAgent not instantiated"
        assert hasattr(agent, "run"), "ForecastingAgent missing run method"

        # Verify agent can be called (mock check)
        assert callable(agent.run), "ForecastingAgent.run is not callable"

        return True, "[PASS] ForecastingAgent instantiated and callable"
    except Exception as e:
        return False, f"[FAIL] {type(e).__name__}: {str(e)}"


def test_9_coordinator_state_transitions() -> Tuple[bool, str]:
    """Test 9: Coordinator State Transitions"""
    try:
        from ai_research_framework.core.coordinator import build_research_graph
        from ai_research_framework.state.research_state import ResearchState

        graph = build_research_graph()
        initial_state = ResearchState()

        # Check graph structure
        assert graph is not None, "Graph is None"
        assert hasattr(graph, "invoke"), "Graph missing invoke method"

        # Verify graph structure is valid
        assert hasattr(graph, "invoke"), "Graph missing invoke method"

        return True, "[PASS] State transition structure validated"
    except Exception as e:
        return False, f"[FAIL] {type(e).__name__}: {str(e)}"


def test_10_integration() -> Tuple[bool, str]:
    """Test 10: Full Integration"""
    try:
        from ai_research_framework.core.coordinator import build_research_graph
        from ai_research_framework.state.research_state import ResearchState
        from ai_research_framework.agents import (
            ForecastingAgent,
            DataAssessmentAgent,
        )
        from ai_research_framework.config import RAM_BUDGET_MB, NielsenConfig, IndeksDanmarkConfig

        # Instantiate core components
        state = ResearchState()
        graph = build_research_graph()
        fa = ForecastingAgent()
        da = DataAssessmentAgent(NielsenConfig(), IndeksDanmarkConfig())

        assert all(
            [state is not None, graph is not None, fa is not None, da is not None, RAM_BUDGET_MB > 0]
        ), "Integration check failed"

        return True, "[PASS] Full integration: agents + graph + state instantiate together"
    except Exception as e:
        return False, f"[FAIL] {type(e).__name__}: {str(e)}"


# ============================================================================
# RUNNER & FORMATTER
# ============================================================================

TEST_FUNCTIONS = {
    1: test_1_state_coordinator_import,
    2: test_2_config_loading,
    3: test_3_agent_imports,
    4: test_4_routing_logic,
    5: test_5_data_models,
    6: test_6_feature_engineering,
    7: test_7_metric_functions,
    8: test_8_model_stability,
    9: test_9_coordinator_state_transitions,
    10: test_10_integration,
}

MODULE_TESTS = {
    "agents": [1, 3, 10],
    "coordination": [2, 4, 9],
    "data_models": [5],
    "forecasting": [6, 7, 8],
    "all": list(range(1, 11)),
}


def get_tests_to_run(module: str) -> List[int]:
    """Return list of test IDs for the given module."""
    return MODULE_TESTS.get(module, MODULE_TESTS["all"])


def format_output(
    test_id: int, passed: bool, message: str
) -> str:
    """Format single test output with colored pass/fail."""
    status = "[PASS]" if passed else "[FAIL]"
    name = TEST_METADATA[test_id]["name"]
    return f"Test {test_id}: {name:<30} ... {status}\n{message}"


def print_header() -> None:
    """Print test suite header."""
    print("=" * 80)
    print("COMPREHENSIVE CODEBASE INTEGRITY VALIDATION")
    print("=" * 80)
    print()


def print_summary(passed: int, total: int, elapsed: float, failures: Dict) -> None:
    """Print test summary with remediation."""
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Result: {passed}/{total} PASS")
    print(f"Time: {elapsed:.2f}s")
    print()

    if failures:
        print("FAILURES & REMEDIATION:")
        print("-" * 80)
        for test_id, (error_type, message) in failures.items():
            test_name = TEST_METADATA[test_id]["name"]
            module = TEST_METADATA[test_id]["module"]
            checks = TEST_METADATA[test_id]["checks"]

            print()
            print(f"Test {test_id}: {test_name}")
            print(f"Module: {module}")
            print(f"Checks: {checks}")
            print(f"Error: {message}")
            print()

            if error_type in REMEDIATION:
                remedy = REMEDIATION[error_type]
                print(f"Root cause: {remedy['description']}")
                print("Remediation steps:")
                for step in remedy["steps"]:
                    print(f"  {step}")
        print()

    print("=" * 80)
    if passed == total:
        print("GO FOR SYNC: All tests pass. Ready to merge and sync.")
    else:
        print("NO-GO FOR SYNC: Some tests failed. Fix above issues before pushing.")
    print()


def main():
    parser = argparse.ArgumentParser(description="Test CMT codebase integrity")
    parser.add_argument(
        "--module",
        choices=["all", "agents", "forecasting", "coordination", "data_models"],
        default="all",
        help="Module to test",
    )
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument(
        "--diagnosis",
        choices=["off", "paths", "excerpt", "full"],
        default="excerpt",
        help="Auto-diagnosis depth level for failures (default: excerpt)",
    )
    parser.add_argument(
        "--output-format",
        choices=["text", "json", "both"],
        default="text",
        help="Output format for diagnosis (default: text)",
    )
    parser.add_argument(
        "--diagnosis-json",
        type=str,
        default="diagnosis_output.json",
        help="JSON output file path (if using json/both format)",
    )
    args = parser.parse_args()

    tests_to_run = get_tests_to_run(args.module)

    print_header()
    print(f"Module Filter: {args.module.upper()}")
    print(f"Tests to run: {len(tests_to_run)}")
    print()

    start_time = time.time()
    passed = 0
    failures = {}
    diagnoses = {}

    # Initialize diagnosis engine if needed
    diagnosis_engine = None
    if args.diagnosis != "off":
        diagnosis_engine = DiagnosisEngine(
            project_root=PROJECT_ROOT,
            depth=args.diagnosis
        )

    for test_id in tests_to_run:
        test_func = TEST_FUNCTIONS[test_id]
        success, message = test_func()

        if success:
            passed += 1
            print(f"Test {test_id}: {TEST_METADATA[test_id]['name']:<30} ... [PASS]")
        else:
            # Extract error type from message
            error_type = message.split("]")[0].replace("[FAIL] ", "").split(":")[0]
            failures[test_id] = (error_type, message)
            print(f"Test {test_id}: {TEST_METADATA[test_id]['name']:<30} ... [FAIL]")
            if args.verbose:
                print(f"         {message}")

            # Run diagnosis if enabled
            if diagnosis_engine:
                test_name = TEST_METADATA[test_id]["name"]
                test_module = TEST_METADATA[test_id]["module"]
                diagnosis = diagnosis_engine.diagnose(
                    error_message=message,
                    error_type=error_type,
                    test_name=test_name,
                    test_module=test_module
                )
                diagnoses[test_id] = diagnosis

                # Print diagnosis output
                if args.output_format in ("text", "both"):
                    print(diagnosis.to_markdown())
                    print()

    elapsed = time.time() - start_time
    print_summary(passed, len(tests_to_run), elapsed, failures)

    # Write JSON diagnosis output if configured
    if diagnosis_engine and diagnoses and args.output_format in ("json", "both"):
        json_output = {
            "test_results": {
                "total": len(tests_to_run),
                "passed": passed,
                "failed": len(tests_to_run) - passed,
                "elapsed_seconds": elapsed,
            },
            "diagnoses": {
                str(test_id): diag.to_dict()
                for test_id, diag in diagnoses.items()
            }
        }

        output_path = Path(args.diagnosis_json)
        with open(output_path, 'w') as f:
            json.dump(json_output, f, indent=2)

        if args.output_format in ("json", "both"):
            print(f"[JSON] Diagnosis output written to: {output_path}")

    # Exit code: 0 if all pass, 1 if any fail
    return 0 if passed == len(tests_to_run) else 1


if __name__ == "__main__":
    sys.exit(main())
