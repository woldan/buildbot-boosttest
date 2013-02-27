## Copyleft. All wrongs reserved.
from buildbot.steps.shell import ShellCommand
from xml.etree import ElementTree
import re

class BoostTest (ShellCommand) :

  def __init__(self, **kwargs) :
    ShellCommand.__init__(self, **kwargs)


  def add_key_to_description(self, description, key) :
    value = self.step_status.getStatistic(key, 0)
    if (value <= 0) :
      return
    total = self.step_status.getStatistic('total', 0)
    if (total > 0) :
      description.append('%s: %d / %d [%3d%]' % (key, value, total, (value * 100 / total)))
    else :
      description.append('%s: %d' % (key, value))

  def describe(self, done=False):
    description = ShellCommand.describe(self, done)

    if done :
      self.add_key_to_description(description, 'passed')
      self.add_key_to_description(description, 'skipped')
      self.add_key_to_description(description, 'failed')

    return description

  def collect_statistical_value(self, name, query, tree) :
    nodes = tree.findall(".//TestSuite")
    value = 0
    for node in nodes :
      value += int(node.get(query, 0));
    self.step_status.setStatistic(name, value)

  def createSummary(self, log):
    ShellCommand.createSummary(self, log)
    output = self.getLog('stdio').getText()
    testresult = re.search('<TestResult>.*</TestResult>', output, re.MULTILINE)
    testresult_root = ElementTree.fromstring(testresult.group(0))

    self.collect_statistical_value('passed', 'test_cases_passed', testresult_root)
    self.collect_statistical_value('failed', 'test_cases_failed', testresult_root)
    self.collect_statistical_value('skipped', 'test_cases_skipped', testresult_root)
    self.collect_statistical_value('aborted', 'test_cases_aborted', testresult_root)

    total = self.step_status.getStatistic('passed', 0)
    total += self.step_status.getStatistic('failed', 0)
    total += self.step_status.getStatistic('skipped', 0)
    total += self.step_status.getStatistic('aborted', 0)
    self.step_status.setStatistic('total', total)

