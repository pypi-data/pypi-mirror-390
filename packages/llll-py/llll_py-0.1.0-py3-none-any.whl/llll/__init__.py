""" 
author:         Felipe Tovar-Henao
email:          felipe.tovar@ufl.edu
date:           2025-11-08
description:    class definitions for llll and parser objects
license: MIT

copyright (c) 2025 Felipe Tovar-Henao
"""

import os
import json
import struct
import re
from typing import Self, Iterator, Any
from fractions import Fraction


class llll:
    """Python representation of a lisp-like linked list."""

    def __init__(self, *items):
        self._items = []
        for item in items:
            self._items.append(self._to_llll(item))

    def __eq__(self, other) -> bool:
        if not isinstance(other, llll):
            other = llll(other)

        if self._is_atom() and other._is_atom():
            return self._value == other._value

        if self._is_atom() or other._is_atom():
            return False

        if len(self._items) != len(other._items):
            return False

        return all(a == b for a, b in zip(self._items, other._items))

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def __lt__(self, other) -> bool:
        if not isinstance(other, llll):
            other = llll(other)

        if self._is_atom() and other._is_atom():
            return self._value < other._value

        if self._is_atom() or other._is_atom():
            return False

        if len(self._items) != len(other._items):
            return False

        return all(a < b for a, b in zip(self._items, other._items))

    def __le__(self, other) -> bool:
        if not isinstance(other, llll):
            other = llll(other)

        if self._is_atom() and other._is_atom():
            return self._value <= other._value

        if self._is_atom() or other._is_atom():
            return False

        if len(self._items) != len(other._items):
            return False

        return all(a <= b for a, b in zip(self._items, other._items))

    def __gt__(self, other) -> bool:
        if not isinstance(other, llll):
            other = llll(other)

        if self._is_atom() and other._is_atom():
            return self._value > other._value

        if self._is_atom() or other._is_atom():
            return False

        if len(self._items) != len(other._items):
            return False

        return all(a > b for a, b in zip(self._items, other._items))

    def __ge__(self, other) -> bool:
        if not isinstance(other, llll):
            other = llll(other)

        if self._is_atom() and other._is_atom():
            return self._value >= other._value

        if self._is_atom() or other._is_atom():
            return False

        if len(self._items) != len(other._items):
            return False

        return all(a >= b for a, b in zip(self._items, other._items))

    def _arithmetic_op(self, other, op, op_name) -> Self:
        if not isinstance(other, llll):
            other = llll(other)

        def _check_wrapper(x: llll):
            if isinstance(x, llll) and (not x._is_atom()) and len(x._items) == 1 and x._items[0]._is_atom():
                return x._items[0]._value
            return x

        if self._is_atom() and other._is_atom():
            if op_name == 'truediv' and isinstance(self._value, int) and isinstance(other._value, int):
                result = Fraction(self._value, other._value)
            else:
                result = op(self._value, other._value)
            return llll(result)

        if self._is_atom() and not other._is_atom():
            new_items = []
            for item in other._items:
                res = self._arithmetic_op(item, op, op_name)
                new_items.append(_check_wrapper(res))
            return llll(*new_items)

        if not self._is_atom() and other._is_atom():
            new_items = []
            for item in self._items:
                res = item._arithmetic_op(other, op, op_name)
                new_items.append(_check_wrapper(res))
            return llll(*new_items)

        len_self = len(self._items)
        len_other = len(other._items)

        if len_self == 1 and len_other > 1:
            new_items = []
            a = self._items[0]
            for b in other._items:
                res = a._arithmetic_op(b, op, op_name)
                new_items.append(_check_wrapper(res))
            return llll(*new_items)

        if len_other == 1 and len_self > 1:
            new_items = []
            b = other._items[0]
            for a in self._items:
                res = a._arithmetic_op(b, op, op_name)
                new_items.append(_check_wrapper(res))
            return llll(*new_items)

        if len_self == len_other:
            new_items = []
            for a, b in zip(self._items, other._items):
                res = a._arithmetic_op(b, op, op_name)
                new_items.append(_check_wrapper(res))
            return llll(*new_items)

        raise ValueError(
            f"Cannot perform element-wise operation on lllls of different lengths: {len_self} vs {len_other}")

    def __add__(self, other) -> Self:
        return self._arithmetic_op(other, lambda a, b: a + b, 'add')

    def __radd__(self, other) -> Self:
        return self.__add__(other)

    def __sub__(self, other) -> Self:
        return self._arithmetic_op(other, lambda a, b: a - b, 'sub')

    def __rsub__(self, other) -> Self:
        if not isinstance(other, llll):
            other = llll(other)
        return other.__sub__(self)

    def __mul__(self, other) -> Self:
        return self._arithmetic_op(other, lambda a, b: a * b, 'mul')

    def __rmul__(self, other) -> Self:
        return self.__mul__(other)

    def __truediv__(self, other) -> Self:
        return self._arithmetic_op(other, lambda a, b: a / b, 'truediv')

    def __rtruediv__(self, other) -> Self:
        if not isinstance(other, llll):
            other = llll(other)
        return other.__truediv__(self)

    def __pow__(self, other) -> Self:
        return self._arithmetic_op(other, lambda a, b: a ** b, 'pow')

    def __rpow__(self, other) -> Self:
        if not isinstance(other, llll):
            other = llll(other)
        return other.__pow__(self)

    def __mod__(self, other) -> Self:
        return self._arithmetic_op(other, lambda a, b: a % b, 'mod')

    def __rmod__(self, other) -> Self:
        if not isinstance(other, llll):
            other = llll(other)
        return other.__mod__(self)

    def __len__(self) -> int:
        if self._is_atom():
            return 1
        return len(self._items)

    def __getitem__(self, key) -> Self:
        if key == 0:
            return llll()

        if self._is_atom():
            return self.value()

        if isinstance(key, str):
            for x in self.__iter__():
                if x[1] == key:
                    return x[2:]
            return llll()

        if isinstance(key, slice):
            start = key.start if key.start is not None else 1
            stop = key.stop if key.stop is not None else len(self._items) + 1
            step = key.step if key.step is not None else 1

            start_idx = start - \
                1 if start > 0 else (len(self._items) +
                                     start if start < 0 else 0)
            stop_idx = stop - \
                1 if stop > 0 else (len(self._items) +
                                    stop if stop < 0 else len(self._items))

            sliced_items = self._items[start_idx:stop_idx + 1:step]
            return llll(*[item.to_python() for item in sliced_items])

        if isinstance(key, (tuple, list)):
            return self._get_by_address(key)

        idx = key - 1 if key > 0 else key
        if idx < 0:
            idx = len(self._items) + idx

        if not (0 <= idx < len(self._items)):
            raise IndexError(f"Index {key} out of range")

        item = self._items[idx]
        return item.value() if item._is_atom() else item

    def _get_by_address(self, address) -> Self:
        if not address:
            return self

        first, *rest = address
        element = self[first]

        if rest:
            return element._get_by_address(rest)
        return element

    def __setitem__(self, key, value) -> None:
        if self._is_atom():
            raise IndexError("Cannot set items in atomic llll")

        if isinstance(key, str):
            for i, x in enumerate(self):
                if x[1] == key:
                    if isinstance(value, (tuple, list, llll)):
                        new = llll(key, *value)
                    else:
                        new = llll(key, value)
                    self[i + 1] = new
                    break
            return

        if isinstance(key, (tuple, list)):
            if len(key) == 1:
                self[key[0]] = value
            else:
                self[key[0]]._set_by_address(key[1:], value)
            return

        idx = key - 1 if key > 0 else key
        if idx < 0:
            idx = len(self._items) + idx

        if not (0 <= idx < len(self._items)):
            raise IndexError(f"Index {key} out of range")

        self._items[idx] = self._to_llll(value)

    def __iter__(self) -> Iterator:
        if self._is_atom():
            return iter([])
        return iter(self._items)

    def __repr__(self) -> str:
        if self._is_atom():
            return repr(self._value)

        items_repr = ' '.join(repr(item) for item in self._items)
        return f"[ {items_repr} ]"

    def __str__(self) -> str:
        return self._to_str(top_level=True, indent=-1, min_depth=2)

    def _set_by_address(self, address, value) -> None:
        if len(address) == 1:
            self[address[0]] = value
        else:
            self[address[0]]._set_by_address(address[1:], value)

    def _to_llll(self, item) -> Self:
        if isinstance(item, llll):
            return item
        elif isinstance(item, (list, tuple)):
            return llll(*item)
        else:
            return llll.__new__(llll)._init_atomic(item)

    def wrap(self, n: int = 1) -> Self:
        for _ in range(n):
            self._items = llll(self._items)
        return self

    def _init_atomic(self, value) -> Self:
        self._items = None
        if isinstance(value, bool):
            value = int(value)
        self._value = value
        return self

    def as_float(self):
        return self.map(lambda x, addr: float(x))

    def as_int(self):
        return self.map(lambda x, addr: int(x))

    def as_rat(self):
        return self.map(lambda x, addr: Fraction.from_float(x))

    def _is_atom(self) -> bool:
        return self._items is None

    def value(self) -> Any:
        if not self._is_atom():
            raise ValueError("Cannot get value of non-atomic llll")
        return self._value

    def append(self, item) -> None:
        if self._is_atom():
            raise ValueError("Cannot append to atomic llll")
        self._items.append(self._to_llll(item))

    def extend(self, items) -> None:
        if self._is_atom():
            raise ValueError("Cannot extend atomic llll")
        for item in items:
            self.append(item)

    def depth(self) -> int:
        def _depth(x: llll):
            if x.__len__() == 0 or x._is_atom():
                return 0
            return 1 + max((_depth(item) for item in x._items), default=0)
        return max(_depth(self), 1)

    def _to_str(self, top_level=False, indent=0, min_depth=2) -> str:
        if self._is_atom():
            return str(self._value)

        if self.__len__() == 0:
            return 'null'

        use_indented = self.depth() >= min_depth

        if use_indented:
            indent_str = '  ' * indent
            next_indent = '  ' * (indent + 1)

            items_str = []
            for item in self._items:
                item_repr = item._to_str(
                    indent=indent + 1, min_depth=min_depth)
                items_str.append(f'\n{next_indent}{item_repr}')

            items_content = ''.join(items_str)

            if top_level:
                return items_content.lstrip()
            return f'[{items_content}\n{indent_str}]'
        else:
            items_str = ' '.join(item._to_str(min_depth=min_depth)
                                 for item in self._items)

            if top_level:
                return items_str
            return f'[ {items_str} ]'

    def to_python(self) -> Any:
        if self._is_atom():
            return self._value
        return [item.to_python() for item in self._items]

    @classmethod
    def from_python(cls, obj) -> Self:
        if isinstance(obj, (list, tuple)):
            return cls(*obj)
        else:
            return cls(obj)

    def map(self, func, mindepth=1, maxdepth=float('inf'), _current_depth=1, _address=()) -> Self:
        if self._is_atom():
            if mindepth <= _current_depth <= maxdepth:
                result = func(self._value, _address)
                return llll(result)
            return llll(self._value)

        if len(self._items) == 0:
            return llll()

        new_items = []
        for idx, item in enumerate(self._items):
            current_address = _address + (idx + 1,)

            if item._is_atom():
                if mindepth <= _current_depth <= maxdepth:
                    result = func(item._value, current_address)
                    new_items.append(result)
                else:
                    new_items.append(item._value)
            else:
                if _current_depth < maxdepth:
                    mapped_item = item.map(
                        func,
                        mindepth=mindepth,
                        maxdepth=maxdepth,
                        _current_depth=_current_depth + 1,
                        _address=current_address
                    )
                    new_items.append(mapped_item)
                else:
                    new_items.append(item)

        return llll(*new_items)

    @classmethod
    def read(cls, file: str) -> Self:
        return Parser.deserialize(file)

    def write(self, file: str) -> None:
        Parser.serialize(l=self, file=file)


class Parser:

    FLOAT64_STR = "_x_x_x_x_bach_float64_x_x_x_x_"

    @classmethod
    def deserialize(cls, file: str) -> llll:
        ext = os.path.splitext(file)[1]
        if ext not in ['.txt', '.llll']:
            raise ImportError(
                f'Invalid extension: {ext}\nFile must be .txt or .llll')
        with open(file, 'r') as f:
            raw_data = f.read()

        if ext == '.llll':
            return cls.__parse_native(raw_data)
        else:
            return cls.__parse_text(raw_data)

    @classmethod
    def __interpret_token(cls, token: str) -> str | int | float | Fraction:
        if (token.startswith("'") and token.endswith("'")) or \
                (token.startswith('"') and token.endswith('"')):
            return token[1:-1]

        # Check for backtick-prefixed symbol
        if token.startswith('`'):
            return token[1:]

        if re.match(r'^[+-]?\d+/\d+$', token):
            rat = token.split('/')
            return Fraction(int(rat[0]), int(rat[1]))

        # Check integer
        if re.match(r'^-?\d+$', token):
            return int(token)

        # Check float
        if re.match(r'^(-?\d*\.\d+|-?Inf)$', token):
            return float(token)

        return token

    @classmethod
    def __parse_text(cls, data: str) -> llll:
        tokens = cls.__tokenize(data)
        return llll(*cls.__parse_tokens(tokens))

    @classmethod
    def __tokenize(cls, content: str) -> list:
        token_pattern = r"""
            '[^']*'                    |  # Single quoted strings
            "[^"]*"                    |  # Double quoted strings
            `\S+                       |  # Backtick-prefixed symbols without spaces
            [\[\]]                     |  # Brackets for nesting
            [^\s\[\]'"`]+                 # Unquoted symbols, integers, and floats
        """

        return re.findall(token_pattern, content, re.VERBOSE)

    @classmethod
    def __parse_tokens(cls, tokens) -> list:
        stack = [[]]

        for token in tokens:
            if token == '[':
                new_list = []
                stack[-1].append(new_list)
                stack.append(new_list)
            elif token == ']':
                if len(stack) == 1:
                    raise ValueError("Unbalanced brackets detected.")
                stack.pop()
            else:
                parsed_token = cls.__interpret_token(token)
                stack[-1].append(parsed_token)

        if len(stack) != 1:
            raise ValueError("Unbalanced brackets detected at end of parsing.")

        return stack[0]

    @classmethod
    def serialize(cls, l: llll, file: str) -> None:
        ext = os.path.splitext(file)[1]
        if ext not in ['.txt', '.llll']:
            raise ValueError(f'Invalid extension: {ext}')
        if ext == '.txt':
            with open(file, 'w') as f:
                f.write(l.__str__())
            return

        data = []

        def traverse(x):
            for item in x:
                if item._is_atom():
                    value = item.value()
                    if isinstance(value, float):
                        low, high = cls.encode_float(value)
                        data.extend(
                            [cls.FLOAT64_STR, low, high])
                    elif isinstance(value, Fraction):
                        data.append(str(value))
                    else:
                        data.append(value)
                else:
                    data.append('[')
                    traverse(item)
                    data.append(']')
        traverse(l)
        data_len = len(data)
        chunk_size = 4096
        num_chunks = data_len // chunk_size + 1
        native_data = {}
        for i in range(num_chunks):
            st = i * chunk_size
            end = st + chunk_size
            key = f"data_{i:010}"
            native_data[key] = data[st:end]
        native_data['data_count'] = [num_chunks]
        with open(file, 'w') as f:
            json.dump(obj=native_data, fp=f)

    @classmethod
    def __parse_native(cls, data: str) -> llll:

        obj = json.loads(s=data)
        data_count = obj['data_count'][0]
        items = []
        for i in range(data_count):
            items.extend(obj[f"data_{i:010}"])

        items = iter(items)

        def consume() -> llll:
            l = llll()
            while True:
                item = next(items, None)
                if item in [None, ']']:
                    return l
                elif item == '[':
                    l.append(consume())
                else:
                    if item == cls.FLOAT64_STR:
                        low, high = (next(items) for _ in range(2))
                        item = cls.decode_float(low=low, high=high)
                    elif isinstance(item, str):
                        pat = re.compile(pattern=r"[+-]?\d+/\d+")
                        match = pat.search(item)
                        if match:
                            rat = match[0].split('/')
                            item = Fraction(int(rat[0]), int(rat[1]))

                    l.append(item)

        return consume()

    @staticmethod
    def decode_float(low: int, high: int) -> float:
        return struct.unpack('<d', struct.pack('<II', low, high))[0]

    @staticmethod
    def encode_float(value: float) -> tuple[int, int]:
        low, high = struct.unpack('<II', struct.pack('<d', value))
        return low, high


__all__ = ["llll"]
