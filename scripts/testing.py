from typing import Self, Callable, Any
import regex

class TestException(Exception):
    @staticmethod
    def generic(test: 'Test', answer, success: bool, reason: Exception=None):
        return {"args": test.args, "kwargs": test.kwargs, "answer": str(answer), "expect": str(test.expect_value), "reason": reason, "success": success}
    @classmethod
    def success(cls, test: 'Test', answer):
        return cls.generic(test, answer, True)
    @classmethod
    def fail(cls, test: 'Test', answer=..., *, reason: Exception=None, verbose=False):
        if not verbose: raise cls(test.funcname, test.args, test.kwargs, test.expect_value, answer, reason)
        return cls.generic(test, answer, False, str(reason) if reason else None)
    def __init__(self, func, args, kwargs, expect, answer=..., reason=None):
        message = f"reason: {reason}\nfunction {func} failed with arguments {args} and keywords {kwargs}"
        if answer != ...:
            message += f" because answer {answer} didn't match and expectation {expect}"
        super().__init__(message)

class Test:
    def __init__(self, *args, _func, _funcname, _tester=None, _isregex=False, _iscontains=False, **kwargs):
        self.func = _func
        self.funcname = _funcname
        self.tester = _tester
        self.isregex = _isregex
        self.iscontains = _iscontains
        self.args = args
        self.kwargs = kwargs
    def claim(self, expect: Callable[[Any], bool]|Any, *args, **kwargs):
        if isinstance(expect, Callable): self.expect_value = expect.__doc__
        else: self.expect_value = expect
        if expect is True:
            self.expect = lambda ans: ans is not None
        elif expect is None:
            self.expect = lambda ans: ans is None
        elif isinstance(expect, Callable):
            self.expect = expect
        elif self.tester is not None:
            self.expect = self.tester(expect, *args, **kwargs)
            self.expect_value = self.expect.__doc__
        elif self.isregex:
            self.expect = lambda ans: regex.match(f"^{expect}$", ans) is not None
        elif self.iscontains:
            self.expect = lambda ans: expect in ans or all(exp in ans for exp in expect)
        else: self.expect = lambda ans: ans == expect
        return self
    def test(self, verbose=False):
        try: answer = self.func(*self.args, **self.kwargs)
        except Exception as e:
            return TestException.fail(self, reason=e, verbose=verbose)
        good = False
        try: good = self.expect(answer)
        except Exception as e:
            return TestException.fail(self, answer, reason=e, verbose=verbose)
        if not good: return TestException.fail(self, answer, verbose=verbose)
        if not verbose: return None
        return TestException.success(self, answer)


class Tester:
    testers: list[Self] = []
    def __init__(self, func, tester=None, regex_expect: bool=False, contains_expect: bool=False):
        self.func = func
        if isinstance(getattr(func, "funcname", None), str):
            self.funcname = func.funcname
        else: self.funcname = func.__name__
        self.tester = tester
        self.regex_expect = regex_expect
        self.contains_expect = contains_expect
        self.tests: list[Test] = []
        self.testers.append(self)
    @classmethod
    def test_all(cls, verbose=False) -> list[list[dict[str, Any]]]|None:
        logs = [tester.test(verbose) for tester in cls.testers]
        return logs if verbose else None
    def test(self, verbose=False) -> list[dict[str, Any]]|None:
        log = [test.test(verbose) for test in self.tests]
        if not verbose: return
        return {"funcname": self.funcname, "tests": log, "success": all(line["success"] for line in log)}
    def __call__(self, *args, **kwargs):
        self.tests.append(Test(*args, _func=self.func, _funcname=self.funcname, _tester=self.tester, _isregex=self.regex_expect, _iscontains=self.contains_expect, **kwargs))
        return self.tests[-1]