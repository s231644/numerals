from utils import *
import numpy as np

basic_numbers = dict()
str2tree_num = dict()

with open('ru_numerals_base.conllu', 'r') as f:
    current_number = []
    current_tokens = []
    root_number = 0
    is_basic = True
    for line in f.readlines()[1:]:
        l = line.strip().split('\t')
        if len(l) <= 1:
            if root_number > 0:
                str2tree_num[' '.join(current_number)] = Tree(current_tokens)
                current_tokens = []
            if is_basic:
                basic_numbers[root_number] = current_number
            current_number = []
            root_number = 0
            continue
        token = l[1]
        if l[9]:
            token += '_'
        current_tokens.append(Token(l[0], token, l[2], l[3], l[4], l[5], l[6], l[7], l[10], 0))
        if len(l) > 11:
            root_number = int(l[11])
            is_basic = len(l) <= 12
        current_number.append(token)


def convert_integer_to_tree(n):
  if n == 0:
    return Tree([])
  if n in basic_numbers:
    # 1 ... 20, 30, 40, 50, 60, 70, 80, 90, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1000000
    numeral = basic_numbers[n]
    return deepcopy(str2tree_num[' '.join(numeral)])
  if n < 100:
    # 21 ... 99
    tree_l = convert_integer_to_tree(n - (n % 10))
    tree_r = convert_integer_to_tree(n % 10)
    return merge_trees(tree_l, tree_r, is_arc_l2r=False, arc_label='add')
  if n < 1000:
    # 101 ... 999
    tree_l = convert_integer_to_tree(n - (n % 100))
    tree_r = convert_integer_to_tree(n % 100)
    return merge_trees(tree_l, tree_r, is_arc_l2r=False, arc_label='add')
  if n < 1000000:
    tree_l = convert_integer_to_tree(n // 1000)
    tree_m = convert_integer_to_tree(1000)
    if tree_l.numeral[-1] == 'один':
      tree_l.tokens[-1].form = 'одна'
    elif tree_l.numeral[-1] == 'два':
      tree_l.tokens[-1].form = 'две'
      tree_m.tokens[-1].form = 'тысячи'
    elif tree_l.numeral[-1] in {'три', 'четыре'}:
      tree_m.tokens[-1].form = 'тысячи'
    else:
      tree_m.tokens[-1].form = 'тысяч'
    tree_lm = merge_trees(tree_l, tree_m, is_arc_l2r=False, arc_label='mult')
    if n % 1000:
      tree_r = convert_integer_to_tree(n % 1000)
      return merge_trees(tree_lm, tree_r, is_arc_l2r=False, arc_label='add')
    else:
      return tree_lm
  if n < 1000000000:
    tree_l = convert_integer_to_tree(n // 1000000)
    tree_m = convert_integer_to_tree(1000000)
    if tree_l.numeral[-1] == 'один':
      pass
    elif tree_l.numeral[-1] in {'два', 'три', 'четыре'}:
      tree_m.tokens[-1].form = 'миллиона'
    else:
      tree_m.tokens[-1].form = 'миллионов'
    tree_lm = merge_trees(tree_l, tree_m, is_arc_l2r=False, arc_label='mult')
    if n % 1000000:
      tree_r = convert_integer_to_tree(n % 1000000)
      return merge_trees(tree_lm, tree_r, is_arc_l2r=False, arc_label='add')
    else:
      return tree_lm


def convert_sum(x, y):
    tree_l = convert_integer_to_tree(x)
    tree_m = Tree([Token(1, 'плюс', 'плюс', 'CONJ', 'CONJ', '', 0, 'root', 0, 0)])
    tree_r = convert_integer_to_tree(y)
    tree_lm = merge_trees(tree_l, tree_m, is_arc_l2r=False, arc_label='larg')
    return merge_trees(tree_lm, tree_r, is_arc_l2r=True, arc_label='rarg'), convert_integer_to_tree(x+y)


def convert_prod(x, y):
    tree_l = convert_integer_to_tree(x)
    tree_m = Tree([Token(1, 'на', 'на', 'CONJ', 'CONJ', '', 0, 'root', 1, 1)])
    tree_r = convert_integer_to_tree(y)
    tree_lm = merge_trees(tree_l, tree_m, is_arc_l2r=False, arc_label='larg')
    return merge_trees(tree_lm, tree_r, is_arc_l2r=True, arc_label='rarg'), convert_integer_to_tree(x*y) 
