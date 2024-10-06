# write your code here
import ast
import re
from distutils.command.clean import clean
from importlib.metadata import files
from itertools import count
from string import whitespace
from sys import path_hooks
from unittest.mock import patch
import argparse
import os
import nltk


def is_snake_case(name):
    return re.match(r'^[_a-z0-9]+(?:_[a-z0-9]+)*', name) is not None

def is_camel_case(name):
    return re.match(r'(?:[A-Z][a-z]+)+', name) is not None


class CodeStyleChecker(ast.NodeVisitor):
    def __init__(self, filename):
        self.filename = filename

    def visit_FunctionDef(self, node):
        for arg in node.args.args:
            if not is_snake_case(arg.arg):
                print(f"{self.filename}: Line {node.lineno}: S010 Argument name '{arg.arg}' should be snake_case")

        if node.args.defaults:
            for default in node.args.defaults:
                if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                    print(f"{self.filename}: Line {node.lineno}: S012 Default argument value is mutable")

        self.generic_visit(node)

    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name) and not is_snake_case(target.id):
                print(f"{self.filename}: Line {node.lineno}: S011 Variable '{target.id}' should be snake_case")

        self.generic_visit(node)

issues_path = '/Users/jakubsadkiewicz/Documents/GitHub/PythonProject/Static Code Analyzer/Static Code Analyzer/task/analyzer/issues.txt'

parser = argparse.ArgumentParser()

parser.add_argument('directory_or_file', nargs=1)
args = parser.parse_args()

directory = args.directory_or_file[0]

flag = False

if not re.search('[^/]+\.[a-zA-Z0-9]+$', directory):
    flag = True
    os.chdir(*args.directory_or_file)
    files = os.listdir()
else:
    files = [directory]

# files = ['text.txt']

def load_issues(path):
    issues_dict = {}
    with open(path) as issues:
        details = issues.read().split('\n')
        for x in details:
            x = x.strip('[')
            x = x.strip(';')
            x = x.split('] ')
            issues_dict.update({x[0]: x[1]})
    return issues_dict

def S001(line):
    if len(line) > 79:
        return True
    else: return False

def S002(line):
    whitespace = 0
    first = False
    for index, char in enumerate(line):
        if char == ' ':
            if index == 0:
                first = True
            whitespace += 1
        if whitespace != 0 and char != ' ' and first:
            if whitespace % 4 == 0:
                return False
            else: return True

def S003(line):
    in_comment = False
    type_semi = ''
    for char in line:
        if char == '"' or char == "'":
            if not in_comment:
                in_comment = True
            else: in_comment = False
        if char == '#':
            return False
        if char == ';' and not in_comment:
            return True
    return False

def S004(line):
    a, b = '', ''
    in_comment = False
    for index, char in enumerate(line):
        if index == 0:
            a = char
        elif index == 1:
            if char == '#' and a == ' ':
                return True
            b = char
        if char == "#" and a == ' ' and b == ' ':
            return False
        if char == "#" and (a != ' ' or b != ' ') and index != 0:
            return True
        if index > 1:
            a = b
            b = char
    return False

def S005(line):
    in_comment = False
    for index, char in enumerate(line):
        if char == '#':
            in_comment = True
        if char.lower() == 't' and len(line) > index + 3:
            char = char + line[index + 1] + line[index + 2] + line[index + 3]
            char = char.lower()
            if char == 'todo' and in_comment:
                return True
    return False

def S007(line):
    in_comment = False
    in_comment_hash = False
    for index, char in enumerate(line):
        if char == '#':
            in_comment_hash = True
            in_comment = True
        if char == '"' or char == "'":
            if in_comment and not in_comment_hash:
                in_comment = True
            elif not in_comment and not in_comment_hash:
                in_comment = False
        if re.search('class [ ]', line) or re.search('def [ ]', line):
            return True
    return False

def S008(line):
    tokens = nltk.word_tokenize(line)
    for index, word in enumerate(tokens):
        if word == 'class' and len(tokens) > index + 1:
            name = re.search('(?:[A-Z][a-z]+)+', tokens[index + 1])
            if not name:
                return tokens[index + 1]
    return None

def S009(line):
    tokens = nltk.word_tokenize(line)
    for index, word in enumerate(tokens):
        if word == 'def' and len(tokens) > index + 1:
            name = re.search('^[_a-z0-9]+(?:_[a-z0-9]+)*', tokens[index + 1])
            if not name:
                return tokens[index + 1]
    return None

issues_dict = load_issues(issues_path)
files.sort()
# print(files) # TODO wyjebac
# os.chdir('/Users/jakubsadkiewicz/Documents/GitHub/PythonProject/Static Code Analyzer/Static Code Analyzer/task/analyzer') # TODO wyjebac
for path in files:
    with open(path, 'r') as f:
        if flag:
            path = directory + '/' + path
        content = f.read().split('\n')
        empty_line = 0
        for index, line in enumerate(content):
            if S001(line):
                print(f'{path}: Line {index + 1}: S001 {issues_dict.get("S001", "Parse Error")}')
            if S002(line):
                print(f'{path}: Line {index + 1}: S002 {issues_dict.get("S002", "Parse Error")}')
            if S003(line):
                print(f'{path}: Line {index + 1}: S003 {issues_dict.get("S003", "Parse Error")}')
            if S004(line):
                print(f'{path}: Line {index + 1}: S004 {issues_dict.get("S004", "Parse Error")}')
            if S005(line):
                print(f'{path}: Line {index + 1}: S005 {issues_dict.get("S005", "Parse Error")}')
            if S007(line):
                print(f'{path}: Line {index + 1}: S007 {issues_dict.get("S007", "Parse Error")}')
            if value := S008(line):
                print(f"{path}: Line {index + 1}: S008 Class name '{value}' should use CamelCase")
            if value := S009(line):
                print(f"{path}: Line {index + 1}: S009 Function name '{value}' should use snake_case")
            if empty_line > 2:
                print(f'{path}: Line {index + 1}: S006 {issues_dict.get("S006", "Parse Error")}')
            if line == '':
                empty_line += 1
            else: empty_line = 0
    program = open(path).read()
    tree = ast.parse(program)

    checker = CodeStyleChecker(path)
    checker.visit(tree)