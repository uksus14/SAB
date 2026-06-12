from typing import Self, Callable, Any, TypedDict, overload, Literal
import regex
import html

TestExceptionResult = TypedDict('TestExceptionResult', {"args": tuple, "kwargs": dict[str, Any], "answer": str, "expect": str, "reason": Exception|str|None, "success": bool})

class TestException(Exception):
    @staticmethod
    def generic(test: 'Test', answer, success: bool, reason: Exception|None=None) -> TestExceptionResult:
        return {"args": test.args, "kwargs": test.kwargs, "answer": str(answer), "expect": str(test.expect_value), "reason": reason, "success": success}
    @classmethod
    def success(cls, test: 'Test', answer):
        return cls.generic(test, answer, True)
    @classmethod
    @overload
    def fail(cls, test: 'Test', answer: Any=..., *, reason: Exception|None=None, verbose: Literal[False]) -> None: ...
    @classmethod
    @overload
    def fail(cls, test: 'Test', answer: Any=..., *, reason: Exception|None=None, verbose: Literal[True]) -> TestExceptionResult: ...
    @classmethod
    def fail(cls, test: 'Test', answer: Any=..., *, reason: Exception|None=None, verbose=False) -> TestExceptionResult|None:
        if not verbose: raise cls(test.funcname, test.args, test.kwargs, test.expect_value, answer, reason)
        return cls.generic(test, answer, False, reason)
    def __init__(self, func, args, kwargs, expect, answer: Any=..., reason=None):
        message = f"reason: {reason}\nfunction {func} failed with arguments {args} and keywords {kwargs}"
        if answer != ...:
            message += f" because answer {answer} didn't match and expectation {expect}"
            if reason is not None: message += "\nThis was an error during comparison with expectation"
        super().__init__(message)

class Test:
    def __init__(self, *args, _func, _funcname, _tester=None, _isregex=False, _iscontains=False, **kwargs):
        self.func = _func
        self.funcname = _funcname
        self.tester = _tester
        self.isregex = _isregex
        self.iscontains = _iscontains
        self.format_answer: Callable[[str], str] = lambda ans: ans
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
            self.expect = lambda ans: regex.search(expect, ans, regex.S) is not None
            self.format_answer = lambda ans: regex.sub(f"({expect})", r"<span>\1</span>", ans)
        elif self.iscontains:
            self.expect = lambda ans: expect in ans or all(exp in ans for exp in expect)
        else: self.expect = lambda ans: ans == expect
        return self
    @overload
    def test(self, verbose: Literal[False]) -> None: ...
    @overload
    def test(self, verbose: Literal[True]) -> TestExceptionResult: ...
    def test(self, verbose=False):
        try: answer = self.func(*self.args, **self.kwargs)
        except Exception as e:
            return TestException.fail(self, reason=e, verbose=verbose)
        good = False
        formated_answer = self.format_answer(html.escape(str(answer)))
        try: good = self.expect(answer)
        except Exception as e:
            return TestException.fail(self, formated_answer, reason=e, verbose=verbose)
        if not good: return TestException.fail(self, formated_answer, verbose=verbose)
        if not verbose: return None
        return TestException.success(self, formated_answer)


TesterResult = TypedDict('TesterResult', {"funcname": str, "tests": list[TestExceptionResult], "success": bool})
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
    @overload
    def test_all(cls, verbose: Literal[False]) -> None: ...
    @classmethod
    @overload
    def test_all(cls, verbose: Literal[True]) -> list[TesterResult]: ...
    @classmethod
    def test_all(cls, verbose=False) -> list[TesterResult]|None:
        if verbose is False:
            logs = [tester.test(False) for tester in cls.testers]
            return
        logs = [tester.test(True) for tester in cls.testers]
        return logs if verbose else None
    @overload
    def test(self, verbose: Literal[False]) -> None: ...
    @overload
    def test(self, verbose: Literal[True]) -> TesterResult: ...
    def test(self, verbose=False) -> TesterResult|None:
        if verbose is False:
            [test.test(False) for test in self.tests]
            return
        log = [test.test(True) for test in self.tests]
        return TesterResult(funcname=self.funcname, tests=log, success=all(line["success"] for line in log))
    def __call__(self, *args, **kwargs):
        self.tests.append(Test(*args, _func=self.func, _funcname=self.funcname, _tester=self.tester, _isregex=self.regex_expect, _iscontains=self.contains_expect, **kwargs))
        return self.tests[-1]