class _EnumReprMixin:
    def __repr__(self) -> str:
        name = self.name  # type: ignore
        return f"{type(self).__name__}.{name}"
