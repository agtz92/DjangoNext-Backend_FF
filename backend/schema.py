import strawberry
from cotizador.graphql.queries import Query as CotizadorQuery
from cotizador.graphql.mutations import Mutation as CotizadorMutation


@strawberry.type
class Query(CotizadorQuery):
    pass


@strawberry.type
class Mutation(CotizadorMutation):
    pass


schema = strawberry.Schema(query=Query, mutation=Mutation)
