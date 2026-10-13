import io
import unittest
from src.runtime import ResponseReader


class RuntimeTests(unittest.TestCase):
    def test_worker_exit_is_not_a_security_success(self):
        reader = ResponseReader(io.StringIO(''))
        with self.assertRaisesRegex(RuntimeError, 'stopped'):
            reader.next(0.1)

    def test_missing_worker_reply_has_bounded_wait(self):
        import threading
        gate = threading.Event()
        class Stalled:
            def readline(self):
                gate.wait(1)
                return ''
        reader = ResponseReader(Stalled())
        try:
            with self.assertRaises(TimeoutError):
                reader.next(0.01)
        finally:
            gate.set()

    def test_replies_keep_order(self):
        reader = ResponseReader(io.StringIO('{"a":1}\n{"b":2}\n'))
        self.assertEqual(reader.next(0.2), {'a': 1})
        self.assertEqual(reader.next(0.2), {'b': 2})
