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
    performed: bool
    estimatedSavings: float
    context: Dict[str, Any]


@dataclass
class OptimizationResponse:
    optimizedJob: Dict[str, Any]
    optimizationResults: List[OptimizationResult]
    estimatedSavings: float
    optimizationPerformed: bool


def parse_optimization_response(data: Dict[str, Any]) -> OptimizationResponse:
    parsed_data = dict(data)

    optimization_results_payload = parsed_data.get("optimizationResults", []) or []
    parsed_data["optimizationResults"] = [
        result if isinstance(result, OptimizationResult) else OptimizationResult(**result)
        for result in optimization_results_payload
    ]

    return OptimizationResponse(**parsed_data) 