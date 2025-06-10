from typing import Self, Callable, Any
import regex

class TestException(Exception):
    @staticmethod
    def generic(test: 'Test', answer, success: bool):
        return {"args": test.args, "kwargs": test.kwargs, "answer": str(answer), "expect": str(test.expect_value), "success": success}
    @classmethod
    def success(cls, test: 'Test', answer):
        return cls.generic(test, answer, True)
    @classmethod
    def fail(cls, test: 'Test', answer=..., *, verbose=False):
        if not verbose: return cls(test.funcname, test.args, test.kwargs, answer, test.expect_value)
        return cls.generic(test, answer, False)
    def __init__(self, func, args, kwargs, answer=..., expect=...):
        message = f"function {func} failed with arguments {args} and keywords {kwargs}"
        if not (answer == expect == ...):
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
            self.expect = lambda ans: True
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
        except:
            e = TestException.fail(self, verbose=verbose)
            if verbose: return e
            else: raise e
        good = False
        try: good = self.expect(answer)
        except: pass
        if good:
            return TestException.success(self, answer) if verbose else None
        e = TestException.fail(self, answer, verbose=verbose)
        if verbose: return e
        else: raise e


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