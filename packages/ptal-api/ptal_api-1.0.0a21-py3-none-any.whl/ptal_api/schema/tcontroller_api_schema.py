import sgqlc.types


tcontroller_api_schema = sgqlc.types.Schema()



########################################################################
# Scalars and Enumerations
########################################################################
class BatchReprocessGetMessageIdTaskStatus(sgqlc.types.Enum):
    __schema__ = tcontroller_api_schema
    __choices__ = ('active', 'failed', 'pending')


class BatchReprocessGetMessageIdTaskStatusFilter(sgqlc.types.Enum):
    __schema__ = tcontroller_api_schema
    __choices__ = ('activeOrPending', 'failed')


Boolean = sgqlc.types.Boolean

class ConceptDedupMethodSort(sgqlc.types.Enum):
    __schema__ = tcontroller_api_schema
    __choices__ = ('id', 'lastTaskTime', 'title')


class ConceptDedupTaskSort(sgqlc.types.Enum):
    __schema__ = tcontroller_api_schema
    __choices__ = ('createTime', 'method', 'state')


class ConceptDedupTaskState(sgqlc.types.Enum):
    __schema__ = tcontroller_api_schema
    __choices__ = ('cancelled', 'failed', 'ok', 'pending')


class ConceptTransformConfigSort(sgqlc.types.Enum):
    __schema__ = tcontroller_api_schema
    __choices__ = ('description', 'id', 'systemRegistrationDate', 'systemUpdateDate')


class ConceptTransformTaskSort(sgqlc.types.Enum):
    __schema__ = tcontroller_api_schema
    __choices__ = ('config', 'createTime', 'state')


class ConceptTransformTaskState(sgqlc.types.Enum):
    __schema__ = tcontroller_api_schema
    __choices__ = ('failed', 'ok', 'pending')


class EventLevel(sgqlc.types.Enum):
    __schema__ = tcontroller_api_schema
    __choices__ = ('error', 'info', 'success', 'warning')


class EventTarget(sgqlc.types.Enum):
    __schema__ = tcontroller_api_schema
    __choices__ = ('analyticsApi', 'api', 'authApi', 'crawlersApi', 'notificationApi', 'talismanConnector', 'talismanTranslator', 'tcontroller', 'tsearch')


class ExportEntityType(sgqlc.types.Enum):
    __schema__ = tcontroller_api_schema
    __choices__ = ('concept', 'document')


class ExportTaskSort(sgqlc.types.Enum):
    __schema__ = tcontroller_api_schema
    __choices__ = ('createTime', 'exporter', 'state')


class ExportTaskState(sgqlc.types.Enum):
    __schema__ = tcontroller_api_schema
    __choices__ = ('cancelled', 'failed', 'ok', 'pending')


class ExporterSort(sgqlc.types.Enum):
    __schema__ = tcontroller_api_schema
    __choices__ = ('id', 'lastTaskTime', 'menuTitle', 'title')


Float = sgqlc.types.Float

ID = sgqlc.types.ID

Int = sgqlc.types.Int

class ItemState(sgqlc.types.Enum):
    __schema__ = tcontroller_api_schema
    __choices__ = ('duplicate', 'failed', 'ok', 'pending')


class ItemsSort(sgqlc.types.Enum):
    __schema__ = tcontroller_api_schema
    __choices__ = ('priority', 'timestamp', 'topic')


class JSON(sgqlc.types.Scalar):
    __schema__ = tcontroller_api_schema


class KafkaTopicSort(sgqlc.types.Enum):
    __schema__ = tcontroller_api_schema
    __choices__ = ('activeMessages', 'configDescription', 'configId', 'description', 'duplicateMessages', 'failedMessages', 'okMessages', 'pendingMessages', 'pipelineIsActive', 'priority', 'stopped', 'systemRegistrationDate', 'systemUpdateDate', 'topic')


class Long(sgqlc.types.Scalar):
    __schema__ = tcontroller_api_schema


class MessagePriority(sgqlc.types.Enum):
    __schema__ = tcontroller_api_schema
    __choices__ = ('Background', 'High', 'Normal', 'VeryHigh')


class MessageSort(sgqlc.types.Enum):
    __schema__ = tcontroller_api_schema
    __choices__ = ('priority', 'timestamp')


class OtherMessageIdType(sgqlc.types.Enum):
    __schema__ = tcontroller_api_schema
    __choices__ = ('crawlerId', 'jobId', 'periodicJobId', 'periodicTaskId', 'projectId', 'reprocessDocument', 'reprocessDocumentPrepare', 'taskId')


class PipelineConfigSort(sgqlc.types.Enum):
    __schema__ = tcontroller_api_schema
    __choices__ = ('description', 'id', 'systemRegistrationDate', 'systemUpdateDate')


class SortDirection(sgqlc.types.Enum):
    __schema__ = tcontroller_api_schema
    __choices__ = ('ascending', 'descending')


String = sgqlc.types.String

class UnixTime(sgqlc.types.Scalar):
    __schema__ = tcontroller_api_schema


class UserPipelineTransformSort(sgqlc.types.Enum):
    __schema__ = tcontroller_api_schema
    __choices__ = ('description', 'id', 'state', 'systemRegistrationDate', 'systemUpdateDate')


class UserServiceState(sgqlc.types.Enum):
    __schema__ = tcontroller_api_schema
    __choices__ = ('buildFailed', 'imageNotReady', 'noImage', 'ready')



########################################################################
# Input Objects
########################################################################
class BatchReprocessGetMessageIdTaskFilter(sgqlc.types.Input):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('created_interval', 'id', 'parent_or_self_id', 'status_filter')
    created_interval = sgqlc.types.Field('TimestampInterval', graphql_name='createdInterval')
    id = sgqlc.types.Field(String, graphql_name='id')
    parent_or_self_id = sgqlc.types.Field(String, graphql_name='parentOrSelfId')
    status_filter = sgqlc.types.Field(BatchReprocessGetMessageIdTaskStatusFilter, graphql_name='statusFilter')


class ConceptDedupMethodFilter(sgqlc.types.Input):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('creator_id', 'last_updater_id', 'title')
    creator_id = sgqlc.types.Field(ID, graphql_name='creatorId')
    last_updater_id = sgqlc.types.Field(ID, graphql_name='lastUpdaterId')
    title = sgqlc.types.Field(String, graphql_name='title')


class ConceptDedupMethodInput(sgqlc.types.Input):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('description', 'title')
    description = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='description')
    title = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='title')


class ConceptDedupTaskFilter(sgqlc.types.Input):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('creator_id', 'id', 'method', 'state', 'system_registration_date')
    creator_id = sgqlc.types.Field(ID, graphql_name='creatorId')
    id = sgqlc.types.Field(ID, graphql_name='id')
    method = sgqlc.types.Field(ID, graphql_name='method')
    state = sgqlc.types.Field(ConceptDedupTaskState, graphql_name='state')
    system_registration_date = sgqlc.types.Field('TimestampInterval', graphql_name='systemRegistrationDate')


class ConceptDedupTaskInput(sgqlc.types.Input):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('concept_ids', 'params', 'tql_query')
    concept_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='conceptIds')
    params = sgqlc.types.Field(sgqlc.types.non_null(JSON), graphql_name='params')
    tql_query = sgqlc.types.Field(String, graphql_name='tqlQuery')


class ConceptTransformConfigFilter(sgqlc.types.Input):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('can_be_used', 'can_transform_concept_type_ids', 'can_transform_multiple_entities', 'can_transform_one_entity', 'creator_id', 'description', 'last_updater_id', 'system_registration_date', 'system_update_date', 'title')
    can_be_used = sgqlc.types.Field(Boolean, graphql_name='canBeUsed')
    can_transform_concept_type_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='canTransformConceptTypeIds')
    can_transform_multiple_entities = sgqlc.types.Field(Boolean, graphql_name='canTransformMultipleEntities')
    can_transform_one_entity = sgqlc.types.Field(Boolean, graphql_name='canTransformOneEntity')
    creator_id = sgqlc.types.Field(ID, graphql_name='creatorId')
    description = sgqlc.types.Field(String, graphql_name='description')
    last_updater_id = sgqlc.types.Field(ID, graphql_name='lastUpdaterId')
    system_registration_date = sgqlc.types.Field('TimestampInterval', graphql_name='systemRegistrationDate')
    system_update_date = sgqlc.types.Field('TimestampInterval', graphql_name='systemUpdateDate')
    title = sgqlc.types.Field(String, graphql_name='title')


class ConceptTransformConfigInput(sgqlc.types.Input):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('can_transform_multiple_entities', 'can_transform_one_entity', 'concept_type_ids', 'description', 'priority', 'title')
    can_transform_multiple_entities = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='canTransformMultipleEntities')
    can_transform_one_entity = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='canTransformOneEntity')
    concept_type_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='conceptTypeIds')
    description = sgqlc.types.Field(String, graphql_name='description')
    priority = sgqlc.types.Field(Int, graphql_name='priority')
    title = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='title')


class ConceptTransformTaskFilter(sgqlc.types.Input):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('config', 'creator_id', 'id', 'state', 'system_registration_date')
    config = sgqlc.types.Field(ID, graphql_name='config')
    creator_id = sgqlc.types.Field(ID, graphql_name='creatorId')
    id = sgqlc.types.Field(ID, graphql_name='id')
    state = sgqlc.types.Field(ConceptTransformTaskState, graphql_name='state')
    system_registration_date = sgqlc.types.Field('TimestampInterval', graphql_name='systemRegistrationDate')


class ConceptTransformTaskInput(sgqlc.types.Input):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('concept_ids', 'config')
    concept_ids = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='conceptIds')
    config = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='config')


class ExportEntityInput(sgqlc.types.Input):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('id', 'type')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    type = sgqlc.types.Field(sgqlc.types.non_null(ExportEntityType), graphql_name='type')


class ExportTaskFilter(sgqlc.types.Input):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('creator_id', 'exporter', 'id', 'state', 'system_registration_date')
    creator_id = sgqlc.types.Field(ID, graphql_name='creatorId')
    exporter = sgqlc.types.Field(ID, graphql_name='exporter')
    id = sgqlc.types.Field(ID, graphql_name='id')
    state = sgqlc.types.Field(ExportTaskState, graphql_name='state')
    system_registration_date = sgqlc.types.Field('TimestampInterval', graphql_name='systemRegistrationDate')


class ExportTaskInput(sgqlc.types.Input):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('entities', 'params')
    entities = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ExportEntityInput))), graphql_name='entities')
    params = sgqlc.types.Field(sgqlc.types.non_null(JSON), graphql_name='params')


class ExporterFilter(sgqlc.types.Input):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('can_export_concept', 'can_export_concept_type_ids', 'can_export_document', 'can_export_multiple_entities', 'can_export_one_entity', 'creator_id', 'last_updater_id', 'menu_title', 'show_in_menu', 'title')
    can_export_concept = sgqlc.types.Field(Boolean, graphql_name='canExportConcept')
    can_export_concept_type_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='canExportConceptTypeIds')
    can_export_document = sgqlc.types.Field(Boolean, graphql_name='canExportDocument')
    can_export_multiple_entities = sgqlc.types.Field(Boolean, graphql_name='canExportMultipleEntities')
    can_export_one_entity = sgqlc.types.Field(Boolean, graphql_name='canExportOneEntity')
    creator_id = sgqlc.types.Field(ID, graphql_name='creatorId')
    last_updater_id = sgqlc.types.Field(ID, graphql_name='lastUpdaterId')
    menu_title = sgqlc.types.Field(String, graphql_name='menuTitle')
    show_in_menu = sgqlc.types.Field(Boolean, graphql_name='showInMenu')
    title = sgqlc.types.Field(String, graphql_name='title')


class ExporterInput(sgqlc.types.Input):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('can_export_multiple_entities', 'can_export_one_entity', 'concept_type_ids', 'default_params', 'description', 'menu_title')
    can_export_multiple_entities = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='canExportMultipleEntities')
    can_export_one_entity = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='canExportOneEntity')
    concept_type_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='conceptTypeIds')
    default_params = sgqlc.types.Field(JSON, graphql_name='defaultParams')
    description = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='description')
    menu_title = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='menuTitle')


class ExporterUserSettingsInput(sgqlc.types.Input):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('show_in_menu',)
    show_in_menu = sgqlc.types.Field(Boolean, graphql_name='showInMenu')


class ItemsFilter(sgqlc.types.Input):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('input_text', 'interval', 'parent_or_self_id', 'state', 'topic')
    input_text = sgqlc.types.Field(String, graphql_name='inputText')
    interval = sgqlc.types.Field('TimestampInterval', graphql_name='interval')
    parent_or_self_id = sgqlc.types.Field(String, graphql_name='parentOrSelfId')
    state = sgqlc.types.Field(ItemState, graphql_name='state')
    topic = sgqlc.types.Field(String, graphql_name='topic')


class JobIdFilter(sgqlc.types.Input):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('crawler_id', 'job_id', 'periodic_job_id', 'periodic_task_id', 'project_id', 'task_id')
    crawler_id = sgqlc.types.Field(ID, graphql_name='crawlerId')
    job_id = sgqlc.types.Field(ID, graphql_name='jobId')
    periodic_job_id = sgqlc.types.Field(ID, graphql_name='periodicJobId')
    periodic_task_id = sgqlc.types.Field(ID, graphql_name='periodicTaskId')
    project_id = sgqlc.types.Field(ID, graphql_name='projectId')
    task_id = sgqlc.types.Field(ID, graphql_name='taskId')


class KafkaTopicFilter(sgqlc.types.Input):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('can_transform_concepts', 'can_transform_documents', 'creator_id', 'description', 'has_pipeline_config', 'last_updater_id', 'name', 'name_only', 'pipeline_config', 'pipeline_config_description', 'pipeline_is_active', 'start_type', 'stopped', 'system_registration_date', 'system_update_date')
    can_transform_concepts = sgqlc.types.Field(Boolean, graphql_name='canTransformConcepts')
    can_transform_documents = sgqlc.types.Field(Boolean, graphql_name='canTransformDocuments')
    creator_id = sgqlc.types.Field(ID, graphql_name='creatorId')
    description = sgqlc.types.Field(String, graphql_name='description')
    has_pipeline_config = sgqlc.types.Field(Boolean, graphql_name='hasPipelineConfig')
    last_updater_id = sgqlc.types.Field(ID, graphql_name='lastUpdaterId')
    name = sgqlc.types.Field(String, graphql_name='name')
    name_only = sgqlc.types.Field(String, graphql_name='nameOnly')
    pipeline_config = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='pipelineConfig')
    pipeline_config_description = sgqlc.types.Field(String, graphql_name='pipelineConfigDescription')
    pipeline_is_active = sgqlc.types.Field(Boolean, graphql_name='pipelineIsActive')
    start_type = sgqlc.types.Field(String, graphql_name='startType')
    stopped = sgqlc.types.Field(Boolean, graphql_name='stopped')
    system_registration_date = sgqlc.types.Field('TimestampInterval', graphql_name='systemRegistrationDate')
    system_update_date = sgqlc.types.Field('TimestampInterval', graphql_name='systemUpdateDate')


class KafkaTopicUpdate(sgqlc.types.Input):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('clear_description', 'clear_move_to_on_timeout', 'clear_pipeline', 'clear_request_timeout_ms', 'description', 'move_to_on_timeout', 'pipeline', 'priority', 'request_timeout_ms', 'stopped')
    clear_description = sgqlc.types.Field(Boolean, graphql_name='clearDescription')
    clear_move_to_on_timeout = sgqlc.types.Field(Boolean, graphql_name='clearMoveToOnTimeout')
    clear_pipeline = sgqlc.types.Field(Boolean, graphql_name='clearPipeline')
    clear_request_timeout_ms = sgqlc.types.Field(Boolean, graphql_name='clearRequestTimeoutMs')
    description = sgqlc.types.Field(String, graphql_name='description')
    move_to_on_timeout = sgqlc.types.Field(String, graphql_name='moveToOnTimeout')
    pipeline = sgqlc.types.Field('PipelineSetupInput', graphql_name='pipeline')
    priority = sgqlc.types.Field(Int, graphql_name='priority')
    request_timeout_ms = sgqlc.types.Field(Int, graphql_name='requestTimeoutMs')
    stopped = sgqlc.types.Field(Boolean, graphql_name='stopped')


class MessageFilter(sgqlc.types.Input):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('batch_reprocess_id', 'created_interval', 'creator_id', 'id', 'input_text', 'job_id_filter', 'parent_id', 'parent_or_self_id', 'pipeline_topic_is_active')
    batch_reprocess_id = sgqlc.types.Field(ID, graphql_name='batchReprocessId')
    created_interval = sgqlc.types.Field('TimestampInterval', graphql_name='createdInterval')
    creator_id = sgqlc.types.Field(ID, graphql_name='creatorId')
    id = sgqlc.types.Field(String, graphql_name='id')
    input_text = sgqlc.types.Field(String, graphql_name='inputText')
    job_id_filter = sgqlc.types.Field(JobIdFilter, graphql_name='jobIdFilter')
    parent_id = sgqlc.types.Field(String, graphql_name='parentId')
    parent_or_self_id = sgqlc.types.Field(String, graphql_name='parentOrSelfId')
    pipeline_topic_is_active = sgqlc.types.Field(Boolean, graphql_name='pipelineTopicIsActive')


class PipelineConfigFilter(sgqlc.types.Input):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('creator_id', 'description', 'has_errors', 'has_transform', 'has_transforms', 'in_type', 'last_updater_id', 'system_registration_date', 'system_update_date')
    creator_id = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='creatorId')
    description = sgqlc.types.Field(String, graphql_name='description')
    has_errors = sgqlc.types.Field(Boolean, graphql_name='hasErrors')
    has_transform = sgqlc.types.Field(ID, graphql_name='hasTransform')
    has_transforms = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='hasTransforms')
    in_type = sgqlc.types.Field(String, graphql_name='inType')
    last_updater_id = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='lastUpdaterId')
    system_registration_date = sgqlc.types.Field('TimestampInterval', graphql_name='systemRegistrationDate')
    system_update_date = sgqlc.types.Field('TimestampInterval', graphql_name='systemUpdateDate')


class PipelineConfigInput(sgqlc.types.Input):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('description', 'settings', 'transforms')
    description = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='description')
    settings = sgqlc.types.Field('PipelineConfigSettingsInput', graphql_name='settings')
    transforms = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('PipelineTransformSetupInput'))), graphql_name='transforms')


class PipelineConfigSettingsInput(sgqlc.types.Input):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('disable_preload',)
    disable_preload = sgqlc.types.Field(Boolean, graphql_name='disablePreload')


class PipelineSetupInput(sgqlc.types.Input):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('pipeline_config',)
    pipeline_config = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='pipelineConfig')


class PipelineTransformFilter(sgqlc.types.Input):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('in_type',)
    in_type = sgqlc.types.Field(String, graphql_name='inType')


class PipelineTransformSetupInput(sgqlc.types.Input):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('id', 'params')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    params = sgqlc.types.Field(sgqlc.types.non_null(JSON), graphql_name='params')


class S3FileInput(sgqlc.types.Input):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('bucket_name', 'object_name')
    bucket_name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='bucketName')
    object_name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='objectName')


class TimestampInterval(sgqlc.types.Input):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('end', 'start')
    end = sgqlc.types.Field(UnixTime, graphql_name='end')
    start = sgqlc.types.Field(UnixTime, graphql_name='start')


class UserPipelineTransformFilter(sgqlc.types.Input):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('creation_date', 'creator', 'description_or_in_type', 'in_type', 'last_updater', 'update_date')
    creation_date = sgqlc.types.Field(TimestampInterval, graphql_name='creationDate')
    creator = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='creator')
    description_or_in_type = sgqlc.types.Field(String, graphql_name='descriptionOrInType')
    in_type = sgqlc.types.Field(String, graphql_name='inType')
    last_updater = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='lastUpdater')
    update_date = sgqlc.types.Field(TimestampInterval, graphql_name='updateDate')


class UserServiceEnvironmentVariableInput(sgqlc.types.Input):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('name', 'value')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    value = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='value')


class UserServiceInput(sgqlc.types.Input):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('cpu_limit', 'cpu_request', 'environment', 'max_pods', 'mem_limit', 'mem_request', 'min_pods')
    cpu_limit = sgqlc.types.Field(Int, graphql_name='cpuLimit')
    cpu_request = sgqlc.types.Field(Int, graphql_name='cpuRequest')
    environment = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(UserServiceEnvironmentVariableInput)), graphql_name='environment')
    max_pods = sgqlc.types.Field(Int, graphql_name='maxPods')
    mem_limit = sgqlc.types.Field(Int, graphql_name='memLimit')
    mem_request = sgqlc.types.Field(Int, graphql_name='memRequest')
    min_pods = sgqlc.types.Field(Int, graphql_name='minPods')



########################################################################
# Output Objects and Interfaces
########################################################################
class RecordInterface(sgqlc.types.Interface):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('creator', 'last_updater', 'system_registration_date', 'system_update_date')
    creator = sgqlc.types.Field(sgqlc.types.non_null('User'), graphql_name='creator')
    last_updater = sgqlc.types.Field('User', graphql_name='lastUpdater')
    system_registration_date = sgqlc.types.Field(sgqlc.types.non_null(UnixTime), graphql_name='systemRegistrationDate')
    system_update_date = sgqlc.types.Field(UnixTime, graphql_name='systemUpdateDate')


class ActiveMessageList(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('messages', 'total')
    messages = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ActiveMessageStatus'))), graphql_name='messages')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class ActiveMessageStatus(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('id', 'info')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    info = sgqlc.types.Field(sgqlc.types.non_null('MessageInProgress'), graphql_name='info')


class AddTransformTasksResult(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('added', 'duplicate', 'failed')
    added = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='added')
    duplicate = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='duplicate')
    failed = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='failed')


class BatchReprocessGetMessageIdTask(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('document_id', 'id', 'status')
    document_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='documentId')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    status = sgqlc.types.Field(sgqlc.types.non_null(BatchReprocessGetMessageIdTaskStatus), graphql_name='status')


class BatchReprocessGetMessageIdTaskList(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('tasks', 'total')
    tasks = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(BatchReprocessGetMessageIdTask))), graphql_name='tasks')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class BatchReprocessMetrics(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('active', 'failed', 'get_id_failed', 'get_id_pending', 'ok', 'pending')
    active = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='active')
    failed = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='failed')
    get_id_failed = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='getIdFailed')
    get_id_pending = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='getIdPending')
    ok = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='ok')
    pending = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='pending')


class CompletedOkMessageList(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('messages', 'total')
    messages = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('CompletedOkMessageStatus'))), graphql_name='messages')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class CompletedOkMessageStatus(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('id', 'info')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    info = sgqlc.types.Field(sgqlc.types.non_null('MessageOk'), graphql_name='info')


class ConceptDedupMethodList(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('methods', 'total')
    methods = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ConceptDedupMethod'))), graphql_name='methods')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class ConceptDedupTaskList(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('tasks', 'total')
    tasks = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ConceptDedupTask'))), graphql_name='tasks')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class ConceptDedupTaskResult(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('error', 'report')
    error = sgqlc.types.Field(String, graphql_name='error')
    report = sgqlc.types.Field('ConceptDuplicateReport', graphql_name='report')


class ConceptDuplicateReport(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('id',)
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')


class ConceptTransformConfigList(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('configs', 'total')
    configs = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ConceptTransformConfig'))), graphql_name='configs')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class ConceptTransformResults(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('concepts', 'error')
    concepts = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='concepts')
    error = sgqlc.types.Field(String, graphql_name='error')


class ConceptTransformTaskList(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('tasks', 'total')
    tasks = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ConceptTransformTask'))), graphql_name='tasks')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class DeleteMessagesResult(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('deleted', 'not_found', 'skipped_completed_ok')
    deleted = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='deleted')
    not_found = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='notFound')
    skipped_completed_ok = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='skippedCompletedOk')


class Document(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('id',)
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')


class DuplicateMessageList(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('messages', 'total')
    messages = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('DuplicateMessageStatus'))), graphql_name='messages')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class DuplicateMessageStatus(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('id', 'info')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    info = sgqlc.types.Field(sgqlc.types.non_null('MessageDuplicate'), graphql_name='info')


class Event(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('creation_time', 'id', 'is_read', 'level', 'message', 'params', 'target')
    creation_time = sgqlc.types.Field(sgqlc.types.non_null(UnixTime), graphql_name='creationTime')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    is_read = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isRead')
    level = sgqlc.types.Field(sgqlc.types.non_null(EventLevel), graphql_name='level')
    message = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='message')
    params = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('Parameter'))), graphql_name='params')
    target = sgqlc.types.Field(sgqlc.types.non_null(EventTarget), graphql_name='target')


class ExportEntity(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('id', 'type')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    type = sgqlc.types.Field(sgqlc.types.non_null(ExportEntityType), graphql_name='type')


class ExportResults(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('error', 'file', 'message')
    error = sgqlc.types.Field(String, graphql_name='error')
    file = sgqlc.types.Field(String, graphql_name='file')
    message = sgqlc.types.Field(String, graphql_name='message')


class ExportTaskList(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('tasks', 'total')
    tasks = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ExportTask'))), graphql_name='tasks')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class ExporterList(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('exporters', 'total')
    exporters = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('Exporter'))), graphql_name='exporters')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class FailedMessageList(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('messages', 'total')
    messages = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('MessageStatus'))), graphql_name='messages')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class Item(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('_url', '_uuid', 'attachments_num', 'id', 'item', 'job_id', 'status', 'timestamp')
    _url = sgqlc.types.Field(String, graphql_name='_url')
    _uuid = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='_uuid')
    attachments_num = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='attachmentsNum')
    id = sgqlc.types.Field(String, graphql_name='id')
    item = sgqlc.types.Field(sgqlc.types.non_null(JSON), graphql_name='item')
    job_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='job_id')
    status = sgqlc.types.Field(sgqlc.types.non_null('MessageStatus'), graphql_name='status')
    timestamp = sgqlc.types.Field(sgqlc.types.non_null(UnixTime), graphql_name='timestamp')


class ItemsList(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('items', 'total')
    items = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(Item))), graphql_name='items')
    total = sgqlc.types.Field(sgqlc.types.non_null(Long), graphql_name='total')


class JobIds(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('crawler_id', 'job_id', 'periodic_job_id', 'periodic_task_id', 'project_id', 'task_id')
    crawler_id = sgqlc.types.Field(ID, graphql_name='crawlerId')
    job_id = sgqlc.types.Field(ID, graphql_name='jobId')
    periodic_job_id = sgqlc.types.Field(ID, graphql_name='periodicJobId')
    periodic_task_id = sgqlc.types.Field(ID, graphql_name='periodicTaskId')
    project_id = sgqlc.types.Field(ID, graphql_name='projectId')
    task_id = sgqlc.types.Field(ID, graphql_name='taskId')


class JobMetrics(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('job_id', 'metrics')
    job_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='jobId')
    metrics = sgqlc.types.Field(sgqlc.types.non_null('MessageMetrics'), graphql_name='metrics')


class KafkaSubTopicMetrics(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('index', 'metrics')
    index = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='index')
    metrics = sgqlc.types.Field(sgqlc.types.non_null('KafkaTopicMetrics'), graphql_name='metrics')


class KafkaTopicList(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('topics', 'total')
    topics = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('KafkaTopic'))), graphql_name='topics')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class KafkaTopicMetrics(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('active_messages', 'cancelled', 'deleted', 'duplicate', 'failed', 'lag', 'messages', 'ok', 'ok_cumulative', 'pending', 'pipeline_is_active')
    active_messages = sgqlc.types.Field(sgqlc.types.non_null(Long), graphql_name='activeMessages')
    cancelled = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='cancelled')
    deleted = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='deleted')
    duplicate = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='duplicate')
    failed = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='failed')
    lag = sgqlc.types.Field(sgqlc.types.non_null(Long), graphql_name='lag')
    messages = sgqlc.types.Field(sgqlc.types.non_null(Long), graphql_name='messages')
    ok = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='ok')
    ok_cumulative = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='okCumulative')
    pending = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='pending')
    pipeline_is_active = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='pipelineIsActive')


class KibanaLink(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('name', 'url')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    url = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='url')


class MessageDuplicate(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('create_time', 'creator', 'deleted', 'finish_time', 'job_ids', 'message', 'original_id', 'pipeline_topic', 'priority', 'reprocessed', 'reprocessed_from_kb', 'result', 'start_time', 'topic')
    create_time = sgqlc.types.Field(sgqlc.types.non_null(UnixTime), graphql_name='createTime')
    creator = sgqlc.types.Field('User', graphql_name='creator')
    deleted = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='deleted')
    finish_time = sgqlc.types.Field(sgqlc.types.non_null(UnixTime), graphql_name='finishTime')
    job_ids = sgqlc.types.Field(sgqlc.types.non_null(JobIds), graphql_name='jobIds')
    message = sgqlc.types.Field(sgqlc.types.non_null(JSON), graphql_name='message')
    original_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='originalId')
    pipeline_topic = sgqlc.types.Field(sgqlc.types.non_null('KafkaTopic'), graphql_name='pipelineTopic')
    priority = sgqlc.types.Field(sgqlc.types.non_null(MessagePriority), graphql_name='priority')
    reprocessed = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='reprocessed')
    reprocessed_from_kb = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='reprocessedFromKb')
    result = sgqlc.types.Field(Document, graphql_name='result')
    start_time = sgqlc.types.Field(sgqlc.types.non_null(UnixTime), graphql_name='startTime')
    topic = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='topic')


class MessageError(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('description', 'last_request')
    description = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='description')
    last_request = sgqlc.types.Field('PipelineRequestInfo', graphql_name='lastRequest')


class MessageFailed(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('create_time', 'creator', 'deleted', 'duplicate_of', 'error', 'finish_time', 'job_ids', 'message', 'pipeline_topic', 'priority', 'reprocessed', 'reprocessed_from_kb', 'result', 'stage', 'start_time', 'topic')
    create_time = sgqlc.types.Field(sgqlc.types.non_null(UnixTime), graphql_name='createTime')
    creator = sgqlc.types.Field('User', graphql_name='creator')
    deleted = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='deleted')
    duplicate_of = sgqlc.types.Field(String, graphql_name='duplicateOf')
    error = sgqlc.types.Field(sgqlc.types.non_null(MessageError), graphql_name='error')
    finish_time = sgqlc.types.Field(sgqlc.types.non_null(UnixTime), graphql_name='finishTime')
    job_ids = sgqlc.types.Field(sgqlc.types.non_null(JobIds), graphql_name='jobIds')
    message = sgqlc.types.Field(sgqlc.types.non_null(JSON), graphql_name='message')
    pipeline_topic = sgqlc.types.Field(sgqlc.types.non_null('KafkaTopic'), graphql_name='pipelineTopic')
    priority = sgqlc.types.Field(sgqlc.types.non_null(MessagePriority), graphql_name='priority')
    reprocessed = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='reprocessed')
    reprocessed_from_kb = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='reprocessedFromKb')
    result = sgqlc.types.Field(Document, graphql_name='result')
    stage = sgqlc.types.Field(sgqlc.types.non_null('PipelineTransformSetup'), graphql_name='stage')
    start_time = sgqlc.types.Field(sgqlc.types.non_null(UnixTime), graphql_name='startTime')
    topic = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='topic')


class MessageInProgress(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('create_time', 'creator', 'job_ids', 'message', 'pipeline_topic', 'priority', 'reprocessed', 'reprocessed_from_kb', 'result', 'stage', 'start_time', 'topic')
    create_time = sgqlc.types.Field(sgqlc.types.non_null(UnixTime), graphql_name='createTime')
    creator = sgqlc.types.Field('User', graphql_name='creator')
    job_ids = sgqlc.types.Field(sgqlc.types.non_null(JobIds), graphql_name='jobIds')
    message = sgqlc.types.Field(sgqlc.types.non_null(JSON), graphql_name='message')
    pipeline_topic = sgqlc.types.Field(sgqlc.types.non_null('KafkaTopic'), graphql_name='pipelineTopic')
    priority = sgqlc.types.Field(sgqlc.types.non_null(MessagePriority), graphql_name='priority')
    reprocessed = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='reprocessed')
    reprocessed_from_kb = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='reprocessedFromKb')
    result = sgqlc.types.Field(Document, graphql_name='result')
    stage = sgqlc.types.Field(sgqlc.types.non_null('PipelineTransformSetup'), graphql_name='stage')
    start_time = sgqlc.types.Field(sgqlc.types.non_null(UnixTime), graphql_name='startTime')
    topic = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='topic')


class MessageList(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('messages', 'total')
    messages = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('MessageStatus'))), graphql_name='messages')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class MessageMetrics(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('active', 'deleted', 'duplicate', 'failed', 'ok', 'pending')
    active = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='active')
    deleted = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='deleted')
    duplicate = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='duplicate')
    failed = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='failed')
    ok = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='ok')
    pending = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='pending')


class MessageNotHandled(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('create_time', 'creator', 'job_ids', 'message', 'not_handled', 'pipeline_topic', 'priority', 'reprocessed', 'reprocessed_from_kb', 'result', 'topic')
    create_time = sgqlc.types.Field(sgqlc.types.non_null(UnixTime), graphql_name='createTime')
    creator = sgqlc.types.Field('User', graphql_name='creator')
    job_ids = sgqlc.types.Field(sgqlc.types.non_null(JobIds), graphql_name='jobIds')
    message = sgqlc.types.Field(sgqlc.types.non_null(JSON), graphql_name='message')
    not_handled = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='notHandled')
    pipeline_topic = sgqlc.types.Field(sgqlc.types.non_null('KafkaTopic'), graphql_name='pipelineTopic')
    priority = sgqlc.types.Field(sgqlc.types.non_null(MessagePriority), graphql_name='priority')
    reprocessed = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='reprocessed')
    reprocessed_from_kb = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='reprocessedFromKb')
    result = sgqlc.types.Field(Document, graphql_name='result')
    topic = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='topic')


class MessageOk(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('create_time', 'creator', 'deleted', 'finish_time', 'job_ids', 'message', 'pipeline_topic', 'priority', 'reprocessed', 'reprocessed_from_kb', 'result', 'start_time', 'topic')
    create_time = sgqlc.types.Field(sgqlc.types.non_null(UnixTime), graphql_name='createTime')
    creator = sgqlc.types.Field('User', graphql_name='creator')
    deleted = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='deleted')
    finish_time = sgqlc.types.Field(sgqlc.types.non_null(UnixTime), graphql_name='finishTime')
    job_ids = sgqlc.types.Field(sgqlc.types.non_null(JobIds), graphql_name='jobIds')
    message = sgqlc.types.Field(sgqlc.types.non_null(JSON), graphql_name='message')
    pipeline_topic = sgqlc.types.Field(sgqlc.types.non_null('KafkaTopic'), graphql_name='pipelineTopic')
    priority = sgqlc.types.Field(sgqlc.types.non_null(MessagePriority), graphql_name='priority')
    reprocessed = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='reprocessed')
    reprocessed_from_kb = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='reprocessedFromKb')
    result = sgqlc.types.Field(Document, graphql_name='result')
    start_time = sgqlc.types.Field(sgqlc.types.non_null(UnixTime), graphql_name='startTime')
    topic = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='topic')


class MessageStatus(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('id', 'info')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    info = sgqlc.types.Field(sgqlc.types.non_null('MessageStatusInfo'), graphql_name='info')


class MessageUnknown(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('unknown',)
    unknown = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='unknown')


class Mutation(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('add_concept_dedup_method', 'add_concept_dedup_task', 'add_concept_transform_config', 'add_concept_transform_task', 'add_exporter', 'add_exporter_task', 'add_message', 'add_pipeline_config', 'add_user_pipeline_transform', 'cancel_concept_dedup_task', 'cancel_concept_transform_task', 'cancel_export_task', 'copy_concept_transform_config', 'copy_pending_to_kafka', 'copy_pipeline_config', 'delete_concept_dedup_method', 'delete_concept_dedup_task', 'delete_concept_transform_config', 'delete_export_task', 'delete_exporter', 'delete_kafka_topic', 'delete_non_completed_ok_messages_by_id', 'delete_pending_messages', 'delete_pipeline_config', 'delete_user_pipeline_transform', 'fix_other_message_metrics', 'fix_pipeline_topic_metrics', 'import_pipeline_config', 'put_kafka_topic', 'reprocess_documents', 'reprocess_message', 'reprocess_messages', 'retry_failed_in_topic', 'retry_failed_message', 'service_stats', 'transform_concepts', 'transform_documents', 'update_concept_dedup_method', 'update_concept_transform_config', 'update_concept_transform_config_transforms', 'update_exporter', 'update_exporter_show_in_menu', 'update_kafka_topics', 'update_pipeline_config', 'update_user_pipeline_transform')
    add_concept_dedup_method = sgqlc.types.Field(sgqlc.types.non_null('ConceptDedupMethod'), graphql_name='addConceptDedupMethod', args=sgqlc.types.ArgDict((
        ('data', sgqlc.types.Arg(ConceptDedupMethodInput, graphql_name='data', default=None)),
        ('service', sgqlc.types.Arg(UserServiceInput, graphql_name='service', default=None)),
        ('service_image', sgqlc.types.Arg(sgqlc.types.non_null(S3FileInput), graphql_name='serviceImage', default=None)),
))
    )
    add_concept_dedup_task = sgqlc.types.Field(sgqlc.types.non_null('ConceptDedupTask'), graphql_name='addConceptDedupTask', args=sgqlc.types.ArgDict((
        ('method_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='methodId', default=None)),
        ('task', sgqlc.types.Arg(sgqlc.types.non_null(ConceptDedupTaskInput), graphql_name='task', default=None)),
))
    )
    add_concept_transform_config = sgqlc.types.Field(sgqlc.types.non_null('ConceptTransformConfig'), graphql_name='addConceptTransformConfig', args=sgqlc.types.ArgDict((
        ('concept_transform', sgqlc.types.Arg(sgqlc.types.non_null(ConceptTransformConfigInput), graphql_name='conceptTransform', default=None)),
))
    )
    add_concept_transform_task = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='addConceptTransformTask', args=sgqlc.types.ArgDict((
        ('task', sgqlc.types.Arg(sgqlc.types.non_null(ConceptTransformTaskInput), graphql_name='task', default=None)),
))
    )
    add_exporter = sgqlc.types.Field(sgqlc.types.non_null('Exporter'), graphql_name='addExporter', args=sgqlc.types.ArgDict((
        ('data', sgqlc.types.Arg(ExporterInput, graphql_name='data', default=None)),
        ('service', sgqlc.types.Arg(UserServiceInput, graphql_name='service', default=None)),
        ('service_image', sgqlc.types.Arg(sgqlc.types.non_null(S3FileInput), graphql_name='serviceImage', default=None)),
        ('user_settings', sgqlc.types.Arg(ExporterUserSettingsInput, graphql_name='userSettings', default=None)),
))
    )
    add_exporter_task = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='addExporterTask', args=sgqlc.types.ArgDict((
        ('exporter', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='exporter', default=None)),
        ('task', sgqlc.types.Arg(sgqlc.types.non_null(ExportTaskInput), graphql_name='task', default=None)),
))
    )
    add_message = sgqlc.types.Field(sgqlc.types.non_null(MessageStatus), graphql_name='addMessage', args=sgqlc.types.ArgDict((
        ('message', sgqlc.types.Arg(sgqlc.types.non_null(JSON), graphql_name='message', default=None)),
        ('priority', sgqlc.types.Arg(MessagePriority, graphql_name='priority', default='Normal')),
        ('topic', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='topic', default=None)),
))
    )
    add_pipeline_config = sgqlc.types.Field(sgqlc.types.non_null('PipelineConfig'), graphql_name='addPipelineConfig', args=sgqlc.types.ArgDict((
        ('pipeline_config', sgqlc.types.Arg(sgqlc.types.non_null(PipelineConfigInput), graphql_name='pipelineConfig', default=None)),
))
    )
    add_user_pipeline_transform = sgqlc.types.Field(sgqlc.types.non_null('UserPipelineTransform'), graphql_name='addUserPipelineTransform', args=sgqlc.types.ArgDict((
        ('description', sgqlc.types.Arg(String, graphql_name='description', default=None)),
        ('menu_title', sgqlc.types.Arg(String, graphql_name='menuTitle', default=None)),
        ('service', sgqlc.types.Arg(UserServiceInput, graphql_name='service', default=None)),
        ('service_image', sgqlc.types.Arg(S3FileInput, graphql_name='serviceImage', default=None)),
))
    )
    cancel_concept_dedup_task = sgqlc.types.Field(sgqlc.types.non_null('ConceptDedupTask'), graphql_name='cancelConceptDedupTask', args=sgqlc.types.ArgDict((
        ('task_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='taskId', default=None)),
))
    )
    cancel_concept_transform_task = sgqlc.types.Field(sgqlc.types.non_null('ConceptTransformTask'), graphql_name='cancelConceptTransformTask', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    cancel_export_task = sgqlc.types.Field(sgqlc.types.non_null('ExportTask'), graphql_name='cancelExportTask', args=sgqlc.types.ArgDict((
        ('task_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='taskId', default=None)),
))
    )
    copy_concept_transform_config = sgqlc.types.Field(sgqlc.types.non_null('ConceptTransformConfig'), graphql_name='copyConceptTransformConfig', args=sgqlc.types.ArgDict((
        ('source_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='sourceId', default=None)),
        ('title', sgqlc.types.Arg(String, graphql_name='title', default=None)),
))
    )
    copy_pending_to_kafka = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='copyPendingToKafka', args=sgqlc.types.ArgDict((
        ('topic', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='topic', default=None)),
))
    )
    copy_pipeline_config = sgqlc.types.Field(sgqlc.types.non_null('PipelineConfig'), graphql_name='copyPipelineConfig', args=sgqlc.types.ArgDict((
        ('description', sgqlc.types.Arg(String, graphql_name='description', default=None)),
        ('source_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='sourceId', default=None)),
))
    )
    delete_concept_dedup_method = sgqlc.types.Field(sgqlc.types.non_null('ConceptDedupMethod'), graphql_name='deleteConceptDedupMethod', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    delete_concept_dedup_task = sgqlc.types.Field(sgqlc.types.non_null('ConceptDedupTask'), graphql_name='deleteConceptDedupTask', args=sgqlc.types.ArgDict((
        ('task_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='taskId', default=None)),
))
    )
    delete_concept_transform_config = sgqlc.types.Field(sgqlc.types.non_null('ConceptTransformConfig'), graphql_name='deleteConceptTransformConfig', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    delete_export_task = sgqlc.types.Field(sgqlc.types.non_null('ExportTask'), graphql_name='deleteExportTask', args=sgqlc.types.ArgDict((
        ('task_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='taskId', default=None)),
))
    )
    delete_exporter = sgqlc.types.Field(sgqlc.types.non_null('Exporter'), graphql_name='deleteExporter', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    delete_kafka_topic = sgqlc.types.Field(sgqlc.types.non_null('KafkaTopic'), graphql_name='deleteKafkaTopic', args=sgqlc.types.ArgDict((
        ('continue_after_timeout', sgqlc.types.Arg(Boolean, graphql_name='continueAfterTimeout', default=True)),
        ('start_type', sgqlc.types.Arg(String, graphql_name='startType', default=None)),
        ('topic', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='topic', default=None)),
))
    )
    delete_non_completed_ok_messages_by_id = sgqlc.types.Field(sgqlc.types.non_null(DeleteMessagesResult), graphql_name='deleteNonCompletedOkMessagesById', args=sgqlc.types.ArgDict((
        ('message_ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='messageIds', default=None)),
))
    )
    delete_pending_messages = sgqlc.types.Field(sgqlc.types.non_null(DeleteMessagesResult), graphql_name='deletePendingMessages', args=sgqlc.types.ArgDict((
        ('filter', sgqlc.types.Arg(MessageFilter, graphql_name='filter', default=None)),
        ('start_type', sgqlc.types.Arg(String, graphql_name='startType', default=None)),
        ('topic', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='topic', default=None)),
))
    )
    delete_pipeline_config = sgqlc.types.Field(sgqlc.types.non_null('PipelineConfig'), graphql_name='deletePipelineConfig', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    delete_user_pipeline_transform = sgqlc.types.Field(sgqlc.types.non_null('UserPipelineTransform'), graphql_name='deleteUserPipelineTransform', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    fix_other_message_metrics = sgqlc.types.Field(sgqlc.types.non_null(KafkaTopicMetrics), graphql_name='fixOtherMessageMetrics', args=sgqlc.types.ArgDict((
        ('dry_run', sgqlc.types.Arg(Boolean, graphql_name='dryRun', default=False)),
        ('id_type', sgqlc.types.Arg(sgqlc.types.non_null(OtherMessageIdType), graphql_name='idType', default=None)),
        ('id_value', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='idValue', default=None)),
))
    )
    fix_pipeline_topic_metrics = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(KafkaSubTopicMetrics))), graphql_name='fixPipelineTopicMetrics', args=sgqlc.types.ArgDict((
        ('dry_run', sgqlc.types.Arg(Boolean, graphql_name='dryRun', default=False)),
        ('topic', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='topic', default=None)),
))
    )
    import_pipeline_config = sgqlc.types.Field(sgqlc.types.non_null('PipelineConfig'), graphql_name='importPipelineConfig', args=sgqlc.types.ArgDict((
        ('export', sgqlc.types.Arg(sgqlc.types.non_null(S3FileInput), graphql_name='export', default=None)),
))
    )
    put_kafka_topic = sgqlc.types.Field(sgqlc.types.non_null('KafkaTopic'), graphql_name='putKafkaTopic', args=sgqlc.types.ArgDict((
        ('description', sgqlc.types.Arg(String, graphql_name='description', default=None)),
        ('move_to_on_timeout', sgqlc.types.Arg(String, graphql_name='moveToOnTimeout', default=None)),
        ('pipeline', sgqlc.types.Arg(PipelineSetupInput, graphql_name='pipeline', default=None)),
        ('priority', sgqlc.types.Arg(Int, graphql_name='priority', default=0)),
        ('request_timeout_ms', sgqlc.types.Arg(Int, graphql_name='requestTimeoutMs', default=None)),
        ('start_type', sgqlc.types.Arg(String, graphql_name='startType', default=None)),
        ('stopped', sgqlc.types.Arg(Boolean, graphql_name='stopped', default=False)),
        ('topic', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='topic', default=None)),
))
    )
    reprocess_documents = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='reprocessDocuments', args=sgqlc.types.ArgDict((
        ('document_ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='documentIds', default=None)),
        ('priority', sgqlc.types.Arg(MessagePriority, graphql_name='priority', default='Normal')),
        ('topic', sgqlc.types.Arg(ID, graphql_name='topic', default=None)),
        ('use_kb', sgqlc.types.Arg(Boolean, graphql_name='useKb', default=False)),
))
    )
    reprocess_message = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='reprocessMessage', args=sgqlc.types.ArgDict((
        ('message_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='messageId', default=None)),
        ('priority', sgqlc.types.Arg(MessagePriority, graphql_name='priority', default='Normal')),
        ('topic', sgqlc.types.Arg(ID, graphql_name='topic', default=None)),
        ('use_kb', sgqlc.types.Arg(Boolean, graphql_name='useKb', default=False)),
))
    )
    reprocess_messages = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='reprocessMessages', args=sgqlc.types.ArgDict((
        ('message_ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='messageIds', default=None)),
        ('priority', sgqlc.types.Arg(MessagePriority, graphql_name='priority', default='Normal')),
        ('topic', sgqlc.types.Arg(ID, graphql_name='topic', default=None)),
        ('use_kb', sgqlc.types.Arg(Boolean, graphql_name='useKb', default=False)),
))
    )
    retry_failed_in_topic = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='retryFailedInTopic', args=sgqlc.types.ArgDict((
        ('full_restart', sgqlc.types.Arg(Boolean, graphql_name='fullRestart', default=False)),
        ('start_type', sgqlc.types.Arg(String, graphql_name='startType', default=None)),
        ('topic', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='topic', default=None)),
))
    )
    retry_failed_message = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='retryFailedMessage', args=sgqlc.types.ArgDict((
        ('full_restart', sgqlc.types.Arg(Boolean, graphql_name='fullRestart', default=False)),
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='id', default=None)),
))
    )
    service_stats = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ServiceStats'))), graphql_name='serviceStats', args=sgqlc.types.ArgDict((
        ('reset', sgqlc.types.Arg(Boolean, graphql_name='reset', default=False)),
        ('service_id', sgqlc.types.Arg(String, graphql_name='serviceId', default=None)),
))
    )
    transform_concepts = sgqlc.types.Field(sgqlc.types.non_null(AddTransformTasksResult), graphql_name='transformConcepts', args=sgqlc.types.ArgDict((
        ('concept_ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='conceptIds', default=None)),
        ('priority', sgqlc.types.Arg(MessagePriority, graphql_name='priority', default='Normal')),
        ('start_type', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='startType', default=None)),
        ('topic', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='topic', default=None)),
))
    )
    transform_documents = sgqlc.types.Field(sgqlc.types.non_null(AddTransformTasksResult), graphql_name='transformDocuments', args=sgqlc.types.ArgDict((
        ('document_ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='documentIds', default=None)),
        ('priority', sgqlc.types.Arg(MessagePriority, graphql_name='priority', default='Normal')),
        ('start_type', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='startType', default=None)),
        ('topic', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='topic', default=None)),
))
    )
    update_concept_dedup_method = sgqlc.types.Field(sgqlc.types.non_null('ConceptDedupMethod'), graphql_name='updateConceptDedupMethod', args=sgqlc.types.ArgDict((
        ('data', sgqlc.types.Arg(ConceptDedupMethodInput, graphql_name='data', default=None)),
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
        ('service', sgqlc.types.Arg(UserServiceInput, graphql_name='service', default=None)),
        ('service_image', sgqlc.types.Arg(S3FileInput, graphql_name='serviceImage', default=None)),
))
    )
    update_concept_transform_config = sgqlc.types.Field(sgqlc.types.non_null('ConceptTransformConfig'), graphql_name='updateConceptTransformConfig', args=sgqlc.types.ArgDict((
        ('concept_transform', sgqlc.types.Arg(sgqlc.types.non_null(ConceptTransformConfigInput), graphql_name='conceptTransform', default=None)),
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    update_concept_transform_config_transforms = sgqlc.types.Field(sgqlc.types.non_null('ConceptTransformConfig'), graphql_name='updateConceptTransformConfigTransforms', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
        ('transforms', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(PipelineTransformSetupInput))), graphql_name='transforms', default=None)),
))
    )
    update_exporter = sgqlc.types.Field(sgqlc.types.non_null('Exporter'), graphql_name='updateExporter', args=sgqlc.types.ArgDict((
        ('data', sgqlc.types.Arg(ExporterInput, graphql_name='data', default=None)),
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
        ('service', sgqlc.types.Arg(UserServiceInput, graphql_name='service', default=None)),
        ('service_image', sgqlc.types.Arg(S3FileInput, graphql_name='serviceImage', default=None)),
        ('user_settings', sgqlc.types.Arg(ExporterUserSettingsInput, graphql_name='userSettings', default=None)),
))
    )
    update_exporter_show_in_menu = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('Exporter'))), graphql_name='updateExporterShowInMenu', args=sgqlc.types.ArgDict((
        ('ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='ids', default=None)),
        ('show_in_menu', sgqlc.types.Arg(Boolean, graphql_name='showInMenu', default=None)),
))
    )
    update_kafka_topics = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='updateKafkaTopics', args=sgqlc.types.ArgDict((
        ('start_type', sgqlc.types.Arg(String, graphql_name='startType', default=None)),
        ('topics', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='topics', default=None)),
        ('update', sgqlc.types.Arg(sgqlc.types.non_null(KafkaTopicUpdate), graphql_name='update', default=None)),
))
    )
    update_pipeline_config = sgqlc.types.Field(sgqlc.types.non_null('PipelineConfig'), graphql_name='updatePipelineConfig', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
        ('pipeline_config', sgqlc.types.Arg(sgqlc.types.non_null(PipelineConfigInput), graphql_name='pipelineConfig', default=None)),
))
    )
    update_user_pipeline_transform = sgqlc.types.Field(sgqlc.types.non_null('UserPipelineTransform'), graphql_name='updateUserPipelineTransform', args=sgqlc.types.ArgDict((
        ('description', sgqlc.types.Arg(String, graphql_name='description', default=None)),
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
        ('menu_title', sgqlc.types.Arg(String, graphql_name='menuTitle', default=None)),
        ('service', sgqlc.types.Arg(UserServiceInput, graphql_name='service', default=None)),
        ('service_image', sgqlc.types.Arg(S3FileInput, graphql_name='serviceImage', default=None)),
))
    )


class Parameter(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('key', 'value')
    key = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='key')
    value = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='value')


class ParamsSchema(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('schema', 'ui_schema')
    schema = sgqlc.types.Field(sgqlc.types.non_null(JSON), graphql_name='schema')
    ui_schema = sgqlc.types.Field(JSON, graphql_name='uiSchema')


class PendingMessageList(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('messages', 'total')
    messages = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('PendingMessageStatus'))), graphql_name='messages')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class PendingMessageStatus(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('id', 'info')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    info = sgqlc.types.Field(sgqlc.types.non_null('PendingMessageStatusInfo'), graphql_name='info')


class PeriodicJobMetrics(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('metrics', 'periodic_job_id')
    metrics = sgqlc.types.Field(sgqlc.types.non_null(MessageMetrics), graphql_name='metrics')
    periodic_job_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='periodicJobId')


class PeriodicTaskMetrics(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('metrics', 'periodic_task_id')
    metrics = sgqlc.types.Field(sgqlc.types.non_null(MessageMetrics), graphql_name='metrics')
    periodic_task_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='periodicTaskId')


class PipelineConfigList(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('pipeline_configs', 'total')
    pipeline_configs = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('PipelineConfig'))), graphql_name='pipelineConfigs')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class PipelineConfigSettings(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('disable_preload',)
    disable_preload = sgqlc.types.Field(Boolean, graphql_name='disablePreload')


class PipelineRequestInfo(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('controller_log_link', 'failed', 'service', 'service_log_links')
    controller_log_link = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='controllerLogLink')
    failed = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='failed')
    service = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='service')
    service_log_links = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(KibanaLink))), graphql_name='serviceLogLinks')


class PipelineSetup(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('pipeline_config',)
    pipeline_config = sgqlc.types.Field(sgqlc.types.non_null('PipelineConfig'), graphql_name='pipelineConfig')


class PipelineTopicType(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('name', 'start_type')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    start_type = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='startType')


class PipelineTransform(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('description', 'id', 'in_type', 'menu_title', 'out_type', 'params_schema', 'repeatable', 'title', 'version')
    description = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='description')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    in_type = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='inType')
    menu_title = sgqlc.types.Field(String, graphql_name='menuTitle')
    out_type = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='outType')
    params_schema = sgqlc.types.Field(sgqlc.types.non_null(ParamsSchema), graphql_name='paramsSchema')
    repeatable = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='repeatable')
    title = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='title')
    version = sgqlc.types.Field(String, graphql_name='version')


class PipelineTransformList(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('total', 'transforms')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')
    transforms = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(PipelineTransform))), graphql_name='transforms')


class PipelineTransformSetup(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('id', 'params', 'transform')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    params = sgqlc.types.Field(sgqlc.types.non_null(JSON), graphql_name='params')
    transform = sgqlc.types.Field(sgqlc.types.non_null(PipelineTransform), graphql_name='transform')


class Query(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('active_messages', 'batch_reprocess', 'batch_reprocess_get_message_id_tasks', 'completed_ok_messages', 'concept_dedup_method', 'concept_dedup_methods', 'concept_dedup_task', 'concept_dedup_tasks', 'concept_transform_config', 'concept_transform_configs', 'concept_transform_message_type', 'concept_transform_task', 'concept_transform_tasks', 'debug_db_load_wait', 'debug_dump_extensions', 'debug_tcontroller_info', 'duplicate_messages', 'export_pipeline_config', 'export_task', 'export_tasks', 'exporter', 'exporters', 'failed_messages', 'job_ids_by_message_uuid2', 'job_items2', 'job_metrics2', 'kafka_pipeline_start_type', 'kafka_topic', 'kafka_topics', 'list_concept_dedup_tasks', 'message_count', 'message_source_available', 'message_status', 'message_statuses', 'message_topic', 'messages_by_parent_id', 'pending_messages', 'periodic_job_items2', 'periodic_job_metrics2', 'periodic_task_items2', 'periodic_task_metrics2', 'pipeline_config', 'pipeline_configs', 'pipeline_topic_types', 'pipeline_transform', 'pipeline_transforms', 'task_items2', 'task_metrics2', 'user_pipeline_transform', 'user_pipeline_transforms')
    active_messages = sgqlc.types.Field(sgqlc.types.non_null(ActiveMessageList), graphql_name='activeMessages', args=sgqlc.types.ArgDict((
        ('filter', sgqlc.types.Arg(MessageFilter, graphql_name='filter', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=None)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=None)),
        ('sort_by', sgqlc.types.Arg(ItemsSort, graphql_name='sortBy', default='timestamp')),
        ('sort_direction', sgqlc.types.Arg(SortDirection, graphql_name='sortDirection', default='descending')),
        ('start_type', sgqlc.types.Arg(String, graphql_name='startType', default=None)),
        ('topic', sgqlc.types.Arg(ID, graphql_name='topic', default=None)),
))
    )
    batch_reprocess = sgqlc.types.Field(sgqlc.types.non_null('BatchReprocess'), graphql_name='batchReprocess', args=sgqlc.types.ArgDict((
        ('batch_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='batchId', default=None)),
))
    )
    batch_reprocess_get_message_id_tasks = sgqlc.types.Field(sgqlc.types.non_null(BatchReprocessGetMessageIdTaskList), graphql_name='batchReprocessGetMessageIdTasks', args=sgqlc.types.ArgDict((
        ('batch_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='batchId', default=None)),
        ('filter', sgqlc.types.Arg(BatchReprocessGetMessageIdTaskFilter, graphql_name='filter', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=None)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=None)),
        ('sort_by', sgqlc.types.Arg(ItemsSort, graphql_name='sortBy', default='timestamp')),
        ('sort_direction', sgqlc.types.Arg(SortDirection, graphql_name='sortDirection', default='descending')),
))
    )
    completed_ok_messages = sgqlc.types.Field(sgqlc.types.non_null(CompletedOkMessageList), graphql_name='completedOkMessages', args=sgqlc.types.ArgDict((
        ('filter', sgqlc.types.Arg(MessageFilter, graphql_name='filter', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=None)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=None)),
        ('sort_by', sgqlc.types.Arg(MessageSort, graphql_name='sortBy', default='timestamp')),
        ('sort_direction', sgqlc.types.Arg(SortDirection, graphql_name='sortDirection', default='descending')),
        ('start_type', sgqlc.types.Arg(String, graphql_name='startType', default=None)),
        ('topic', sgqlc.types.Arg(ID, graphql_name='topic', default=None)),
))
    )
    concept_dedup_method = sgqlc.types.Field(sgqlc.types.non_null('ConceptDedupMethod'), graphql_name='conceptDedupMethod', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    concept_dedup_methods = sgqlc.types.Field(sgqlc.types.non_null(ConceptDedupMethodList), graphql_name='conceptDedupMethods', args=sgqlc.types.ArgDict((
        ('filter', sgqlc.types.Arg(ConceptDedupMethodFilter, graphql_name='filter', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=None)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=None)),
        ('sort_by', sgqlc.types.Arg(ConceptDedupMethodSort, graphql_name='sortBy', default='id')),
        ('sort_direction', sgqlc.types.Arg(SortDirection, graphql_name='sortDirection', default='ascending')),
))
    )
    concept_dedup_task = sgqlc.types.Field(sgqlc.types.non_null('ConceptDedupTask'), graphql_name='conceptDedupTask', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    concept_dedup_tasks = sgqlc.types.Field(sgqlc.types.non_null(ConceptDedupTaskList), graphql_name='conceptDedupTasks', args=sgqlc.types.ArgDict((
        ('filter', sgqlc.types.Arg(ConceptDedupTaskFilter, graphql_name='filter', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=None)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=None)),
        ('sort_by', sgqlc.types.Arg(ConceptDedupTaskSort, graphql_name='sortBy', default='createTime')),
        ('sort_direction', sgqlc.types.Arg(SortDirection, graphql_name='sortDirection', default='descending')),
))
    )
    concept_transform_config = sgqlc.types.Field(sgqlc.types.non_null('ConceptTransformConfig'), graphql_name='conceptTransformConfig', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    concept_transform_configs = sgqlc.types.Field(sgqlc.types.non_null(ConceptTransformConfigList), graphql_name='conceptTransformConfigs', args=sgqlc.types.ArgDict((
        ('filter', sgqlc.types.Arg(ConceptTransformConfigFilter, graphql_name='filter', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=None)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=None)),
        ('sort_by', sgqlc.types.Arg(ConceptTransformConfigSort, graphql_name='sortBy', default='id')),
        ('sort_direction', sgqlc.types.Arg(SortDirection, graphql_name='sortDirection', default='ascending')),
))
    )
    concept_transform_message_type = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='conceptTransformMessageType')
    concept_transform_task = sgqlc.types.Field(sgqlc.types.non_null('ConceptTransformTask'), graphql_name='conceptTransformTask', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    concept_transform_tasks = sgqlc.types.Field(sgqlc.types.non_null(ConceptTransformTaskList), graphql_name='conceptTransformTasks', args=sgqlc.types.ArgDict((
        ('filter', sgqlc.types.Arg(ConceptTransformTaskFilter, graphql_name='filter', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=None)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=None)),
        ('sort_by', sgqlc.types.Arg(ConceptTransformTaskSort, graphql_name='sortBy', default='createTime')),
        ('sort_direction', sgqlc.types.Arg(SortDirection, graphql_name='sortDirection', default='descending')),
))
    )
    debug_db_load_wait = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='debugDbLoadWait')
    debug_dump_extensions = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='debugDumpExtensions')
    debug_tcontroller_info = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(Parameter))), graphql_name='debugTcontrollerInfo')
    duplicate_messages = sgqlc.types.Field(sgqlc.types.non_null(DuplicateMessageList), graphql_name='duplicateMessages', args=sgqlc.types.ArgDict((
        ('filter', sgqlc.types.Arg(MessageFilter, graphql_name='filter', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=None)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=None)),
        ('sort_by', sgqlc.types.Arg(MessageSort, graphql_name='sortBy', default='timestamp')),
        ('sort_direction', sgqlc.types.Arg(SortDirection, graphql_name='sortDirection', default='descending')),
        ('start_type', sgqlc.types.Arg(String, graphql_name='startType', default=None)),
        ('topic', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='topic', default=None)),
))
    )
    export_pipeline_config = sgqlc.types.Field(sgqlc.types.non_null(JSON), graphql_name='exportPipelineConfig', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    export_task = sgqlc.types.Field(sgqlc.types.non_null('ExportTask'), graphql_name='exportTask', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    export_tasks = sgqlc.types.Field(sgqlc.types.non_null(ExportTaskList), graphql_name='exportTasks', args=sgqlc.types.ArgDict((
        ('filter', sgqlc.types.Arg(ExportTaskFilter, graphql_name='filter', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=None)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=None)),
        ('sort_by', sgqlc.types.Arg(ExportTaskSort, graphql_name='sortBy', default='createTime')),
        ('sort_direction', sgqlc.types.Arg(SortDirection, graphql_name='sortDirection', default='descending')),
))
    )
    exporter = sgqlc.types.Field(sgqlc.types.non_null('Exporter'), graphql_name='exporter', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    exporters = sgqlc.types.Field(sgqlc.types.non_null(ExporterList), graphql_name='exporters', args=sgqlc.types.ArgDict((
        ('filter', sgqlc.types.Arg(ExporterFilter, graphql_name='filter', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=None)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=None)),
        ('sort_by', sgqlc.types.Arg(ExporterSort, graphql_name='sortBy', default='id')),
        ('sort_direction', sgqlc.types.Arg(SortDirection, graphql_name='sortDirection', default='ascending')),
))
    )
    failed_messages = sgqlc.types.Field(sgqlc.types.non_null(FailedMessageList), graphql_name='failedMessages', args=sgqlc.types.ArgDict((
        ('filter', sgqlc.types.Arg(MessageFilter, graphql_name='filter', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=None)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=None)),
        ('sort_by', sgqlc.types.Arg(MessageSort, graphql_name='sortBy', default='timestamp')),
        ('sort_direction', sgqlc.types.Arg(SortDirection, graphql_name='sortDirection', default='descending')),
        ('start_type', sgqlc.types.Arg(String, graphql_name='startType', default=None)),
        ('topic', sgqlc.types.Arg(ID, graphql_name='topic', default=None)),
))
    )
    job_ids_by_message_uuid2 = sgqlc.types.Field(JobIds, graphql_name='jobIdsByMessageUUID2', args=sgqlc.types.ArgDict((
        ('message_uuid', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='messageUUID', default=None)),
))
    )
    job_items2 = sgqlc.types.Field(sgqlc.types.non_null(ItemsList), graphql_name='jobItems2', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
        ('items_filter', sgqlc.types.Arg(ItemsFilter, graphql_name='itemsFilter', default={'inputText': None, 'interval': None, 'parentOrSelfId': None, 'state': None, 'topic': None})),
        ('items_sort', sgqlc.types.Arg(ItemsSort, graphql_name='itemsSort', default='timestamp')),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=10)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('sort_direction', sgqlc.types.Arg(SortDirection, graphql_name='sortDirection', default='descending')),
))
    )
    job_metrics2 = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(JobMetrics))), graphql_name='jobMetrics2', args=sgqlc.types.ArgDict((
        ('job_ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='jobIds', default=None)),
        ('old', sgqlc.types.Arg(Boolean, graphql_name='old', default=False)),
))
    )
    kafka_pipeline_start_type = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='kafkaPipelineStartType')
    kafka_topic = sgqlc.types.Field(sgqlc.types.non_null('KafkaTopic'), graphql_name='kafkaTopic', args=sgqlc.types.ArgDict((
        ('start_type', sgqlc.types.Arg(String, graphql_name='startType', default=None)),
        ('topic', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='topic', default=None)),
))
    )
    kafka_topics = sgqlc.types.Field(sgqlc.types.non_null(KafkaTopicList), graphql_name='kafkaTopics', args=sgqlc.types.ArgDict((
        ('filter', sgqlc.types.Arg(KafkaTopicFilter, graphql_name='filter', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=None)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=None)),
        ('sort_by', sgqlc.types.Arg(KafkaTopicSort, graphql_name='sortBy', default='topic')),
        ('sort_direction', sgqlc.types.Arg(SortDirection, graphql_name='sortDirection', default='ascending')),
))
    )
    list_concept_dedup_tasks = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of('ConceptDedupTask')), graphql_name='listConceptDedupTasks', args=sgqlc.types.ArgDict((
        ('ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='ids', default=None)),
))
    )
    message_count = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='messageCount', args=sgqlc.types.ArgDict((
        ('filter', sgqlc.types.Arg(sgqlc.types.non_null(MessageFilter), graphql_name='filter', default=None)),
))
    )
    message_source_available = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='messageSourceAvailable', args=sgqlc.types.ArgDict((
        ('ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='ids', default=None)),
))
    )
    message_status = sgqlc.types.Field(sgqlc.types.non_null(MessageStatus), graphql_name='messageStatus', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    message_statuses = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(MessageStatus))), graphql_name='messageStatuses', args=sgqlc.types.ArgDict((
        ('ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='ids', default=None)),
))
    )
    message_topic = sgqlc.types.Field(ID, graphql_name='messageTopic', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    messages_by_parent_id = sgqlc.types.Field(sgqlc.types.non_null(MessageList), graphql_name='messagesByParentId', args=sgqlc.types.ArgDict((
        ('filter', sgqlc.types.Arg(MessageFilter, graphql_name='filter', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=None)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=None)),
        ('parent_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='parentId', default=None)),
        ('sort_by', sgqlc.types.Arg(ItemsSort, graphql_name='sortBy', default='timestamp')),
        ('sort_direction', sgqlc.types.Arg(SortDirection, graphql_name='sortDirection', default='descending')),
))
    )
    pending_messages = sgqlc.types.Field(sgqlc.types.non_null(PendingMessageList), graphql_name='pendingMessages', args=sgqlc.types.ArgDict((
        ('filter', sgqlc.types.Arg(MessageFilter, graphql_name='filter', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=None)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=None)),
        ('sort_by', sgqlc.types.Arg(ItemsSort, graphql_name='sortBy', default='timestamp')),
        ('sort_direction', sgqlc.types.Arg(SortDirection, graphql_name='sortDirection', default='descending')),
        ('start_type', sgqlc.types.Arg(String, graphql_name='startType', default=None)),
        ('topic', sgqlc.types.Arg(ID, graphql_name='topic', default=None)),
))
    )
    periodic_job_items2 = sgqlc.types.Field(sgqlc.types.non_null(ItemsList), graphql_name='periodicJobItems2', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
        ('items_filter', sgqlc.types.Arg(ItemsFilter, graphql_name='itemsFilter', default={'inputText': None, 'interval': None, 'parentOrSelfId': None, 'state': None, 'topic': None})),
        ('items_sort', sgqlc.types.Arg(ItemsSort, graphql_name='itemsSort', default='timestamp')),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=10)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('sort_direction', sgqlc.types.Arg(SortDirection, graphql_name='sortDirection', default='descending')),
))
    )
    periodic_job_metrics2 = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(PeriodicJobMetrics))), graphql_name='periodicJobMetrics2', args=sgqlc.types.ArgDict((
        ('periodic_job_ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='periodicJobIds', default=None)),
))
    )
    periodic_task_items2 = sgqlc.types.Field(sgqlc.types.non_null(ItemsList), graphql_name='periodicTaskItems2', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
        ('items_filter', sgqlc.types.Arg(ItemsFilter, graphql_name='itemsFilter', default={'inputText': None, 'interval': None, 'parentOrSelfId': None, 'state': None, 'topic': None})),
        ('items_sort', sgqlc.types.Arg(ItemsSort, graphql_name='itemsSort', default='timestamp')),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=10)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('sort_direction', sgqlc.types.Arg(SortDirection, graphql_name='sortDirection', default='descending')),
))
    )
    periodic_task_metrics2 = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(PeriodicTaskMetrics))), graphql_name='periodicTaskMetrics2', args=sgqlc.types.ArgDict((
        ('periodic_task_ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='periodicTaskIds', default=None)),
))
    )
    pipeline_config = sgqlc.types.Field(sgqlc.types.non_null('PipelineConfig'), graphql_name='pipelineConfig', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    pipeline_configs = sgqlc.types.Field(sgqlc.types.non_null(PipelineConfigList), graphql_name='pipelineConfigs', args=sgqlc.types.ArgDict((
        ('filter', sgqlc.types.Arg(PipelineConfigFilter, graphql_name='filter', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=None)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=None)),
        ('sort_by', sgqlc.types.Arg(PipelineConfigSort, graphql_name='sortBy', default='id')),
        ('sort_direction', sgqlc.types.Arg(SortDirection, graphql_name='sortDirection', default='ascending')),
))
    )
    pipeline_topic_types = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(PipelineTopicType))), graphql_name='pipelineTopicTypes')
    pipeline_transform = sgqlc.types.Field(sgqlc.types.non_null(PipelineTransform), graphql_name='pipelineTransform', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    pipeline_transforms = sgqlc.types.Field(sgqlc.types.non_null(PipelineTransformList), graphql_name='pipelineTransforms', args=sgqlc.types.ArgDict((
        ('filter', sgqlc.types.Arg(PipelineTransformFilter, graphql_name='filter', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=None)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=None)),
))
    )
    task_items2 = sgqlc.types.Field(sgqlc.types.non_null(ItemsList), graphql_name='taskItems2', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
        ('items_filter', sgqlc.types.Arg(ItemsFilter, graphql_name='itemsFilter', default={'inputText': None, 'interval': None, 'parentOrSelfId': None, 'state': None, 'topic': None})),
        ('items_sort', sgqlc.types.Arg(ItemsSort, graphql_name='itemsSort', default='timestamp')),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=10)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('sort_direction', sgqlc.types.Arg(SortDirection, graphql_name='sortDirection', default='descending')),
))
    )
    task_metrics2 = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('TaskMetrics'))), graphql_name='taskMetrics2', args=sgqlc.types.ArgDict((
        ('task_ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='taskIds', default=None)),
))
    )
    user_pipeline_transform = sgqlc.types.Field(sgqlc.types.non_null('UserPipelineTransform'), graphql_name='userPipelineTransform', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    user_pipeline_transforms = sgqlc.types.Field(sgqlc.types.non_null('UserPipelineTransformList'), graphql_name='userPipelineTransforms', args=sgqlc.types.ArgDict((
        ('filter', sgqlc.types.Arg(UserPipelineTransformFilter, graphql_name='filter', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=None)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=None)),
        ('sort_by', sgqlc.types.Arg(UserPipelineTransformSort, graphql_name='sortBy', default='id')),
        ('sort_direction', sgqlc.types.Arg(SortDirection, graphql_name='sortDirection', default='descending')),
))
    )


class ServiceStats(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('active_slots', 'cancelled_requests', 'duration', 'failed_request_max_duration', 'failed_requests', 'free_servers', 'in_progress', 'load', 'name', 'ok_request_max_duration', 'ok_requests', 'prepared_requests', 'queue', 'queue_tasks', 'ready_servers', 'responses', 'servers', 'waiting_slots')
    active_slots = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='activeSlots')
    cancelled_requests = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='cancelledRequests')
    duration = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='duration')
    failed_request_max_duration = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='failedRequestMaxDuration')
    failed_requests = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='failedRequests')
    free_servers = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='freeServers')
    in_progress = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='inProgress')
    load = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='load')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    ok_request_max_duration = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='okRequestMaxDuration')
    ok_requests = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='okRequests')
    prepared_requests = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='preparedRequests')
    queue = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='queue')
    queue_tasks = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))), graphql_name='queueTasks')
    ready_servers = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='readyServers')
    responses = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='responses')
    servers = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='servers')
    waiting_slots = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='waitingSlots')


class TaskMetrics(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('metrics', 'task_id')
    metrics = sgqlc.types.Field(sgqlc.types.non_null(MessageMetrics), graphql_name='metrics')
    task_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='taskId')


class User(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('id',)
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')


class UserPipelineTransformList(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('total', 'transforms')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')
    transforms = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('UserPipelineTransform'))), graphql_name='transforms')


class UserService(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('cpu_limit', 'cpu_request', 'environment', 'max_pods', 'mem_limit', 'mem_request', 'min_pods', 'state')
    cpu_limit = sgqlc.types.Field(Int, graphql_name='cpuLimit')
    cpu_request = sgqlc.types.Field(Int, graphql_name='cpuRequest')
    environment = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('UserServiceEnvironmentVariable')), graphql_name='environment')
    max_pods = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='maxPods')
    mem_limit = sgqlc.types.Field(Int, graphql_name='memLimit')
    mem_request = sgqlc.types.Field(Int, graphql_name='memRequest')
    min_pods = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='minPods')
    state = sgqlc.types.Field(sgqlc.types.non_null(UserServiceState), graphql_name='state')


class UserServiceEnvironmentVariable(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('name', 'value')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    value = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='value')


class BatchReprocess(sgqlc.types.Type, RecordInterface):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('metrics',)
    metrics = sgqlc.types.Field(sgqlc.types.non_null(BatchReprocessMetrics), graphql_name='metrics')


class ConceptDedupMethod(sgqlc.types.Type, RecordInterface):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('description', 'id', 'last_task_time', 'metrics', 'params_schema', 'service', 'title')
    description = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='description')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    last_task_time = sgqlc.types.Field(UnixTime, graphql_name='lastTaskTime')
    metrics = sgqlc.types.Field(sgqlc.types.non_null(KafkaTopicMetrics), graphql_name='metrics')
    params_schema = sgqlc.types.Field(sgqlc.types.non_null(ParamsSchema), graphql_name='paramsSchema')
    service = sgqlc.types.Field(sgqlc.types.non_null(UserService), graphql_name='service')
    title = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='title')


class ConceptDedupTask(sgqlc.types.Type, RecordInterface):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('active', 'concept_ids', 'create_time', 'id', 'method', 'params', 'result', 'state', 'tql_query')
    active = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='active')
    concept_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='conceptIds')
    create_time = sgqlc.types.Field(sgqlc.types.non_null(UnixTime), graphql_name='createTime')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    method = sgqlc.types.Field(ConceptDedupMethod, graphql_name='method')
    params = sgqlc.types.Field(sgqlc.types.non_null(JSON), graphql_name='params')
    result = sgqlc.types.Field(ConceptDedupTaskResult, graphql_name='result')
    state = sgqlc.types.Field(sgqlc.types.non_null(ConceptDedupTaskState), graphql_name='state')
    tql_query = sgqlc.types.Field(String, graphql_name='tqlQuery')


class ConceptTransformConfig(sgqlc.types.Type, RecordInterface):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('can_transform_multiple_entities', 'can_transform_one_entity', 'concept_type_ids', 'deleted', 'description', 'id', 'last_task_time', 'metrics', 'priority', 'title', 'transforms')
    can_transform_multiple_entities = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='canTransformMultipleEntities')
    can_transform_one_entity = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='canTransformOneEntity')
    concept_type_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='conceptTypeIds')
    deleted = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='deleted')
    description = sgqlc.types.Field(String, graphql_name='description')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    last_task_time = sgqlc.types.Field(UnixTime, graphql_name='lastTaskTime')
    metrics = sgqlc.types.Field(sgqlc.types.non_null(KafkaTopicMetrics), graphql_name='metrics')
    priority = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='priority')
    title = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='title')
    transforms = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(PipelineTransformSetup))), graphql_name='transforms')


class ConceptTransformTask(sgqlc.types.Type, RecordInterface):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('active', 'concept_ids', 'config', 'id', 'result', 'state')
    active = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='active')
    concept_ids = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='conceptIds')
    config = sgqlc.types.Field(ConceptTransformConfig, graphql_name='config')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    result = sgqlc.types.Field(ConceptTransformResults, graphql_name='result')
    state = sgqlc.types.Field(sgqlc.types.non_null(ConceptTransformTaskState), graphql_name='state')


class ExportTask(sgqlc.types.Type, RecordInterface):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('active', 'create_time', 'entities', 'exporter', 'id', 'params', 'result', 'state')
    active = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='active')
    create_time = sgqlc.types.Field(sgqlc.types.non_null(UnixTime), graphql_name='createTime')
    entities = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ExportEntity))), graphql_name='entities')
    exporter = sgqlc.types.Field('Exporter', graphql_name='exporter')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    params = sgqlc.types.Field(sgqlc.types.non_null(JSON), graphql_name='params')
    result = sgqlc.types.Field(ExportResults, graphql_name='result')
    state = sgqlc.types.Field(sgqlc.types.non_null(ExportTaskState), graphql_name='state')


class Exporter(sgqlc.types.Type, RecordInterface):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('can_export_concept', 'can_export_document', 'can_export_multiple_entities', 'can_export_one_entity', 'concept_type_ids', 'default_params', 'default_params_schema', 'description', 'id', 'last_task_time', 'menu_title', 'metrics', 'params_schema', 'service', 'show_in_menu', 'title')
    can_export_concept = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='canExportConcept')
    can_export_document = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='canExportDocument')
    can_export_multiple_entities = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='canExportMultipleEntities')
    can_export_one_entity = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='canExportOneEntity')
    concept_type_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='conceptTypeIds')
    default_params = sgqlc.types.Field(sgqlc.types.non_null(JSON), graphql_name='defaultParams')
    default_params_schema = sgqlc.types.Field(sgqlc.types.non_null(ParamsSchema), graphql_name='defaultParamsSchema')
    description = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='description')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    last_task_time = sgqlc.types.Field(UnixTime, graphql_name='lastTaskTime')
    menu_title = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='menuTitle')
    metrics = sgqlc.types.Field(sgqlc.types.non_null(KafkaTopicMetrics), graphql_name='metrics')
    params_schema = sgqlc.types.Field(sgqlc.types.non_null(ParamsSchema), graphql_name='paramsSchema')
    service = sgqlc.types.Field(sgqlc.types.non_null(UserService), graphql_name='service')
    show_in_menu = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='showInMenu')
    title = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='title')


class KafkaTopic(sgqlc.types.Type, RecordInterface):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('can_have_duplicates', 'description', 'metrics', 'move_to_on_timeout', 'pipeline', 'priority', 'request_timeout_ms', 'start_type', 'stopped', 'sub_topic_metrics', 'system_topic', 'topic')
    can_have_duplicates = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='canHaveDuplicates')
    description = sgqlc.types.Field(String, graphql_name='description')
    metrics = sgqlc.types.Field(sgqlc.types.non_null(KafkaTopicMetrics), graphql_name='metrics')
    move_to_on_timeout = sgqlc.types.Field(String, graphql_name='moveToOnTimeout')
    pipeline = sgqlc.types.Field(PipelineSetup, graphql_name='pipeline')
    priority = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='priority')
    request_timeout_ms = sgqlc.types.Field(Int, graphql_name='requestTimeoutMs')
    start_type = sgqlc.types.Field(sgqlc.types.non_null(PipelineTopicType), graphql_name='startType')
    stopped = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='stopped')
    sub_topic_metrics = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(KafkaSubTopicMetrics))), graphql_name='subTopicMetrics')
    system_topic = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='systemTopic')
    topic = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='topic')


class PipelineConfig(sgqlc.types.Type, RecordInterface):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('description', 'error', 'id', 'settings', 'start_type', 'transform_count', 'transforms', 'used_in_topics')
    description = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='description')
    error = sgqlc.types.Field(Event, graphql_name='error')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    settings = sgqlc.types.Field(PipelineConfigSettings, graphql_name='settings')
    start_type = sgqlc.types.Field(sgqlc.types.non_null(PipelineTopicType), graphql_name='startType')
    transform_count = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='transformCount')
    transforms = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(PipelineTransformSetup))), graphql_name='transforms')
    used_in_topics = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='usedInTopics')


class UserPipelineTransform(sgqlc.types.Type, RecordInterface):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('description', 'id', 'in_type', 'menu_title', 'out_type', 'service', 'title', 'used_in_pipeline_configs', 'version')
    description = sgqlc.types.Field(String, graphql_name='description')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    in_type = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='inType')
    menu_title = sgqlc.types.Field(String, graphql_name='menuTitle')
    out_type = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='outType')
    service = sgqlc.types.Field(sgqlc.types.non_null(UserService), graphql_name='service')
    title = sgqlc.types.Field(String, graphql_name='title')
    used_in_pipeline_configs = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='usedInPipelineConfigs')
    version = sgqlc.types.Field(String, graphql_name='version')



########################################################################
# Unions
########################################################################
class MessageStatusInfo(sgqlc.types.Union):
    __schema__ = tcontroller_api_schema
    __types__ = (MessageDuplicate, MessageFailed, MessageInProgress, MessageNotHandled, MessageOk, MessageUnknown)


class PendingMessageStatusInfo(sgqlc.types.Union):
    __schema__ = tcontroller_api_schema
    __types__ = (MessageInProgress, MessageNotHandled)



########################################################################
# Schema Entry Points
########################################################################
tcontroller_api_schema.query_type = Query
tcontroller_api_schema.mutation_type = Mutation
tcontroller_api_schema.subscription_type = None

