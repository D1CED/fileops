from unittest import TestCase, main
import fileops


class TestFileops(TestCase):

    def test_lexer(self):
        testdict = {
            'min': ("()", ['(', ')']),
            'std': (
                "(if (eq (# ../.) 14) () (u $1 /home/jannis/Music/))",
                ['(', 'if', '(', 'eq', '(', '#', '../.', ')', '14', ')',
                 '(', ')', '(', 'u', '$1', '/home/jannis/Music/', ')', ')']
            ),
            'hard': (
                "(((((sdagsadg (&ad, (381)) fasdf)) ()",
                ['(', '(', '(', '(', '(', 'sdagsadg', '(', '&ad,', '(',
                 '381', ')', ')', 'fasdf', ')', ')', '(', ')']
            ),
        }
        for name, (inp, want) in testdict.items():
            with self.subTest(name=name, inp=inp, want=want):
                self.assertEqual(list(fileops.tokenize(inp)), want)

    def test_next_paren(self):
        data = "eq (# ../.) 1) () (u $1 /home/jannis/Music/))"
        self.assertEqual(fileops.next_paren(data), 14)

    def test_next_paren_it(self):
        from itertools import takewhile, chain

        data = fileops.tokenize("(if (eq 2 (# $12))) abc ) 1")
        l = list(chain(takewhile(fileops.next_paren_it(), data), ")")) # consume iterator
        self.assertEqual(l, ["(", "if", "(","eq", "2", "(", "#", "$12", ")", ")", ")"])
        self.assertEqual(list(data), ["abc", ")", "1"])

    def test_parser(self):
        fileops._indirs = ['.']
        tests = [
            ("()", None),
            ("(eq 14 20)", False),
            ("(eq 3 3)", True),
            ("(# .)", 2),
            ("(# $1)", 2),
            ("(u . .)", {'fileops.py', 'test_fileops.py'}),
            ("(d . .)", False),
            ("(in . .)", True),
            ("(if (in . .) (eq 2 (# $1)) ())", True),
            ("(if (lt 14 2) (eq 2 (# $1)) ())", None),
        ]
        for inp, want in tests:
            with self.subTest(inp=inp, want=want):
                self.assertEqual(fileops.parse(inp), want)


if __name__ == '__main__':
    main()
