import unittest

from rabbit_bq_job_optimizer.models import OptimizationResult, parse_optimization_response


class OptimizationResponseDeserializationTest(unittest.TestCase):
    def test_optimization_results_are_dataclasses(self):
        response_data = {
            "optimizedJob": {"configuration": {"query": {"query": "SELECT 1"}}},
            "optimizationResults": [
                {
                    "type": "reservation_assignment",
                    "performed": True,
                    "estimatedSavings": 1.23,
                    "context": {"comment": "example"},
                    "changes": [
                        {"op": "replace", "path": "/reservation", "value": "projects/foo/locations/US/reservations/bar"}
                    ],
                }
            ],
            "estimatedSavings": 1.23,
            "optimizationPerformed": True,
        }

        response = parse_optimization_response(response_data)

        optimization_result = response.optimizationResults[0]

        print(f"Type of optimization_result: {type(optimization_result)}")

        self.assertIsInstance(optimization_result, OptimizationResult)
        self.assertEqual(optimization_result.type, "reservation_assignment")
        self.assertTrue(optimization_result.performed)
        self.assertEqual(optimization_result.estimatedSavings, 1.23)
        self.assertEqual(optimization_result.context["comment"], "example")
        self.assertEqual(
            optimization_result.changes,
            [{"op": "replace", "path": "/reservation", "value": "projects/foo/locations/US/reservations/bar"}],
        )


if __name__ == "__main__":
    unittest.main()

