from dataclasses import dataclass

import enum

from ariadne import ObjectType, QueryType, snake_case_fallback_resolvers, EnumType, fallback_resolvers, ScalarType
from ariadne_extensions.federation import FederatedManager, FederatedObjectType

from schema.data_interface import DataStorage

@dataclass
class BoundaryGeneric:

    def __init__(self, child_name, kwargs=None):
        self.typename = child_name

        if kwargs:
            self.update_class(kwargs)

        self.get_updated()

    def update_class(self, kwargs):
        for k, v in kwargs.items():
            if not hasattr(self, k):
                setattr(self, k, v)

    def get_updated(self):
        return self


class Bundle_Enum_schema(enum.IntEnum):
    Bundle = 1


bundle_enum_schema = EnumType("Bundle_Enum_schema", Bundle_Enum_schema)

"""
Dataclasses, These need to be defined for Boundry Types (A GraphQL type from another server that you are Extending
"""
@dataclass
class User(BoundaryGeneric):
    def __init__(self, **kwargs):
        super().__init__(self.__class__.__name__, kwargs)

@dataclass
class Account(BoundaryGeneric):
    def __init__(self, **kwargs):
        super().__init__(self.__class__.__name__, kwargs)

@dataclass
class Bundle(BoundaryGeneric):
    def __init__(self, **kwargs):
        self.resourceType = bundle_enum_schema
        super().__init__(self.__class__.__name__, kwargs)


class AccountList(Bundle):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

@dataclass
class Patient(BoundaryGeneric):
    def __init__(self, obj, info):
        self.update_class(info)

@dataclass
class HumanName(BoundaryGeneric):
    def __init__(self, obj, info):
        self.update_class(info)

    def __init__(self, value):
        print(value, flush=True)


"""
Creates the Schema and adds the Federation Declerations to it according to the [https://www.apollographql.com/docs/apollo-server/federation/federation-spec/](Apollo Spec).
"""
class SchemaCreator:
    data = DataStorage()
    query = QueryType()
    account = FederatedObjectType("Account")
    bundle = FederatedObjectType("Bundle")
    patient = FederatedObjectType("Patient")
    text = FederatedObjectType("Narrative")
    human_name = ScalarType("HumanName")

    def __init__(self):
        self.ds = DataStorage()

    def getSchema(self):

        manager = FederatedManager(
            schema_sdl_file='schema/fhir_schema_4_0_0.graphql',
            query=self.query,
        )

        @self.human_name.serializer
        def serialize_datetime(value):
            return HumanName(value)

        @self.query.field("Patient")
        def resolve_patient(obj, info, **kwargs):
            return Patient(obj, info=self.data.getPatient(**kwargs)[0])

        @self.query.field("Account")
        def resolve_account(*_, **kwargs):
            return Account(**kwargs)

        @self.query.field("ActivityDefinition")
        def resolve_account(*_, **kwargs):
            return Account(**kwargs)

        @self.query.field("AccountList")
        def resolve_account_list(obj, info):
            alist = AccountList(obj, info)
            return [alist,]

        @self.account.resolve_references
        def resolve_accounts(obj, info):
            return AccountList(name="test")

        @self.patient.resolve_reference
        def resolve_patient(obj, info):
            return Patient(obj, info)

        manager.add_types(self.account, self.bundle, self.patient, self.text)
        manager.add_types(bundle_enum_schema)
        manager.add_types(snake_case_fallback_resolvers, fallback_resolvers)

        return manager.get_schema()