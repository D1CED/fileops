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

if __name__ == '__main__':
    unittest.main()
