path = r"ner-pk/tests/test_submission_pipeline.py"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

text = text.replace("import pytest", "try:\n    import pytest\nexcept ImportError:\n    pytest = None")
text = text.replace("@pytest.fixture(scope=\"module\")\ndef predictor():", "def predictor():")

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

print("Updated test_submission_pipeline.py")
