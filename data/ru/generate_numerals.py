from utils import *
from generate_datasets import *
np.random.seed(0)

numbers1 = np.arange(1, 11)
numbers2 = np.arange(11, 20)
numbers3 = np.arange(2, 10) * 10
numbers4 = np.array(list(np.arange(1, 11) * 100) + [1000000])
numbers5 = np.array([np.arange(1, 10) + 10 * i for i in range(2, 10)]).reshape(-1)
numbers6 = np.array([np.arange(1, 100) + 100 * i for i in range(1, 10)]).reshape(-1)

perm1 = np.random.permutation(numbers1)
train1, test1 = perm1[:5], perm1[5:]

perm2 = np.random.permutation(numbers2)
train2, test2 = perm2[:4], perm2[4:]

perm3 = np.random.permutation(numbers3)
train3, test3 = perm3[:4], perm3[4:]

perm4 = np.random.permutation(numbers4)
train4, test4 = perm4[:6], perm4[6:]

perm5 = np.random.permutation(numbers5)
train5, test5 = perm5[:18], perm5[18:]

perm6 = np.random.permutation(numbers6)
train6, test6 = perm6[:90], perm6[90:]

numbers7 = np.random.randint(low=1001, high=1000000, size=10000)
train7, test7 = numbers7[:2000], numbers7[2000:]

numbers8 = np.random.randint(low=1000001, high=1000000000, size=10000)
train8, test8 = numbers8[:2000], numbers8[2000:]

with open('natural_train.txt', 'w') as f:
    for arr in [train1, train2, train3, train4, train5, train6, train7, train8]:
        for i, num in enumerate(arr):
            out = convert_integer_to_tree(num)
            t = f'# {num}\n' + '\n'.join([t.__repr__() for t in out.tokens]) + '\n\n'
            f.writelines([t])

with open('natural_test.txt', 'w') as f:
    for arr in [test1, test2, test3, test4, test5, test6, test7, test8]:
        for i, num in enumerate(arr):
            out = convert_integer_to_tree(num)
            t = f'# {num}\n' + '\n'.join([t.__repr__() for t in out.tokens]) + '\n\n'
            f.writelines([t])