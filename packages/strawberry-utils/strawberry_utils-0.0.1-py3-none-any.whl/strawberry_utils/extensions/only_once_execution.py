import typing as t

from graphql import GraphQLError
from strawberry import Info
from strawberry.extensions import FieldExtension
from strawberry.extensions.field_extension import (
    AsyncExtensionResolver,
    SyncExtensionResolver,
)


class OnlyOnceExecution(FieldExtension):
    """
    A GraphQL field extension that guarantees a field is resolved only
    once per request.

    Usage:

        Ensure your context includes an `only_once_set` attribute,
        initialized as an empty set:

        >>> @dataclass
        >>> class Context:
        >>>     only_once_set: set[str] = field(default_factory=set)

        Then, apply the extension to your field:

        >>> @strawberry.type
        >>> class Query:
        >>>     @strawberry.field(extensions=[OnlyOnceExecution()])
        >>>     async def not_optimized_field(self) -> str:
        >>>         return 'not optimized'

        If the same field is requested multiple times in a single query,
        an error will be raised:

        {
            notOptimizedField
            notOptimizedField2: notOptimizedField # will raise an error
        }
    """

    def validate(self, source: t.Any, info: Info) -> None:
        field_name = f"{source.__class__.__name__}.{info.field_name}"

        if field_name in info.context.only_once_set:
            raise GraphQLError(
                f"Field '{field_name}' has already been resolved"
            )

        info.context.only_once_set.add(field_name)

        return None

    def resolve(
        self,
        next_: SyncExtensionResolver,
        source: t.Any,
        info: Info,
        **kwargs: t.Any,
    ) -> t.Any:
        self.validate(source, info)

        return next_(source, info, **kwargs)

    async def resolve_async(
        self,
        next_: AsyncExtensionResolver,
        source: t.Any,
        info: Info,
        **kwargs: t.Any,
    ) -> t.Any:
        self.validate(source, info)

        return await next_(source, info, **kwargs)
