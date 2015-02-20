from tokens import IntTokenizer

class Stack(object):
  def __init__(self):
    self.values = []

  def push(self, value, index=0):
    self.values.append(value)
    return index+1

  def pop(self):
    self.values, value = self.values[:-1], self.values[-1]
    return value

  def two_operands(self, op):
    a = self.pop()
    b = self.pop()
    self.push(op(a, b))

  def add(self, index=0):
    self.two_operands(lambda x,y:x+y)
    return index+1

  def multiply(self, index=0):
    self.two_operands(lambda x,y:x*y)
    return index+1

  def peek(self):
    return self.values[-1]

  def __str__(self):
    return '->'.join([str(v) for v in self.values])

class Language(object):
  def __init__(self):
    self.stack = Stack()
    self.tokenizer = IntTokenizer()

    self.actions = {}
    self.variables = {}
    self.labels = {}
    self.int_actions()

  def int_actions(self):
    self.actions['PUSH'] = lambda x, index=0: self.stack.push(int(x), index=index)
    self.actions['ADD'] = self.stack.add
    self.actions['MULT'] = self.stack.multiply
    self.actions['GOTO'] = self.goto
    self.actions['JUMPEQUAL'] = self.jump_equal
    self.actions['STORE'] = self.store
    self.actions['LOAD'] = self.load
    self.actions['PRINT'] = self.print_var

  def print_var(self, adress, index=0):
    print self.variables[adress]
    return index+1

  def save_label(self, label, index):
    self.labels[label] = index

  def goto(self, label, index=0):
    return self.labels[label]

  def jump_equal(self, comp, label, index=0):
    if self.stack.peek() == int(comp):
      return self.goto(label, index)
    else:
      return index+1

  def load(self, adress, index=0):
    i = self.stack.push(self.variables[adress], index)
    return i

  def store(self, adress, index=0):
    self.variables[adress] = self.stack.pop()
    return index+1

  def compile(self, filename):
    self.instructions = []
    nr_instruc = 0
    with open(filename, 'r') as f:
      for i, l in enumerate(f.readlines()):
        match = self.tokenizer.tokenize(l)
        if match is not None:
          token, args = match
          print "{}:{}".format(token, args)

          if self.is_action(token):
            self.instructions.append(match)
            nr_instruc += 1

          if token == 'LABEL':
            self.save_label(args[0], nr_instruc)

        else:
          print "Incorrect instruction at line {} ({})".format(i+1, l.strip())

  def is_action(self, label):
    return label in self.actions.keys()

  def execute(self):
    i = 0
    while i < len(self.instructions):
      token, args = self.instructions[i]
      i = self.actions[token](*args, index=i)

if __name__ == '__main__':
  l = Language()
  print "COMPILING..."
  l.compile('source.bc')
  print l.labels
  print 
  print "EXECUTE!"
  l.execute()
