import json
import sys
import types
import typing


class TSTError(Exception):
    _func_trace: list[str]
    _message: str
    _tag: str
    _metadata: typing.Dict[str, typing.Any] | None

    def __init__(
        self,
        tag: str,
        message: str,
        can_inspect=True,
        other_exception: Exception | None = None,
        metadata: typing.Dict[str, typing.Any] | None = None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._func_trace = []
        self._message = message
        self._tag = tag
        self._metadata = metadata

        if can_inspect:
            tb = None

            # Collect stack frames from current (depth=1 to skip __init__ frame) to outermost
            frames = []
            depth = 1  # Start from caller to exclude this __init__
            while True:
                try:
                    frames.append(sys._getframe(depth))
                    depth += 1
                except ValueError:
                    break

            # Build the traceback chain: innermost first, tb_next pointing outward

            for frame in reversed(frames):  # Process from outermost to innermost
                tb = types.TracebackType(tb, frame, frame.f_lasti, frame.f_lineno)

            while tb is not None:
                frame = tb.tb_frame
                func_name = frame.f_code.co_name
                if "self" in frame.f_locals:
                    class_name = frame.f_locals["self"].__class__.__name__
                    self._func_trace.append(f"{class_name}.{func_name}")
                else:
                    self._func_trace.append(func_name)
                tb = tb.tb_next

            self._func_trace.reverse()

            if other_exception is not None:
                call_stack = []
                tb = other_exception.__traceback__
                while tb is not None:
                    frame = tb.tb_frame
                    func_name = frame.f_code.co_name
                    if "self" in frame.f_locals:
                        class_name = frame.f_locals["self"].__class__.__name__
                        call_stack.append(f"{class_name}.{func_name}")
                    else:
                        call_stack.append(func_name)
                    tb = tb.tb_next

                self._func_trace = self._func_trace + call_stack

            self._func_trace[len(self._func_trace) - 1] = (
                f"{self._func_trace[len(self._func_trace) - 1]}.{tag}"
            )

    def __str__(self) -> str:
        if self._message:
            return self._message
        else:
            return super().__str__()

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        return {
            "func_trace": self._func_trace,
            "message": self._message,
            "tag": self._tag,
        }

    def func_trace(self) -> list[str]:
        return self._func_trace

    def message(self) -> str:
        return self._message

    def tag(self) -> str:
        return self._tag

    def metadata(self) -> typing.Dict[str, typing.Any] | None:
        return self._metadata

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    def routes(self, *func_names: str) -> bool:
        return self._func_trace == list(func_names)

    def sub_routes(self, *func_names: str) -> bool:
        param_fns = list(func_names)
        # empty sublist will be always false as there is no reason to
        # check with empty list
        if not param_fns:
            return False

        i = 0
        m = len(param_fns)
        for elem in self._func_trace:
            if i < m and elem == param_fns[i]:
                i += 1
            if i == m:
                return True
        return False

    def fuzzy_routes(self, *func_names: str) -> bool:
        ls_func_names = list(func_names)
        for v in self._func_trace:
            if len(ls_func_names) > 0:
                if v == ls_func_names[0]:
                    del ls_func_names[0]
            else:
                return True
        return not len(ls_func_names) > 0

    def set_func_trace(self, func_trace: list[str]) -> None:
        self._func_trace = func_trace

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TSTError):
            return False
        return (
            self.func_trace() == other.func_trace()
            and self.message() == other.message()
            and self.tag() == other.tag()
            and self.message() == other.message()
        )
