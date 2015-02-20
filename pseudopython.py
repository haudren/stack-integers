from tokens import PpyTokenizer
import itertools
import re
import os

class PseudoPython():
  def __init__(self):
    self.tokenizer = PpyTokenizer()
    self.variables = {}
    self.bytecode = []

    self.cur_adress = 0
    self.cur_num_for = 0
    self.for_loop_index = []

    self.init_translators()

  def init_translators(self):
    self.translators = {}
    self.pre_translators = {}
    self.post_translators = {}

    self.translators['VARINT'] = self.varint
    self.translators['ASSIGN'] = self.assign
    self.translators['PRINT'] = self.print_bc
    self.pre_translators['FORLOOP'] = self.pre_for_loop
    self.post_translators['FORLOOP'] = self.post_for_loop

  def print_bc(self, var):
    v = var.strip()
    self.exists_var(v)
    self.bytecode.append('print {}'.format(self.variables[v]))

  def varint(self, var, value):
    adress = '0x{}'.format(self.cur_adress)
    self.variables[var] = adress
    self.cur_adress += 1
    self.bytecode.append('push {}'.format(value))
    self.bytecode.append('store {}'.format(adress))

  def assign(self, var, operands):
    v = var.strip()
    self.exists_var(v)

    regex = re.compile('(.+)([+*])(.+)')
    m = regex.match(operands)
    if m is not None:
      v1, op, v2 = m.groups()

      try:
        lit = int(v1)
        self.bytecode.append('push {}'.format(lit))
      except ValueError:
        self.exists_var(v1)
        add_1 = self.variables[v1]
        self.bytecode.append('load {}'.format(add_1))

      try:
        lit = int(v2)
        self.bytecode.append('push {}'.format(lit))
      except ValueError:
        self.exists_var(v2)
        add_2 = self.variables[v2]
        self.bytecode.append('load {}'.format(add_2))

    add = self.variables[v]

    if op == '+':
      self.bytecode.append('add')
    elif op == '*':
      self.bytecode.append('mult')

    self.bytecode.append('store {}'.format(add))

  def exists_var(self, var):
    if not var in self.variables.keys():
      raise Exception('Variable referenced before assignment')

  def pre_for_loop(self, varname, cond, op):
    v = varname.strip()
    c = cond.strip()
    o = op.strip()
    if not v in c or not v in o:
      raise Exception('Only litteral loops allowed')

    label = 'for{}'.format(self.cur_num_for)
    self.for_loop_index.append(self.cur_num_for)
    self.cur_num_for += 1
    self.bytecode.append('label:{}'.format(label))

  def post_for_loop(self, varname, cond, op):
    v = varname.strip()
    c = cond.strip()
    o = op.strip()

    regex = re.compile('^{} = (\d+)$'.format(v))
    m = regex.match(c)
    if m is not None:
      limit = int(m.groups()[0])
    else:
      raise Exception('Unrecognized for loop')

    if o != v+'++':
      raise Exception('Only ++ allowed for now... {} vs {}'.format(o, v+'++'))

    var_adress = self.variables[v]
    closing_num = self.for_loop_index.pop()
    self.bytecode.append('load {}'.format(var_adress))
    self.bytecode.append('push 1')
    self.bytecode.append('add')
    self.bytecode.append('store {}'.format(var_adress))
    self.bytecode.append('load {}'.format(var_adress))
    self.bytecode.append('je {} end{}'.format(limit, closing_num))
    self.bytecode.append('goto:for{}'.format(closing_num))
    self.bytecode.append('label:end{}'.format(closing_num))

  def generate_code(self, token, args):
    try:
      self.translators[token](*args)
    except KeyError:
      print "Unknown token : {}".format(token)

  def generate_pre_code(self, token, args):
    try:
      self.pre_translators[token](*args)
    except KeyError:
      print "Unknown pre-token : {}".format(token)

  def generate_post_code(self, token, args):
    try:
      self.post_translators[token](*args)
    except KeyError:
      print "Unknown pre-token : {}".format(token)

  def compile_file(self, filename):
    with open(filename) as code:
      self.compile(code.readlines())

    root, ext = os.path.splitext(filename)
    outfile = root+'.bc'

    with open(outfile, 'w') as out:
      out.write('\n'.join(self.bytecode))

  def compile(self, text, indentation_level=0):
    print "compiling {}-th level".format(indentation_level)
    i = 0
    while i < len(text):
      line = text[i]
      tokens = self.tokenizer.tokenize(line)
      if tokens is not None:
        token, args = tokens
      else:
        print "Unrecognized line {}".format(line)
        i += 1
        continue
      #Generate regular code
      if not token in self.pre_translators.keys():
        self.generate_code(token, args)
        i += 1
      else:
        self.generate_pre_code(token, args)
        inner = self.select_inner(text[i+1:], indentation_level+1)
        print indentation_level, text[i+1:], inner
        self.compile(inner, indentation_level+1)
        self.generate_post_code(token, args)
        i += len(inner)+1

  def select_inner(self, text, indentation_level):
    exp = '^\s{{{},}}'.format(indentation_level)
    regex = re.compile(exp)
    lines = itertools.takewhile(lambda x: regex.match(x) is not None, text)
    ret = [l[indentation_level:] for l in lines]
    return ret

if __name__ == '__main__':
  comp = PseudoPython()
  comp.compile_file('source.ppc')
