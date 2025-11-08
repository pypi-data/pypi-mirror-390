"""Module for processing yaml files, adding support for (nested) for loops and variable definition.
Credit to Jon Burr (Made for METTrigger PlotMaker framework).
"""

import yaml
import json
from yaml.reader import Reader
from yaml.scanner import Scanner
from yaml.parser import Parser
from yaml.composer import Composer
from yaml.constructor import SafeConstructor, ConstructorError
from yaml.resolver import Resolver
from yaml.nodes import Node, MappingNode, SequenceNode
import argparse
from copy import deepcopy
import re
import logging
import os

logger = logging.getLogger("process_yaml")

env_regex = re.compile(r"ENV\[([a-zA-Z_][a-zA-Z0-9_]*)\]")

def flatten_dict(d: dict, flatopts: list[str]) -> dict:
        
  ret = {}
  for key, value in d.items():
      
      # Only flatten for items in flatopts:
      if key not in flatopts:
          ret[key] = value
      elif isinstance(value, list):
          ret[key] = flatten_list(value, flatopts)
      elif isinstance(value, dict):
          ret[key] = flatten_dict(value, flatopts)
      else:
          ret[key] = value
          
  return ret

def flatten_list(l: list, flatopts: list[str]) -> list:
  ret = []
  for v in l:
      if v is None:
          continue
      elif isinstance(v, list):
          ret += flatten_list(v, flatopts)
      elif isinstance(v, dict):
          ret.append(flatten_dict(v, flatopts))
      else:
          ret.append(v)
          #raise ValueError("Invalid value format for output JSON file. {0} inserted into output list!".format(v) )
  return ret


class MyConstructor(SafeConstructor):

  job_variables = {}

  def __init__(self):
    super(MyConstructor, self).__init__()
    self.variables = deepcopy(MyConstructor.job_variables)
    self.in_for_loop = False

  def construct_document(self, node):
    return flatten_dict( super(MyConstructor, self).construct_document(node), flatopts=['plots', 'configurations'] )

  def construct_declare(self, node, deep=False):
    """Declare a variable"""
    for kv_pair in node.value:
      self.declare(*kv_pair)

  def construct_redeclare(self, node, deep=False):
    for kv_pair in node.value:
      self.undeclare(kv_pair[0])
      self.declare(*kv_pair)

  def declare(self, key_node, value):
    key = key_node.value
    if env_regex.match(key):
      raise ConstructorError("Attempting to declare variable {0}. This matches an environment variable call!");
    if key in self.variables:
      raise ConstructorError("Attempt to redeclare variable {0}".format(key) )
    self.variables[key] = value

  def undeclare(self, key_node):
    del self.variables[key_node.value]

  def construct_object(self, node, deep = False):
    # Need to remove the cached value as the value stored in a loop variable might have changed
    # if self.in_for_loop and node in self.constructed_objects:
    if node in self.constructed_objects:
      del self.constructed_objects[node]
    ret = super(MyConstructor, self).construct_object(node, deep)
    if isinstance(ret, str):
      return str(ret)
    else:
      return ret

  def get_variable(self, var_name):
    # First check to see if this is searching out an environment variable
    match = env_regex.match(var_name)
    if match:
      val = os.environ.get(match.group(1) )
      if val is None:
        logger.warn("Requested environment variable {0} not set! Will use a blank string".format(val) )
        val = ""
      return val
    val = self.variables[var_name]
    if isinstance(val, Node):
      return self.construct_object(val, deep=True)
    else:
      return val

  def construct_evaluate(self, node, deep=False):
    """Evaluate a reference to a variable OR a string containing variables"""
    if node.value in self.variables:
      return self.get_variable(node.value)
    eval_str = node.value
    # First replace any variables with their counterparts
    idx = 0
    while idx >= 0:
      idx = eval_str.find('$', idx)
      if idx < 0:
        break
      if eval_str[idx+1] == "$": # $$ becomes $ (use $ to escape itself)
        eval_str = eval_str[:idx]+"$"+eval_str[idx+2:]
        idx += 1 # move past this
      elif eval_str[idx+1] == "{": # variable name is wrapped in '{}'
        idx_end = eval_str.index("}", idx+1)
        var_name = eval_str[idx+2:idx_end]
        eval_str = eval_str[:idx] + str(self.get_variable(var_name) ) + eval_str[idx_end+1:]
      else:
        idx_end = eval_str.find(" ", idx+1)
        if idx_end < 0:
          idx_end = len(eval_str)
        var_name = eval_str[idx+1:idx_end]
        eval_str = eval_str[:idx] + str(self.get_variable(var_name) ) + eval_str[idx_end:]
    return eval_str
    # node.value = eval_str
    # return self.construct_object(node, deep=True)

  def construct_for_loop(self, node, deep = False):
    if not isinstance(node, SequenceNode):
      raise ConstructorError("For loops must be defined as a list")
    if len(node.value) == 0 or not isinstance(node.value[0], MappingNode):
      raise ConstructorError("Invalid for loop syntax")
    var_node = node.value[0].value[0][0]
    data = []
    self.in_for_loop = True
    for val in self.construct_object(node.value[0].value[0][1], deep = True):
      self.declare(var_node, val)
      for obj in node.value[1:]:
        data.append(self.construct_object(obj, deep=True) )
      self.undeclare(var_node)
    self.in_for_loop = False
    return data

class MyLoader(Reader, Scanner, Parser, Composer, MyConstructor, Resolver):
  
  def __init__(self, stream):
    Reader.__init__(self, stream)
    Scanner.__init__(self)
    Parser.__init__(self)
    Composer.__init__(self)
    MyConstructor.__init__(self)
    Resolver.__init__(self)

MyLoader.add_constructor("!declare", MyConstructor.construct_declare)
MyLoader.add_constructor("!redeclare", MyConstructor.construct_redeclare)
MyLoader.add_constructor("!undeclare", MyConstructor.undeclare)
MyLoader.add_constructor("!evaluate", MyConstructor.construct_evaluate)
MyLoader.add_constructor("!for_loop", MyLoader.construct_for_loop)

def read_yaml(yaml_file):
  return yaml.load(yaml_file, Loader = MyLoader)


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description = "Convert YAML files to JSON files")
  parser.add_argument("-i", "--input", help="Input YAML file")
  parser.add_argument("-o", "--output", help="Output JSON file")
  # parser.add_argument("-v", "--variables", type=json.loads, help="Dictionary of variables to add to the parser dictionary")


  args = parser.parse_args()

  # if args.variables:
    # for k, v in args.variables:
      # MyConstructor[k] = v
  with open(args.input, 'r') as yaml_file, open(args.output, 'w') as json_file:
    json.dump(read_yaml(yaml_file), json_file, indent=2)
