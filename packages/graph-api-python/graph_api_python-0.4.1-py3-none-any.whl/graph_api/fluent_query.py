from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from .base_element import BaseElement
    from .element_store import ElementStore


class FluentQuery:
    """Base class for fluent query operations."""

    def __init__(self, store: "ElementStore"):
        self.store = store
        self.result: List[BaseElement] = []
        self._operations_performed = False

    def r(self) -> List["BaseElement"]:
        """Get current result set or all elements if no operations performed."""
        if not self.result and not self._operations_performed:
            return self.store.get_all_elements()
        return self.result

    def reset(self) -> "FluentQuery":
        """Reset query result to all elements."""
        self.result = []
        self._operations_performed = False
        return self

    def get_result(self) -> List["BaseElement"]:
        """Get the current query result."""
        return self.result
