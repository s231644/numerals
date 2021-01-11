from utils import *
import numpy as np


basic_numbers = dict()
basic_str_numbers = dict()
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
                basic_str_numbers[str(root_number)] = current_number
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


zillion_numbers = dict()
zillion_aux_numbers = dict()
str2tree_num_aux = dict()

l = "1	иллион	-иллион	NUM	NUM		0	root			10^3	10^(3+d*3)".split('\t')
illion = Tree([Token(l[0], l[1], l[2], l[3], l[4], l[5], l[6], l[7], l[10], 0)])


with open('ru_zillions_base1.conllu', 'r') as f:
    current_number = []
    current_tokens = []
    root_number = 0
    is_basic = True
    for line in f.readlines()[1:]:
        l = line.replace(',', '\t').strip().split('\t')
        if len(l) <= 1:
            str2tree_num[' '.join(current_number)] = Tree(current_tokens)
            current_tokens = []
            zillion_numbers[str(root_number)] = current_number
            current_number = []
            root_number = 0
            continue
        token = l[1]
        if l[9]:
            token += '_'
        if len(l) > 11:
            # 1	окто	окт-	NUM	NUM		0	root			8	8
            # 8 -> 8
            root_number = int(l[11])
        current_tokens.append(Token(l[0], token, l[2], l[3], l[4], l[5], l[6], l[7], l[10], 0))
        current_number.append(token)

with open('ru_zillions_base2.conllu', 'r') as f:
    current_number = []
    current_tokens = []
    root_number = 0
    is_basic = True
    for line in f.readlines()[1:]:
        l = line.replace(',', '\t').strip().split('\t')
        if len(l) <= 1:
            str2tree_num_aux[' '.join(current_number)] = Tree(current_tokens)
            current_tokens = []
            zillion_aux_numbers[str(root_number)] = current_number
            current_number = []
            root_number = 0
            continue
        token = l[1]
        if l[9]:
            token += '_'
        if len(l) > 11:
            # 1	окто	окт-	NUM	NUM		0	root			8	8
            # 8 -> 8
            root_number = int(l[11])
        current_tokens.append(Token(l[0], token, l[2], l[3], l[4], l[5], l[6], l[7], l[10], 0))
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
        tree_l = convert_integer_to_tree(n // 10)
        tree_r = convert_integer_to_tree(n % 10)
        return merge_trees(tree_l, tree_r, is_arc_l2r=False, arc_label='add')
    if n < 1000:
        # 101 ... 999
        tree_l = convert_integer_to_tree(n // 100)
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


def drop_leading_zeros(n: str):
    d = len(n)
    i = 0
    while i < d and n[i] == '0':
        i += 1
    return n[i:]


def convert_zillion_to_tree(n: str, is_aux=False):
    is_aux = is_aux or n.startswith('0')
    n = drop_leading_zeros(n)
    if is_aux:
        base_dict = zillion_aux_numbers
        str_dict = str2tree_num_aux
    else:
        base_dict = zillion_numbers
        str_dict = str2tree_num
    if n in base_dict:
        # 1, 2, ..., 9, 10, 20, ..., 90, 100, 200, ..., 900
        # or 1, 2, ..., 9
        numeral = base_dict[n]
        return deepcopy(str_dict[' '.join(numeral)])
    d = len(n)
    if d == 2:
        # 11 ... 99 \ 20, ..., 90, e. g. 87 -> септин|окто|гинт|иллион
        tree_r = convert_zillion_to_tree(n[0] + "0", is_aux=is_aux)  # '80'
        tree_l = convert_zillion_to_tree(n[-1:], is_aux=True)  # '7'
        return merge_trees(tree_l, tree_r, is_arc_l2r=True, arc_label='add')
    if d == 3:
        # 101 ... 999
        tree_r = convert_zillion_to_tree(n[0] + "00")  # 400
        tree_l = convert_zillion_to_tree(n[-2:], is_aux=True)  # 87
        return merge_trees(tree_l, tree_r, is_arc_l2r=True, arc_label='add')
    raise NotImplementedError("Too large number! :(")


def convert_str_integer_to_tree(n: str):
    n = drop_leading_zeros(n)
    if not n:
        return Tree([])
    if n in basic_str_numbers:
        # 1 ... 20, 30, 40, 50, 60, 70, 80, 90, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000
        numeral = basic_str_numbers[n]
        return deepcopy(str2tree_num[' '.join(numeral)])
    d = len(n)
    if d == 2:
        # 21 ... 99
        tree_l = convert_str_integer_to_tree(n[0] + "0")
        tree_r = convert_str_integer_to_tree(n[-1:])
        return merge_trees(tree_l, tree_r, is_arc_l2r=False, arc_label='add')
    if d == 3:
        # 101 ... 999
        tree_l = convert_str_integer_to_tree(n[0] + "00")
        tree_r = convert_str_integer_to_tree(n[-2:])
        return merge_trees(tree_l, tree_r, is_arc_l2r=False, arc_label='add')
    if d <= 6:
        tree_l = convert_str_integer_to_tree(n[:-3])
        tree_m = convert_str_integer_to_tree('1000')
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
        if not n.endswith('000'):
            tree_r = convert_str_integer_to_tree(n[-3:])
            return merge_trees(tree_lm, tree_r, is_arc_l2r=False, arc_label='add')
        else:
            return tree_lm
    if d <= 3003:
        # 1.000.000, 1.000.001, ...,
        # 123456789 123 [456 789]

        d_r = 3 * ((d - 1) // 3)  # 3.000.000 (7) -> 000.000 (6), 8 -> 6, 9 -> 6
        d_l = d - d_r  # 3.000.000 (7) -> 1 (1), 23.000.000 (8) -> 23 (2), 123.000.000 (9) -> 123 (3)
        tree_l = convert_str_integer_to_tree(n[:d_l])  # 123 ... -> "сто двадцать три ..."
        latin_base = (d_r - 3) // 3  # 6 -> 1, 9 -> 2 (bi), 12 -> 3 (tri), ...

        tree_z = convert_zillion_to_tree(str(latin_base))  # 10^(3 + 3 * latin_base)
        tree_m = merge_trees(tree_z, deepcopy(illion), is_arc_l2r=False, arc_label='zillionize')

        if tree_l.numeral[-1] == 'один':
            pass
        elif tree_l.numeral[-1] in {'два', 'три', 'четыре'}:
            tree_m.tokens[-1].form += 'а'
        else:
            tree_m.tokens[-1].form += 'ов'
        tree_lm = merge_trees(tree_l, tree_m, is_arc_l2r=False, arc_label='mult')
        rest = drop_leading_zeros(n[d_l:])
        if rest:
            tree_r = convert_str_integer_to_tree(rest)
            return merge_trees(tree_lm, tree_r, is_arc_l2r=False, arc_label='add')
        else:
            return tree_lm


number = ''.join(map(str, np.random.randint(0, 10, 167)))


# number = '1' + '0' * (3 + 3 * 295)
# number = '67483324'
res = convert_str_integer_to_tree(number)
res.sent_id = number
with open('try_conllu.txt', 'w') as f:
    f.write(res.to_conllu())
print(res.to_conllu())


def convert_sum(x, y):
    tree_l = convert_str_integer_to_tree(x)
    tree_m = Tree([Token(1, 'плюс', 'плюс', 'CONJ', 'CONJ', '', 0, 'root', 0, 0)])
    tree_r = convert_str_integer_to_tree(y)
    tree_lm = merge_trees(tree_l, tree_m, is_arc_l2r=False, arc_label='larg')
    return merge_trees(tree_lm, tree_r, is_arc_l2r=True, arc_label='rarg'), convert_str_integer_to_tree(str(int(x) + int(y)))


def convert_prod(x, y):
    tree_l = convert_str_integer_to_tree(x)
    tree_m = Tree([Token(1, 'на', 'на', 'CONJ', 'CONJ', '', 0, 'root', 1, 1)])
    tree_r = convert_str_integer_to_tree(y)
    tree_lm = merge_trees(tree_l, tree_m, is_arc_l2r=False, arc_label='larg')
    return merge_trees(tree_lm, tree_r, is_arc_l2r=True, arc_label='rarg'), convert_str_integer_to_tree(str(int(x) * int(y)))


# p, r = convert_prod('89756754246', '79126685941583')
# with open('try_conllu_add.txt', 'w') as f:
#     f.write(p.to_conllu())
#
# print(p.to_conllu())
# print(r.to_conllu())
