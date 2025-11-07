from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class OptimizationConfig:
    type: str
    defaultPricingMode: Optional[str] = None
    config: Optional[Dict[str, Any]] = None


@dataclass
class OptimizationResult:
    type: str
    changes: List[Dict[str, Any]]
    context: Dict[str, Any]
    estimatedSavings: float
    performed: bool


@dataclass
class OptimizationResponse:
    optimizedJob: Dict[str, Any]
    optimizationResults: List[OptimizationResult]
    estimatedSavings: float
    optimizationPerformed: bool


def parse_optimization_response(data: Dict[str, Any]) -> OptimizationResponse:
    parsed_data = dict(data)

    optimization_results_payload = parsed_data.get("optimizationResults", []) or []
    parsed_results: List[OptimizationResult] = []
    for result in optimization_results_payload:
        if isinstance(result, OptimizationResult):
            parsed_results.append(result)
            continue

        result_dict = dict(result)
        result_dict.setdefault("changes", [])
        result_dict.setdefault("context", {})
        result_dict.setdefault("estimatedSavings", 0)
        result_dict.setdefault("performed", False)

        parsed_results.append(OptimizationResult(**result_dict))

    parsed_data["optimizationResults"] = parsed_results

    return OptimizationResponse(**parsed_data) 