"""
Tests for statement classifier.
Copyright (c) 2025-2026 Greg Smethells. All rights reserved.
See the accompanying AUTHORS file for a complete list of authors.
This file is subject to the terms and conditions defined in LICENSE.
"""

from prism.classifier import StatementClassifier
from prism.types import BlockType


class TestStatementClassifier:
  def testAssignmentClassification(self):
    # Variable assignment
    assert StatementClassifier.classifyStatement(['x = 1']) == BlockType.ASSIGNMENT
    assert StatementClassifier.classifyStatement(['result = func()']) == BlockType.ASSIGNMENT

    # Multiline assignment
    lines = ['result = complexFunction(', '  arg1,', '  arg2', ')']

    assert StatementClassifier.classifyStatement(lines) == BlockType.ASSIGNMENT

  def testCallClassification(self):
    assert StatementClassifier.classifyStatement(['func()']) == BlockType.CALL
    assert StatementClassifier.classifyStatement(['pass']) == BlockType.CALL
    assert StatementClassifier.classifyStatement(['assert x']) == BlockType.CALL
    assert StatementClassifier.classifyStatement(['raise ValueError()']) == BlockType.CALL

  def testFlowControlClassification(self):
    assert StatementClassifier.classifyStatement(['return x']) == BlockType.FLOW_CONTROL
    assert StatementClassifier.classifyStatement(['return']) == BlockType.FLOW_CONTROL
    assert StatementClassifier.classifyStatement(['yield item']) == BlockType.FLOW_CONTROL
    assert StatementClassifier.classifyStatement(['yield from generator()']) == BlockType.FLOW_CONTROL

  def testImportClassification(self):
    assert StatementClassifier.classifyStatement(['import sys']) == BlockType.IMPORT
    assert StatementClassifier.classifyStatement(['from os import path']) == BlockType.IMPORT

  def testControlClassification(self):
    assert StatementClassifier.classifyStatement(['if True:']) == BlockType.CONTROL
    assert StatementClassifier.classifyStatement(['for i in range(10):']) == BlockType.CONTROL
    assert StatementClassifier.classifyStatement(['try:']) == BlockType.CONTROL

  def testDefinitionClassification(self):
    assert StatementClassifier.classifyStatement(['def func():']) == BlockType.DEFINITION
    assert StatementClassifier.classifyStatement(['class MyClass:']) == BlockType.DEFINITION
    assert StatementClassifier.classifyStatement(['@decorator']) == BlockType.DEFINITION

  def testSecondaryClause(self):
    assert StatementClassifier.isSecondaryClause('elif condition:')
    assert StatementClassifier.isSecondaryClause('else:')
    assert StatementClassifier.isSecondaryClause('except Exception:')
    assert StatementClassifier.isSecondaryClause('finally:')
    assert not StatementClassifier.isSecondaryClause('if condition:')


class TestClassifierRegressions:
  """Regression tests for classifier bugs"""

  def testAsyncDefClassifiedAsDefinition(self):
    """Regression: async def should be DEFINITION, not CALL"""

    asyncDefLine = ['  async def method(self):']
    blockType = StatementClassifier.classifyStatement(asyncDefLine)

    assert blockType == BlockType.DEFINITION, f'async def should be DEFINITION, got {blockType.name}'

    # Test regular def for comparison
    defLine = ['  def method(self):']
    blockType = StatementClassifier.classifyStatement(defLine)

    assert blockType == BlockType.DEFINITION

  def testDictionaryAssignmentWithStringKeyClassification(self):
    """Regression: environ['STRING_KEY'] = value was misclassified as CALL instead of ASSIGNMENT"""

    # Test dictionary assignment with string literal key
    line1 = ["  environ['JOINTS_TEST_SUITE'] = 'True'"]
    blockType1 = StatementClassifier.classifyStatement(line1)

    assert blockType1 == BlockType.ASSIGNMENT, f"environ['STRING'] = value should be ASSIGNMENT, got {blockType1.name}"

    # Test dictionary assignment with constant key
    line2 = ["  environ[CONSTANT_KEY] = 'False'"]
    blockType2 = StatementClassifier.classifyStatement(line2)

    assert blockType2 == BlockType.ASSIGNMENT, f'environ[CONSTANT] = value should be ASSIGNMENT, got {blockType2.name}'

    # Test with attribute access in key
    line3 = ["  environ[Secret.KEY] = 'value'"]
    blockType3 = StatementClassifier.classifyStatement(line3)

    assert blockType3 == BlockType.ASSIGNMENT, f'environ[obj.attr] = value should be ASSIGNMENT, got {blockType3.name}'

  def testIfStatementWithParenthesesClassifiedAsControl(self):
    """Regression: if statements with parentheses should be CONTROL, not CALL"""

    # Test various if statement formats
    lines1 = ['  if (IS_LINUX) and path and username:']
    blockType1 = StatementClassifier.classifyStatement(lines1)

    assert blockType1 == BlockType.CONTROL, f'if (complex) should be CONTROL, got {blockType1.name}'

    lines2 = ['  if (not wasDir or forceMode) and isDir:']
    blockType2 = StatementClassifier.classifyStatement(lines2)

    assert blockType2 == BlockType.CONTROL, f'if (complex boolean) should be CONTROL, got {blockType2.name}'

    lines3 = ['  while (x > 0) and (y < 10):']
    blockType3 = StatementClassifier.classifyStatement(lines3)

    assert blockType3 == BlockType.CONTROL, f'while (complex) should be CONTROL, got {blockType3.name}'

  def testReturnAndYieldClassifiedAsFlowControl(self):
    """Regression: return and yield should be FLOW_CONTROL, not CALL"""

    # Test return statements
    assert StatementClassifier.classifyStatement(['return result']) == BlockType.FLOW_CONTROL
    assert StatementClassifier.classifyStatement(['return']) == BlockType.FLOW_CONTROL

    # Test yield statements
    assert StatementClassifier.classifyStatement(['yield item']) == BlockType.FLOW_CONTROL
    assert StatementClassifier.classifyStatement(['yield from generator()']) == BlockType.FLOW_CONTROL

    # Test that other keywords remain CALL
    assert StatementClassifier.classifyStatement(['assert condition']) == BlockType.CALL
    assert StatementClassifier.classifyStatement(['raise ValueError()']) == BlockType.CALL
    assert StatementClassifier.classifyStatement(['pass']) == BlockType.CALL
    assert StatementClassifier.classifyStatement(['del item']) == BlockType.CALL

  def testControlStatementWithEqualsInStringLiteral(self):
    """Regression: if 'CN=' in subject was misclassified as ASSIGNMENT due to equals in string"""

    # Control statement with equals sign in string literal
    assert StatementClassifier.classifyStatement(["if subject is not None and 'CN=' in subject:"]) == BlockType.CONTROL

    # Control statement with equals in various string formats
    assert StatementClassifier.classifyStatement(['if "key=value" in text:']) == BlockType.CONTROL
    assert StatementClassifier.classifyStatement(["if 'x=5' in data:"]) == BlockType.CONTROL

  def testYieldWithParenthesesClassifiedAsFlowControl(self):
    """Regression: yield (Status.SUCCESS, None) was misclassified as CALL instead of FLOW_CONTROL"""

    # yield with parentheses (tuple syntax)
    assert StatementClassifier.classifyStatement(['yield (Status.SUCCESS, None)']) == BlockType.FLOW_CONTROL

    # yield with function call result
    assert StatementClassifier.classifyStatement(['yield getData()']) == BlockType.FLOW_CONTROL

    # return with parentheses
    assert StatementClassifier.classifyStatement(['return (x, y)']) == BlockType.FLOW_CONTROL
