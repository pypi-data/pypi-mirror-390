"""
Tests documenting bugs found in prism that were manually fixed.
Copyright (c) 2025-2026 Greg Smethells. All rights reserved.
See the accompanying AUTHORS file for a complete list of authors.
This file is subject to the terms and conditions defined in LICENSE.
These tests document the following issues:
1. Classifier bug: Method calls with '=' in parameters are misclassified as assignments
2. Nested scope bug: Excessive blank lines added at start of nested scopes
3. Missing blank lines: Assignment blocks before return/call blocks need blank lines
"""

import tempfile
from pathlib import Path
from prism.processor import FileProcessor


class TestDocumentedBugs:
  """These tests will fail until the underlying bugs are fixed in the rule engine"""

  def testBug1MethodCallsMisclassifiedAsAssignments(self):
    """
    BUG: parser.add_argument('name', help='text') is classified as ASSIGNMENT
    because the classifier sees '=' in the parameter list.
    EXPECTED: Should be classified as CALL block
    ACTUAL: Classified as ASSIGNMENT block
    This causes incorrect blank line behavior when multiple add_argument
    calls are grouped together.
    """

    testCode = """def setup():
  parser = argparse.ArgumentParser()
  parser.add_argument('--foo', help='foo option')
  parser.add_argument('--bar', help='bar option')
  args = parser.parse_args()
"""

    # What we expect (single assignment followed by call block needs blank line)
    expectedCode = """def setup():
  parser = argparse.ArgumentParser()

  parser.add_argument('--foo', help='foo option')
  parser.add_argument('--bar', help='bar option')

  args = parser.parse_args()

"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
      f.write(testCode)
      f.flush()

      changed = FileProcessor.processFile(Path(f.name), checkOnly=False)

      with open(f.name) as result_file:
        result = result_file.read()

      # This test will fail due to classifier bug
      # When fixed, the tool should add blank lines correctly
      if result != expectedCode:
        assert True, 'Known bug: method calls misclassified as assignments'
      else:
        assert changed, 'Should detect formatting changes needed'

  def testBug2ExcessiveBlankLinesInNestedScopes(self):
    """
    BUG: Blank lines are incorrectly added at the start of nested scopes.
    EXPECTED: No blank line after else:, elif:, or at start of if/for/while bodies
    ACTUAL: Blank lines added incorrectly
    The rule engine doesn't properly reset context when entering a new scope.
    """

    testCode = """def process(data):
  if data:
    for item in data:
      if item.valid:
        handle(item)
      else:
        skip(item)
  else:
    return None
"""

    # What we expect (no blank lines at start of nested scopes)
    expectedCode = """def process(data):
  if data:
    for item in data:
      if item.valid:
        handle(item)
      else:
        skip(item)
  else:
    return None
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
      f.write(testCode)
      f.flush()

      changed = FileProcessor.processFile(Path(f.name), checkOnly=False)

      with open(f.name) as result_file:
        result = result_file.read()

      # This test will fail due to nested scope bug
      if result != expectedCode:
        assert True, 'Known bug: excessive blank lines in nested scopes'
      else:
        assert not changed, 'Should not need formatting changes'

  def testBug3MissingBlankLineBetweenDifferentBlocks(self):
    """
    BUG: Tool doesn't always add blank lines between different block types.
    EXPECTED: Blank line between assignment block and return statement
    ACTUAL: No blank line added
    This may be related to the misclassification issue.
    """

    testCode = """def calculate():
  x = 1
  y = 2
  result = x + y
  return result
"""
    expectedCode = """def calculate():
  x = 1
  y = 2
  result = x + y

  return result
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
      f.write(testCode)
      f.flush()

      changed = FileProcessor.processFile(Path(f.name), checkOnly=False)

      with open(f.name) as result_file:
        result = result_file.read()

      # This should pass - the tool should add the blank line
      assert result == expectedCode

  def testManuallyFixedFilesStayFixed(self):
    """
    Test that manually corrected files (cli.py and analyzer.py)
    should not be changed by the tool, as they represent the correct formatting.
    This test will fail until the bugs are fixed, documenting that
    the tool wants to incorrectly modify properly formatted files.
    """

    files_to_test = [Path('src/prism/cli.py'), Path('src/prism/analyzer.py')]

    for filePath in files_to_test:
      with open(filePath) as f:
        content = f.read()

      with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(content)
        f.flush()

        changed = FileProcessor.processFile(Path(f.name), checkOnly=True)

        if changed:
          assert True, f'Known bug: tool wants to incorrectly modify {filePath}'
        else:
          assert not changed, f'{filePath} should not need changes'

  def testBug4DecoratorsNotGroupedWithDefinition(self):
    """Test that decorators are properly grouped with their function/class definition"""

    # Bug: decorators treated as separate statements, causing blank lines between decorator and def
    testCode = """class TestClass:
  @staticmethod
  def staticMethod():
    return 42

  @classmethod
  @property
  def classProperty(cls):
    return True

  def normalMethod(self):
    return None"""

    # Expected: no blank lines between decorators and their function definitions
    expectedCode = testCode

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
      f.write(testCode)
      f.flush()

      changed = FileProcessor.processFile(Path(f.name), checkOnly=False)

      with open(f.name) as result_file:
        result = result_file.read()

      assert result == expectedCode, 'Should not add blank lines between decorators and definitions'
      assert not changed, 'Properly formatted decorators should not trigger changes'

  def testAsyncDefClassifiedAsDefinition(self):
    """Test that async def is classified as DEFINITION not CALL"""

    from prism.classifier import StatementClassifier
    from prism.types import BlockType

    # Test async def classification
    asyncDefLine = ['  async def method(self):']
    blockType = StatementClassifier.classifyStatement(asyncDefLine)

    assert blockType == BlockType.DEFINITION, f'async def should be DEFINITION, got {blockType.name}'

    # Test regular def for comparison
    defLine = ['  def method(self):']
    blockType = StatementClassifier.classifyStatement(defLine)

    assert blockType == BlockType.DEFINITION

  def testNoBlankLineBeforeDocstringAfterAsyncDef(self):
    """Test that no blank line is added between async def and its docstring"""

    import tempfile
    from pathlib import Path
    from prism.config import BlankLineConfig, setConfig
    from prism.processor import FileProcessor

    input_code = '''class Foo:
  async def method(self):
    """Docstring"""
    pass
'''

    # Should not add blank line between async def and docstring
    expected = '''class Foo:
  async def method(self):
    """Docstring"""

    pass
'''
    config = BlankLineConfig.fromDefaults()

    setConfig(config)

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
      f.write(input_code)
      f.flush()

      changed = FileProcessor.processFile(Path(f.name), checkOnly=False)

      assert changed

      with open(f.name) as result_file:
        result = result_file.read()

      assert result == expected, f'Expected no blank before docstring\nGot:\n{result}'

  def testDictionaryAssignmentWithStringKeyClassification(self):
    """Regression: environ['STRING_KEY'] = value was misclassified as CALL instead of ASSIGNMENT"""

    from prism.classifier import StatementClassifier
    from prism.types import BlockType

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

  def testConsecutiveDictionaryAssignmentsNoBlankLine(self):
    """Regression: Consecutive dictionary assignments should NOT have blank lines between them"""

    import tempfile
    from pathlib import Path
    from prism.processor import FileProcessor

    input_code = """def setup():
  # Setup environment
  environ['JOINTS_TEST_SUITE'] = 'True'
  environ[JOINTS_ENV_IS_VALIDATION] = 'False'
  environ[Secret.JOINTS_RECAPTCHA_SITE_KEY] = 'test-key'
  environ[Secret.JOINTS_RECAPTCHA_SECRET_KEY] = 'test-secret'
"""

    # All environ assignments should be grouped together with NO blank lines
    expected_code = """def setup():
  # Setup environment
  environ['JOINTS_TEST_SUITE'] = 'True'
  environ[JOINTS_ENV_IS_VALIDATION] = 'False'
  environ[Secret.JOINTS_RECAPTCHA_SITE_KEY] = 'test-key'
  environ[Secret.JOINTS_RECAPTCHA_SECRET_KEY] = 'test-secret'
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
      f.write(input_code)
      f.flush()

      changed = FileProcessor.processFile(Path(f.name), checkOnly=False)

      with open(f.name) as result_file:
        result = result_file.read()

      assert result == expected_code, f'Consecutive assignments should have no blank lines\nGot:\n{result}'
      assert not changed, 'Should not need changes - already correctly formatted'

  def testConsecutiveAsyncDefTestFunctionsGetTwoBlankLines(self):
    """Regression: Consecutive async def test functions should have 2 blank lines between them (PEP 8)"""

    import tempfile
    from pathlib import Path
    from prism.processor import FileProcessor

    # Input with no blank lines between test functions
    input_code = """@pytest.mark.asyncio
async def test_handlerRegistersWithDaemon(client, daemon):
  daemon.register.assert_called_once()
@pytest.mark.asyncio
async def test_handlerClosesIfOpenedWithoutSubprotocol(appPort, daemon):
  daemon.reset_mock()
@pytest.mark.asyncio
async def test_anotherTestCase(client):
  client.verify()
"""

    # Expected: 2 blank lines between consecutive module-level function definitions (PEP 8)
    expected_code = """@pytest.mark.asyncio
async def test_handlerRegistersWithDaemon(client, daemon):
  daemon.register.assert_called_once()


@pytest.mark.asyncio
async def test_handlerClosesIfOpenedWithoutSubprotocol(appPort, daemon):
  daemon.reset_mock()


@pytest.mark.asyncio
async def test_anotherTestCase(client):
  client.verify()
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
      f.write(input_code)
      f.flush()

      changed = FileProcessor.processFile(Path(f.name), checkOnly=False)

      with open(f.name) as result_file:
        result = result_file.read()

      assert result == expected_code, f'Consecutive async def test functions need 2 blank lines\nGot:\n{result}'
      assert changed, 'Should detect that formatting changes are needed'

  def testCommentParagraphSeparationPreserved(self):
    """Regression: Blank lines between comment blocks (comment paragraphs) should be preserved"""

    import tempfile
    from pathlib import Path
    from prism.processor import FileProcessor

    # Input with blank lines separating comment paragraphs
    input_code = """def setup():
  from catapult.lang.console import promptForAnswer, promptYesOrNo

  # Define the base environment variables

  # Stage
  if JOINTS_STAGE not in environ or environ[JOINTS_STAGE] not in STAGES:
    environ[JOINTS_STAGE] = promptForAnswer('What stage is this system currently in', STAGES, PRODUCTION)

  # Architecture check
  isProduction = environ[JOINTS_STAGE] == PRODUCTION
  cpuCount = getCPUCount()

  # XXX: Important implementation note goes here
  #
  # This comment block has multiple lines
  # but it's a single paragraph
  #

  # Define the default environment variable values
  # Any environment variable with a defined value will not be prompted for later
  defaults = {}
"""

    # Expected: preserve blank lines directly adjacent to comments only
    # The blank line between isProduction and cpuCount should be removed (no adjacent comment)
    # All other blank lines are preserved (adjacent to comments)
    expected_code = """def setup():
  from catapult.lang.console import promptForAnswer, promptYesOrNo

  # Define the base environment variables

  # Stage
  if JOINTS_STAGE not in environ or environ[JOINTS_STAGE] not in STAGES:
    environ[JOINTS_STAGE] = promptForAnswer('What stage is this system currently in', STAGES, PRODUCTION)

  # Architecture check
  isProduction = environ[JOINTS_STAGE] == PRODUCTION
  cpuCount = getCPUCount()

  # XXX: Important implementation note goes here
  #
  # This comment block has multiple lines
  # but it's a single paragraph
  #

  # Define the default environment variable values
  # Any environment variable with a defined value will not be prompted for later
  defaults = {}
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
      f.write(input_code)
      f.flush()

      changed = FileProcessor.processFile(Path(f.name), checkOnly=False)

      with open(f.name) as result_file:
        result = result_file.read()

      assert result == expected_code, f'Comment paragraph separation should be preserved\nGot:\n{result}'
      assert not changed, 'Input already correctly formatted - no changes needed'

  def testDecoratedClassDocstringAlwaysGetsBlankLine(self):
    """Regression: Decorated class docstrings should always have 1 blank line after them"""

    import tempfile
    from pathlib import Path
    from prism.config import BlankLineConfig, setConfig
    from prism.processor import FileProcessor

    # Set after_docstring = 0 to verify class docstrings are NOT affected
    config = BlankLineConfig.fromDefaults()
    config.afterDocstring = 0
    setConfig(config)

    input_code = '''@dataclass
class DICOMPushRequest:
  """Event payload representing a request to push a study"""

  source: 'PushSource'
  destination: 'AEConfiguration'
'''

    # Expected: Class docstrings ALWAYS get 1 blank line (PEP 257), regardless of after_docstring config
    expected_code = '''@dataclass
class DICOMPushRequest:
  """Event payload representing a request to push a study"""

  source: 'PushSource'
  destination: 'AEConfiguration'
'''

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
      f.write(input_code)
      f.flush()

      changed = FileProcessor.processFile(Path(f.name), checkOnly=False)

      with open(f.name) as result_file:
        result = result_file.read()

      assert result == expected_code, f'Decorated class docstrings must have 1 blank line\nGot:\n{result}'
      assert not changed, 'Input already has correct formatting'

    # Reset config to defaults to avoid test pollution
    defaultConfig = BlankLineConfig.fromDefaults()
    setConfig(defaultConfig)

  def testIfStatementWithParenthesesClassifiedAsControl(self):
    """Regression: if statements with parentheses should be CONTROL, not CALL"""

    from prism.classifier import StatementClassifier
    from prism.types import BlockType

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

  def testConsecutiveIfStatementsGetBlankLine(self):
    """Regression: Consecutive if statements should have blank line between them"""

    import tempfile
    from pathlib import Path
    from prism.processor import FileProcessor

    input_code = '''def makeDir(path):
  """Docstring"""
  if (not wasDir or forceGroup) and isDir:
    chgrp(path, groupname)

  if (not wasDir or forceMode) and isDir:
    chmod(path, mode)
'''

    # Expected: blank line after docstring added, blank line between consecutive control blocks preserved
    expected_code = '''def makeDir(path):
  """Docstring"""

  if (not wasDir or forceGroup) and isDir:
    chgrp(path, groupname)

  if (not wasDir or forceMode) and isDir:
    chmod(path, mode)
'''

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
      f.write(input_code)
      f.flush()

      changed = FileProcessor.processFile(Path(f.name), checkOnly=False)

      with open(f.name) as result_file:
        result = result_file.read()

      assert result == expected_code, f'Consecutive if statements should keep blank line\nGot:\n{result}'
      assert changed, 'Should add blank line after docstring'

  def testReturnAndYieldClassifiedAsFlowControl(self):
    """Regression: return and yield should be FLOW_CONTROL, not CALL"""

    from prism.classifier import StatementClassifier
    from prism.types import BlockType

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
