import graphene
from cotizador.graphql.queries import Query as CotizadorQuery
from cotizador.graphql.mutations import Mutation as CotizadorMutation

class Query(CotizadorQuery, graphene.ObjectType):
    pass

class Mutation(CotizadorMutation, graphene.ObjectType):
    pass



schema = graphene.Schema(query=Query, mutation=Mutation)
