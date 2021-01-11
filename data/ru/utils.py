from copy import deepcopy


class Token:
    def __init__(self, position, form, lemma, pos, pos_phrase, tags, parent, label, value, value_phrase=None):
        self.position = int(position)
        self.form = form
        self.lemma = lemma
        self.pos = pos
        self.pos_phrase = pos_phrase
        self.tags = set(tags.split('|'))
        self.parent = int(parent)
        self.label = label
        self.value = value
        self.value_phrase = value_phrase

    def __str__(self):
        return f'{self.position}\t{self.form}\t{self.lemma}\t{self.pos}\t{self.parent}\t{self.label}\t{self.value}'

    def __repr__(self):
        return self.__str__()

    def to_conllu(self):
        """
        1	Die	der	DET	ART	Case=Nom|Number=Plur|PronType=Art	2	det	_	_
        :return:
        """
        return "\t".join([
            str(self.position), self.form, self.lemma,
            self.pos, self.pos_phrase, '|'.join(self.tags) or '_',
            str(self.parent), self.label,
            '_', str(self.value)
            # str(self.value_phrase)
        ])


class Tree:
    def __init__(self, tokens, sent_id="", sent_text=None):
        self.tokens = tokens
        self.numeral = [t.form for t in self.tokens]
        self.arcs = [(t.parent, t.label) for t in self.tokens]
        for i, token in enumerate(self.tokens):
            if (token.parent, token.label) == (0, 'root'):
                self.root = i
        self.sent_id = sent_id
        self.sent_text = sent_text or ' '.join(self.numeral).replace('_ ', '')

    def __str__(self):
        return ' '.join(self.numeral) + ' ' + ' '.join([f'{parent}:{label}' for (parent, label) in self.arcs])

    def __repr__(self):
        return self.__str__()

    def to_conllu(self):
        return "\n".join(
            [
                f'# sent_id = {self.sent_id}',
                f'# text = {self.sent_text}'
            ] + [
                t.to_conllu() for t in self.tokens
            ] + [""]
        )


def merge_trees(tree_l, tree_r, is_arc_l2r=True, arc_label='add'):
    tokens_l = deepcopy(tree_l.tokens)
    tokens_r = deepcopy(tree_r.tokens)
    for t in tokens_r:
        t.position += len(tree_l.tokens)
        if t.parent > 0:
            t.parent += len(tree_l.tokens)
    if is_arc_l2r:
        tokens_r[tree_r.root].parent = tokens_l[tree_l.root].position
        tokens_r[tree_r.root].label = arc_label
    else:
        tokens_l[tree_l.root].parent = tree_r.tokens[tree_r.root].position + len(tree_l.tokens)
        tokens_l[tree_l.root].label = arc_label
    return Tree(tokens_l + tokens_r)
