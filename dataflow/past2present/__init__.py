# -*- coding: UTF-8 -*-

from __future__ import print_function
import traceback

from pattern.en import conjugate


class Verb(object):
    """
    This class if for those verbs which have the following dependency labels:

    VERB ROOT
    WHNP > WDT --relcl--> NN
    VERB --advcl--> NN
    VERB --advcl--> IN
    VERB --ccomp--> NN
    """
    AUXILIARY_MODALS = [
        'can', 'could', 'may', 'might', 'must', 'shall', 'should', 'will',
        'would'
    ]

    def __init__(self, tok=None, clause=None, number_person='pl'):
        """
        If the verb comes from a fragment without a subject,
        then default conjugation is past plural.
        """
        self.is_parsed = False
        self.break_recursion = False
        self.tok = tok
        self.clause = clause
        self.aux = []
        self.nsubj = None
        self.do = False
        self.been = False
        self.number_person = number_person
        self.is_past = False
        self.is_future = False
        self.have_pres = False
        self.have_past = False
        self.is_modal = False
        self.is_participle = False
        if self.tok and self.clause:
            self.parse()

    def __str__(self):
        s = """
        is parsed: %s
        verb: %s
        verb lemma: %s
        verb dependency label: %s
        verb constituent tag: %s""" % (
            self.is_parsed, self.tok.lower_,
            self.tok.lemma_, self.tok.dep_, self.tok.tag_)
        for i, a in enumerate(self.aux):
            s += """
        aux %d: %s
        aux %d lemma: %s
        aux %d dependency label: %s""" % (
                i, a.lower_, i, a.lemma_, i, a.dep_)
        s += """
        subject: %s
        number_person: %s
        has 'do': %s
        has 'been': %s
        is past tense: %s
        is future tense: %s
        is participle: %s
        has 'have' in present tense: %s
        has 'have' in past tense: %s
        has modal: %s
""" % (
            self.nsubj, self.number_person, self.do, self.been,
            self.is_past, self.is_future, self.is_participle,
            self.have_pres, self.have_past, self.is_modal)
        return s

    def parse(self):
        if not self.tok or not self.clause:
            raise Exception('Verb.parse_verb() requires the `tok` and `clause` '
                            'variables to be set.')
        if self.break_recursion:
            raise Exception(
                'There is a circular dependency among conjunctive verbs.')
        # Reset variables.
        self.aux = []
        self.do = False
        self.been = False
        self.have_pres = False
        self.have_past = False
        self.is_modal = False
        self.is_past = False
        self.is_future = False
        # Check for previous verb joined by conjunction.
        self.break_recursion = True
        prev_verb = self.clause.prev_verb(self)
        self.break_recursion = False
        if prev_verb:
            self.nsubj = prev_verb.nsubj
            self.number_person = prev_verb.number_person
            for child in self.tok.children:
                if child.lemma_ == 'not':
                    self.not_token = child
                elif child.dep_ == 'aux' or child.dep_ == 'auxpass':
                    self.aux.append(child)
            if not self.aux:
                if prev_verb.do:
                    # Special exception: He did not walk but talked.
                    if self.tok.tag_ == 'VBD':
                        self.do = False
                        self.aux = []
                    else:
                        self.do = True
                        self.aux = prev_verb.aux
                else:
                    self.do = False
                    self.aux = prev_verb.aux
                self.been = prev_verb.been
                self.have_pres = prev_verb.have_pres
                self.have_past = prev_verb.have_past
                self.is_modal = prev_verb.is_modal
                self.is_past = prev_verb.is_past
                self.is_future = prev_verb.is_future
            else:
                self.is_past = self._is_past()
            # Calculate negation status.
            # Algo: calculate negation status of previous verb
            #       then calculate neg of current verb by
            #       searching for not/n't/but
            #
            # * "not"/"n't" have dep_ == 'neg'
            # * "but" has dep_ == 'cc' and is child of
            #   the first verb of conjunction
            #
            # Ex:
            #   did not talk or walk
            #   did not talk but walked and balked
            #   did talk but didn't walk or balk
            #   didn't talk but did walk and balk
        else:
            # Iterates children in order of appearance.
            for child in self.tok.children:
                if child.dep_ == 'nsubj' or child.dep_ == 'nsubjpass':
                    self.nsubj = child
                elif child.dep_ == 'aux' or child.dep_ == 'auxpass':
                    self.aux.append(child)
            for a in self.aux:
                if a.lemma_ == 'do':
                    self.do = True
                elif a.lower_ == 'been':
                    self.been = True
                elif a.lower_ == 'will':
                    self.is_future = True
                if (a.lower_ == 'have' or a.lower_ == 'has'):
                    self.have_pres = True
                if a.lower_ == 'had':
                    self.have_past = True
            self.is_modal = self.aux and self._is_aux_modal(self.aux[0])
            self.number_person = self._number_person(self.nsubj)
            self.is_past = self._is_past()
        self.is_participle = self._is_participle(self.tok)
        self.is_parsed = True

    def transform_to_present_str(self, tok):
        """
        Takes in a token. If the token is this verb or one of its auxiliaries,
        then it converts it to present tense.

        Assumes that `self` is a past tense verb.

        Rules:
        * past > present
        * had + ppart > has/have + ppart
        * had + been + ppart > has/have + been + ppart
        * was + ppart > is + ppart
        * did > does, had > has/have, was > is
        * would have + ppart > would + inf
        * would have + been + ppart> would be + ppart
        """
        if self.aux and tok == self.aux[0]:
            if tok.lemma_ == 'do':
                return conjugate('do', self.number_person) + tok.whitespace_
            elif self.is_modal:
                return tok.text_with_ws
            elif self.is_participle and tok.lower_ == 'has':
                return conjugate('have', self.number_person) + tok.whitespace_
            else:
                return conjugate(tok.lemma_, self.number_person) \
                        + tok.whitespace_
        elif tok in self.aux:
            if self.is_modal and not self.is_future and tok.lower_ == 'have':
                return ''
            elif self.is_modal and not self.is_future and tok.lower_ == 'been':
                return 'be' + tok.whitespace_
            else:
                return tok.text_with_ws
        elif tok == self.tok:
            if not self.aux:
                return conjugate(tok.lemma_, self.number_person) \
                        + tok.whitespace_
            elif self.is_modal and not self.been and not self.is_future:
                return tok.lemma_ + tok.whitespace_
            else:
                return tok.text_with_ws
        return None

    @classmethod
    def _is_aux_modal(cls, tok):
        return tok.lower_ in cls.AUXILIARY_MODALS

    @classmethod
    def _contains_one_of(cls, haystack, needles):
        for item in haystack:
            for needle in needles:
                if item == needle:
                    return True
        return False

    @classmethod
    def _number_person(cls, token):
        """
        Expects a token with POS == 'NOUN'.
        """
        # Default is plural.
        if not token:
            return 'pl'
        for tok in token.children:
            if tok.lower_ == 'and':
                return 'pl'
        if (token.tag_ == 'NNPS' or token.tag_ == 'NNS' or
                token.lower_ == 'we' or token.lower_ == 'they'):
            return 'pl'
        elif token.lower_ == 'i':
            return '1sg'
        elif token.lower_ == 'you':
            return '2sg'
        else:
            return '3sg'

    def _is_past(self):
        if self.is_future:
            return False
        if self.do:
            return self._is_past_tok(self.aux[0], self.number_person)
        else:
            if self.aux and self._is_past_tok(self.aux[0], self.number_person):
                return True
            elif self._is_past_tok(self.tok, self.number_person):
                return True
        return False

    @classmethod
    def _is_past_tok(cls, tok, number_person=None):
        """
        Is `verb` past tense, where `verb` has lemma `lemma`
        and number/person `number_person`?
        """
        PAST_CONJ = {
            '1sg': '1sgp',
            '2sg': '2sgp',
            '3sg': '3sgp',
            'pl': 'ppl',
            'part': 'ppart',
        }
        if tok.tag_ == 'VBN' or tok.tag_ == 'VBD':
            return True
        if number_person:
            return conjugate(tok.lemma_, PAST_CONJ[number_person]) == tok.text
        return (conjugate(tok.lemma_, '1sgp') == tok.text or
                conjugate(tok.lemma_, '2sgp') == tok.text or
                conjugate(tok.lemma_, '3sgp') == tok.text)

    @classmethod
    def _is_participle(cls, tok):
        """
        Expects a token.
        """
        return tok.tag_ == 'VBG' or tok.tag_ == 'VBN'


class Clause(object):
    VERB_DEPS = ['ROOT', 'conj', 'relcl', 'advcl', 'ccomp']

    def __init__(self, span):
        self.verbs = []
        self.span = span

    def prev_verb(self, verb):
        """
        If a verb is connected by a conjunction to a previous verb,
        then get that verb.
        """
        prev_verb = None
        if verb.tok.dep_ == 'conj':
            for tok in verb.tok.ancestors:
                if tok.dep_ in self.VERB_DEPS:
                    for v in self.verbs:
                        if v.tok == tok:
                            prev_verb = v
                            if not prev_verb.is_parsed:
                                prev_verb.parse()
                    break
        return prev_verb

    def parse_verbs(self):
        self.verbs = []
        first = True
        # Depth-first search to find verbs.
        s = []
        s.append(self.span)
        while s:
            span = s.pop()
            if 'S' in span._.labels or 'SBAR' in span._.labels:
                if first:
                    first = False
                else:
                    continue
            elif len(span) == 1 and span[0].dep_ in self.VERB_DEPS:
                self.verbs.append(Verb(span[0], self))
            s.extend(reversed(list(span._.children)))

    def transform_present(self):
        self.parse_verbs()
        past_verbs = [v for v in self.verbs if v.is_past]
        first = True
        new_text = ''
        # Depth-first search to transform past to present.
        s = []
        s.append(self.span)
        while s:
            span = s.pop()
            if len(span) == 1:
                span_is_past_verb = False
                if span[0].pos_ == 'VERB':
                    for v in past_verbs:
                        present = v.transform_to_present_str(span[0])
                        if present is not None:
                            new_text += present
                            span_is_past_verb = True
                            break
                if not span_is_past_verb:
                    new_text += span.text_with_ws
            elif 'S' in span._.labels or 'SBAR' in span._.labels:
                if first:
                    first = False
                    s.extend(reversed(list(span._.children)))
                else:
                    ws = ' ' if span.text_with_ws[-1] == ' ' else ''
                    new_text += Clause(span).transform_present() + ws
            else:
                s.extend(reversed(list(span._.children)))
        new_text = new_text.replace(' .', '.').replace(' ,', ',')
        if new_text and new_text[-1] == ' ':
            new_text = new_text[:-1]
        return new_text


class Sentence(object):

    def __init__(self, span):
        self.span = span

    def transform_present(self):
        if not self.span:
            raise Exception(
                'Sentence.transform_present() requires `span` to be set.')
        try:
            text = Clause(self.span).transform_present()
            if text:
                text = text[0].upper() + text[1:]
            return text
        except Exception as e:
            print('There was an error parsing the following sentence')
            print()
            print(self.span.text)
            print()
            if (hasattr(self.span, '_') and
                    hasattr(self.span._, 'parse_string')):
                print('with parse:')
                print()
                print(self.span._.parse_string)
                print()
            print(str(e) + '\n' + traceback.format_exc())
            return self.span.text


def transform_present(nlp, text, echo=False):
    """
    It is not allowed to have sentences that conjunct verbs of different tenses
    without auxiliary verbs:

    * "We will go tomorrow and go today."

    This is because they are ambiguous without knowledge of adverbs like
    "tomorrow" and "today":

    "We will go and eat."

    Should eat be present or future tense? We assume future to avoid having to
    analyze the semantics of adverbial phrases.
    """
    doc = nlp(text)
    trans_text = []
    for sent in doc.sents:
        trans_text.append(Sentence(sent).transform_present())
        if echo:
            print(trans_text[-1])
    return ' '.join(trans_text)


def transform_present_span(sent):
    return Sentence(sent).transform_present()
