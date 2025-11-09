from typing import Any, List, Optional


class Stack:
    def __init__(self) -> None:
        self._items: List[Any] = []
    
    def push(self, item: Any) -> None:
        self._items.append(item)
    
    def pop(self) -> Any:
        if self.is_empty():
            raise IndexError("pop from empty stack")
        return self._items.pop()
    
    def peek(self) -> Any:
        if self.is_empty():
            raise IndexError("peek from empty stack")
        return self._items[-1]
    
    def is_empty(self) -> bool:
        return len(self._items) == 0
    
    def size(self) -> int:
        return len(self._items)
    
    def clear(self) -> None:
        self._items.clear()
    
    def __repr__(self) -> str:
        return f"Stack({self._items})"
    
    def __str__(self) -> str:
        if self.is_empty():
            return "Stack(empty)"
        items_str = " -> ".join(str(item) for item in reversed(self._items))
        return f"Stack(top -> {items_str})"
    
    def __len__(self) -> int:
        return len(self._items)


def reverse_string(text: str) -> str:
    stack = Stack()
    for char in text:
        stack.push(char)
    
    result = []
    while not stack.is_empty():
        result.append(stack.pop())
    
    return "".join(result)


def is_balanced(expression: str) -> bool:
    stack = Stack()
    pairs = {"(": ")", "[": "]", "{": "}"}
    
    for char in expression:
        if char in pairs:
            stack.push(char)
        elif char in pairs.values():
            if stack.is_empty():
                return False
            if pairs[stack.pop()] != char:
                return False
    
    return stack.is_empty()
