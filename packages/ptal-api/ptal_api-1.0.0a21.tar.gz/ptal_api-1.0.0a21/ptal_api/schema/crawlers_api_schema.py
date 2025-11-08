import sgqlc.types


crawlers_api_schema = sgqlc.types.Schema()



########################################################################
# Scalars and Enumerations
########################################################################
Boolean = sgqlc.types.Boolean

class CollectionStatus(sgqlc.types.Enum):
    __schema__ = crawlers_api_schema
    __choices__ = ('Canceled', 'Error', 'InProgress', 'Pending', 'Success', 'WithMistakes')


class CrawlStateSorting(sgqlc.types.Enum):
    __schema__ = crawlers_api_schema
    __choices__ = ('crawlKey', 'creatorId', 'id', 'lastUpdaterId', 'systemRegistrationDate', 'systemUpdateDate')


class CrawlerSorting(sgqlc.types.Enum):
    __schema__ = crawlers_api_schema
    __choices__ = ('avgPerformanceTime', 'id', 'lastCollectionDate', 'projectTitle', 'title')


class CrawlerType(sgqlc.types.Enum):
    __schema__ = crawlers_api_schema
    __choices__ = ('Emulator', 'Search', 'Target')


class CredentialSorting(sgqlc.types.Enum):
    __schema__ = crawlers_api_schema
    __choices__ = ('dataType', 'domain', 'id', 'status', 'value')


class CredentialStatus(sgqlc.types.Enum):
    __schema__ = crawlers_api_schema
    __choices__ = ('Invalid', 'Valid')


class CredentialType(sgqlc.types.Enum):
    __schema__ = crawlers_api_schema
    __choices__ = ('Account', 'Token')


class DeployStatus(sgqlc.types.Enum):
    __schema__ = crawlers_api_schema
    __choices__ = ('Error', 'InProgress', 'NothingToDeploy', 'Success')


class DistributionType(sgqlc.types.Enum):
    __schema__ = crawlers_api_schema
    __choices__ = ('EggFile', 'External', 'Sitemap')


class EventTarget(sgqlc.types.Enum):
    __schema__ = crawlers_api_schema
    __choices__ = ('crawlersApi',)


Float = sgqlc.types.Float

ID = sgqlc.types.ID

class InformationSourceLoaderActualStatus(sgqlc.types.Enum):
    __schema__ = crawlers_api_schema
    __choices__ = ('Daily', 'EveryTwoDays', 'Never', 'TwiceADay', 'Weekly')


class InformationSourceLoaderSorting(sgqlc.types.Enum):
    __schema__ = crawlers_api_schema
    __choices__ = ('id', 'status')


class InformationSourceSorting(sgqlc.types.Enum):
    __schema__ = crawlers_api_schema
    __choices__ = ('error', 'id', 'job', 'siteName', 'status', 'url')


Int = sgqlc.types.Int

class JSON(sgqlc.types.Scalar):
    __schema__ = crawlers_api_schema


class JobPriorityType(sgqlc.types.Enum):
    __schema__ = crawlers_api_schema
    __choices__ = ('High', 'Highest', 'Low', 'Normal')


class JobSorting(sgqlc.types.Enum):
    __schema__ = crawlers_api_schema
    __choices__ = ('args', 'collectionStatus', 'crawlerName', 'creator', 'endTime', 'id', 'jobPriority', 'periodicJobId', 'projectName', 'queueTime', 'settings', 'startTime', 'systemRegistrationDate')


class JobStatus(sgqlc.types.Enum):
    __schema__ = crawlers_api_schema
    __choices__ = ('Finished', 'Paused', 'Pending', 'Running')


class LogLevel(sgqlc.types.Enum):
    __schema__ = crawlers_api_schema
    __choices__ = ('Critical', 'Debug', 'Error', 'Info', 'Trace', 'Warning')


class LogSorting(sgqlc.types.Enum):
    __schema__ = crawlers_api_schema
    __choices__ = ('level', 'timestamp')


class Long(sgqlc.types.Scalar):
    __schema__ = crawlers_api_schema


class MessagePriority(sgqlc.types.Enum):
    __schema__ = crawlers_api_schema
    __choices__ = ('Background', 'High', 'Normal', 'VeryHigh')


class MetricSorting(sgqlc.types.Enum):
    __schema__ = crawlers_api_schema
    __choices__ = ('timestamp',)


class MonitoringStatus(sgqlc.types.Enum):
    __schema__ = crawlers_api_schema
    __choices__ = ('Critical', 'Ok', 'Pending', 'SameItemsJob', 'SameItemsPeriodic', 'ZeroItemsZeroDuplicates')


class PeriodicJobSorting(sgqlc.types.Enum):
    __schema__ = crawlers_api_schema
    __choices__ = ('crawlerId', 'crawlerName', 'creator', 'credentialId', 'id', 'lastUpdater', 'name', 'nextScheduleTime', 'priority', 'projectId', 'projectName', 'status', 'systemRegistrationDate', 'systemUpdateDate')


class ProjectSorting(sgqlc.types.Enum):
    __schema__ = crawlers_api_schema
    __choices__ = ('creator', 'description', 'id', 'lastUpdater', 'name', 'systemRegistrationDate', 'systemUpdateDate', 'title')


class RecoveryJobSorting(sgqlc.types.Enum):
    __schema__ = crawlers_api_schema
    __choices__ = ('createdAt', 'endTime', 'id', 'progress', 'startTime', 'status', 'updatedAt')


class RecoveryJobStatus(sgqlc.types.Enum):
    __schema__ = crawlers_api_schema
    __choices__ = ('Canceled', 'Error', 'InProgress', 'Pending', 'Success')


class RequestSorting(sgqlc.types.Enum):
    __schema__ = crawlers_api_schema
    __choices__ = ('timestamp',)


class RunningStatus(sgqlc.types.Enum):
    __schema__ = crawlers_api_schema
    __choices__ = ('Disabled', 'Enabled')


class SettingsType(sgqlc.types.Enum):
    __schema__ = crawlers_api_schema
    __choices__ = ('array', 'boolean', 'float', 'int', 'object', 'string')


class SortDirection(sgqlc.types.Enum):
    __schema__ = crawlers_api_schema
    __choices__ = ('ascending', 'descending')


String = sgqlc.types.String

class TypeOfCrawl(sgqlc.types.Enum):
    __schema__ = crawlers_api_schema
    __choices__ = ('Actual', 'Retrospective')


class UnixTime(sgqlc.types.Scalar):
    __schema__ = crawlers_api_schema


class VersionSorting(sgqlc.types.Enum):
    __schema__ = crawlers_api_schema
    __choices__ = ('id', 'systemRegistrationDate', 'versionName')


class VersionStatus(sgqlc.types.Enum):
    __schema__ = crawlers_api_schema
    __choices__ = ('Active', 'Outdated', 'Removed')



########################################################################
# Input Objects
########################################################################
class AddCrawlStateInput(sgqlc.types.Input):
    __schema__ = crawlers_api_schema
    __field_names__ = ('state', 'cookie', 'parameters')
    state = sgqlc.types.Field(sgqlc.types.non_null(JSON), graphql_name='state')
    cookie = sgqlc.types.Field(JSON, graphql_name='cookie')
    parameters = sgqlc.types.Field(sgqlc.types.non_null('CrawlStateParameters'), graphql_name='parameters')


class AddRecoveryJobInput(sgqlc.types.Input):
    __schema__ = crawlers_api_schema
    __field_names__ = ('crawler_id', 'version_id')
    crawler_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='crawlerId')
    version_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='versionId')


class CancelJobInput(sgqlc.types.Input):
    __schema__ = crawlers_api_schema
    __field_names__ = ('ids', 'status')
    ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='ids')
    status = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(JobStatus)), graphql_name='status')


class CrawlStateFilterSettings(sgqlc.types.Input):
    __schema__ = crawlers_api_schema
    __field_names__ = ('input_value', 'crawler_ids', 'periodic_job_ids', 'credential_ids', 'information_source_ids', 'creator_ids', 'last_updater_ids', 'system_registration_date', 'system_update_date')
    input_value = sgqlc.types.Field(String, graphql_name='inputValue')
    crawler_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='crawlerIds')
    periodic_job_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='periodicJobIds')
    credential_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='credentialIds')
    information_source_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='informationSourceIds')
    creator_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='creatorIds')
    last_updater_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='lastUpdaterIds')
    system_registration_date = sgqlc.types.Field('TimestampInterval', graphql_name='systemRegistrationDate')
    system_update_date = sgqlc.types.Field('TimestampInterval', graphql_name='systemUpdateDate')


class CrawlStateParameters(sgqlc.types.Input):
    __schema__ = crawlers_api_schema
    __field_names__ = ('crawler_id', 'periodic_job_id', 'credential_id', 'information_source_id', 'crawl_key')
    crawler_id = sgqlc.types.Field(ID, graphql_name='crawlerId')
    periodic_job_id = sgqlc.types.Field(ID, graphql_name='periodicJobId')
    credential_id = sgqlc.types.Field(ID, graphql_name='credentialId')
    information_source_id = sgqlc.types.Field(ID, graphql_name='informationSourceId')
    crawl_key = sgqlc.types.Field(String, graphql_name='crawlKey')


class CrawlerFilterSettings(sgqlc.types.Input):
    __schema__ = crawlers_api_schema
    __field_names__ = ('input_value', 'projects', 'distribution_types', 'last_collection_date', 'creators', 'updaters', 'system_registration_date', 'system_update_date', 'have_active_versions', 'crawler_types')
    input_value = sgqlc.types.Field(String, graphql_name='inputValue')
    projects = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='projects')
    distribution_types = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(DistributionType)), graphql_name='distributionTypes')
    last_collection_date = sgqlc.types.Field('TimestampInterval', graphql_name='lastCollectionDate')
    creators = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='creators')
    updaters = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='updaters')
    system_registration_date = sgqlc.types.Field('TimestampInterval', graphql_name='systemRegistrationDate')
    system_update_date = sgqlc.types.Field('TimestampInterval', graphql_name='systemUpdateDate')
    have_active_versions = sgqlc.types.Field(Boolean, graphql_name='haveActiveVersions')
    crawler_types = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(CrawlerType)), graphql_name='crawlerTypes')


class CrawlerUpdateInput(sgqlc.types.Input):
    __schema__ = crawlers_api_schema
    __field_names__ = ('project_id', 'title', 'description', 'settings', 'args')
    project_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='projectId')
    title = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='title')
    description = sgqlc.types.Field(String, graphql_name='description')
    settings = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('KeyValueInputType'))), graphql_name='settings')
    args = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('KeyValueInputType'))), graphql_name='args')


class CredentialFilterSettings(sgqlc.types.Input):
    __schema__ = crawlers_api_schema
    __field_names__ = ('input_value', 'projects', 'status', 'data_type', 'creators', 'updaters', 'system_registration_date', 'system_update_date')
    input_value = sgqlc.types.Field(String, graphql_name='inputValue')
    projects = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='projects')
    status = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(CredentialStatus)), graphql_name='status')
    data_type = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(CredentialType)), graphql_name='dataType')
    creators = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='creators')
    updaters = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='updaters')
    system_registration_date = sgqlc.types.Field('TimestampInterval', graphql_name='systemRegistrationDate')
    system_update_date = sgqlc.types.Field('TimestampInterval', graphql_name='systemUpdateDate')


class CredentialInput(sgqlc.types.Input):
    __schema__ = crawlers_api_schema
    __field_names__ = ('projects', 'status', 'domain', 'description', 'data_type', 'login', 'password', 'token')
    projects = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='projects')
    status = sgqlc.types.Field(CredentialStatus, graphql_name='status')
    domain = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='domain')
    description = sgqlc.types.Field(String, graphql_name='description')
    data_type = sgqlc.types.Field(sgqlc.types.non_null(CredentialType), graphql_name='dataType')
    login = sgqlc.types.Field(String, graphql_name='login')
    password = sgqlc.types.Field(String, graphql_name='password')
    token = sgqlc.types.Field(String, graphql_name='token')


class InformationSourceFilterSettings(sgqlc.types.Input):
    __schema__ = crawlers_api_schema
    __field_names__ = ('information_source_id', 'input_value', 'status')
    information_source_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='informationSourceId')
    input_value = sgqlc.types.Field(String, graphql_name='inputValue')
    status = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(CollectionStatus)), graphql_name='status')


class InformationSourceLoaderFilterSettings(sgqlc.types.Input):
    __schema__ = crawlers_api_schema
    __field_names__ = ('input_value', 'type_of_crawl', 'status', 'creators', 'updaters', 'system_registration_date', 'system_update_date')
    input_value = sgqlc.types.Field(String, graphql_name='inputValue')
    type_of_crawl = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(TypeOfCrawl)), graphql_name='typeOfCrawl')
    status = sgqlc.types.Field(CollectionStatus, graphql_name='status')
    creators = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='creators')
    updaters = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='updaters')
    system_registration_date = sgqlc.types.Field('TimestampInterval', graphql_name='systemRegistrationDate')
    system_update_date = sgqlc.types.Field('TimestampInterval', graphql_name='systemUpdateDate')


class InformationSourceLoaderInput(sgqlc.types.Input):
    __schema__ = crawlers_api_schema
    __field_names__ = ('file_settings', 'urls', 'is_retrospective', 'retrospective_interval', 'running_status', 'actual_status')
    file_settings = sgqlc.types.Field('S3FileSettings', graphql_name='fileSettings')
    urls = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('KeyOptionValueInput')), graphql_name='urls')
    is_retrospective = sgqlc.types.Field(Boolean, graphql_name='isRetrospective')
    retrospective_interval = sgqlc.types.Field('TimestampInterval', graphql_name='retrospectiveInterval')
    running_status = sgqlc.types.Field(RunningStatus, graphql_name='runningStatus')
    actual_status = sgqlc.types.Field(InformationSourceLoaderActualStatus, graphql_name='actualStatus')


class JobInput(sgqlc.types.Input):
    __schema__ = crawlers_api_schema
    __field_names__ = ('crawler_id', 'version_id', 'credential_id', 'priority', 'message_priority', 'is_noise', 'research_map_id', 'external_search_loader_id', 'settings', 'args')
    crawler_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='crawlerId')
    version_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='versionId')
    credential_id = sgqlc.types.Field(ID, graphql_name='credentialId')
    priority = sgqlc.types.Field(sgqlc.types.non_null(JobPriorityType), graphql_name='priority')
    message_priority = sgqlc.types.Field(MessagePriority, graphql_name='messagePriority')
    is_noise = sgqlc.types.Field(Boolean, graphql_name='isNoise')
    research_map_id = sgqlc.types.Field(ID, graphql_name='researchMapId')
    external_search_loader_id = sgqlc.types.Field(ID, graphql_name='externalSearchLoaderId')
    settings = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('KeyValueInputType'))), graphql_name='settings')
    args = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('KeyValueInputType'))), graphql_name='args')


class JobsFilterSettings(sgqlc.types.Input):
    __schema__ = crawlers_api_schema
    __field_names__ = ('input_value', 'projects', 'crawlers', 'creators', 'updaters', 'system_registration_date', 'system_update_date', 'periodic_jobs', 'collection_statuses', 'job_statuses', 'job_ids', 'start_time', 'end_time')
    input_value = sgqlc.types.Field(String, graphql_name='inputValue')
    projects = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='projects')
    crawlers = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='crawlers')
    creators = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='creators')
    updaters = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='updaters')
    system_registration_date = sgqlc.types.Field('TimestampInterval', graphql_name='systemRegistrationDate')
    system_update_date = sgqlc.types.Field('TimestampInterval', graphql_name='systemUpdateDate')
    periodic_jobs = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='periodicJobs')
    collection_statuses = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(CollectionStatus)), graphql_name='collectionStatuses')
    job_statuses = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(JobStatus)), graphql_name='jobStatuses')
    job_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='jobIds')
    start_time = sgqlc.types.Field('TimestampInterval', graphql_name='startTime')
    end_time = sgqlc.types.Field('TimestampInterval', graphql_name='endTime')


class KeyOptionValueInput(sgqlc.types.Input):
    __schema__ = crawlers_api_schema
    __field_names__ = ('key', 'value')
    key = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='key')
    value = sgqlc.types.Field(String, graphql_name='value')


class KeyValueInputType(sgqlc.types.Input):
    __schema__ = crawlers_api_schema
    __field_names__ = ('key', 'value')
    key = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='key')
    value = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='value')


class LogFilterSettings(sgqlc.types.Input):
    __schema__ = crawlers_api_schema
    __field_names__ = ('input_text', 'levels', 'interval')
    input_text = sgqlc.types.Field(String, graphql_name='inputText')
    levels = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(LogLevel)), graphql_name='levels')
    interval = sgqlc.types.Field('TimestampInterval', graphql_name='interval')


class MetricFilterSettings(sgqlc.types.Input):
    __schema__ = crawlers_api_schema
    __field_names__ = ('input_text', 'interval')
    input_text = sgqlc.types.Field(String, graphql_name='inputText')
    interval = sgqlc.types.Field('TimestampInterval', graphql_name='interval')


class PeriodicJobFilterSettings(sgqlc.types.Input):
    __schema__ = crawlers_api_schema
    __field_names__ = ('input_value', 'projects', 'crawlers', 'priorities', 'running_statuses', 'creators', 'updaters', 'system_registration_date', 'system_update_date', 'next_schedule_time')
    input_value = sgqlc.types.Field(String, graphql_name='inputValue')
    projects = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='projects')
    crawlers = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='crawlers')
    priorities = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(JobPriorityType)), graphql_name='priorities')
    running_statuses = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(RunningStatus)), graphql_name='runningStatuses')
    creators = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='creators')
    updaters = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='updaters')
    system_registration_date = sgqlc.types.Field('TimestampInterval', graphql_name='systemRegistrationDate')
    system_update_date = sgqlc.types.Field('TimestampInterval', graphql_name='systemUpdateDate')
    next_schedule_time = sgqlc.types.Field('TimestampInterval', graphql_name='nextScheduleTime')


class PeriodicJobInput(sgqlc.types.Input):
    __schema__ = crawlers_api_schema
    __field_names__ = ('title', 'description', 'crawler_id', 'version_id', 'credential_id', 'status', 'priority', 'message_priority', 'cron_expression', 'cron_utcoffset_minutes', 'disable_time', 'settings', 'args', 'update_on_reload')
    title = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='title')
    description = sgqlc.types.Field(String, graphql_name='description')
    crawler_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='crawlerId')
    version_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='versionId')
    credential_id = sgqlc.types.Field(ID, graphql_name='credentialId')
    status = sgqlc.types.Field(RunningStatus, graphql_name='status')
    priority = sgqlc.types.Field(JobPriorityType, graphql_name='priority')
    message_priority = sgqlc.types.Field(MessagePriority, graphql_name='messagePriority')
    cron_expression = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='cronExpression')
    cron_utcoffset_minutes = sgqlc.types.Field(Int, graphql_name='cronUTCOffsetMinutes')
    disable_time = sgqlc.types.Field(UnixTime, graphql_name='disableTime')
    settings = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(KeyValueInputType))), graphql_name='settings')
    args = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(KeyValueInputType))), graphql_name='args')
    update_on_reload = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='updateOnReload')


class ProjectFilterSettings(sgqlc.types.Input):
    __schema__ = crawlers_api_schema
    __field_names__ = ('input_value', 'name', 'creators', 'updaters', 'system_registration_date', 'system_update_date')
    input_value = sgqlc.types.Field(String, graphql_name='inputValue')
    name = sgqlc.types.Field(String, graphql_name='name')
    creators = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='creators')
    updaters = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='updaters')
    system_registration_date = sgqlc.types.Field('TimestampInterval', graphql_name='systemRegistrationDate')
    system_update_date = sgqlc.types.Field('TimestampInterval', graphql_name='systemUpdateDate')


class ProjectInput(sgqlc.types.Input):
    __schema__ = crawlers_api_schema
    __field_names__ = ('title', 'name', 'description', 's3_file', 'settings', 'args')
    title = sgqlc.types.Field(String, graphql_name='title')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    description = sgqlc.types.Field(String, graphql_name='description')
    s3_file = sgqlc.types.Field('S3FileInput', graphql_name='s3File')
    settings = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(KeyValueInputType))), graphql_name='settings')
    args = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(KeyValueInputType))), graphql_name='args')


class RecoveryJobFilterSettings(sgqlc.types.Input):
    __schema__ = crawlers_api_schema
    __field_names__ = ('input_value', 'crawlers', 'statuses', 'start_time', 'end_time', 'creators', 'created_at', 'updaters', 'updated_at')
    input_value = sgqlc.types.Field(String, graphql_name='inputValue')
    crawlers = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='crawlers')
    statuses = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(RecoveryJobStatus)), graphql_name='statuses')
    start_time = sgqlc.types.Field('TimestampInterval', graphql_name='startTime')
    end_time = sgqlc.types.Field('TimestampInterval', graphql_name='endTime')
    creators = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='creators')
    created_at = sgqlc.types.Field('TimestampInterval', graphql_name='createdAt')
    updaters = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='updaters')
    updated_at = sgqlc.types.Field('TimestampInterval', graphql_name='updatedAt')


class RequestFilterSettings(sgqlc.types.Input):
    __schema__ = crawlers_api_schema
    __field_names__ = ('input_text', 'interval')
    input_text = sgqlc.types.Field(String, graphql_name='inputText')
    interval = sgqlc.types.Field('TimestampInterval', graphql_name='interval')


class S3FileInput(sgqlc.types.Input):
    __schema__ = crawlers_api_schema
    __field_names__ = ('bucket_name', 'object_name')
    bucket_name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='bucketName')
    object_name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='objectName')


class S3FileSettings(sgqlc.types.Input):
    __schema__ = crawlers_api_schema
    __field_names__ = ('s3_file', 'is_first_row_title', 'is_site_name_not_exist')
    s3_file = sgqlc.types.Field(sgqlc.types.non_null(S3FileInput), graphql_name='s3File')
    is_first_row_title = sgqlc.types.Field(Boolean, graphql_name='isFirstRowTitle')
    is_site_name_not_exist = sgqlc.types.Field(Boolean, graphql_name='isSiteNameNotExist')


class TimestampInterval(sgqlc.types.Input):
    __schema__ = crawlers_api_schema
    __field_names__ = ('start', 'end')
    start = sgqlc.types.Field(UnixTime, graphql_name='start')
    end = sgqlc.types.Field(UnixTime, graphql_name='end')


class UpdateCrawlStateInput(sgqlc.types.Input):
    __schema__ = crawlers_api_schema
    __field_names__ = ('state', 'cookie', 'state_version', 'credential_status')
    state = sgqlc.types.Field(sgqlc.types.non_null(JSON), graphql_name='state')
    cookie = sgqlc.types.Field(JSON, graphql_name='cookie')
    state_version = sgqlc.types.Field(sgqlc.types.non_null(Long), graphql_name='stateVersion')
    credential_status = sgqlc.types.Field(CredentialStatus, graphql_name='credentialStatus')


class VersionFilterSettings(sgqlc.types.Input):
    __schema__ = crawlers_api_schema
    __field_names__ = ('input_value', 'with_removed_versions')
    input_value = sgqlc.types.Field(String, graphql_name='inputValue')
    with_removed_versions = sgqlc.types.Field(Boolean, graphql_name='withRemovedVersions')



########################################################################
# Output Objects and Interfaces
########################################################################
class RecordInterface(sgqlc.types.Interface):
    __schema__ = crawlers_api_schema
    __field_names__ = ('system_registration_date', 'system_update_date', 'creator', 'last_updater')
    system_registration_date = sgqlc.types.Field(sgqlc.types.non_null(UnixTime), graphql_name='systemRegistrationDate')
    system_update_date = sgqlc.types.Field(UnixTime, graphql_name='systemUpdateDate')
    creator = sgqlc.types.Field(sgqlc.types.non_null('User'), graphql_name='creator')
    last_updater = sgqlc.types.Field('User', graphql_name='lastUpdater')


class ArgsAndSettingsDescription(sgqlc.types.Type):
    __schema__ = crawlers_api_schema
    __field_names__ = ('args', 'settings')
    args = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('SettingDescription')), graphql_name='args')
    settings = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('SettingDescription')), graphql_name='settings')


class CrawlStatePagination(sgqlc.types.Type):
    __schema__ = crawlers_api_schema
    __field_names__ = ('total', 'list_crawl_state')
    total = sgqlc.types.Field(sgqlc.types.non_null(Long), graphql_name='total')
    list_crawl_state = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('CrawlState'))), graphql_name='listCrawlState')


class CrawlerHistogram(sgqlc.types.Type):
    __schema__ = crawlers_api_schema
    __field_names__ = ('crawler_name', 'items_scraped_count', 'jobs_count', 'with_mistakes', 'error_job_count', 'canceled_job_count', 'successful_job_count')
    crawler_name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='crawlerName')
    items_scraped_count = sgqlc.types.Field(Long, graphql_name='itemsScrapedCount')
    jobs_count = sgqlc.types.Field(Int, graphql_name='jobsCount')
    with_mistakes = sgqlc.types.Field(Int, graphql_name='withMistakes')
    error_job_count = sgqlc.types.Field(Int, graphql_name='errorJobCount')
    canceled_job_count = sgqlc.types.Field(Int, graphql_name='canceledJobCount')
    successful_job_count = sgqlc.types.Field(Int, graphql_name='successfulJobCount')


class CrawlerPagination(sgqlc.types.Type):
    __schema__ = crawlers_api_schema
    __field_names__ = ('total', 'list_crawler')
    total = sgqlc.types.Field(sgqlc.types.non_null(Long), graphql_name='total')
    list_crawler = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('Crawler'))), graphql_name='listCrawler')


class CrawlerStats(sgqlc.types.Type):
    __schema__ = crawlers_api_schema
    __field_names__ = ('items_scraped_count', 'next_schedule_time', 'total_time', 'items_scraped_count_last', 'avg_performance_time', 'last_collection_date')
    items_scraped_count = sgqlc.types.Field(Long, graphql_name='itemsScrapedCount')
    next_schedule_time = sgqlc.types.Field(UnixTime, graphql_name='nextScheduleTime')
    total_time = sgqlc.types.Field(Long, graphql_name='totalTime')
    items_scraped_count_last = sgqlc.types.Field(Long, graphql_name='itemsScrapedCountLast')
    avg_performance_time = sgqlc.types.Field(Long, graphql_name='avgPerformanceTime')
    last_collection_date = sgqlc.types.Field(UnixTime, graphql_name='lastCollectionDate')


class CredentialPagination(sgqlc.types.Type):
    __schema__ = crawlers_api_schema
    __field_names__ = ('total', 'list_credential')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')
    list_credential = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('Credential'))), graphql_name='listCredential')


class DateHistogramBucket(sgqlc.types.Type):
    __schema__ = crawlers_api_schema
    __field_names__ = ('date', 'timestamp', 'doc_count')
    date = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='date')
    timestamp = sgqlc.types.Field(sgqlc.types.non_null(Long), graphql_name='timestamp')
    doc_count = sgqlc.types.Field(sgqlc.types.non_null(Long), graphql_name='docCount')


class Event(sgqlc.types.Type):
    __schema__ = crawlers_api_schema
    __field_names__ = ('id', 'target', 'message', 'is_read')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    target = sgqlc.types.Field(sgqlc.types.non_null(EventTarget), graphql_name='target')
    message = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='message')
    is_read = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isRead')


class InformationSource(sgqlc.types.Type):
    __schema__ = crawlers_api_schema
    __field_names__ = ('id', 'url', 'site_name', 'status', 'error_message', 'crawler', 'periodic_job', 'job', 'version')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    url = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='url')
    site_name = sgqlc.types.Field(String, graphql_name='siteName')
    status = sgqlc.types.Field(sgqlc.types.non_null(CollectionStatus), graphql_name='status')
    error_message = sgqlc.types.Field(String, graphql_name='errorMessage')
    crawler = sgqlc.types.Field('Crawler', graphql_name='crawler')
    periodic_job = sgqlc.types.Field('PeriodicJob', graphql_name='periodicJob')
    job = sgqlc.types.Field('Job', graphql_name='job')
    version = sgqlc.types.Field('Version', graphql_name='version')


class InformationSourceLoaderFileTitle(sgqlc.types.Type):
    __schema__ = crawlers_api_schema
    __field_names__ = ('title',)
    title = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='title')


class InformationSourceLoaderPagination(sgqlc.types.Type):
    __schema__ = crawlers_api_schema
    __field_names__ = ('list_information_source_loader', 'total')
    list_information_source_loader = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('InformationSourceLoader'))), graphql_name='listInformationSourceLoader')
    total = sgqlc.types.Field(sgqlc.types.non_null(Long), graphql_name='total')


class InformationSourceLoaderStats(sgqlc.types.Type):
    __schema__ = crawlers_api_schema
    __field_names__ = ('total_source_count', 'finished_source_count')
    total_source_count = sgqlc.types.Field(sgqlc.types.non_null(Long), graphql_name='totalSourceCount')
    finished_source_count = sgqlc.types.Field(sgqlc.types.non_null(Long), graphql_name='finishedSourceCount')


class InformationSourceLoaderURLTitle(sgqlc.types.Type):
    __schema__ = crawlers_api_schema
    __field_names__ = ('title', 'source_count')
    title = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='title')
    source_count = sgqlc.types.Field(sgqlc.types.non_null(Long), graphql_name='sourceCount')


class InformationSourcePagination(sgqlc.types.Type):
    __schema__ = crawlers_api_schema
    __field_names__ = ('total', 'list_information_source')
    total = sgqlc.types.Field(sgqlc.types.non_null(Long), graphql_name='total')
    list_information_source = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(InformationSource))), graphql_name='listInformationSource')


class JobMetrics(sgqlc.types.Type):
    __schema__ = crawlers_api_schema
    __field_names__ = ('job_id',)
    job_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='jobId')


class JobPagination(sgqlc.types.Type):
    __schema__ = crawlers_api_schema
    __field_names__ = ('total', 'list_job')
    total = sgqlc.types.Field(sgqlc.types.non_null(Long), graphql_name='total')
    list_job = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('Job'))), graphql_name='listJob')


class JobStats(sgqlc.types.Type):
    __schema__ = crawlers_api_schema
    __field_names__ = ('jobs_count', 'total_time', 'items_scraped_count', 'requests_count', 'errors_count', 'duplicated_request_count', 'with_mistakes', 'error_job_count', 'successful_job_count', 'canceled_job_count')
    jobs_count = sgqlc.types.Field(Int, graphql_name='jobsCount')
    total_time = sgqlc.types.Field(Long, graphql_name='totalTime')
    items_scraped_count = sgqlc.types.Field(Long, graphql_name='itemsScrapedCount')
    requests_count = sgqlc.types.Field(Long, graphql_name='requestsCount')
    errors_count = sgqlc.types.Field(Int, graphql_name='errorsCount')
    duplicated_request_count = sgqlc.types.Field(Int, graphql_name='duplicatedRequestCount')
    with_mistakes = sgqlc.types.Field(Int, graphql_name='withMistakes')
    error_job_count = sgqlc.types.Field(Int, graphql_name='errorJobCount')
    successful_job_count = sgqlc.types.Field(Int, graphql_name='successfulJobCount')
    canceled_job_count = sgqlc.types.Field(Int, graphql_name='canceledJobCount')


class JobSubscription(sgqlc.types.Type):
    __schema__ = crawlers_api_schema
    __field_names__ = ('job', 'position')
    job = sgqlc.types.Field(sgqlc.types.non_null('Job'), graphql_name='job')
    position = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='position')


class KeyValue(sgqlc.types.Type):
    __schema__ = crawlers_api_schema
    __field_names__ = ('key', 'value')
    key = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='key')
    value = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='value')


class Log(sgqlc.types.Type):
    __schema__ = crawlers_api_schema
    __field_names__ = ('job_id', 'timestamp', 'level', 'message', 'logger_name', 'stack_trace')
    job_id = sgqlc.types.Field(String, graphql_name='jobId')
    timestamp = sgqlc.types.Field(sgqlc.types.non_null(UnixTime), graphql_name='timestamp')
    level = sgqlc.types.Field(sgqlc.types.non_null(LogLevel), graphql_name='level')
    message = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='message')
    logger_name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='loggerName')
    stack_trace = sgqlc.types.Field(String, graphql_name='stackTrace')


class LogPagination(sgqlc.types.Type):
    __schema__ = crawlers_api_schema
    __field_names__ = ('total', 'list_log')
    total = sgqlc.types.Field(sgqlc.types.non_null(Long), graphql_name='total')
    list_log = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(Log))), graphql_name='listLog')


class Metric(sgqlc.types.Type):
    __schema__ = crawlers_api_schema
    __field_names__ = ('job_id', 'timestamp', 'metric')
    job_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='jobId')
    timestamp = sgqlc.types.Field(sgqlc.types.non_null(UnixTime), graphql_name='timestamp')
    metric = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='metric')


class MetricPagination(sgqlc.types.Type):
    __schema__ = crawlers_api_schema
    __field_names__ = ('total', 'list_metric')
    total = sgqlc.types.Field(sgqlc.types.non_null(Long), graphql_name='total')
    list_metric = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(Metric))), graphql_name='listMetric')


class Mutation(sgqlc.types.Type):
    __schema__ = crawlers_api_schema
    __field_names__ = ('update_crawler', 'update_crawler_settings_arguments', 'delete_crawler_versions', 'delete_crawlers', 'update_site_map_crawler_body', 'add_crawl_state', 'update_crawl_state', 'delete_crawl_state', 'add_credential', 'update_credential', 'delete_credential', 'add_job', 'delete_job', 'cancel_job', 'suspend_job', 'resume_job', 'download_pending_jobs', 'schedule_uploaded_jobs', 'restart_job', 'add_periodic_job', 'run_periodic_jobs', 'update_enable_jobs_scheduling', 'update_disable_jobs_scheduling', 'delete_periodic_job', 'update_periodic_job', 'update_periodic_job_settings_and_arguments', 'import_periodic_jobs', 'delete_project', 'delete_project_versions', 'add_project', 'update_project', 'update_project_settings_and_arguments', 'add_information_source_loader', 'delete_information_source_loader', 'update_enable_information_source_loader', 'update_disable_information_source_loader', 'add_recovery_job', 'cancel_recovery_job')
    update_crawler = sgqlc.types.Field(sgqlc.types.non_null('Crawler'), graphql_name='updateCrawler', args=sgqlc.types.ArgDict((
        ('crawler_update_input', sgqlc.types.Arg(sgqlc.types.non_null(CrawlerUpdateInput), graphql_name='crawlerUpdateInput', default=None)),
        ('crawler_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='crawlerId', default=None)),
        ('project_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='projectId', default=None)),
))
    )
    update_crawler_settings_arguments = sgqlc.types.Field(sgqlc.types.non_null('Crawler'), graphql_name='updateCrawlerSettingsArguments', args=sgqlc.types.ArgDict((
        ('crawler_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='crawlerId', default=None)),
        ('settings', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(KeyValueInputType))), graphql_name='settings', default=None)),
        ('args', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(KeyValueInputType))), graphql_name='args', default=None)),
))
    )
    delete_crawler_versions = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='deleteCrawlerVersions', args=sgqlc.types.ArgDict((
        ('crawler_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='crawlerId', default=None)),
        ('version_ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='versionIds', default=None)),
))
    )
    delete_crawlers = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='deleteCrawlers', args=sgqlc.types.ArgDict((
        ('ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='ids', default=None)),
))
    )
    update_site_map_crawler_body = sgqlc.types.Field(sgqlc.types.non_null('Crawler'), graphql_name='updateSiteMapCrawlerBody', args=sgqlc.types.ArgDict((
        ('crawler_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='crawlerId', default=None)),
        ('project_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='projectId', default=None)),
        ('json', sgqlc.types.Arg(sgqlc.types.non_null(JSON), graphql_name='json', default=None)),
))
    )
    add_crawl_state = sgqlc.types.Field(sgqlc.types.non_null('CrawlState'), graphql_name='addCrawlState', args=sgqlc.types.ArgDict((
        ('add_crawl_state_input', sgqlc.types.Arg(sgqlc.types.non_null(AddCrawlStateInput), graphql_name='addCrawlStateInput', default=None)),
))
    )
    update_crawl_state = sgqlc.types.Field(sgqlc.types.non_null('CrawlState'), graphql_name='updateCrawlState', args=sgqlc.types.ArgDict((
        ('crawl_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='crawlId', default=None)),
        ('update_crawl_state_input', sgqlc.types.Arg(sgqlc.types.non_null(UpdateCrawlStateInput), graphql_name='updateCrawlStateInput', default=None)),
))
    )
    delete_crawl_state = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='deleteCrawlState', args=sgqlc.types.ArgDict((
        ('crawl_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='crawlId', default=None)),
))
    )
    add_credential = sgqlc.types.Field(sgqlc.types.non_null('Credential'), graphql_name='addCredential', args=sgqlc.types.ArgDict((
        ('credential_input', sgqlc.types.Arg(sgqlc.types.non_null(CredentialInput), graphql_name='credentialInput', default=None)),
))
    )
    update_credential = sgqlc.types.Field(sgqlc.types.non_null('Credential'), graphql_name='updateCredential', args=sgqlc.types.ArgDict((
        ('credential_input', sgqlc.types.Arg(sgqlc.types.non_null(CredentialInput), graphql_name='credentialInput', default=None)),
        ('version', sgqlc.types.Arg(sgqlc.types.non_null(Int), graphql_name='version', default=None)),
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    delete_credential = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='deleteCredential', args=sgqlc.types.ArgDict((
        ('ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='ids', default=None)),
))
    )
    add_job = sgqlc.types.Field(sgqlc.types.non_null('Job'), graphql_name='addJob', args=sgqlc.types.ArgDict((
        ('job_input', sgqlc.types.Arg(sgqlc.types.non_null(JobInput), graphql_name='jobInput', default=None)),
))
    )
    delete_job = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='deleteJob', args=sgqlc.types.ArgDict((
        ('ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='ids', default=None)),
))
    )
    cancel_job = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='cancelJob', args=sgqlc.types.ArgDict((
        ('cancel_job_input', sgqlc.types.Arg(CancelJobInput, graphql_name='cancelJobInput', default={'ids': (), 'status': ()})),
))
    )
    suspend_job = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='suspendJob', args=sgqlc.types.ArgDict((
        ('ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='ids', default=None)),
))
    )
    resume_job = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='resumeJob', args=sgqlc.types.ArgDict((
        ('ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='ids', default=None)),
))
    )
    download_pending_jobs = sgqlc.types.Field(sgqlc.types.non_null(JSON), graphql_name='downloadPendingJobs')
    schedule_uploaded_jobs = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('Job'))), graphql_name='scheduleUploadedJobs', args=sgqlc.types.ArgDict((
        ('s3_file_input', sgqlc.types.Arg(sgqlc.types.non_null(S3FileInput), graphql_name='s3FileInput', default=None)),
))
    )
    restart_job = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('Job'))), graphql_name='restartJob', args=sgqlc.types.ArgDict((
        ('ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='ids', default=None)),
))
    )
    add_periodic_job = sgqlc.types.Field(sgqlc.types.non_null('PeriodicJob'), graphql_name='addPeriodicJob', args=sgqlc.types.ArgDict((
        ('periodic_job_input', sgqlc.types.Arg(sgqlc.types.non_null(PeriodicJobInput), graphql_name='periodicJobInput', default=None)),
))
    )
    run_periodic_jobs = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('Job'))), graphql_name='runPeriodicJobs', args=sgqlc.types.ArgDict((
        ('periodic_job_ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='periodicJobIds', default=None)),
))
    )
    update_enable_jobs_scheduling = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('PeriodicJob'))), graphql_name='updateEnableJobsScheduling', args=sgqlc.types.ArgDict((
        ('ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='ids', default=None)),
))
    )
    update_disable_jobs_scheduling = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('PeriodicJob'))), graphql_name='updateDisableJobsScheduling', args=sgqlc.types.ArgDict((
        ('ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='ids', default=None)),
))
    )
    delete_periodic_job = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='deletePeriodicJob', args=sgqlc.types.ArgDict((
        ('ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='ids', default=None)),
))
    )
    update_periodic_job = sgqlc.types.Field(sgqlc.types.non_null('PeriodicJob'), graphql_name='updatePeriodicJob', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
        ('periodic_job_input', sgqlc.types.Arg(sgqlc.types.non_null(PeriodicJobInput), graphql_name='periodicJobInput', default=None)),
))
    )
    update_periodic_job_settings_and_arguments = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='updatePeriodicJobSettingsAndArguments', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
        ('settings', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(KeyValueInputType))), graphql_name='settings', default=None)),
        ('args', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(KeyValueInputType))), graphql_name='args', default=None)),
))
    )
    import_periodic_jobs = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='importPeriodicJobs', args=sgqlc.types.ArgDict((
        ('s3_file_input', sgqlc.types.Arg(sgqlc.types.non_null(S3FileInput), graphql_name='s3FileInput', default=None)),
))
    )
    delete_project = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='deleteProject', args=sgqlc.types.ArgDict((
        ('ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='ids', default=None)),
))
    )
    delete_project_versions = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='deleteProjectVersions', args=sgqlc.types.ArgDict((
        ('project_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='projectId', default=None)),
        ('ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='ids', default=None)),
))
    )
    add_project = sgqlc.types.Field(sgqlc.types.non_null('Project'), graphql_name='addProject', args=sgqlc.types.ArgDict((
        ('project_input', sgqlc.types.Arg(sgqlc.types.non_null(ProjectInput), graphql_name='projectInput', default=None)),
))
    )
    update_project = sgqlc.types.Field(sgqlc.types.non_null('Project'), graphql_name='updateProject', args=sgqlc.types.ArgDict((
        ('project_input', sgqlc.types.Arg(sgqlc.types.non_null(ProjectInput), graphql_name='projectInput', default=None)),
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    update_project_settings_and_arguments = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='updateProjectSettingsAndArguments', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
        ('settings', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(KeyValueInputType))), graphql_name='settings', default=None)),
        ('args', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(KeyValueInputType))), graphql_name='args', default=None)),
))
    )
    add_information_source_loader = sgqlc.types.Field(sgqlc.types.non_null('InformationSourceLoader'), graphql_name='addInformationSourceLoader', args=sgqlc.types.ArgDict((
        ('information_source_loader_input', sgqlc.types.Arg(sgqlc.types.non_null(InformationSourceLoaderInput), graphql_name='informationSourceLoaderInput', default=None)),
))
    )
    delete_information_source_loader = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='deleteInformationSourceLoader', args=sgqlc.types.ArgDict((
        ('ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='ids', default=None)),
))
    )
    update_enable_information_source_loader = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='updateEnableInformationSourceLoader', args=sgqlc.types.ArgDict((
        ('ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='ids', default=None)),
))
    )
    update_disable_information_source_loader = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='updateDisableInformationSourceLoader', args=sgqlc.types.ArgDict((
        ('ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='ids', default=None)),
))
    )
    add_recovery_job = sgqlc.types.Field(sgqlc.types.non_null('RecoveryJob'), graphql_name='addRecoveryJob', args=sgqlc.types.ArgDict((
        ('add_recovery_job_input', sgqlc.types.Arg(sgqlc.types.non_null(AddRecoveryJobInput), graphql_name='addRecoveryJobInput', default=None)),
))
    )
    cancel_recovery_job = sgqlc.types.Field(sgqlc.types.non_null('RecoveryJob'), graphql_name='cancelRecoveryJob', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )


class PeriodicJobMetrics(sgqlc.types.Type):
    __schema__ = crawlers_api_schema
    __field_names__ = ('periodic_job_id',)
    periodic_job_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='periodicJobId')


class PeriodicJobPagination(sgqlc.types.Type):
    __schema__ = crawlers_api_schema
    __field_names__ = ('total', 'list_periodic_job')
    total = sgqlc.types.Field(sgqlc.types.non_null(Long), graphql_name='total')
    list_periodic_job = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('PeriodicJob'))), graphql_name='listPeriodicJob')


class Platform(sgqlc.types.Type):
    __schema__ = crawlers_api_schema
    __field_names__ = ('id',)
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')


class ProjectHistogram(sgqlc.types.Type):
    __schema__ = crawlers_api_schema
    __field_names__ = ('project_name', 'items_scraped_count', 'jobs_count', 'error_job_count', 'with_mistakes', 'canceled_job_count', 'successful_job_count')
    project_name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='projectName')
    items_scraped_count = sgqlc.types.Field(Long, graphql_name='itemsScrapedCount')
    jobs_count = sgqlc.types.Field(Int, graphql_name='jobsCount')
    error_job_count = sgqlc.types.Field(Int, graphql_name='errorJobCount')
    with_mistakes = sgqlc.types.Field(Int, graphql_name='withMistakes')
    canceled_job_count = sgqlc.types.Field(Int, graphql_name='canceledJobCount')
    successful_job_count = sgqlc.types.Field(Int, graphql_name='successfulJobCount')


class ProjectPagination(sgqlc.types.Type):
    __schema__ = crawlers_api_schema
    __field_names__ = ('total', 'list_project')
    total = sgqlc.types.Field(sgqlc.types.non_null(Long), graphql_name='total')
    list_project = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('Project'))), graphql_name='listProject')


class ProjectStats(sgqlc.types.Type):
    __schema__ = crawlers_api_schema
    __field_names__ = ('items_scraped_count', 'errors_count', 'jobs_count', 'with_mistakes', 'error_job_count', 'successful_job_count', 'canceled_job_count')
    items_scraped_count = sgqlc.types.Field(Long, graphql_name='itemsScrapedCount')
    errors_count = sgqlc.types.Field(Int, graphql_name='errorsCount')
    jobs_count = sgqlc.types.Field(Int, graphql_name='jobsCount')
    with_mistakes = sgqlc.types.Field(Int, graphql_name='withMistakes')
    error_job_count = sgqlc.types.Field(Int, graphql_name='errorJobCount')
    successful_job_count = sgqlc.types.Field(Int, graphql_name='successfulJobCount')
    canceled_job_count = sgqlc.types.Field(Int, graphql_name='canceledJobCount')


class Query(sgqlc.types.Type):
    __schema__ = crawlers_api_schema
    __field_names__ = ('analytics', 'event_materializer', 'crawler', 'list_crawler', 'pagination_crawler', 'crawler_args_and_settings_description', 'crawler_site_map', 'crawler_by_information_source', 'crawl_state', 'crawl_state_by_parameters', 'pagination_crawl_state', 'credential', 'pagination_credential', 'job', 'list_job', 'pagination_job_logs', 'pagination_job_requests', 'pagination_job_metrics', 'pagination_job', 'periodic_job', 'pagination_periodic_job', 'pagination_periodic_job_logs', 'pagination_periodic_job_requests', 'pagination_periodic_job_metrics', 'check_periodic_job_by_input', 'export_periodic_jobs', 'project', 'pagination_project', 'project_args_and_settings_description', 'project_default_args_and_settings_description', 'information_source_loader', 'pagination_information_source_loader', 'information_source', 'pagination_information_source', 'recovery_job', 'pagination_recovery_job', 'version', 'list_version', 'pagination_versions_crawler', 'pagination_egg_file_versions_project')
    analytics = sgqlc.types.Field(sgqlc.types.non_null('Stats'), graphql_name='analytics')
    event_materializer = sgqlc.types.Field(Event, graphql_name='eventMaterializer')
    crawler = sgqlc.types.Field(sgqlc.types.non_null('Crawler'), graphql_name='crawler', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    list_crawler = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of('Crawler')), graphql_name='listCrawler', args=sgqlc.types.ArgDict((
        ('ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='ids', default=None)),
))
    )
    pagination_crawler = sgqlc.types.Field(sgqlc.types.non_null(CrawlerPagination), graphql_name='paginationCrawler', args=sgqlc.types.ArgDict((
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('filter_settings', sgqlc.types.Arg(CrawlerFilterSettings, graphql_name='filterSettings', default={})),
        ('sort_field', sgqlc.types.Arg(CrawlerSorting, graphql_name='sortField', default='id')),
        ('direction', sgqlc.types.Arg(SortDirection, graphql_name='direction', default='descending')),
))
    )
    crawler_args_and_settings_description = sgqlc.types.Field(sgqlc.types.non_null(ArgsAndSettingsDescription), graphql_name='crawlerArgsAndSettingsDescription', args=sgqlc.types.ArgDict((
        ('crawler_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='crawlerId', default=None)),
        ('version_id', sgqlc.types.Arg(ID, graphql_name='versionId', default=None)),
))
    )
    crawler_site_map = sgqlc.types.Field(sgqlc.types.non_null(JSON), graphql_name='crawlerSiteMap', args=sgqlc.types.ArgDict((
        ('crawler_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='crawlerId', default=None)),
        ('version_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='versionId', default=None)),
))
    )
    crawler_by_information_source = sgqlc.types.Field(sgqlc.types.non_null('Crawler'), graphql_name='crawlerByInformationSource', args=sgqlc.types.ArgDict((
        ('source', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='source', default=None)),
        ('crawler_type', sgqlc.types.Arg(sgqlc.types.non_null(CrawlerType), graphql_name='crawlerType', default=None)),
))
    )
    crawl_state = sgqlc.types.Field(sgqlc.types.non_null('CrawlState'), graphql_name='crawlState', args=sgqlc.types.ArgDict((
        ('crawl_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='crawlId', default=None)),
))
    )
    crawl_state_by_parameters = sgqlc.types.Field(sgqlc.types.non_null('CrawlState'), graphql_name='crawlStateByParameters', args=sgqlc.types.ArgDict((
        ('crawl_state_parameters', sgqlc.types.Arg(sgqlc.types.non_null(CrawlStateParameters), graphql_name='crawlStateParameters', default=None)),
))
    )
    pagination_crawl_state = sgqlc.types.Field(sgqlc.types.non_null(CrawlStatePagination), graphql_name='paginationCrawlState', args=sgqlc.types.ArgDict((
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('filter_settings', sgqlc.types.Arg(CrawlStateFilterSettings, graphql_name='filterSettings', default={})),
        ('sort_field', sgqlc.types.Arg(CrawlStateSorting, graphql_name='sortField', default='id')),
        ('direction', sgqlc.types.Arg(SortDirection, graphql_name='direction', default='descending')),
))
    )
    credential = sgqlc.types.Field(sgqlc.types.non_null('Credential'), graphql_name='credential', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    pagination_credential = sgqlc.types.Field(sgqlc.types.non_null(CredentialPagination), graphql_name='paginationCredential', args=sgqlc.types.ArgDict((
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('sort_field', sgqlc.types.Arg(CredentialSorting, graphql_name='sortField', default='id')),
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(CredentialFilterSettings), graphql_name='filterSettings', default=None)),
        ('direction', sgqlc.types.Arg(SortDirection, graphql_name='direction', default='descending')),
))
    )
    job = sgqlc.types.Field(sgqlc.types.non_null('Job'), graphql_name='job', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    list_job = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of('Job')), graphql_name='listJob', args=sgqlc.types.ArgDict((
        ('ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='ids', default=None)),
))
    )
    pagination_job_logs = sgqlc.types.Field(sgqlc.types.non_null(LogPagination), graphql_name='paginationJobLogs', args=sgqlc.types.ArgDict((
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
        ('filter_settings', sgqlc.types.Arg(LogFilterSettings, graphql_name='filterSettings', default={})),
        ('direction', sgqlc.types.Arg(SortDirection, graphql_name='direction', default='descending')),
        ('sort_field', sgqlc.types.Arg(LogSorting, graphql_name='sortField', default='timestamp')),
))
    )
    pagination_job_requests = sgqlc.types.Field(sgqlc.types.non_null('RequestPagination'), graphql_name='paginationJobRequests', args=sgqlc.types.ArgDict((
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
        ('filter_settings', sgqlc.types.Arg(RequestFilterSettings, graphql_name='filterSettings', default={})),
        ('direction', sgqlc.types.Arg(SortDirection, graphql_name='direction', default='descending')),
        ('sort_field', sgqlc.types.Arg(RequestSorting, graphql_name='sortField', default='timestamp')),
))
    )
    pagination_job_metrics = sgqlc.types.Field(sgqlc.types.non_null(MetricPagination), graphql_name='paginationJobMetrics', args=sgqlc.types.ArgDict((
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
        ('filter_settings', sgqlc.types.Arg(MetricFilterSettings, graphql_name='filterSettings', default={})),
        ('direction', sgqlc.types.Arg(SortDirection, graphql_name='direction', default='descending')),
        ('sort_field', sgqlc.types.Arg(MetricSorting, graphql_name='sortField', default='timestamp')),
))
    )
    pagination_job = sgqlc.types.Field(sgqlc.types.non_null(JobPagination), graphql_name='paginationJob', args=sgqlc.types.ArgDict((
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('jobs_filter_settings', sgqlc.types.Arg(JobsFilterSettings, graphql_name='jobsFilterSettings', default={})),
        ('sort_field', sgqlc.types.Arg(JobSorting, graphql_name='sortField', default='id')),
        ('direction', sgqlc.types.Arg(SortDirection, graphql_name='direction', default='descending')),
))
    )
    periodic_job = sgqlc.types.Field(sgqlc.types.non_null('PeriodicJob'), graphql_name='periodicJob', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    pagination_periodic_job = sgqlc.types.Field(sgqlc.types.non_null(PeriodicJobPagination), graphql_name='paginationPeriodicJob', args=sgqlc.types.ArgDict((
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('filter_settings', sgqlc.types.Arg(PeriodicJobFilterSettings, graphql_name='filterSettings', default={})),
        ('sort_field', sgqlc.types.Arg(PeriodicJobSorting, graphql_name='sortField', default='id')),
        ('direction', sgqlc.types.Arg(SortDirection, graphql_name='direction', default='descending')),
))
    )
    pagination_periodic_job_logs = sgqlc.types.Field(sgqlc.types.non_null(LogPagination), graphql_name='paginationPeriodicJobLogs', args=sgqlc.types.ArgDict((
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
        ('filter_settings', sgqlc.types.Arg(LogFilterSettings, graphql_name='filterSettings', default={})),
        ('direction', sgqlc.types.Arg(SortDirection, graphql_name='direction', default='descending')),
        ('sort_field', sgqlc.types.Arg(LogSorting, graphql_name='sortField', default='timestamp')),
))
    )
    pagination_periodic_job_requests = sgqlc.types.Field(sgqlc.types.non_null('RequestPagination'), graphql_name='paginationPeriodicJobRequests', args=sgqlc.types.ArgDict((
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
        ('filter_settings', sgqlc.types.Arg(RequestFilterSettings, graphql_name='filterSettings', default={})),
        ('direction', sgqlc.types.Arg(SortDirection, graphql_name='direction', default='descending')),
        ('sort_field', sgqlc.types.Arg(RequestSorting, graphql_name='sortField', default='timestamp')),
))
    )
    pagination_periodic_job_metrics = sgqlc.types.Field(sgqlc.types.non_null(MetricPagination), graphql_name='paginationPeriodicJobMetrics', args=sgqlc.types.ArgDict((
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
        ('filter_settings', sgqlc.types.Arg(MetricFilterSettings, graphql_name='filterSettings', default={})),
        ('direction', sgqlc.types.Arg(SortDirection, graphql_name='direction', default='descending')),
        ('sort_field', sgqlc.types.Arg(MetricSorting, graphql_name='sortField', default='timestamp')),
))
    )
    check_periodic_job_by_input = sgqlc.types.Field('PeriodicJob', graphql_name='checkPeriodicJobByInput', args=sgqlc.types.ArgDict((
        ('periodic_job_input', sgqlc.types.Arg(sgqlc.types.non_null(PeriodicJobInput), graphql_name='periodicJobInput', default=None)),
))
    )
    export_periodic_jobs = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='exportPeriodicJobs', args=sgqlc.types.ArgDict((
        ('ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='ids', default=None)),
        ('filter_settings', sgqlc.types.Arg(PeriodicJobFilterSettings, graphql_name='filterSettings', default={})),
))
    )
    project = sgqlc.types.Field(sgqlc.types.non_null('Project'), graphql_name='project', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    pagination_project = sgqlc.types.Field(sgqlc.types.non_null(ProjectPagination), graphql_name='paginationProject', args=sgqlc.types.ArgDict((
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('sort_field', sgqlc.types.Arg(ProjectSorting, graphql_name='sortField', default='id')),
        ('filter_settings', sgqlc.types.Arg(ProjectFilterSettings, graphql_name='filterSettings', default={})),
        ('direction', sgqlc.types.Arg(SortDirection, graphql_name='direction', default='descending')),
))
    )
    project_args_and_settings_description = sgqlc.types.Field(sgqlc.types.non_null(ArgsAndSettingsDescription), graphql_name='projectArgsAndSettingsDescription', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
        ('version_id', sgqlc.types.Arg(ID, graphql_name='versionId', default=None)),
))
    )
    project_default_args_and_settings_description = sgqlc.types.Field(sgqlc.types.non_null(ArgsAndSettingsDescription), graphql_name='projectDefaultArgsAndSettingsDescription')
    information_source_loader = sgqlc.types.Field(sgqlc.types.non_null('InformationSourceLoader'), graphql_name='informationSourceLoader', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    pagination_information_source_loader = sgqlc.types.Field(sgqlc.types.non_null(InformationSourceLoaderPagination), graphql_name='paginationInformationSourceLoader', args=sgqlc.types.ArgDict((
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('filter_settings', sgqlc.types.Arg(InformationSourceLoaderFilterSettings, graphql_name='filterSettings', default={})),
        ('sort_field', sgqlc.types.Arg(InformationSourceLoaderSorting, graphql_name='sortField', default='id')),
        ('direction', sgqlc.types.Arg(SortDirection, graphql_name='direction', default='descending')),
))
    )
    information_source = sgqlc.types.Field(sgqlc.types.non_null(InformationSource), graphql_name='informationSource', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    pagination_information_source = sgqlc.types.Field(sgqlc.types.non_null(InformationSourcePagination), graphql_name='paginationInformationSource', args=sgqlc.types.ArgDict((
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(InformationSourceFilterSettings), graphql_name='filterSettings', default=None)),
        ('sort_field', sgqlc.types.Arg(InformationSourceSorting, graphql_name='sortField', default='id')),
        ('direction', sgqlc.types.Arg(SortDirection, graphql_name='direction', default='descending')),
))
    )
    recovery_job = sgqlc.types.Field(sgqlc.types.non_null('RecoveryJob'), graphql_name='recoveryJob', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    pagination_recovery_job = sgqlc.types.Field(sgqlc.types.non_null('RecoveryJobPagination'), graphql_name='paginationRecoveryJob', args=sgqlc.types.ArgDict((
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('filter_settings', sgqlc.types.Arg(RecoveryJobFilterSettings, graphql_name='filterSettings', default={})),
        ('sort_field', sgqlc.types.Arg(RecoveryJobSorting, graphql_name='sortField', default='id')),
        ('direction', sgqlc.types.Arg(SortDirection, graphql_name='direction', default='descending')),
))
    )
    version = sgqlc.types.Field(sgqlc.types.non_null('Version'), graphql_name='version', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    list_version = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of('Version')), graphql_name='listVersion', args=sgqlc.types.ArgDict((
        ('ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='ids', default=None)),
))
    )
    pagination_versions_crawler = sgqlc.types.Field(sgqlc.types.non_null('VersionPagination'), graphql_name='paginationVersionsCrawler', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('filter_settings', sgqlc.types.Arg(VersionFilterSettings, graphql_name='filterSettings', default={'withRemovedVersions': False})),
        ('sort_field', sgqlc.types.Arg(VersionSorting, graphql_name='sortField', default='id')),
        ('direction', sgqlc.types.Arg(SortDirection, graphql_name='direction', default='descending')),
))
    )
    pagination_egg_file_versions_project = sgqlc.types.Field(sgqlc.types.non_null('VersionPagination'), graphql_name='paginationEggFileVersionsProject', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('with_removed', sgqlc.types.Arg(sgqlc.types.non_null(Boolean), graphql_name='withRemoved', default=False)),
        ('sort_field', sgqlc.types.Arg(VersionSorting, graphql_name='sortField', default='id')),
        ('direction', sgqlc.types.Arg(SortDirection, graphql_name='direction', default='descending')),
))
    )


class RecoveryJob(sgqlc.types.Type):
    __schema__ = crawlers_api_schema
    __field_names__ = ('id', 'status', 'start_time', 'end_time', 'progress', 'progress_message', 'creator', 'system_registration_date', 'last_updater', 'system_update_date', 'crawler', 'source_version', 'result_version')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    status = sgqlc.types.Field(sgqlc.types.non_null(RecoveryJobStatus), graphql_name='status')
    start_time = sgqlc.types.Field(UnixTime, graphql_name='startTime')
    end_time = sgqlc.types.Field(UnixTime, graphql_name='endTime')
    progress = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='progress')
    progress_message = sgqlc.types.Field(String, graphql_name='progressMessage')
    creator = sgqlc.types.Field(sgqlc.types.non_null('User'), graphql_name='creator')
    system_registration_date = sgqlc.types.Field(sgqlc.types.non_null(UnixTime), graphql_name='systemRegistrationDate')
    last_updater = sgqlc.types.Field('User', graphql_name='lastUpdater')
    system_update_date = sgqlc.types.Field(UnixTime, graphql_name='systemUpdateDate')
    crawler = sgqlc.types.Field(sgqlc.types.non_null('Crawler'), graphql_name='crawler')
    source_version = sgqlc.types.Field(sgqlc.types.non_null('Version'), graphql_name='sourceVersion')
    result_version = sgqlc.types.Field('Version', graphql_name='resultVersion')


class RecoveryJobPagination(sgqlc.types.Type):
    __schema__ = crawlers_api_schema
    __field_names__ = ('total', 'list_recovery_job')
    total = sgqlc.types.Field(sgqlc.types.non_null(Long), graphql_name='total')
    list_recovery_job = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(RecoveryJob))), graphql_name='listRecoveryJob')


class Request(sgqlc.types.Type):
    __schema__ = crawlers_api_schema
    __field_names__ = ('job_id', 'timestamp', 'last_seen', 'url', 'request_url', 'fingerprint', 'method', 'http_status', 'response_size', 'duration')
    job_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='jobId')
    timestamp = sgqlc.types.Field(sgqlc.types.non_null(UnixTime), graphql_name='timestamp')
    last_seen = sgqlc.types.Field(sgqlc.types.non_null(UnixTime), graphql_name='lastSeen')
    url = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='url')
    request_url = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='requestUrl')
    fingerprint = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='fingerprint')
    method = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='method')
    http_status = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='httpStatus')
    response_size = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='responseSize')
    duration = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='duration')


class RequestPagination(sgqlc.types.Type):
    __schema__ = crawlers_api_schema
    __field_names__ = ('total', 'list_request')
    total = sgqlc.types.Field(sgqlc.types.non_null(Long), graphql_name='total')
    list_request = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(Request))), graphql_name='listRequest')


class SettingDescription(sgqlc.types.Type):
    __schema__ = crawlers_api_schema
    __field_names__ = ('name', 'type', 'short_description', 'long_description', 'required', 'default')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    type = sgqlc.types.Field(sgqlc.types.non_null(SettingsType), graphql_name='type')
    short_description = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='shortDescription')
    long_description = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='longDescription')
    required = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='required')
    default = sgqlc.types.Field(String, graphql_name='default')


class State(sgqlc.types.Type):
    __schema__ = crawlers_api_schema
    __field_names__ = ('is_success',)
    is_success = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isSuccess')


class Stats(sgqlc.types.Type):
    __schema__ = crawlers_api_schema
    __field_names__ = ('type_of_stats', 'user_id', 'jobs_metrics', 'items_histogram', 'projects_histogram', 'previous_items_histogram')
    type_of_stats = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='typeOfStats')
    user_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='userId')
    jobs_metrics = sgqlc.types.Field(sgqlc.types.non_null(JobStats), graphql_name='jobsMetrics', args=sgqlc.types.ArgDict((
        ('interval', sgqlc.types.Arg(TimestampInterval, graphql_name='interval', default=None)),
))
    )
    items_histogram = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(DateHistogramBucket))), graphql_name='itemsHistogram', args=sgqlc.types.ArgDict((
        ('interval', sgqlc.types.Arg(TimestampInterval, graphql_name='interval', default=None)),
))
    )
    projects_histogram = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ProjectHistogram))), graphql_name='projectsHistogram', args=sgqlc.types.ArgDict((
        ('interval', sgqlc.types.Arg(TimestampInterval, graphql_name='interval', default=None)),
))
    )
    previous_items_histogram = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(DateHistogramBucket))), graphql_name='previousItemsHistogram', args=sgqlc.types.ArgDict((
        ('interval', sgqlc.types.Arg(TimestampInterval, graphql_name='interval', default=None)),
))
    )


class Subscription(sgqlc.types.Type):
    __schema__ = crawlers_api_schema
    __field_names__ = ('job',)
    job = sgqlc.types.Field(sgqlc.types.non_null(JobSubscription), graphql_name='job', args=sgqlc.types.ArgDict((
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('jobs_filter_settings', sgqlc.types.Arg(JobsFilterSettings, graphql_name='jobsFilterSettings', default={})),
        ('sort_field', sgqlc.types.Arg(JobSorting, graphql_name='sortField', default='id')),
        ('direction', sgqlc.types.Arg(SortDirection, graphql_name='direction', default='descending')),
))
    )


class User(sgqlc.types.Type):
    __schema__ = crawlers_api_schema
    __field_names__ = ('id',)
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')


class VersionPagination(sgqlc.types.Type):
    __schema__ = crawlers_api_schema
    __field_names__ = ('total', 'list_version')
    total = sgqlc.types.Field(sgqlc.types.non_null(Long), graphql_name='total')
    list_version = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('Version'))), graphql_name='listVersion')


class CrawlState(sgqlc.types.Type, RecordInterface):
    __schema__ = crawlers_api_schema
    __field_names__ = ('id', 'crawler_id', 'periodic_job_id', 'credential_id', 'information_source_id', 'crawl_key', 'state', 'cookie', 'state_version')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    crawler_id = sgqlc.types.Field(ID, graphql_name='crawlerId')
    periodic_job_id = sgqlc.types.Field(ID, graphql_name='periodicJobId')
    credential_id = sgqlc.types.Field(ID, graphql_name='credentialId')
    information_source_id = sgqlc.types.Field(ID, graphql_name='informationSourceId')
    crawl_key = sgqlc.types.Field(String, graphql_name='crawlKey')
    state = sgqlc.types.Field(sgqlc.types.non_null(JSON), graphql_name='state')
    cookie = sgqlc.types.Field(JSON, graphql_name='cookie')
    state_version = sgqlc.types.Field(sgqlc.types.non_null(Long), graphql_name='stateVersion')


class Crawler(sgqlc.types.Type, RecordInterface):
    __schema__ = crawlers_api_schema
    __field_names__ = ('id', 'name', 'title', 'description', 'crawler_type', 'last_collection_date', 'avg_performance_time', 'distribution_type', 'project', 'periodic_jobs_num', 'onetime_jobs_num', 'settings', 'args', 'analytics', 'histogram_items', 'histogram_requests', 'job_stats', 'current_version', 'start_urls')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    title = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='title')
    description = sgqlc.types.Field(String, graphql_name='description')
    crawler_type = sgqlc.types.Field(sgqlc.types.non_null(CrawlerType), graphql_name='crawlerType')
    last_collection_date = sgqlc.types.Field(UnixTime, graphql_name='lastCollectionDate')
    avg_performance_time = sgqlc.types.Field(Float, graphql_name='avgPerformanceTime')
    distribution_type = sgqlc.types.Field(sgqlc.types.non_null(DistributionType), graphql_name='distributionType')
    project = sgqlc.types.Field(sgqlc.types.non_null('Project'), graphql_name='project')
    periodic_jobs_num = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='periodicJobsNum')
    onetime_jobs_num = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='onetimeJobsNum')
    settings = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(KeyValue))), graphql_name='settings')
    args = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(KeyValue))), graphql_name='args')
    analytics = sgqlc.types.Field(sgqlc.types.non_null(CrawlerStats), graphql_name='analytics', args=sgqlc.types.ArgDict((
        ('interval', sgqlc.types.Arg(TimestampInterval, graphql_name='interval', default=None)),
))
    )
    histogram_items = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(DateHistogramBucket))), graphql_name='histogramItems', args=sgqlc.types.ArgDict((
        ('interval', sgqlc.types.Arg(TimestampInterval, graphql_name='interval', default=None)),
))
    )
    histogram_requests = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(DateHistogramBucket))), graphql_name='histogramRequests', args=sgqlc.types.ArgDict((
        ('interval', sgqlc.types.Arg(TimestampInterval, graphql_name='interval', default=None)),
))
    )
    job_stats = sgqlc.types.Field(sgqlc.types.non_null(JobStats), graphql_name='jobStats', args=sgqlc.types.ArgDict((
        ('interval', sgqlc.types.Arg(TimestampInterval, graphql_name='interval', default=None)),
))
    )
    current_version = sgqlc.types.Field('Version', graphql_name='currentVersion')
    start_urls = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='startUrls')


class Credential(sgqlc.types.Type, RecordInterface):
    __schema__ = crawlers_api_schema
    __field_names__ = ('id', 'data_type', 'description', 'login', 'password', 'token', 'domain', 'status', 'projects')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    data_type = sgqlc.types.Field(sgqlc.types.non_null(CredentialType), graphql_name='dataType')
    description = sgqlc.types.Field(String, graphql_name='description')
    login = sgqlc.types.Field(String, graphql_name='login')
    password = sgqlc.types.Field(String, graphql_name='password')
    token = sgqlc.types.Field(String, graphql_name='token')
    domain = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='domain')
    status = sgqlc.types.Field(sgqlc.types.non_null(CredentialStatus), graphql_name='status')
    projects = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('Project'))), graphql_name='projects')


class InformationSourceLoader(sgqlc.types.Type, RecordInterface):
    __schema__ = crawlers_api_schema
    __field_names__ = ('id', 'is_retrospective', 'retrospective_start', 'retrospective_end', 'running_status', 'actual_status', 'status', 'metrics', 'title')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    is_retrospective = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isRetrospective')
    retrospective_start = sgqlc.types.Field(UnixTime, graphql_name='retrospectiveStart')
    retrospective_end = sgqlc.types.Field(UnixTime, graphql_name='retrospectiveEnd')
    running_status = sgqlc.types.Field(sgqlc.types.non_null(RunningStatus), graphql_name='runningStatus')
    actual_status = sgqlc.types.Field(sgqlc.types.non_null(InformationSourceLoaderActualStatus), graphql_name='actualStatus')
    status = sgqlc.types.Field(sgqlc.types.non_null(CollectionStatus), graphql_name='status')
    metrics = sgqlc.types.Field(sgqlc.types.non_null(InformationSourceLoaderStats), graphql_name='metrics')
    title = sgqlc.types.Field(sgqlc.types.non_null('InformationSourceLoaderTitle'), graphql_name='title')


class Job(sgqlc.types.Type, RecordInterface):
    __schema__ = crawlers_api_schema
    __field_names__ = ('id', 'status', 'priority', 'message_priority', 'start_time', 'end_time', 'collection_status', 'monitoring_status', 'is_noise', 'crawler', 'project', 'version', 'credential', 'periodic_job', 'settings', 'args', 'metrics', 'job_stats', 'platforms', 'histogram_requests', 'histogram_items', 'schema')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    status = sgqlc.types.Field(sgqlc.types.non_null(JobStatus), graphql_name='status')
    priority = sgqlc.types.Field(sgqlc.types.non_null(JobPriorityType), graphql_name='priority')
    message_priority = sgqlc.types.Field(sgqlc.types.non_null(MessagePriority), graphql_name='messagePriority')
    start_time = sgqlc.types.Field(UnixTime, graphql_name='startTime')
    end_time = sgqlc.types.Field(UnixTime, graphql_name='endTime')
    collection_status = sgqlc.types.Field(sgqlc.types.non_null(CollectionStatus), graphql_name='collectionStatus')
    monitoring_status = sgqlc.types.Field(sgqlc.types.non_null(MonitoringStatus), graphql_name='monitoringStatus')
    is_noise = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isNoise')
    crawler = sgqlc.types.Field(sgqlc.types.non_null(Crawler), graphql_name='crawler')
    project = sgqlc.types.Field(sgqlc.types.non_null('Project'), graphql_name='project')
    version = sgqlc.types.Field(sgqlc.types.non_null('Version'), graphql_name='version')
    credential = sgqlc.types.Field(Credential, graphql_name='credential')
    periodic_job = sgqlc.types.Field('PeriodicJob', graphql_name='periodicJob')
    settings = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(KeyValue))), graphql_name='settings')
    args = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(KeyValue))), graphql_name='args')
    metrics = sgqlc.types.Field(JobMetrics, graphql_name='metrics')
    job_stats = sgqlc.types.Field(JobStats, graphql_name='jobStats')
    platforms = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(Platform))), graphql_name='platforms')
    histogram_requests = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(DateHistogramBucket))), graphql_name='histogramRequests')
    histogram_items = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(DateHistogramBucket))), graphql_name='histogramItems')
    schema = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(KeyValue))), graphql_name='schema')


class PeriodicJob(sgqlc.types.Type, RecordInterface):
    __schema__ = crawlers_api_schema
    __field_names__ = ('id', 'name', 'description', 'priority', 'message_priority', 'status', 'monitoring_status', 'cron', 'cron_utcoffset_minutes', 'next_schedule_time', 'disable_time', 'update_on_reload', 'crawler', 'project', 'version', 'credential', 'settings', 'args', 'metrics', 'histogram_requests', 'histogram_items', 'job_stats', 'platforms', 'job_failed_monitoring_statuses')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    name = sgqlc.types.Field(String, graphql_name='name')
    description = sgqlc.types.Field(String, graphql_name='description')
    priority = sgqlc.types.Field(sgqlc.types.non_null(JobPriorityType), graphql_name='priority')
    message_priority = sgqlc.types.Field(sgqlc.types.non_null(MessagePriority), graphql_name='messagePriority')
    status = sgqlc.types.Field(sgqlc.types.non_null(RunningStatus), graphql_name='status')
    monitoring_status = sgqlc.types.Field(sgqlc.types.non_null(MonitoringStatus), graphql_name='monitoringStatus')
    cron = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='cron')
    cron_utcoffset_minutes = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='cronUTCOffsetMinutes')
    next_schedule_time = sgqlc.types.Field(UnixTime, graphql_name='nextScheduleTime')
    disable_time = sgqlc.types.Field(UnixTime, graphql_name='disableTime')
    update_on_reload = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='updateOnReload')
    crawler = sgqlc.types.Field(sgqlc.types.non_null(Crawler), graphql_name='crawler')
    project = sgqlc.types.Field(sgqlc.types.non_null('Project'), graphql_name='project')
    version = sgqlc.types.Field(sgqlc.types.non_null('Version'), graphql_name='version')
    credential = sgqlc.types.Field(Credential, graphql_name='credential')
    settings = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(KeyValue))), graphql_name='settings')
    args = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(KeyValue))), graphql_name='args')
    metrics = sgqlc.types.Field(PeriodicJobMetrics, graphql_name='metrics')
    histogram_requests = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(DateHistogramBucket))), graphql_name='histogramRequests', args=sgqlc.types.ArgDict((
        ('interval', sgqlc.types.Arg(TimestampInterval, graphql_name='interval', default=None)),
))
    )
    histogram_items = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(DateHistogramBucket))), graphql_name='histogramItems', args=sgqlc.types.ArgDict((
        ('interval', sgqlc.types.Arg(TimestampInterval, graphql_name='interval', default=None)),
))
    )
    job_stats = sgqlc.types.Field(sgqlc.types.non_null(JobStats), graphql_name='jobStats', args=sgqlc.types.ArgDict((
        ('interval', sgqlc.types.Arg(TimestampInterval, graphql_name='interval', default=None)),
))
    )
    platforms = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(Platform))), graphql_name='platforms')
    job_failed_monitoring_statuses = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(MonitoringStatus))), graphql_name='jobFailedMonitoringStatuses')


class Project(sgqlc.types.Type, RecordInterface):
    __schema__ = crawlers_api_schema
    __field_names__ = ('id', 'name', 'title', 'description', 'crawlers_num', 'periodic_jobs_num', 'jobs_num', 'settings', 'args', 'project_stats', 'histogram_items', 'histogram_crawlers', 'current_version', 'egg_file')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    title = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='title')
    description = sgqlc.types.Field(String, graphql_name='description')
    crawlers_num = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='crawlersNum')
    periodic_jobs_num = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='periodicJobsNum')
    jobs_num = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='jobsNum')
    settings = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(KeyValue))), graphql_name='settings')
    args = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(KeyValue))), graphql_name='args')
    project_stats = sgqlc.types.Field(sgqlc.types.non_null(ProjectStats), graphql_name='projectStats', args=sgqlc.types.ArgDict((
        ('interval', sgqlc.types.Arg(TimestampInterval, graphql_name='interval', default=None)),
))
    )
    histogram_items = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(DateHistogramBucket))), graphql_name='histogramItems', args=sgqlc.types.ArgDict((
        ('interval', sgqlc.types.Arg(TimestampInterval, graphql_name='interval', default=None)),
))
    )
    histogram_crawlers = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(CrawlerHistogram))), graphql_name='histogramCrawlers', args=sgqlc.types.ArgDict((
        ('interval', sgqlc.types.Arg(TimestampInterval, graphql_name='interval', default=None)),
))
    )
    current_version = sgqlc.types.Field('Version', graphql_name='currentVersion')
    egg_file = sgqlc.types.Field(String, graphql_name='eggFile')


class Version(sgqlc.types.Type, RecordInterface):
    __schema__ = crawlers_api_schema
    __field_names__ = ('id', 'version_name', 'project_id', 'status', 'deploy_status')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    version_name = sgqlc.types.Field(sgqlc.types.non_null(Long), graphql_name='versionName')
    project_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='projectId')
    status = sgqlc.types.Field(sgqlc.types.non_null(VersionStatus), graphql_name='status')
    deploy_status = sgqlc.types.Field(sgqlc.types.non_null(DeployStatus), graphql_name='deployStatus')



########################################################################
# Unions
########################################################################
class InformationSourceLoaderTitle(sgqlc.types.Union):
    __schema__ = crawlers_api_schema
    __types__ = (InformationSourceLoaderURLTitle, InformationSourceLoaderFileTitle)



########################################################################
# Schema Entry Points
########################################################################
crawlers_api_schema.query_type = Query
crawlers_api_schema.mutation_type = Mutation
crawlers_api_schema.subscription_type = Subscription

