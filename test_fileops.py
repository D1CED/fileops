from unittest import TestCase, main
from pathlib import Path
import tempfile
import fileops


class TestFileops(TestCase):

    def test_lexer(self):
        testdict = {
            'min': ("()", ['(', ')']),
            'std': (
                "(if (eq (# ../.) 14) () (u $1 /home/my/Music/))",
                ['(', 'if', '(', 'eq', '(', '#', '../.', ')', '14', ')',
                 '(', ')', '(', 'u', '$1', '/home/my/Music/', ')', ')']
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

    def test_next_paren_it(self):
        from itertools import takewhile, chain

        data = fileops.tokenize("(if (eq 2 (# $12))) abc ) 1")
        l = list(chain(takewhile(fileops.next_paren_it(), data), ")")) # consume iterator
        self.assertEqual(l, ["(", "if", "(","eq", "2", "(", "#", "$12", ")", ")", ")"])
        self.assertEqual(list(data), ["abc", ")", "1"])

    def test_parser(self):
        temp_dir = tempfile.TemporaryDirectory()
        temp_path = Path(temp_dir.name)
        (temp_path / "file1").touch()
        (temp_path / "file2").touch()

        fileops._indirs = [str(temp_path)]
        tests = [
            ("()", None),
            ("(eq 14 20)", False),
            ("(eq 3 3)", True),
            (f"(# {temp_path!s})", 2),
            ("(# $1)", 2),
            (f"(u {temp_path!s} {temp_path!s})", {'file1', 'file2'}),
            (f"(d {temp_path!s} {temp_path!s})", False),
            (f"(in {temp_path!s} {temp_path!s})", True),
            (f"(if (in {temp_path!s} {temp_path!s}) (eq 2 (# $1)) ())", True),
            ("(if (lt 14 2) (eq 2 (# $1)) ())", None),
        ]
        for inp, want in tests:
            with self.subTest(inp=inp, want=want):
                self.assertEqual(fileops.parse(inp), want)

        temp_dir.cleanup()

if __name__ == '__main__':
    main()
