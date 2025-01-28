import strawberry
from gqlauth.user.queries import UserQueries, UserType
from gqlauth.core.middlewares import JwtSchema
from gqlauth.user import arg_mutations
from django.contrib.auth import get_user_model

from cotizador.graphql.queries import Query as CotizadorQuery
from cotizador.graphql.mutations import Mutation as CotizadorMutation

# Define user queries separately, limiting to only necessary fields
@strawberry.type
class AuthQuery:
    me: UserType = UserQueries.me
    public: UserType = UserQueries.public_user

# Merge authentication and application queries
@strawberry.type
class Query(CotizadorQuery, AuthQuery):
    pass

# Define authentication-related mutations, keeping only essential ones
@strawberry.type
class AuthMutation:
    verify_token = arg_mutations.VerifyToken.field
    update_account = arg_mutations.UpdateAccount.field
    delete_account = arg_mutations.DeleteAccount.field
    password_change = arg_mutations.PasswordChange.field
    token_auth = arg_mutations.ObtainJSONWebToken.field
    register = arg_mutations.Register.field
    verify_account = arg_mutations.VerifyAccount.field
    resend_activation_email = arg_mutations.ResendActivationEmail.field
    send_password_reset_email = arg_mutations.SendPasswordResetEmail.field
    password_reset = arg_mutations.PasswordReset.field
    password_set = arg_mutations.PasswordSet.field
    refresh_token = arg_mutations.RefreshToken.field
    revoke_token = arg_mutations.RevokeToken.field

# Merge authentication and application mutations
@strawberry.type
class Mutation(CotizadorMutation, AuthMutation):
    pass

# Create schema with JWT authentication middleware
schema = JwtSchema(query=Query, mutation=Mutation)
