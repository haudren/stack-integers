import re

class Tokenizer(object):
  def __init__(self):
    self.patterns = {}

  def add_pattern(self, pattern, label):
    self.patterns[re.compile(pattern)] = label

  def tokenize(self, line):
    for regex, label in self.patterns.iteritems():
      m = regex.match(line)
      if m is not None:
        return (label, m.groups(line))
    return None

class IntTokenizer(Tokenizer):
  def __init__(self):
    Tokenizer.__init__(self)
    self.add_pattern('push (\d+)$', 'PUSH')
    self.add_pattern('add$', 'ADD')
    self.add_pattern('mult$', 'MULT')
    self.add_pattern('#(.*)#$', 'COMMENT')
    self.add_pattern('label:(.+)$', 'LABEL')
    self.add_pattern('goto:(.+)$', 'GOTO')
    self.add_pattern('je (\d+) (.+)$', 'JUMPEQUAL')
    self.add_pattern('store (.+)$', 'STORE')
    self.add_pattern('load (.+)$', 'LOAD')
    self.add_pattern('print (\S+)', 'PRINT')

class PpyTokenizer(Tokenizer):
  def __init__(self):
    Tokenizer.__init__(self)
    self.add_pattern('#(.*)#$', 'COMMENT')
    self.add_pattern('int (.+) = (\d+)$', 'VARINT')
    self.add_pattern('for\((.+);(.+[=<>].+); (.+)\):$', 'FORLOOP')
    self.add_pattern('(\S+) = (.+)$', 'ASSIGN')
    self.add_pattern('print (\S+)$', 'PRINT')

if __name__ == '__main__':
  tokenizer = IntTokenizer()

  print tokenizer.tokenize('add')
  print tokenizer.tokenize('add 123456')
  print tokenizer.tokenize('mult')
  print tokenizer.tokenize('mult 123456')
  print tokenizer.tokenize('push 123')
  print tokenizer.tokenize(' push 123')
