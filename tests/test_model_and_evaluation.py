import unittest
from pathlib import Path

from nastech_tts.evaluation import predicted_fidelity, run_behavior_suite
from nastech_tts.model import NASTECH_ORPHEUS_V1
from nastech_tts.types import Fidelity

PROJECT_ROOT = Path(__file__).resolve().parents[1]


class NastechSingleModelTests(unittest.TestCase):
    def test_selected_model_is_ready_made_orpheus_finetune(self):
        self.assertEqual(NASTECH_ORPHEUS_V1.product_model_id, "nastech-voice-en-v1")
        self.assertEqual(NASTECH_ORPHEUS_V1.upstream_model_id, "canopylabs/orpheus-3b-0.1-ft")
        self.assertEqual(NASTECH_ORPHEUS_V1.upstream_license, "Apache-2.0")
        self.assertEqual(NASTECH_ORPHEUS_V1.direct_emotions, ())
        self.assertIn("cough", NASTECH_ORPHEUS_V1.direct_sounds)
        self.assertIn("laugh", NASTECH_ORPHEUS_V1.direct_sounds)

    def test_behavior_suite_matches_base_model_capability_contract(self):
        suite_path = PROJECT_ROOT / "evaluation" / "fixtures" / "behavior_suite.json"
        results = run_behavior_suite(suite_path)
        self.assertEqual(len(results), 5)
        self.assertTrue(all(result.passed for result in results))

    def test_sadness_is_approximated_until_adapter_training(self):
        markup = '<speak><emotion name="sad" intensity="0.7">I am sorry.</emotion></speak>'
        self.assertEqual(predicted_fidelity(markup), Fidelity.APPROXIMATED)

    def test_sound_capability_is_direct(self):
        markup = '<speak>One moment.<sound type="cough" /></speak>'
        self.assertEqual(predicted_fidelity(markup), Fidelity.DIRECT)


if __name__ == "__main__":
    unittest.main()
