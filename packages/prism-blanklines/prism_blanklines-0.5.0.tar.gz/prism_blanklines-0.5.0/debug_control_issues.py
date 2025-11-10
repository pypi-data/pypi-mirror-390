"""Debug control block blank line issues"""

from pathlib import Path
import tempfile
from prism.processor import FileProcessor
from prism.analyzer import FileAnalyzer
from prism.rules import BlankLineRuleEngine

print("=" * 70)
print("BUG 1: Blank line added after if statement before imports")
print("=" * 70)

testCode1 = '''def chown(path, username):
  """Docstring"""
  from catapult.config.osdep import IS_LINUX

  if (IS_LINUX) and path and username:
    from errno import EINVAL
    from grp import getgrnam
'''

print("\nINPUT:")
print(testCode1)

analyzer = FileAnalyzer()
statements = analyzer.analyzeFile(testCode1.split('\n'))

print("\nSTATEMENTS:")
for i, stmt in enumerate(statements):
  typeStr = 'BLANK' if stmt.isBlank else stmt.blockType.name
  print(f'{i}: {typeStr:12} indent={stmt.indentLevel:2} line={repr(stmt.lines[0][:50]) if stmt.lines else ""}')

ruleEngine = BlankLineRuleEngine()
blankLineCounts = ruleEngine.applyRules(statements)

print("\nBLANK LINE COUNTS:")
for i, (stmt, count) in enumerate(zip(statements, blankLineCounts)):
  typeStr = 'BLANK' if stmt.isBlank else stmt.blockType.name
  print(f'{i}: {typeStr:12} -> count={count}')

with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
  f.write(testCode1)
  f.flush()
  FileProcessor.processFile(Path(f.name))
  with open(f.name) as r:
    result1 = r.read()

print("\nOUTPUT:")
print(result1)

print("\n" + "=" * 70)
print("BUG 2: Blank line removed between consecutive if statements")
print("=" * 70)

testCode2 = '''def makeDir(path):
  """Docstring"""
  if (not wasDir or forceGroup) and isDir:
    chgrp(path, groupname)

  if (not wasDir or forceMode) and isDir:
    chmod(path, mode)
'''

print("\nINPUT:")
print(testCode2)

statements = analyzer.analyzeFile(testCode2.split('\n'))

print("\nSTATEMENTS:")
for i, stmt in enumerate(statements):
  typeStr = 'BLANK' if stmt.isBlank else stmt.blockType.name
  print(f'{i}: {typeStr:12} indent={stmt.indentLevel:2} line={repr(stmt.lines[0][:50]) if stmt.lines else ""}')

blankLineCounts = ruleEngine.applyRules(statements)

print("\nBLANK LINE COUNTS:")
for i, (stmt, count) in enumerate(zip(statements, blankLineCounts)):
  typeStr = 'BLANK' if stmt.isBlank else stmt.blockType.name
  print(f'{i}: {typeStr:12} -> count={count}')

with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
  f.write(testCode2)
  f.flush()
  FileProcessor.processFile(Path(f.name))
  with open(f.name) as r:
    result2 = r.read()

print("\nOUTPUT:")
print(result2)
