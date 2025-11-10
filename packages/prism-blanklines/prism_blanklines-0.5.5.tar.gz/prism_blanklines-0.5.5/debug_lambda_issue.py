"""Debug lambda expressions in method calls"""

from prism.classifier import StatementClassifier
from prism.types import BlockType

# Test the statements from the user's example
lines = [
    "output[STUDY].sort(key=lambda k: k[SDATE])",
    "output[STUDY].reverse()  # Reverse the ordering of studies",
    "output[PATIENT].sort(key=lambda k: k[PNAME])",
    "what = 'all' if obj is None else obj"
]

print("=== STATEMENT CLASSIFICATION ===")
for line in lines:
    blockType = StatementClassifier.classifyStatement([line])
    print(f"{blockType.name:15} | {line[:80]}")
