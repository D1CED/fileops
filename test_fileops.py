import unittest
import fileops


class TestFileops(unittest.TestCase):

    def test_lexer_min(self):
        want = ['(', ')']
        self.assertEqual(list(fileops.tokenize("()")), want)

    def test_lexer_std(self):
        data = "(if (eq (# ../.) 14) () (u $1 /home/jannis/Music/))"
        want = ['(', 'if', '(', 'eq', '(', '#', '../.', ')', '14', ')',
        '(', ')', '(', 'u', '$1', '/home/jannis/Music/', ')', ')' ]
        self.assertEqual(list(fileops.tokenize(data)), want)

    def test_lexer_hard(self):
        data = "(((((sdagsadg (&ad, (381)) fasdf)) ()"
        want = ['(', '(', '(', '(', '(', 'sdagsadg', '(', '&ad,', '(',
            '381', ')', ')', 'fasdf', ')', ')', '(', ')']
        self.assertEqual(list(fileops.tokenize(data)), want)

    def test_next_paren(self):
        data = "eq (# ../.) 1) () (u $1 /home/jannis/Music/))"
        self.assertEqual(fileops.next_paren(data), 14)

    def test_parse_min(self):
        self.assertEqual(fileops.parse("()"), None)
        self.assertEqual(fileops.parse("(eq 14 20)"), False)
        self.assertEqual(fileops.parse("(eq 3 3)"), True)

    def test_parse_std(self):
        fileops.indirs = ['.']
        self.assertEqual(fileops.parse("(# .)"), 2)
        self.assertEqual(fileops.parse("(# $1)"), 2)
        self.assertEqual(fileops.parse("(u . .)"), frozenset(['fileops.py', 'test_fileops.py']))
        self.assertEqual(fileops.parse("(d . .)"), False)
        self.assertEqual(fileops.parse("(in . .)"), True)
        self.assertEqual(fileops.parse("(if (in . .) (eq 2 (# $1)) ())"), True)
        self.assertEqual(fileops.parse("(if (lt 14 2) (eq 2 (# $1)) ())"), None)

if __name__ == '__main__':
    unittest.main()
