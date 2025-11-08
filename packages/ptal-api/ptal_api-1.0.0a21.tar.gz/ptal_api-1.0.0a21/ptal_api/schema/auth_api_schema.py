import sgqlc.types


auth_api_schema = sgqlc.types.Schema()



########################################################################
# Scalars and Enumerations
########################################################################
class AllowedFunctionsEnum(sgqlc.types.Enum):
    __schema__ = auth_api_schema
    __choices__ = ('Administration', 'Developer', 'EditCrawlers', 'EditDataImport', 'EditDocumentFeeds', 'EditExport', 'EditExternalSearch', 'EditKBAndDocuments', 'EditReferenceInfo', 'EditResearchMaps', 'EditStream', 'EditTransformations', 'ExportKBAndDocuments', 'ReadCrawlers', 'ReadDataImport', 'ReadDocumentFeeds', 'ReadExport', 'ReadExternalSearch', 'ReadKBAndDocuments', 'ReadReferenceInfo', 'ReadReportExport', 'ReadResearchMaps', 'ReadStream', 'ReadTransformations', 'RunCrawlers', 'RunDataImport', 'RunExternalSearch', 'RunTransformations', 'SourcesCustomizer', 'SourcesTechSupport', 'SourcesVerifier')


class AttributeSource(sgqlc.types.Enum):
    __schema__ = auth_api_schema
    __choices__ = ('Personal', 'Role')


class AttributeType(sgqlc.types.Enum):
    __schema__ = auth_api_schema
    __choices__ = ('boolean', 'booleanList', 'double', 'doubleList', 'int', 'intList', 'string', 'stringList')


Boolean = sgqlc.types.Boolean

Float = sgqlc.types.Float

ID = sgqlc.types.ID

Int = sgqlc.types.Int

class JSON(sgqlc.types.Scalar):
    __schema__ = auth_api_schema


class Long(sgqlc.types.Scalar):
    __schema__ = auth_api_schema


class PolicyIndex(sgqlc.types.Enum):
    __schema__ = auth_api_schema
    __choices__ = ('concepts', 'documents')


class PolicyType(sgqlc.types.Enum):
    __schema__ = auth_api_schema
    __choices__ = ('es', 'local')


class SortDirection(sgqlc.types.Enum):
    __schema__ = auth_api_schema
    __choices__ = ('ascending', 'descending')


String = sgqlc.types.String

class UnixTime(sgqlc.types.Scalar):
    __schema__ = auth_api_schema


class UserAction(sgqlc.types.Enum):
    __schema__ = auth_api_schema
    __choices__ = ('create', 'delete', 'markup', 'read', 'work')


class UserActivityAction(sgqlc.types.Enum):
    __schema__ = auth_api_schema
    __choices__ = ('createConcept', 'createDocument', 'createLink', 'deleteConcept', 'deleteDocument', 'deleteLink', 'markupDocument', 'readConcept', 'readDocument', 'updateConcept', 'updateDocument', 'updateLink')


class UserActivityEntityType(sgqlc.types.Enum):
    __schema__ = auth_api_schema
    __choices__ = ('concept', 'document', 'link')


class UserActivitySearchType(sgqlc.types.Enum):
    __schema__ = auth_api_schema
    __choices__ = ('conceptRegistry', 'crawler', 'documentRegistry', 'externalSearch')


class UserActivitySorting(sgqlc.types.Enum):
    __schema__ = auth_api_schema
    __choices__ = ('createdAt',)


class UserHistoryGrouping(sgqlc.types.Enum):
    __schema__ = auth_api_schema
    __choices__ = ('daily', 'none')


class UserSearchHistorySorting(sgqlc.types.Enum):
    __schema__ = auth_api_schema
    __choices__ = ('createdAt',)



########################################################################
# Input Objects
########################################################################
class AddUserActivityInput(sgqlc.types.Input):
    __schema__ = auth_api_schema
    __field_names__ = ('entity_ids', 'entity_type', 'metadata', 'user_action')
    entity_ids = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='entityIds')
    entity_type = sgqlc.types.Field(sgqlc.types.non_null(UserActivityEntityType), graphql_name='entityType')
    metadata = sgqlc.types.Field(String, graphql_name='metadata')
    user_action = sgqlc.types.Field(sgqlc.types.non_null(UserAction), graphql_name='userAction')


class AddUserGroupInput(sgqlc.types.Input):
    __schema__ = auth_api_schema
    __field_names__ = ('description', 'name')
    description = sgqlc.types.Field(String, graphql_name='description')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')


class AddUserGroupMembersInput(sgqlc.types.Input):
    __schema__ = auth_api_schema
    __field_names__ = ('group_ids', 'user_ids')
    group_ids = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='groupIds')
    user_ids = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='userIds')


class AddUserInput(sgqlc.types.Input):
    __schema__ = auth_api_schema
    __field_names__ = ('access_level_id', 'email', 'enabled', 'fathers_name', 'first_name', 'last_name', 'login', 'receive_notifications', 'receive_telegram_notifications', 'telegram_chat_id')
    access_level_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='accessLevelId')
    email = sgqlc.types.Field(String, graphql_name='email')
    enabled = sgqlc.types.Field(Boolean, graphql_name='enabled')
    fathers_name = sgqlc.types.Field(String, graphql_name='fathersName')
    first_name = sgqlc.types.Field(String, graphql_name='firstName')
    last_name = sgqlc.types.Field(String, graphql_name='lastName')
    login = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='login')
    receive_notifications = sgqlc.types.Field(Boolean, graphql_name='receiveNotifications')
    receive_telegram_notifications = sgqlc.types.Field(Boolean, graphql_name='receiveTelegramNotifications')
    telegram_chat_id = sgqlc.types.Field(Long, graphql_name='telegramChatId')


class AddUserRoleAssignmentsInput(sgqlc.types.Input):
    __schema__ = auth_api_schema
    __field_names__ = ('role_ids', 'user_ids')
    role_ids = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='roleIds')
    user_ids = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='userIds')


class AddUserRoleInput(sgqlc.types.Input):
    __schema__ = auth_api_schema
    __field_names__ = ('description', 'name')
    description = sgqlc.types.Field(String, graphql_name='description')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')


class AddUserSearchHistoryInput(sgqlc.types.Input):
    __schema__ = auth_api_schema
    __field_names__ = ('search_string', 'search_type')
    search_string = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='searchString')
    search_type = sgqlc.types.Field(sgqlc.types.non_null(UserActivitySearchType), graphql_name='searchType')


class AttributeFilterSettings(sgqlc.types.Input):
    __schema__ = auth_api_schema
    __field_names__ = ('description', 'input_value', 'name')
    description = sgqlc.types.Field(String, graphql_name='description')
    input_value = sgqlc.types.Field(String, graphql_name='inputValue')
    name = sgqlc.types.Field(String, graphql_name='name')


class DeleteUserGroupMembersInput(sgqlc.types.Input):
    __schema__ = auth_api_schema
    __field_names__ = ('group_ids', 'user_ids')
    group_ids = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='groupIds')
    user_ids = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='userIds')


class DeleteUserRoleAssignmentsInput(sgqlc.types.Input):
    __schema__ = auth_api_schema
    __field_names__ = ('role_ids', 'user_ids')
    role_ids = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='roleIds')
    user_ids = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='userIds')


class PolicyParameterInputGQL(sgqlc.types.Input):
    __schema__ = auth_api_schema
    __field_names__ = ('param', 'parameter_type')
    param = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='param')
    parameter_type = sgqlc.types.Field(sgqlc.types.non_null(AttributeType), graphql_name='parameterType')


class SecurityPolicyArg(sgqlc.types.Input):
    __schema__ = auth_api_schema
    __field_names__ = ('id', 'index', 'name', 'params', 'policy_type', 'rule', 'target')
    id = sgqlc.types.Field(String, graphql_name='id')
    index = sgqlc.types.Field(PolicyIndex, graphql_name='index')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    params = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(PolicyParameterInputGQL))), graphql_name='params')
    policy_type = sgqlc.types.Field(sgqlc.types.non_null(PolicyType), graphql_name='policyType')
    rule = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='rule')
    target = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='target')


class TimestampInterval(sgqlc.types.Input):
    __schema__ = auth_api_schema
    __field_names__ = ('end', 'start')
    end = sgqlc.types.Field(UnixTime, graphql_name='end')
    start = sgqlc.types.Field(UnixTime, graphql_name='start')


class UpdateCurrentUserInput(sgqlc.types.Input):
    __schema__ = auth_api_schema
    __field_names__ = ('current_password', 'email', 'fathers_name', 'first_name', 'last_name', 'receive_notifications', 'receive_telegram_notifications', 'telegram_chat_id')
    current_password = sgqlc.types.Field(String, graphql_name='currentPassword')
    email = sgqlc.types.Field(String, graphql_name='email')
    fathers_name = sgqlc.types.Field(String, graphql_name='fathersName')
    first_name = sgqlc.types.Field(String, graphql_name='firstName')
    last_name = sgqlc.types.Field(String, graphql_name='lastName')
    receive_notifications = sgqlc.types.Field(Boolean, graphql_name='receiveNotifications')
    receive_telegram_notifications = sgqlc.types.Field(Boolean, graphql_name='receiveTelegramNotifications')
    telegram_chat_id = sgqlc.types.Field(Long, graphql_name='telegramChatId')


class UpdateUserGroupInput(sgqlc.types.Input):
    __schema__ = auth_api_schema
    __field_names__ = ('description', 'name')
    description = sgqlc.types.Field(String, graphql_name='description')
    name = sgqlc.types.Field(String, graphql_name='name')


class UpdateUserInput(sgqlc.types.Input):
    __schema__ = auth_api_schema
    __field_names__ = ('access_level_id', 'email', 'enabled', 'fathers_name', 'first_name', 'last_name', 'receive_notifications', 'receive_telegram_notifications', 'telegram_chat_id')
    access_level_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='accessLevelId')
    email = sgqlc.types.Field(String, graphql_name='email')
    enabled = sgqlc.types.Field(Boolean, graphql_name='enabled')
    fathers_name = sgqlc.types.Field(String, graphql_name='fathersName')
    first_name = sgqlc.types.Field(String, graphql_name='firstName')
    last_name = sgqlc.types.Field(String, graphql_name='lastName')
    receive_notifications = sgqlc.types.Field(Boolean, graphql_name='receiveNotifications')
    receive_telegram_notifications = sgqlc.types.Field(Boolean, graphql_name='receiveTelegramNotifications')
    telegram_chat_id = sgqlc.types.Field(Long, graphql_name='telegramChatId')


class UpdateUserRoleInput(sgqlc.types.Input):
    __schema__ = auth_api_schema
    __field_names__ = ('description', 'name')
    description = sgqlc.types.Field(String, graphql_name='description')
    name = sgqlc.types.Field(String, graphql_name='name')


class UserActivityFilterSettings(sgqlc.types.Input):
    __schema__ = auth_api_schema
    __field_names__ = ('created_at', 'entity_ids', 'entity_type_ids', 'history_grouping')
    created_at = sgqlc.types.Field(TimestampInterval, graphql_name='createdAt')
    entity_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='entityIds')
    entity_type_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='entityTypeIds')
    history_grouping = sgqlc.types.Field(UserHistoryGrouping, graphql_name='historyGrouping')


class UserAttributeInput(sgqlc.types.Input):
    __schema__ = auth_api_schema
    __field_names__ = ('id', 'json_value')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    json_value = sgqlc.types.Field(sgqlc.types.non_null(JSON), graphql_name='jsonValue')


class UserFilterSettings(sgqlc.types.Input):
    __schema__ = auth_api_schema
    __field_names__ = ('created_at', 'creators', 'email', 'enabled', 'fathers_name', 'first_name', 'group_ids', 'input_value', 'last_name', 'login', 'role_ids', 'show_system_users', 'updated_at', 'updaters', 'user_id')
    created_at = sgqlc.types.Field(TimestampInterval, graphql_name='createdAt')
    creators = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='creators')
    email = sgqlc.types.Field(String, graphql_name='email')
    enabled = sgqlc.types.Field(Boolean, graphql_name='enabled')
    fathers_name = sgqlc.types.Field(String, graphql_name='fathersName')
    first_name = sgqlc.types.Field(String, graphql_name='firstName')
    group_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='groupIds')
    input_value = sgqlc.types.Field(String, graphql_name='inputValue')
    last_name = sgqlc.types.Field(String, graphql_name='lastName')
    login = sgqlc.types.Field(String, graphql_name='login')
    role_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='roleIds')
    show_system_users = sgqlc.types.Field(Boolean, graphql_name='showSystemUsers')
    updated_at = sgqlc.types.Field(TimestampInterval, graphql_name='updatedAt')
    updaters = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='updaters')
    user_id = sgqlc.types.Field(ID, graphql_name='userId')


class UserGroupFilterSettings(sgqlc.types.Input):
    __schema__ = auth_api_schema
    __field_names__ = ('created_at', 'creators', 'description', 'input_value', 'name', 'updated_at', 'updaters', 'user_group_id')
    created_at = sgqlc.types.Field(TimestampInterval, graphql_name='createdAt')
    creators = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='creators')
    description = sgqlc.types.Field(String, graphql_name='description')
    input_value = sgqlc.types.Field(String, graphql_name='inputValue')
    name = sgqlc.types.Field(String, graphql_name='name')
    updated_at = sgqlc.types.Field(TimestampInterval, graphql_name='updatedAt')
    updaters = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='updaters')
    user_group_id = sgqlc.types.Field(ID, graphql_name='userGroupId')


class UserRoleFilterSettings(sgqlc.types.Input):
    __schema__ = auth_api_schema
    __field_names__ = ('created_at', 'creators', 'description', 'input_value', 'name', 'updated_at', 'updaters', 'user_role_id')
    created_at = sgqlc.types.Field(TimestampInterval, graphql_name='createdAt')
    creators = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='creators')
    description = sgqlc.types.Field(String, graphql_name='description')
    input_value = sgqlc.types.Field(String, graphql_name='inputValue')
    name = sgqlc.types.Field(String, graphql_name='name')
    updated_at = sgqlc.types.Field(TimestampInterval, graphql_name='updatedAt')
    updaters = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='updaters')
    user_role_id = sgqlc.types.Field(ID, graphql_name='userRoleId')


class UserSearchHistoryFilterSettings(sgqlc.types.Input):
    __schema__ = auth_api_schema
    __field_names__ = ('created_at', 'history_grouping', 'search_string', 'search_type')
    created_at = sgqlc.types.Field(TimestampInterval, graphql_name='createdAt')
    history_grouping = sgqlc.types.Field(UserHistoryGrouping, graphql_name='historyGrouping')
    search_string = sgqlc.types.Field(String, graphql_name='searchString')
    search_type = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(UserActivitySearchType)), graphql_name='searchType')



########################################################################
# Output Objects and Interfaces
########################################################################
class RecordInterface(sgqlc.types.Interface):
    __schema__ = auth_api_schema
    __field_names__ = ('creator', 'last_updater', 'system_registration_date', 'system_update_date')
    creator = sgqlc.types.Field(sgqlc.types.non_null('User'), graphql_name='creator')
    last_updater = sgqlc.types.Field('User', graphql_name='lastUpdater')
    system_registration_date = sgqlc.types.Field(sgqlc.types.non_null(UnixTime), graphql_name='systemRegistrationDate')
    system_update_date = sgqlc.types.Field(UnixTime, graphql_name='systemUpdateDate')


class AccessLevel(sgqlc.types.Type):
    __schema__ = auth_api_schema
    __field_names__ = ('id', 'name', 'order')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    order = sgqlc.types.Field(sgqlc.types.non_null(Long), graphql_name='order')


class Attribute(sgqlc.types.Type):
    __schema__ = auth_api_schema
    __field_names__ = ('description', 'id', 'name', 'params_schema', 'value_type')
    description = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='description')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    params_schema = sgqlc.types.Field(sgqlc.types.non_null('ParamsSchema'), graphql_name='paramsSchema')
    value_type = sgqlc.types.Field(sgqlc.types.non_null(AttributeType), graphql_name='valueType')


class AttributePagination(sgqlc.types.Type):
    __schema__ = auth_api_schema
    __field_names__ = ('list_attribute', 'total')
    list_attribute = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(Attribute))), graphql_name='listAttribute')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class BooleanListValue(sgqlc.types.Type):
    __schema__ = auth_api_schema
    __field_names__ = ('value',)
    value = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(Boolean))), graphql_name='value')


class BooleanValue(sgqlc.types.Type):
    __schema__ = auth_api_schema
    __field_names__ = ('value',)
    value = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='value')


class Concept(sgqlc.types.Type):
    __schema__ = auth_api_schema
    __field_names__ = ('concept_type', 'id', 'name')
    concept_type = sgqlc.types.Field(sgqlc.types.non_null('ConceptType'), graphql_name='conceptType')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')


class ConceptLink(sgqlc.types.Type):
    __schema__ = auth_api_schema
    __field_names__ = ('id', 'link_type', 'name')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    link_type = sgqlc.types.Field(sgqlc.types.non_null('ConceptLinkType'), graphql_name='linkType')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')


class ConceptLinkType(sgqlc.types.Type):
    __schema__ = auth_api_schema
    __field_names__ = ('id', 'name')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')


class ConceptType(sgqlc.types.Type):
    __schema__ = auth_api_schema
    __field_names__ = ('id', 'name')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')


class Document(sgqlc.types.Type):
    __schema__ = auth_api_schema
    __field_names__ = ('document_type', 'id', 'name')
    document_type = sgqlc.types.Field(sgqlc.types.non_null('DocumentType'), graphql_name='documentType')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')


class DocumentType(sgqlc.types.Type):
    __schema__ = auth_api_schema
    __field_names__ = ('id', 'name')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')


class DoubleListValue(sgqlc.types.Type):
    __schema__ = auth_api_schema
    __field_names__ = ('value',)
    value = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(Float))), graphql_name='value')


class DoubleValue(sgqlc.types.Type):
    __schema__ = auth_api_schema
    __field_names__ = ('value',)
    value = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='value')


class IntListValue(sgqlc.types.Type):
    __schema__ = auth_api_schema
    __field_names__ = ('value',)
    value = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(Int))), graphql_name='value')


class IntValue(sgqlc.types.Type):
    __schema__ = auth_api_schema
    __field_names__ = ('value',)
    value = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='value')


class Mutation(sgqlc.types.Type):
    __schema__ = auth_api_schema
    __field_names__ = ('add_policy', 'add_user', 'add_user_activity', 'add_user_group', 'add_user_group_members', 'add_user_role', 'add_user_role_assignments', 'add_user_search_history', 'delete_kvstore_item', 'delete_policy', 'delete_user', 'delete_user_group', 'delete_user_group_members', 'delete_user_role', 'delete_user_role_assignments', 'set_kvstore_item', 'update_current_user', 'update_current_user_password', 'update_user', 'update_user_activity', 'update_user_attributes', 'update_user_group', 'update_user_password', 'update_user_role', 'update_user_role_attributes')
    add_policy = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='addPolicy', args=sgqlc.types.ArgDict((
        ('policy_params', sgqlc.types.Arg(sgqlc.types.non_null(SecurityPolicyArg), graphql_name='policyParams', default=None)),
))
    )
    add_user = sgqlc.types.Field(sgqlc.types.non_null('User'), graphql_name='addUser', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(AddUserInput), graphql_name='input', default=None)),
))
    )
    add_user_activity = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='addUserActivity', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(AddUserActivityInput), graphql_name='input', default=None)),
))
    )
    add_user_group = sgqlc.types.Field('UserGroup', graphql_name='addUserGroup', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(AddUserGroupInput), graphql_name='input', default=None)),
))
    )
    add_user_group_members = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='addUserGroupMembers', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(AddUserGroupMembersInput), graphql_name='input', default=None)),
))
    )
    add_user_role = sgqlc.types.Field('UserRole', graphql_name='addUserRole', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(AddUserRoleInput), graphql_name='input', default=None)),
))
    )
    add_user_role_assignments = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='addUserRoleAssignments', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(AddUserRoleAssignmentsInput), graphql_name='input', default=None)),
))
    )
    add_user_search_history = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='addUserSearchHistory', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(AddUserSearchHistoryInput), graphql_name='input', default=None)),
))
    )
    delete_kvstore_item = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='deleteKVStoreItem', args=sgqlc.types.ArgDict((
        ('key', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='key', default=None)),
))
    )
    delete_policy = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='deletePolicy', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    delete_user = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='deleteUser', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    delete_user_group = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='deleteUserGroup', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    delete_user_group_members = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='deleteUserGroupMembers', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(DeleteUserGroupMembersInput), graphql_name='input', default=None)),
))
    )
    delete_user_role = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='deleteUserRole', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    delete_user_role_assignments = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='deleteUserRoleAssignments', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(DeleteUserRoleAssignmentsInput), graphql_name='input', default=None)),
))
    )
    set_kvstore_item = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='setKVStoreItem', args=sgqlc.types.ArgDict((
        ('key', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='key', default=None)),
        ('value', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='value', default=None)),
))
    )
    update_current_user = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='updateCurrentUser', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(UpdateCurrentUserInput), graphql_name='input', default=None)),
))
    )
    update_current_user_password = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='updateCurrentUserPassword', args=sgqlc.types.ArgDict((
        ('old_password', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='oldPassword', default=None)),
        ('password', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='password', default=None)),
))
    )
    update_user = sgqlc.types.Field(sgqlc.types.non_null('User'), graphql_name='updateUser', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(UpdateUserInput), graphql_name='input', default=None)),
))
    )
    update_user_activity = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='updateUserActivity', args=sgqlc.types.ArgDict((
        ('ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='ids', default=None)),
        ('is_enabled', sgqlc.types.Arg(sgqlc.types.non_null(Boolean), graphql_name='isEnabled', default=None)),
))
    )
    update_user_attributes = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='updateUserAttributes', args=sgqlc.types.ArgDict((
        ('attributes', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(UserAttributeInput))), graphql_name='attributes', default=None)),
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    update_user_group = sgqlc.types.Field(sgqlc.types.non_null('UserGroup'), graphql_name='updateUserGroup', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(UpdateUserGroupInput), graphql_name='input', default=None)),
))
    )
    update_user_password = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='updateUserPassword', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
        ('password', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='password', default=None)),
))
    )
    update_user_role = sgqlc.types.Field(sgqlc.types.non_null('UserRole'), graphql_name='updateUserRole', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(UpdateUserRoleInput), graphql_name='input', default=None)),
))
    )
    update_user_role_attributes = sgqlc.types.Field(sgqlc.types.non_null('UserRole'), graphql_name='updateUserRoleAttributes', args=sgqlc.types.ArgDict((
        ('attributes', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(UserAttributeInput))), graphql_name='attributes', default=None)),
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )


class ParamsSchema(sgqlc.types.Type):
    __schema__ = auth_api_schema
    __field_names__ = ('schema', 'ui_schema')
    schema = sgqlc.types.Field(sgqlc.types.non_null(JSON), graphql_name='schema')
    ui_schema = sgqlc.types.Field(JSON, graphql_name='uiSchema')


class PolicyParameterGQL(sgqlc.types.Type):
    __schema__ = auth_api_schema
    __field_names__ = ('param', 'parameter_type')
    param = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='param')
    parameter_type = sgqlc.types.Field(sgqlc.types.non_null(AttributeType), graphql_name='parameterType')


class Query(sgqlc.types.Type):
    __schema__ = auth_api_schema
    __field_names__ = ('current_user', 'get_kvstore_item', 'list_policy', 'pagination_attribute', 'pagination_user', 'pagination_user_activity', 'pagination_user_group', 'pagination_user_role', 'pagination_user_search_history', 'refresh_token', 'token_exchange', 'user', 'user_by_internal_id', 'user_by_login', 'user_group', 'user_group_by_internal_id', 'user_idlist', 'user_idlist_sys', 'user_role', 'user_role_by_internal_id', 'user_sys')
    current_user = sgqlc.types.Field(sgqlc.types.non_null('User'), graphql_name='currentUser')
    get_kvstore_item = sgqlc.types.Field(String, graphql_name='getKVStoreItem', args=sgqlc.types.ArgDict((
        ('key', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='key', default=None)),
))
    )
    list_policy = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('SecurityPolicyGQL'))), graphql_name='listPolicy', args=sgqlc.types.ArgDict((
        ('ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='ids', default=None)),
))
    )
    pagination_attribute = sgqlc.types.Field(sgqlc.types.non_null(AttributePagination), graphql_name='paginationAttribute', args=sgqlc.types.ArgDict((
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(AttributeFilterSettings), graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
))
    )
    pagination_user = sgqlc.types.Field(sgqlc.types.non_null('UserPagination'), graphql_name='paginationUser', args=sgqlc.types.ArgDict((
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(UserFilterSettings), graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
))
    )
    pagination_user_activity = sgqlc.types.Field(sgqlc.types.non_null('UserActivityPagination'), graphql_name='paginationUserActivity', args=sgqlc.types.ArgDict((
        ('direction', sgqlc.types.Arg(SortDirection, graphql_name='direction', default='descending')),
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(UserActivityFilterSettings), graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('sort_field', sgqlc.types.Arg(UserActivitySorting, graphql_name='sortField', default='createdAt')),
))
    )
    pagination_user_group = sgqlc.types.Field(sgqlc.types.non_null('UserGroupPagination'), graphql_name='paginationUserGroup', args=sgqlc.types.ArgDict((
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(UserGroupFilterSettings), graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
))
    )
    pagination_user_role = sgqlc.types.Field(sgqlc.types.non_null('UserRolePagination'), graphql_name='paginationUserRole', args=sgqlc.types.ArgDict((
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(UserRoleFilterSettings), graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
))
    )
    pagination_user_search_history = sgqlc.types.Field(sgqlc.types.non_null('UserSearchHistoryPagination'), graphql_name='paginationUserSearchHistory', args=sgqlc.types.ArgDict((
        ('direction', sgqlc.types.Arg(SortDirection, graphql_name='direction', default='descending')),
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(UserSearchHistoryFilterSettings), graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('sort_field', sgqlc.types.Arg(UserSearchHistorySorting, graphql_name='sortField', default='createdAt')),
))
    )
    refresh_token = sgqlc.types.Field(sgqlc.types.non_null('Token'), graphql_name='refreshToken', args=sgqlc.types.ArgDict((
        ('refresh_token', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='refreshToken', default=None)),
))
    )
    token_exchange = sgqlc.types.Field(sgqlc.types.non_null('Token'), graphql_name='tokenExchange', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    user = sgqlc.types.Field(sgqlc.types.non_null('User'), graphql_name='user', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    user_by_internal_id = sgqlc.types.Field(sgqlc.types.non_null('User'), graphql_name='userByInternalId', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    user_by_login = sgqlc.types.Field(sgqlc.types.non_null('User'), graphql_name='userByLogin', args=sgqlc.types.ArgDict((
        ('password', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='password', default=None)),
        ('username', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='username', default=None)),
))
    )
    user_group = sgqlc.types.Field(sgqlc.types.non_null('UserGroup'), graphql_name='userGroup', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    user_group_by_internal_id = sgqlc.types.Field(sgqlc.types.non_null('UserGroup'), graphql_name='userGroupByInternalId', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    user_idlist = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of('User')), graphql_name='userIDList', args=sgqlc.types.ArgDict((
        ('ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='ids', default=None)),
))
    )
    user_idlist_sys = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('User'))), graphql_name='userIDListSys', args=sgqlc.types.ArgDict((
        ('ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='ids', default=None)),
))
    )
    user_role = sgqlc.types.Field(sgqlc.types.non_null('UserRole'), graphql_name='userRole', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    user_role_by_internal_id = sgqlc.types.Field(sgqlc.types.non_null('UserRole'), graphql_name='userRoleByInternalId', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    user_sys = sgqlc.types.Field(sgqlc.types.non_null('User'), graphql_name='userSys', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )


class SecurityPolicyGQL(sgqlc.types.Type):
    __schema__ = auth_api_schema
    __field_names__ = ('id', 'index', 'name', 'params', 'policy_type', 'rule', 'target')
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')
    index = sgqlc.types.Field(PolicyIndex, graphql_name='index')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    params = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(PolicyParameterGQL))), graphql_name='params')
    policy_type = sgqlc.types.Field(sgqlc.types.non_null(PolicyType), graphql_name='policyType')
    rule = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='rule')
    target = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='target')


class State(sgqlc.types.Type):
    __schema__ = auth_api_schema
    __field_names__ = ('is_success',)
    is_success = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isSuccess')


class StringListValue(sgqlc.types.Type):
    __schema__ = auth_api_schema
    __field_names__ = ('value',)
    value = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))), graphql_name='value')


class StringValue(sgqlc.types.Type):
    __schema__ = auth_api_schema
    __field_names__ = ('value',)
    value = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='value')


class Token(sgqlc.types.Type):
    __schema__ = auth_api_schema
    __field_names__ = ('access_token', 'access_token_expires_at', 'refresh_token', 'refresh_token_expires_at')
    access_token = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='accessToken')
    access_token_expires_at = sgqlc.types.Field(sgqlc.types.non_null(Long), graphql_name='accessTokenExpiresAt')
    refresh_token = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='refreshToken')
    refresh_token_expires_at = sgqlc.types.Field(sgqlc.types.non_null(Long), graphql_name='refreshTokenExpiresAt')


class UserActivity(sgqlc.types.Type):
    __schema__ = auth_api_schema
    __field_names__ = ('entity', 'id', 'metadata', 'system_registration_date', 'user_action')
    entity = sgqlc.types.Field(sgqlc.types.non_null('UserActivityEntity'), graphql_name='entity')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    metadata = sgqlc.types.Field(String, graphql_name='metadata')
    system_registration_date = sgqlc.types.Field(sgqlc.types.non_null(UnixTime), graphql_name='systemRegistrationDate')
    user_action = sgqlc.types.Field(sgqlc.types.non_null(UserActivityAction), graphql_name='userAction')


class UserActivityPagination(sgqlc.types.Type):
    __schema__ = auth_api_schema
    __field_names__ = ('list_user_activity', 'total')
    list_user_activity = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(UserActivity))), graphql_name='listUserActivity')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class UserAttribute(sgqlc.types.Type):
    __schema__ = auth_api_schema
    __field_names__ = ('attribute_source', 'description', 'id', 'json_value', 'name', 'value')
    attribute_source = sgqlc.types.Field(sgqlc.types.non_null(AttributeSource), graphql_name='attributeSource')
    description = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='description')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    json_value = sgqlc.types.Field(sgqlc.types.non_null(JSON), graphql_name='jsonValue')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    value = sgqlc.types.Field(sgqlc.types.non_null('AttributeValue'), graphql_name='value')


class UserGroupMetrics(sgqlc.types.Type):
    __schema__ = auth_api_schema
    __field_names__ = ('count_user',)
    count_user = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='countUser')


class UserGroupPagination(sgqlc.types.Type):
    __schema__ = auth_api_schema
    __field_names__ = ('list_user_group', 'total')
    list_user_group = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('UserGroup'))), graphql_name='listUserGroup')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class UserMetrics(sgqlc.types.Type):
    __schema__ = auth_api_schema
    __field_names__ = ('count_group', 'count_role')
    count_group = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='countGroup')
    count_role = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='countRole')


class UserPagination(sgqlc.types.Type):
    __schema__ = auth_api_schema
    __field_names__ = ('list_user', 'total')
    list_user = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('User'))), graphql_name='listUser')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class UserRoleMetrics(sgqlc.types.Type):
    __schema__ = auth_api_schema
    __field_names__ = ('count_user',)
    count_user = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='countUser')


class UserRolePagination(sgqlc.types.Type):
    __schema__ = auth_api_schema
    __field_names__ = ('list_user_role', 'total')
    list_user_role = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('UserRole'))), graphql_name='listUserRole')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class UserSearchHistory(sgqlc.types.Type):
    __schema__ = auth_api_schema
    __field_names__ = ('id', 'search_string', 'search_type', 'system_registration_date')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    search_string = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='searchString')
    search_type = sgqlc.types.Field(sgqlc.types.non_null(UserActivitySearchType), graphql_name='searchType')
    system_registration_date = sgqlc.types.Field(sgqlc.types.non_null(UnixTime), graphql_name='systemRegistrationDate')


class UserSearchHistoryPagination(sgqlc.types.Type):
    __schema__ = auth_api_schema
    __field_names__ = ('list_user_search_history', 'total')
    list_user_search_history = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(UserSearchHistory))), graphql_name='listUserSearchHistory')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class User(sgqlc.types.Type, RecordInterface):
    __schema__ = auth_api_schema
    __field_names__ = ('access_level', 'allowed_functions', 'attributes', 'created_at', 'email', 'enabled', 'fathers_name', 'first_name', 'id', 'is_admin', 'last_name', 'list_user_group', 'list_user_role', 'login', 'metrics', 'name', 'receive_notifications', 'receive_telegram_notifications', 'telegram_chat_id', 'updated_at')
    access_level = sgqlc.types.Field(sgqlc.types.non_null(AccessLevel), graphql_name='accessLevel')
    allowed_functions = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(AllowedFunctionsEnum))), graphql_name='allowedFunctions')
    attributes = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(UserAttribute))), graphql_name='attributes')
    created_at = sgqlc.types.Field(sgqlc.types.non_null(UnixTime), graphql_name='createdAt')
    email = sgqlc.types.Field(String, graphql_name='email')
    enabled = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='enabled')
    fathers_name = sgqlc.types.Field(String, graphql_name='fathersName')
    first_name = sgqlc.types.Field(String, graphql_name='firstName')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    is_admin = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isAdmin')
    last_name = sgqlc.types.Field(String, graphql_name='lastName')
    list_user_group = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('UserGroup'))), graphql_name='listUserGroup')
    list_user_role = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('UserRole'))), graphql_name='listUserRole')
    login = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='login')
    metrics = sgqlc.types.Field(sgqlc.types.non_null(UserMetrics), graphql_name='metrics')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    receive_notifications = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='receiveNotifications')
    receive_telegram_notifications = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='receiveTelegramNotifications')
    telegram_chat_id = sgqlc.types.Field(Long, graphql_name='telegramChatId')
    updated_at = sgqlc.types.Field(UnixTime, graphql_name='updatedAt')


class UserGroup(sgqlc.types.Type, RecordInterface):
    __schema__ = auth_api_schema
    __field_names__ = ('created_at', 'description', 'id', 'list_user', 'metrics', 'name', 'updated_at')
    created_at = sgqlc.types.Field(sgqlc.types.non_null(UnixTime), graphql_name='createdAt')
    description = sgqlc.types.Field(String, graphql_name='description')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    list_user = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(User))), graphql_name='listUser')
    metrics = sgqlc.types.Field(sgqlc.types.non_null(UserGroupMetrics), graphql_name='metrics')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    updated_at = sgqlc.types.Field(UnixTime, graphql_name='updatedAt')


class UserRole(sgqlc.types.Type, RecordInterface):
    __schema__ = auth_api_schema
    __field_names__ = ('attributes', 'created_at', 'description', 'id', 'metrics', 'name', 'updated_at')
    attributes = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(UserAttribute))), graphql_name='attributes')
    created_at = sgqlc.types.Field(sgqlc.types.non_null(UnixTime), graphql_name='createdAt')
    description = sgqlc.types.Field(String, graphql_name='description')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    metrics = sgqlc.types.Field(sgqlc.types.non_null(UserRoleMetrics), graphql_name='metrics')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    updated_at = sgqlc.types.Field(UnixTime, graphql_name='updatedAt')



########################################################################
# Unions
########################################################################
class AttributeValue(sgqlc.types.Union):
    __schema__ = auth_api_schema
    __types__ = (BooleanListValue, BooleanValue, DoubleListValue, DoubleValue, IntListValue, IntValue, StringListValue, StringValue)


class UserActivityEntity(sgqlc.types.Union):
    __schema__ = auth_api_schema
    __types__ = (Concept, ConceptLink, Document)



########################################################################
# Schema Entry Points
########################################################################
auth_api_schema.query_type = Query
auth_api_schema.mutation_type = Mutation
auth_api_schema.subscription_type = None

