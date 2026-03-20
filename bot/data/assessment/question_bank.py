"""Re-export question_bank from service layer."""
import importlib.util
import os

_service_path = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "service", "data", "assessment", "question_bank.py"
)
_spec = importlib.util.spec_from_file_location("_service_question_bank", _service_path)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

QUESTIONS = _mod.QUESTIONS
CATEGORIES = _mod.CATEGORIES
