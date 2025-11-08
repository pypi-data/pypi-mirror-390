import sgqlc.types


utils_api_schema = sgqlc.types.Schema()



########################################################################
# Scalars and Enumerations
########################################################################
class AccessLevelSorting(sgqlc.types.Enum):
    __schema__ = utils_api_schema
    __choices__ = ('id', 'name', 'order')


class AccountSorting(sgqlc.types.Enum):
    __schema__ = utils_api_schema
    __choices__ = ('creator', 'id', 'key', 'lastUpdater', 'name', 'platformKey', 'systemRegistrationDate', 'systemUpdateDate', 'url')


Boolean = sgqlc.types.Boolean

class ChildVisibility(sgqlc.types.Enum):
    __schema__ = utils_api_schema
    __choices__ = ('all', 'childrenOnly')


class ComponentView(sgqlc.types.Enum):
    __schema__ = utils_api_schema
    __choices__ = ('keyValue', 'value')


class CompositePropertyValueTemplateSorting(sgqlc.types.Enum):
    __schema__ = utils_api_schema
    __choices__ = ('id', 'name', 'registrationDate')


class ConceptLinkDirection(sgqlc.types.Enum):
    __schema__ = utils_api_schema
    __choices__ = ('from', 'to')


class ConceptLinkTypeSorting(sgqlc.types.Enum):
    __schema__ = utils_api_schema
    __choices__ = ('conceptType', 'id', 'name')


class ConceptPropertyTypeSorting(sgqlc.types.Enum):
    __schema__ = utils_api_schema
    __choices__ = ('name', 'registrationDate')


class ConceptPropertyValueTypeSorting(sgqlc.types.Enum):
    __schema__ = utils_api_schema
    __choices__ = ('id', 'name')


class ConceptSorting(sgqlc.types.Enum):
    __schema__ = utils_api_schema
    __choices__ = ('id', 'name', 'score', 'status', 'systemRegistrationDate', 'systemUpdateDate')


class ConceptTypeLinkMetadata(sgqlc.types.Enum):
    __schema__ = utils_api_schema
    __choices__ = ('creator', 'endDate', 'lastUpdater', 'linkType', 'registrationDate', 'startDate', 'updateDate')


class ConceptTypeMetadata(sgqlc.types.Enum):
    __schema__ = utils_api_schema
    __choices__ = ('concept', 'conceptType', 'creator', 'endDate', 'image', 'lastUpdater', 'markers', 'name', 'notes', 'startDate', 'systemRegistrationDate', 'systemUpdateDate')


class ConceptTypePresentationWidgetTypeSorting(sgqlc.types.Enum):
    __schema__ = utils_api_schema
    __choices__ = ('id', 'name', 'order')


class ConceptTypeSorting(sgqlc.types.Enum):
    __schema__ = utils_api_schema
    __choices__ = ('dictionary', 'id', 'name', 'regexp')


class ConceptUpdate(sgqlc.types.Enum):
    __schema__ = utils_api_schema
    __choices__ = ('link', 'linkProperty', 'metadata', 'property')


class ConceptVariant(sgqlc.types.Enum):
    __schema__ = utils_api_schema
    __choices__ = ('event', 'obj')


class DocumentContentType(sgqlc.types.Enum):
    __schema__ = utils_api_schema
    __choices__ = ('audio', 'image', 'text', 'video')


class DocumentGrouping(sgqlc.types.Enum):
    __schema__ = utils_api_schema
    __choices__ = ('none', 'story')


class DocumentGroupingCategory(sgqlc.types.Enum):
    __schema__ = utils_api_schema
    __choices__ = ('account', 'accountCountry', 'concept', 'conceptLinkType', 'conceptPropertyType', 'conceptPropertyValue', 'conceptType', 'documentLanguage', 'marker', 'platform', 'platformCountry', 'platformLanguage', 'platformType', 'publicationAuthor')


class DocumentSorting(sgqlc.types.Enum):
    __schema__ = utils_api_schema
    __choices__ = ('countLinks', 'countNamedEntities', 'id', 'publicationDate', 'registrationDate', 'relevance', 'score', 'title', 'updateDate')


class DocumentSourceType(sgqlc.types.Enum):
    __schema__ = utils_api_schema
    __choices__ = ('external', 'internal')


class DocumentTypeSorting(sgqlc.types.Enum):
    __schema__ = utils_api_schema
    __choices__ = ('dictionary', 'id', 'name', 'regexp')


class DocumentUpdate(sgqlc.types.Enum):
    __schema__ = utils_api_schema
    __choices__ = ('content', 'markup', 'metadata')


class DomainName(sgqlc.types.Enum):
    __schema__ = utils_api_schema
    __choices__ = ('compositeConceptPropertyType', 'compositeLinkPropertyType', 'conceptPropertyType', 'conceptType', 'conceptTypePresentation', 'conceptTypePresentationWidgetType', 'linkPropertyType', 'linkType', 'valueType')


Float = sgqlc.types.Float

ID = sgqlc.types.ID

Int = sgqlc.types.Int

class JSON(sgqlc.types.Scalar):
    __schema__ = utils_api_schema


class KbFactStatus(sgqlc.types.Enum):
    __schema__ = utils_api_schema
    __choices__ = ('approved', 'notApproved')


class KbFactStatusFilter(sgqlc.types.Enum):
    __schema__ = utils_api_schema
    __choices__ = ('all', 'approved', 'notApproved')


class LinkDirection(sgqlc.types.Enum):
    __schema__ = utils_api_schema
    __choices__ = ('in', 'out', 'undirected')


class Locale(sgqlc.types.Enum):
    __schema__ = utils_api_schema
    __choices__ = ('eng', 'other', 'ru')


class Long(sgqlc.types.Scalar):
    __schema__ = utils_api_schema


class MapEdgeType(sgqlc.types.Enum):
    __schema__ = utils_api_schema
    __choices__ = ('conceptCandidateFactLink', 'conceptFactLink', 'conceptLink', 'conceptTypeLink', 'documentLink')


class MapNodeType(sgqlc.types.Enum):
    __schema__ = utils_api_schema
    __choices__ = ('concept', 'conceptType', 'document', 'documentType')


class MentionLinkType(sgqlc.types.Enum):
    __schema__ = utils_api_schema
    __choices__ = ('equivalent', 'reference', 'translation')


class Name(sgqlc.types.Enum):
    __schema__ = utils_api_schema
    __choices__ = ('approvedPropsRelevance', 'conceptApprovedPropsRelevance', 'conceptFactRelevance', 'conceptMeaningPropsRelevance', 'conceptNercRelevance', 'conceptNercSearchRelevance', 'conceptPropsRelevance', 'conceptSubstituteRelevance', 'factRelevance', 'mapApprovedPropsRelevance', 'mapFactRelevance', 'mapMeaningPropsRelevance', 'mapNercRelevance', 'mapNercSearchRelevance', 'mapPropsRelevance', 'meaningPropsRelevance', 'nercRelevance', 'nercSearchRelevance', 'propsRelevance', 'queryScore', 'significantTextRelevance', 'totalRelevance')


class NodeType(sgqlc.types.Enum):
    __schema__ = utils_api_schema
    __choices__ = ('audio', 'base64', 'cell', 'file', 'header', 'image', 'json', 'key', 'list', 'other', 'row', 'table', 'text', 'video')


class PlatformSorting(sgqlc.types.Enum):
    __schema__ = utils_api_schema
    __choices__ = ('creator', 'id', 'key', 'lastUpdater', 'name', 'platformType', 'systemRegistrationDate', 'systemUpdateDate', 'url')


class PlatformType(sgqlc.types.Enum):
    __schema__ = utils_api_schema
    __choices__ = ('blog', 'database', 'fileStorage', 'forum', 'government', 'media', 'messenger', 'newsAggregator', 'procurement', 'review', 'socialNetwork')


class PropertyParent(sgqlc.types.Enum):
    __schema__ = utils_api_schema
    __choices__ = ('concept', 'conceptLink', 'document')


class ResearchMapSorting(sgqlc.types.Enum):
    __schema__ = utils_api_schema
    __choices__ = ('accessLevel', 'conceptAndDocumentLink', 'conceptLink', 'creator', 'documentLink', 'id', 'lastUpdater', 'name', 'systemRegistrationDate', 'systemUpdateDate')


class RubricatorType(sgqlc.types.Enum):
    __schema__ = utils_api_schema
    __choices__ = ('auto', 'manual')


class SortDirection(sgqlc.types.Enum):
    __schema__ = utils_api_schema
    __choices__ = ('ascending', 'descending')


String = sgqlc.types.String

class TDMProcessStage(sgqlc.types.Enum):
    __schema__ = utils_api_schema
    __choices__ = ('all', 'preprocessed', 'processed')


class TdmHandlingStatus(sgqlc.types.Enum):
    __schema__ = utils_api_schema
    __choices__ = ('Failed', 'Pending', 'Success', 'WithErrors')


class TrustLevel(sgqlc.types.Enum):
    __schema__ = utils_api_schema
    __choices__ = ('high', 'low', 'medium')


class UnixTime(sgqlc.types.Scalar):
    __schema__ = utils_api_schema


class ValueType(sgqlc.types.Enum):
    __schema__ = utils_api_schema
    __choices__ = ('Date', 'Double', 'Geo', 'Int', 'Link', 'String', 'StringLocale', 'Timestamp')


class WidgetTypeTableType(sgqlc.types.Enum):
    __schema__ = utils_api_schema
    __choices__ = ('horizontal', 'vertical')



########################################################################
# Input Objects
########################################################################
class AccountFilterSettings(sgqlc.types.Input):
    __schema__ = utils_api_schema
    __field_names__ = ('country', 'creator', 'ids', 'keys', 'last_updater', 'markers', 'platform_ids', 'registration_date', 'search_string', 'update_date')
    country = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='country')
    creator = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='creator')
    ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='ids')
    keys = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='keys')
    last_updater = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='lastUpdater')
    markers = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='markers')
    platform_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='platformIds')
    registration_date = sgqlc.types.Field('TimestampIntervalInput', graphql_name='registrationDate')
    search_string = sgqlc.types.Field(String, graphql_name='searchString')
    update_date = sgqlc.types.Field('TimestampIntervalInput', graphql_name='updateDate')


class AccountGetOrCreateInput(sgqlc.types.Input):
    __schema__ = utils_api_schema
    __field_names__ = ('key', 'name', 'platform_key', 'url')
    key = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='key')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    platform_key = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='platformKey')
    url = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='url')


class AddDocumentToOriginalDocumentInput(sgqlc.types.Input):
    __schema__ = utils_api_schema
    __field_names__ = ('concept_id', 'job_id', 'original_document_uuid', 'periodic_job_id', 'periodic_task_id', 'task_id', 'uuid')
    concept_id = sgqlc.types.Field(ID, graphql_name='conceptId')
    job_id = sgqlc.types.Field(String, graphql_name='jobId')
    original_document_uuid = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='originalDocumentUUID')
    periodic_job_id = sgqlc.types.Field(String, graphql_name='periodicJobId')
    periodic_task_id = sgqlc.types.Field(String, graphql_name='periodicTaskId')
    task_id = sgqlc.types.Field(String, graphql_name='taskId')
    uuid = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='uuid')


class AnnotationInput(sgqlc.types.Input):
    __schema__ = utils_api_schema
    __field_names__ = ('end', 'node_id', 'start')
    end = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='end')
    node_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='nodeId')
    start = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='start')


class BatchUpdateFactInput(sgqlc.types.Input):
    __schema__ = utils_api_schema
    __field_names__ = ('access_level_id', 'composite_property_value_component_fact', 'composite_property_value_fact', 'concept_fact', 'concept_link_fact', 'concept_link_property_fact', 'concept_property_fact', 'mention', 'property_value_fact', 'property_value_mention_fact')
    access_level_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='accessLevelId')
    composite_property_value_component_fact = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('CompositePropertyValueComponentFactInput')), graphql_name='compositePropertyValueComponentFact')
    composite_property_value_fact = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('CompositePropertyValueFactInput')), graphql_name='compositePropertyValueFact')
    concept_fact = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('ConceptFactInput')), graphql_name='conceptFact')
    concept_link_fact = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('ConceptLinkFactInput')), graphql_name='conceptLinkFact')
    concept_link_property_fact = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('ConceptLinkPropertyFactInput')), graphql_name='conceptLinkPropertyFact')
    concept_property_fact = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('ConceptPropertyFactInput')), graphql_name='conceptPropertyFact')
    mention = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('MentionInput')), graphql_name='mention')
    property_value_fact = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('PropertyValueFactInput')), graphql_name='propertyValueFact')
    property_value_mention_fact = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('PropertyValueMentionFactInput')), graphql_name='propertyValueMentionFact')


class CompositePropertyValueComponentFactInput(sgqlc.types.Input):
    __schema__ = utils_api_schema
    __field_names__ = ('component_value_type_id', 'composite_property_value_fact_id', 'id', 'reject', 'value_fact_id')
    component_value_type_id = sgqlc.types.Field(ID, graphql_name='componentValueTypeId')
    composite_property_value_fact_id = sgqlc.types.Field(ID, graphql_name='compositePropertyValueFactId')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    reject = sgqlc.types.Field(Boolean, graphql_name='reject')
    value_fact_id = sgqlc.types.Field(ID, graphql_name='valueFactId')


class CompositePropertyValueFactInput(sgqlc.types.Input):
    __schema__ = utils_api_schema
    __field_names__ = ('composite_value_type_id', 'id', 'reject')
    composite_value_type_id = sgqlc.types.Field(ID, graphql_name='compositeValueTypeId')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    reject = sgqlc.types.Field(Boolean, graphql_name='reject')


class CompositePropertyValueTemplateFilterSettings(sgqlc.types.Input):
    __schema__ = utils_api_schema
    __field_names__ = ('creator', 'last_updater', 'name', 'registration_date', 'update_date')
    creator = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='creator')
    last_updater = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='lastUpdater')
    name = sgqlc.types.Field(String, graphql_name='name')
    registration_date = sgqlc.types.Field('TimestampIntervalInput', graphql_name='registrationDate')
    update_date = sgqlc.types.Field('TimestampIntervalInput', graphql_name='updateDate')


class ConceptDuplicateFilterSettings(sgqlc.types.Input):
    __schema__ = utils_api_schema
    __field_names__ = ('concept_id', 'group_id', 'input_value')
    concept_id = sgqlc.types.Field(ID, graphql_name='conceptId')
    group_id = sgqlc.types.Field(ID, graphql_name='groupId')
    input_value = sgqlc.types.Field(String, graphql_name='inputValue')


class ConceptDuplicateGroupFilterSettings(sgqlc.types.Input):
    __schema__ = utils_api_schema
    __field_names__ = ('concept_type_ids', 'contains_concept_id', 'creators', 'input_value', 'report_id', 'task_created_at', 'task_ids', 'task_method_ids')
    concept_type_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='conceptTypeIds')
    contains_concept_id = sgqlc.types.Field(ID, graphql_name='containsConceptId')
    creators = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='creators')
    input_value = sgqlc.types.Field(String, graphql_name='inputValue')
    report_id = sgqlc.types.Field(ID, graphql_name='reportId')
    task_created_at = sgqlc.types.Field('TimestampIntervalInput', graphql_name='taskCreatedAt')
    task_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='taskIds')
    task_method_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='taskMethodIds')


class ConceptExtraSettings(sgqlc.types.Input):
    __schema__ = utils_api_schema
    __field_names__ = ('search_on_map', 'selected_content')
    search_on_map = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='searchOnMap')
    selected_content = sgqlc.types.Field('ResearchMapContentSelectInput', graphql_name='selectedContent')


class ConceptFactInput(sgqlc.types.Input):
    __schema__ = utils_api_schema
    __field_names__ = ('approved', 'concept_id', 'concept_type_id', 'id', 'reject')
    approved = sgqlc.types.Field(Boolean, graphql_name='approved')
    concept_id = sgqlc.types.Field(ID, graphql_name='conceptId')
    concept_type_id = sgqlc.types.Field(ID, graphql_name='conceptTypeId')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    reject = sgqlc.types.Field(Boolean, graphql_name='reject')


class ConceptFactsCreationInput(sgqlc.types.Input):
    __schema__ = utils_api_schema
    __field_names__ = ('access_level_id', 'composite_property_value_component_fact', 'composite_property_value_fact', 'concept_fact', 'concept_property_fact', 'document_id', 'mention', 'property_value_fact', 'property_value_mention_fact')
    access_level_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='accessLevelId')
    composite_property_value_component_fact = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(CompositePropertyValueComponentFactInput)), graphql_name='compositePropertyValueComponentFact')
    composite_property_value_fact = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(CompositePropertyValueFactInput)), graphql_name='compositePropertyValueFact')
    concept_fact = sgqlc.types.Field(sgqlc.types.non_null(ConceptFactInput), graphql_name='conceptFact')
    concept_property_fact = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ConceptPropertyFactInput'))), graphql_name='conceptPropertyFact')
    document_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='documentId')
    mention = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('MentionInput')), graphql_name='mention')
    property_value_fact = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('PropertyValueFactInput'))), graphql_name='propertyValueFact')
    property_value_mention_fact = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('PropertyValueMentionFactInput')), graphql_name='propertyValueMentionFact')


class ConceptFilterSettings(sgqlc.types.Input):
    __schema__ = utils_api_schema
    __field_names__ = ('access_level_id', 'concept_type_ids', 'concept_variant', 'creation_date', 'creator', 'exact_name', 'last_updater', 'link_filter_settings', 'markers', 'name', 'property_filter_settings', 'status', 'substring', 'update_date')
    access_level_id = sgqlc.types.Field(ID, graphql_name='accessLevelId')
    concept_type_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='conceptTypeIds')
    concept_variant = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ConceptVariant)), graphql_name='conceptVariant')
    creation_date = sgqlc.types.Field('TimestampIntervalInput', graphql_name='creationDate')
    creator = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='creator')
    exact_name = sgqlc.types.Field(String, graphql_name='exactName')
    last_updater = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='lastUpdater')
    link_filter_settings = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('LinkFilterSettings')), graphql_name='linkFilterSettings')
    markers = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='markers')
    name = sgqlc.types.Field(String, graphql_name='name')
    property_filter_settings = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('PropertyFilterSettings')), graphql_name='propertyFilterSettings')
    status = sgqlc.types.Field(KbFactStatusFilter, graphql_name='status')
    substring = sgqlc.types.Field(String, graphql_name='substring')
    update_date = sgqlc.types.Field('TimestampIntervalInput', graphql_name='updateDate')


class ConceptLinkFactInput(sgqlc.types.Input):
    __schema__ = utils_api_schema
    __field_names__ = ('approved', 'concept_from_fact_id', 'concept_to_fact_id', 'id', 'link_type_id', 'reject')
    approved = sgqlc.types.Field(Boolean, graphql_name='approved')
    concept_from_fact_id = sgqlc.types.Field(ID, graphql_name='conceptFromFactId')
    concept_to_fact_id = sgqlc.types.Field(ID, graphql_name='conceptToFactId')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    link_type_id = sgqlc.types.Field(ID, graphql_name='linkTypeId')
    reject = sgqlc.types.Field(Boolean, graphql_name='reject')


class ConceptLinkFilterSettings(sgqlc.types.Input):
    __schema__ = utils_api_schema
    __field_names__ = ('concept_link_type', 'creation_date', 'document_id', 'is_event', 'other_concept_name', 'other_entity_name', 'status', 'update_date', 'value', 'value_type')
    concept_link_type = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='conceptLinkType')
    creation_date = sgqlc.types.Field('TimestampIntervalInput', graphql_name='creationDate')
    document_id = sgqlc.types.Field(ID, graphql_name='documentId')
    is_event = sgqlc.types.Field(Boolean, graphql_name='isEvent')
    other_concept_name = sgqlc.types.Field(String, graphql_name='otherConceptName')
    other_entity_name = sgqlc.types.Field(String, graphql_name='otherEntityName')
    status = sgqlc.types.Field(KbFactStatusFilter, graphql_name='status')
    update_date = sgqlc.types.Field('TimestampIntervalInput', graphql_name='updateDate')
    value = sgqlc.types.Field('ValueFilterInput', graphql_name='value')
    value_type = sgqlc.types.Field(ValueType, graphql_name='valueType')


class ConceptLinkPropertyFactInput(sgqlc.types.Input):
    __schema__ = utils_api_schema
    __field_names__ = ('approved', 'concept_link_fact_id', 'id', 'link_property_type_id', 'reject', 'value_fact_id')
    approved = sgqlc.types.Field(Boolean, graphql_name='approved')
    concept_link_fact_id = sgqlc.types.Field(ID, graphql_name='conceptLinkFactId')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    link_property_type_id = sgqlc.types.Field(ID, graphql_name='linkPropertyTypeId')
    reject = sgqlc.types.Field(Boolean, graphql_name='reject')
    value_fact_id = sgqlc.types.Field(ID, graphql_name='valueFactId')


class ConceptLinkTypeFilterSettings(sgqlc.types.Input):
    __schema__ = utils_api_schema
    __field_names__ = ('concept_from_type_id', 'concept_to_type_id', 'concept_type_and_event_filter', 'creator', 'has_rel_ext_models', 'is_directed', 'is_hierarchical', 'last_updater', 'name', 'registration_date', 'update_date')
    concept_from_type_id = sgqlc.types.Field(ID, graphql_name='conceptFromTypeId')
    concept_to_type_id = sgqlc.types.Field(ID, graphql_name='conceptToTypeId')
    concept_type_and_event_filter = sgqlc.types.Field('conceptTypeAndEventFilter', graphql_name='conceptTypeAndEventFilter')
    creator = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='creator')
    has_rel_ext_models = sgqlc.types.Field(Boolean, graphql_name='hasRelExtModels')
    is_directed = sgqlc.types.Field(Boolean, graphql_name='isDirected')
    is_hierarchical = sgqlc.types.Field(Boolean, graphql_name='isHierarchical')
    last_updater = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='lastUpdater')
    name = sgqlc.types.Field(String, graphql_name='name')
    registration_date = sgqlc.types.Field('TimestampIntervalInput', graphql_name='registrationDate')
    update_date = sgqlc.types.Field('TimestampIntervalInput', graphql_name='updateDate')


class ConceptMutationInput(sgqlc.types.Input):
    __schema__ = utils_api_schema
    __field_names__ = ('access_level_id', 'concept_type_id', 'end_date', 'fact_info', 'markers', 'name', 'notes', 'start_date')
    access_level_id = sgqlc.types.Field(ID, graphql_name='accessLevelId')
    concept_type_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='conceptTypeId')
    end_date = sgqlc.types.Field('DateTimeInput', graphql_name='endDate')
    fact_info = sgqlc.types.Field('FactInput', graphql_name='factInfo')
    markers = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='markers')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    notes = sgqlc.types.Field(String, graphql_name='notes')
    start_date = sgqlc.types.Field('DateTimeInput', graphql_name='startDate')


class ConceptPropertyFactInput(sgqlc.types.Input):
    __schema__ = utils_api_schema
    __field_names__ = ('approved', 'concept_fact_id', 'id', 'property_type_id', 'reject', 'value_fact_id')
    approved = sgqlc.types.Field(Boolean, graphql_name='approved')
    concept_fact_id = sgqlc.types.Field(ID, graphql_name='conceptFactId')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    property_type_id = sgqlc.types.Field(ID, graphql_name='propertyTypeId')
    reject = sgqlc.types.Field(Boolean, graphql_name='reject')
    value_fact_id = sgqlc.types.Field(ID, graphql_name='valueFactId')


class ConceptPropertyFilterSettings(sgqlc.types.Input):
    __schema__ = utils_api_schema
    __field_names__ = ('document_id', 'only_main', 'property_type', 'status', 'value', 'value_type')
    document_id = sgqlc.types.Field(ID, graphql_name='documentId')
    only_main = sgqlc.types.Field(Boolean, graphql_name='onlyMain')
    property_type = sgqlc.types.Field(ID, graphql_name='propertyType')
    status = sgqlc.types.Field(KbFactStatusFilter, graphql_name='status')
    value = sgqlc.types.Field('ValueFilterInput', graphql_name='value')
    value_type = sgqlc.types.Field(ValueType, graphql_name='valueType')


class ConceptPropertyTypeFilterSettings(sgqlc.types.Input):
    __schema__ = utils_api_schema
    __field_names__ = ('concept_link_type_id', 'concept_link_type_name', 'concept_type_from_link_type_id', 'concept_type_id', 'concept_type_name', 'concept_value_type_id', 'document_type_id', 'document_type_name', 'name', 'property_parent', 'value_type')
    concept_link_type_id = sgqlc.types.Field(ID, graphql_name='conceptLinkTypeId')
    concept_link_type_name = sgqlc.types.Field(String, graphql_name='conceptLinkTypeName')
    concept_type_from_link_type_id = sgqlc.types.Field(ID, graphql_name='conceptTypeFromLinkTypeId')
    concept_type_id = sgqlc.types.Field(ID, graphql_name='conceptTypeId')
    concept_type_name = sgqlc.types.Field(String, graphql_name='conceptTypeName')
    concept_value_type_id = sgqlc.types.Field(ID, graphql_name='conceptValueTypeId')
    document_type_id = sgqlc.types.Field(ID, graphql_name='documentTypeId')
    document_type_name = sgqlc.types.Field(String, graphql_name='documentTypeName')
    name = sgqlc.types.Field(String, graphql_name='name')
    property_parent = sgqlc.types.Field(PropertyParent, graphql_name='propertyParent')
    value_type = sgqlc.types.Field(ValueType, graphql_name='valueType')


class ConceptPropertyValueTypeFilterSettings(sgqlc.types.Input):
    __schema__ = utils_api_schema
    __field_names__ = ('creator', 'dictionary_exists', 'last_updater', 'name', 'pretrained_nercmodels', 'regexp_exists', 'registration_date', 'update_date', 'value_type')
    creator = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='creator')
    dictionary_exists = sgqlc.types.Field(Boolean, graphql_name='dictionaryExists')
    last_updater = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='lastUpdater')
    name = sgqlc.types.Field(String, graphql_name='name')
    pretrained_nercmodels = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='pretrainedNERCModels')
    regexp_exists = sgqlc.types.Field(Boolean, graphql_name='regexpExists')
    registration_date = sgqlc.types.Field('TimestampIntervalInput', graphql_name='registrationDate')
    update_date = sgqlc.types.Field('TimestampIntervalInput', graphql_name='updateDate')
    value_type = sgqlc.types.Field(ValueType, graphql_name='valueType')


class ConceptTypeFilterSettings(sgqlc.types.Input):
    __schema__ = utils_api_schema
    __field_names__ = ('creator', 'dictionary_exists', 'is_event', 'last_updater', 'name', 'pretrained_nercmodels', 'regexp_exists', 'registration_date', 'update_date')
    creator = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='creator')
    dictionary_exists = sgqlc.types.Field(Boolean, graphql_name='dictionaryExists')
    is_event = sgqlc.types.Field(Boolean, graphql_name='isEvent')
    last_updater = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='lastUpdater')
    name = sgqlc.types.Field(String, graphql_name='name')
    pretrained_nercmodels = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='pretrainedNERCModels')
    regexp_exists = sgqlc.types.Field(Boolean, graphql_name='regexpExists')
    registration_date = sgqlc.types.Field('TimestampIntervalInput', graphql_name='registrationDate')
    update_date = sgqlc.types.Field('TimestampIntervalInput', graphql_name='updateDate')


class CoordinatesInput(sgqlc.types.Input):
    __schema__ = utils_api_schema
    __field_names__ = ('latitude', 'longitude')
    latitude = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='latitude')
    longitude = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='longitude')


class DateInput(sgqlc.types.Input):
    __schema__ = utils_api_schema
    __field_names__ = ('day', 'month', 'year')
    day = sgqlc.types.Field(Int, graphql_name='day')
    month = sgqlc.types.Field(Int, graphql_name='month')
    year = sgqlc.types.Field(Int, graphql_name='year')


class DateTimeInput(sgqlc.types.Input):
    __schema__ = utils_api_schema
    __field_names__ = ('date', 'time')
    date = sgqlc.types.Field(sgqlc.types.non_null(DateInput), graphql_name='date')
    time = sgqlc.types.Field('TimeInput', graphql_name='time')


class DateTimeIntervalInput(sgqlc.types.Input):
    __schema__ = utils_api_schema
    __field_names__ = ('end', 'start')
    end = sgqlc.types.Field(DateTimeInput, graphql_name='end')
    start = sgqlc.types.Field(DateTimeInput, graphql_name='start')


class DocumentFilterSettings(sgqlc.types.Input):
    __schema__ = utils_api_schema
    __field_names__ = ('access_level_id', 'accounts', 'child_docs_num', 'child_visibility', 'concepts', 'concepts_num', 'creator', 'document_content_type', 'document_is_media', 'document_is_processed', 'document_type_ids', 'external_url', 'fact_types', 'job_ids', 'last_update', 'last_updater', 'links', 'markers', 'meaning_concept_candidates', 'named_entities', 'nerc_num', 'nested_ids', 'periodic_job_ids', 'periodic_task_ids', 'platforms', 'property_filter_settings', 'publication_author', 'publication_date', 'registration_date', 'search_string', 'show_read', 'source_type', 'story', 'substring', 'task_ids', 'tdm_process_stage', 'trust_level')
    access_level_id = sgqlc.types.Field(ID, graphql_name='accessLevelId')
    accounts = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='accounts')
    child_docs_num = sgqlc.types.Field('IntIntervalInput', graphql_name='childDocsNum')
    child_visibility = sgqlc.types.Field(ChildVisibility, graphql_name='childVisibility')
    concepts = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='concepts')
    concepts_num = sgqlc.types.Field('IntIntervalInput', graphql_name='conceptsNum')
    creator = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='creator')
    document_content_type = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(DocumentContentType)), graphql_name='documentContentType')
    document_is_media = sgqlc.types.Field(Boolean, graphql_name='documentIsMedia')
    document_is_processed = sgqlc.types.Field(Boolean, graphql_name='documentIsProcessed')
    document_type_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='documentTypeIds')
    external_url = sgqlc.types.Field(String, graphql_name='externalUrl')
    fact_types = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='factTypes')
    job_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='jobIds')
    last_update = sgqlc.types.Field('TimestampIntervalInput', graphql_name='lastUpdate')
    last_updater = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='lastUpdater')
    links = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='links')
    markers = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='markers')
    meaning_concept_candidates = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='meaningConceptCandidates')
    named_entities = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='namedEntities')
    nerc_num = sgqlc.types.Field('IntIntervalInput', graphql_name='nercNum')
    nested_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='nestedIds')
    periodic_job_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='periodicJobIds')
    periodic_task_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='periodicTaskIds')
    platforms = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='platforms')
    property_filter_settings = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('PropertyFilterSettings')), graphql_name='propertyFilterSettings')
    publication_author = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='publicationAuthor')
    publication_date = sgqlc.types.Field('TimestampIntervalInput', graphql_name='publicationDate')
    registration_date = sgqlc.types.Field('TimestampIntervalInput', graphql_name='registrationDate')
    search_string = sgqlc.types.Field(String, graphql_name='searchString')
    show_read = sgqlc.types.Field(Boolean, graphql_name='showRead')
    source_type = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(DocumentSourceType)), graphql_name='sourceType')
    story = sgqlc.types.Field(String, graphql_name='story')
    substring = sgqlc.types.Field(String, graphql_name='substring')
    task_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='taskIds')
    tdm_process_stage = sgqlc.types.Field(TDMProcessStage, graphql_name='tdmProcessStage')
    trust_level = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(TrustLevel)), graphql_name='trustLevel')


class DocumentRelevanceMetricsInput(sgqlc.types.Input):
    __schema__ = utils_api_schema
    __field_names__ = ('approved_props_relevance', 'concept_approved_props_relevance', 'concept_fact_relevance', 'concept_meaning_props_relevance', 'concept_nerc_relevance', 'concept_nerc_search_relevance', 'concept_props_relevance', 'concept_substitute_relevance', 'fact_relevance', 'map_approved_props_relevance', 'map_fact_relevance', 'map_meaning_props_relevance', 'map_nerc_relevance', 'map_nerc_search_relevance', 'map_props_relevance', 'meaning_props_relevance', 'nerc_relevance', 'nerc_search_relevance', 'props_relevance', 'significant_text_relevance')
    approved_props_relevance = sgqlc.types.Field(Int, graphql_name='approvedPropsRelevance')
    concept_approved_props_relevance = sgqlc.types.Field(Int, graphql_name='conceptApprovedPropsRelevance')
    concept_fact_relevance = sgqlc.types.Field(Int, graphql_name='conceptFactRelevance')
    concept_meaning_props_relevance = sgqlc.types.Field(Int, graphql_name='conceptMeaningPropsRelevance')
    concept_nerc_relevance = sgqlc.types.Field(Int, graphql_name='conceptNercRelevance')
    concept_nerc_search_relevance = sgqlc.types.Field(Int, graphql_name='conceptNercSearchRelevance')
    concept_props_relevance = sgqlc.types.Field(Int, graphql_name='conceptPropsRelevance')
    concept_substitute_relevance = sgqlc.types.Field(Int, graphql_name='conceptSubstituteRelevance')
    fact_relevance = sgqlc.types.Field(Int, graphql_name='factRelevance')
    map_approved_props_relevance = sgqlc.types.Field(Int, graphql_name='mapApprovedPropsRelevance')
    map_fact_relevance = sgqlc.types.Field(Int, graphql_name='mapFactRelevance')
    map_meaning_props_relevance = sgqlc.types.Field(Int, graphql_name='mapMeaningPropsRelevance')
    map_nerc_relevance = sgqlc.types.Field(Int, graphql_name='mapNercRelevance')
    map_nerc_search_relevance = sgqlc.types.Field(Int, graphql_name='mapNercSearchRelevance')
    map_props_relevance = sgqlc.types.Field(Int, graphql_name='mapPropsRelevance')
    meaning_props_relevance = sgqlc.types.Field(Int, graphql_name='meaningPropsRelevance')
    nerc_relevance = sgqlc.types.Field(Int, graphql_name='nercRelevance')
    nerc_search_relevance = sgqlc.types.Field(Int, graphql_name='nercSearchRelevance')
    props_relevance = sgqlc.types.Field(Int, graphql_name='propsRelevance')
    significant_text_relevance = sgqlc.types.Field(Int, graphql_name='significantTextRelevance')


class DocumentTypeFilterSettings(sgqlc.types.Input):
    __schema__ = utils_api_schema
    __field_names__ = ('creator', 'dictionary_exists', 'last_updater', 'name', 'pretrained_nercmodels', 'regexp_exists', 'registration_date', 'update_date')
    creator = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='creator')
    dictionary_exists = sgqlc.types.Field(Boolean, graphql_name='dictionaryExists')
    last_updater = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='lastUpdater')
    name = sgqlc.types.Field(String, graphql_name='name')
    pretrained_nercmodels = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='pretrainedNERCModels')
    regexp_exists = sgqlc.types.Field(Boolean, graphql_name='regexpExists')
    registration_date = sgqlc.types.Field('TimestampIntervalInput', graphql_name='registrationDate')
    update_date = sgqlc.types.Field('TimestampIntervalInput', graphql_name='updateDate')


class DoubleIntervalInput(sgqlc.types.Input):
    __schema__ = utils_api_schema
    __field_names__ = ('end', 'start')
    end = sgqlc.types.Field(Float, graphql_name='end')
    start = sgqlc.types.Field(Float, graphql_name='start')


class DoubleValueInput(sgqlc.types.Input):
    __schema__ = utils_api_schema
    __field_names__ = ('double',)
    double = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='double')


class ExtraSettings(sgqlc.types.Input):
    __schema__ = utils_api_schema
    __field_names__ = ('ranking_script', 'search_on_map', 'selected_content')
    ranking_script = sgqlc.types.Field(String, graphql_name='rankingScript')
    search_on_map = sgqlc.types.Field(Boolean, graphql_name='searchOnMap')
    selected_content = sgqlc.types.Field('ResearchMapContentSelectInput', graphql_name='selectedContent')


class FactInput(sgqlc.types.Input):
    __schema__ = utils_api_schema
    __field_names__ = ('add_as_name', 'annotations', 'document_id', 'fact_id')
    add_as_name = sgqlc.types.Field(Boolean, graphql_name='addAsName')
    annotations = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('TextBoundingInput')), graphql_name='annotations')
    document_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='documentId')
    fact_id = sgqlc.types.Field(ID, graphql_name='factId')


class GeoCircularAreaInput(sgqlc.types.Input):
    __schema__ = utils_api_schema
    __field_names__ = ('latitude_center', 'longitude_center', 'radius')
    latitude_center = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='latitudeCenter')
    longitude_center = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='longitudeCenter')
    radius = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='radius')


class GeoPointInput(sgqlc.types.Input):
    __schema__ = utils_api_schema
    __field_names__ = ('name', 'point')
    name = sgqlc.types.Field(String, graphql_name='name')
    point = sgqlc.types.Field(CoordinatesInput, graphql_name='point')


class GeoPointWithNameInput(sgqlc.types.Input):
    __schema__ = utils_api_schema
    __field_names__ = ('circular_area', 'name', 'rectangular_area')
    circular_area = sgqlc.types.Field(GeoCircularAreaInput, graphql_name='circularArea')
    name = sgqlc.types.Field(String, graphql_name='name')
    rectangular_area = sgqlc.types.Field('GeoRectangularAreaInput', graphql_name='rectangularArea')


class GeoRectangularAreaInput(sgqlc.types.Input):
    __schema__ = utils_api_schema
    __field_names__ = ('latitude_max', 'latitude_min', 'longitude_max', 'longitude_min')
    latitude_max = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='latitudeMax')
    latitude_min = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='latitudeMin')
    longitude_max = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='longitudeMax')
    longitude_min = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='longitudeMin')


class IntIntervalInput(sgqlc.types.Input):
    __schema__ = utils_api_schema
    __field_names__ = ('end', 'start')
    end = sgqlc.types.Field(Int, graphql_name='end')
    start = sgqlc.types.Field(Int, graphql_name='start')


class IntValueInput(sgqlc.types.Input):
    __schema__ = utils_api_schema
    __field_names__ = ('int',)
    int = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='int')


class LinkFilterSettings(sgqlc.types.Input):
    __schema__ = utils_api_schema
    __field_names__ = ('link_direction', 'link_type_id', 'other_concept_id', 'status')
    link_direction = sgqlc.types.Field(LinkDirection, graphql_name='linkDirection')
    link_type_id = sgqlc.types.Field(ID, graphql_name='linkTypeId')
    other_concept_id = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='otherConceptId')
    status = sgqlc.types.Field(KbFactStatusFilter, graphql_name='status')


class LinkValueInput(sgqlc.types.Input):
    __schema__ = utils_api_schema
    __field_names__ = ('link',)
    link = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='link')


class LinkedDocumentFilterSettings(sgqlc.types.Input):
    __schema__ = utils_api_schema
    __field_names__ = ('document_content_type',)
    document_content_type = sgqlc.types.Field(DocumentContentType, graphql_name='documentContentType')


class MapEdgeFilterSettings(sgqlc.types.Input):
    __schema__ = utils_api_schema
    __field_names__ = ('edge_type',)
    edge_type = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(MapEdgeType)), graphql_name='edgeType')


class MapNodeFilterSettings(sgqlc.types.Input):
    __schema__ = utils_api_schema
    __field_names__ = ('node_type',)
    node_type = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(MapNodeType)), graphql_name='nodeType')


class MentionInput(sgqlc.types.Input):
    __schema__ = utils_api_schema
    __field_names__ = ('annotation', 'id')
    annotation = sgqlc.types.Field(AnnotationInput, graphql_name='annotation')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')


class PlatformFilterSettings(sgqlc.types.Input):
    __schema__ = utils_api_schema
    __field_names__ = ('country', 'creator', 'ids', 'keys', 'language', 'last_updater', 'markers', 'platform_type', 'registration_date', 'search_string', 'update_date')
    country = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='country')
    creator = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='creator')
    ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='ids')
    keys = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='keys')
    language = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='language')
    last_updater = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='lastUpdater')
    markers = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='markers')
    platform_type = sgqlc.types.Field(PlatformType, graphql_name='platformType')
    registration_date = sgqlc.types.Field('TimestampIntervalInput', graphql_name='registrationDate')
    search_string = sgqlc.types.Field(String, graphql_name='searchString')
    update_date = sgqlc.types.Field('TimestampIntervalInput', graphql_name='updateDate')


class PlatformGetOrCreateInput(sgqlc.types.Input):
    __schema__ = utils_api_schema
    __field_names__ = ('key', 'name', 'platform_type', 'url')
    key = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='key')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    platform_type = sgqlc.types.Field(sgqlc.types.non_null(PlatformType), graphql_name='platformType')
    url = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='url')


class PropertyFilterSettings(sgqlc.types.Input):
    __schema__ = utils_api_schema
    __field_names__ = ('component_id', 'date_time_filter', 'double_filter', 'geo_filter', 'int_filter', 'property_type_id', 'status', 'string_filter')
    component_id = sgqlc.types.Field(ID, graphql_name='componentId')
    date_time_filter = sgqlc.types.Field(DateTimeIntervalInput, graphql_name='dateTimeFilter')
    double_filter = sgqlc.types.Field(DoubleIntervalInput, graphql_name='doubleFilter')
    geo_filter = sgqlc.types.Field(GeoPointWithNameInput, graphql_name='geoFilter')
    int_filter = sgqlc.types.Field(IntIntervalInput, graphql_name='intFilter')
    property_type_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='propertyTypeId')
    status = sgqlc.types.Field(KbFactStatusFilter, graphql_name='status')
    string_filter = sgqlc.types.Field('StringFilterInput', graphql_name='stringFilter')


class PropertyValueFactInput(sgqlc.types.Input):
    __schema__ = utils_api_schema
    __field_names__ = ('id', 'reject', 'value')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    reject = sgqlc.types.Field(Boolean, graphql_name='reject')
    value = sgqlc.types.Field('ValueInput', graphql_name='value')


class PropertyValueMentionFactInput(sgqlc.types.Input):
    __schema__ = utils_api_schema
    __field_names__ = ('id', 'mention_id', 'reject', 'value_fact_id')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    mention_id = sgqlc.types.Field(ID, graphql_name='mentionId')
    reject = sgqlc.types.Field(Boolean, graphql_name='reject')
    value_fact_id = sgqlc.types.Field(ID, graphql_name='valueFactId')


class ResearchMapContentSelectInput(sgqlc.types.Input):
    __schema__ = utils_api_schema
    __field_names__ = ('nodes',)
    nodes = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='nodes')


class ResearchMapContentUpdateInput(sgqlc.types.Input):
    __schema__ = utils_api_schema
    __field_names__ = ('nodes',)
    nodes = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='nodes')


class ResearchMapFilterSettings(sgqlc.types.Input):
    __schema__ = utils_api_schema
    __field_names__ = ('access_level_id', 'concept_id', 'creation_date', 'creator', 'description', 'last_updater', 'markers', 'name', 'update_date')
    access_level_id = sgqlc.types.Field(ID, graphql_name='accessLevelId')
    concept_id = sgqlc.types.Field(ID, graphql_name='conceptId')
    creation_date = sgqlc.types.Field('TimestampIntervalInput', graphql_name='creationDate')
    creator = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='creator')
    description = sgqlc.types.Field(String, graphql_name='description')
    last_updater = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='lastUpdater')
    markers = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='markers')
    name = sgqlc.types.Field(String, graphql_name='name')
    update_date = sgqlc.types.Field('TimestampIntervalInput', graphql_name='updateDate')


class S3FileInput(sgqlc.types.Input):
    __schema__ = utils_api_schema
    __field_names__ = ('bucket_name', 'object_name')
    bucket_name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='bucketName')
    object_name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='objectName')


class StringFilterInput(sgqlc.types.Input):
    __schema__ = utils_api_schema
    __field_names__ = ('exact', 'str')
    exact = sgqlc.types.Field(Boolean, graphql_name='exact')
    str = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='str')


class StringLocaleValueInput(sgqlc.types.Input):
    __schema__ = utils_api_schema
    __field_names__ = ('locale', 'str')
    locale = sgqlc.types.Field(sgqlc.types.non_null(Locale), graphql_name='locale')
    str = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='str')


class StringValueInput(sgqlc.types.Input):
    __schema__ = utils_api_schema
    __field_names__ = ('str',)
    str = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='str')


class TextBoundingInput(sgqlc.types.Input):
    __schema__ = utils_api_schema
    __field_names__ = ('component_id', 'end', 'node_id', 'start')
    component_id = sgqlc.types.Field(ID, graphql_name='componentId')
    end = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='end')
    node_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='nodeId')
    start = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='start')


class TimeInput(sgqlc.types.Input):
    __schema__ = utils_api_schema
    __field_names__ = ('hour', 'minute', 'second')
    hour = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='hour')
    minute = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='minute')
    second = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='second')


class TimestampIntervalInput(sgqlc.types.Input):
    __schema__ = utils_api_schema
    __field_names__ = ('end', 'start')
    end = sgqlc.types.Field(UnixTime, graphql_name='end')
    start = sgqlc.types.Field(UnixTime, graphql_name='start')


class TimestampValueInput(sgqlc.types.Input):
    __schema__ = utils_api_schema
    __field_names__ = ('value',)
    value = sgqlc.types.Field(sgqlc.types.non_null(UnixTime), graphql_name='value')


class ValueFilterInput(sgqlc.types.Input):
    __schema__ = utils_api_schema
    __field_names__ = ('date_time_filter', 'double_filter', 'geo_filter', 'int_filter', 'string_filter')
    date_time_filter = sgqlc.types.Field(DateTimeIntervalInput, graphql_name='dateTimeFilter')
    double_filter = sgqlc.types.Field(DoubleIntervalInput, graphql_name='doubleFilter')
    geo_filter = sgqlc.types.Field(GeoPointWithNameInput, graphql_name='geoFilter')
    int_filter = sgqlc.types.Field(IntIntervalInput, graphql_name='intFilter')
    string_filter = sgqlc.types.Field(StringFilterInput, graphql_name='stringFilter')


class ValueInput(sgqlc.types.Input):
    __schema__ = utils_api_schema
    __field_names__ = ('date_time_value_input', 'double_value_input', 'geo_point_value_input', 'int_value_input', 'link_value_input', 'string_locale_value_input', 'string_value_input', 'timestamp_value_input')
    date_time_value_input = sgqlc.types.Field(DateTimeInput, graphql_name='dateTimeValueInput')
    double_value_input = sgqlc.types.Field(DoubleValueInput, graphql_name='doubleValueInput')
    geo_point_value_input = sgqlc.types.Field(GeoPointInput, graphql_name='geoPointValueInput')
    int_value_input = sgqlc.types.Field(IntValueInput, graphql_name='intValueInput')
    link_value_input = sgqlc.types.Field(LinkValueInput, graphql_name='linkValueInput')
    string_locale_value_input = sgqlc.types.Field(StringLocaleValueInput, graphql_name='stringLocaleValueInput')
    string_value_input = sgqlc.types.Field(StringValueInput, graphql_name='stringValueInput')
    timestamp_value_input = sgqlc.types.Field(TimestampValueInput, graphql_name='timestampValueInput')


class conceptTypeAndEventFilter(sgqlc.types.Input):
    __schema__ = utils_api_schema
    __field_names__ = ('full_type', 'is_event')
    full_type = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='fullType')
    is_event = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isEvent')



########################################################################
# Output Objects and Interfaces
########################################################################
class DocumentGroupFacet(sgqlc.types.Interface):
    __schema__ = utils_api_schema
    __field_names__ = ('count', 'group')
    count = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='count')
    group = sgqlc.types.Field(sgqlc.types.non_null(DocumentGroupingCategory), graphql_name='group')


class EntityTypePresentation(sgqlc.types.Interface):
    __schema__ = utils_api_schema
    __field_names__ = ('list_concept_link_type', 'metric', 'show_in_menu')
    list_concept_link_type = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ConceptLinkType'))), graphql_name='listConceptLinkType')
    metric = sgqlc.types.Field(sgqlc.types.non_null('EntityTypePresentationStatistics'), graphql_name='metric')
    show_in_menu = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='showInMenu')


class FactInterface(sgqlc.types.Interface):
    __schema__ = utils_api_schema
    __field_names__ = ('document', 'id', 'system_registration_date', 'system_update_date')
    document = sgqlc.types.Field(sgqlc.types.non_null('Document'), graphql_name='document')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    system_registration_date = sgqlc.types.Field(sgqlc.types.non_null(UnixTime), graphql_name='systemRegistrationDate')
    system_update_date = sgqlc.types.Field(UnixTime, graphql_name='systemUpdateDate')


class HasTypeSearchElements(sgqlc.types.Interface):
    __schema__ = utils_api_schema
    __field_names__ = ('list_black_dictionary', 'list_black_regexp', 'list_type_black_search_element', 'list_type_search_element', 'list_white_dictionary', 'list_white_regexp', 'pretrained_nercmodels')
    list_black_dictionary = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))), graphql_name='listBlackDictionary')
    list_black_regexp = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('NERCRegexp'))), graphql_name='listBlackRegexp')
    list_type_black_search_element = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('TypeSearchElement'))), graphql_name='listTypeBlackSearchElement')
    list_type_search_element = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('TypeSearchElement'))), graphql_name='listTypeSearchElement')
    list_white_dictionary = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))), graphql_name='listWhiteDictionary')
    list_white_regexp = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('NERCRegexp'))), graphql_name='listWhiteRegexp')
    pretrained_nercmodels = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))), graphql_name='pretrainedNERCModels')


class LinkTarget(sgqlc.types.Interface):
    __schema__ = utils_api_schema
    __field_names__ = ('pagination_link',)
    pagination_link = sgqlc.types.Field(sgqlc.types.non_null('ConceptLinkPagination'), graphql_name='paginationLink', args=sgqlc.types.ArgDict((
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(ConceptLinkFilterSettings), graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
))
    )


class LinkTypeTarget(sgqlc.types.Interface):
    __schema__ = utils_api_schema
    __field_names__ = ('list_link_type', 'pagination_link_type')
    list_link_type = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ConceptLinkType'))), graphql_name='listLinkType')
    pagination_link_type = sgqlc.types.Field(sgqlc.types.non_null('ConceptLinkTypePagination'), graphql_name='paginationLinkType', args=sgqlc.types.ArgDict((
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(ConceptLinkTypeFilterSettings), graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('sort_direction', sgqlc.types.Arg(SortDirection, graphql_name='sortDirection', default='descending')),
        ('sorting', sgqlc.types.Arg(ConceptLinkTypeSorting, graphql_name='sorting', default='id')),
))
    )


class MentionInterface(sgqlc.types.Interface):
    __schema__ = utils_api_schema
    __field_names__ = ('document', 'id', 'mention_fact', 'system_registration_date', 'system_update_date')
    document = sgqlc.types.Field(sgqlc.types.non_null('Document'), graphql_name='document')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    mention_fact = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(FactInterface))), graphql_name='mentionFact')
    system_registration_date = sgqlc.types.Field(sgqlc.types.non_null(UnixTime), graphql_name='systemRegistrationDate')
    system_update_date = sgqlc.types.Field(UnixTime, graphql_name='systemUpdateDate')


class PropertyTarget(sgqlc.types.Interface):
    __schema__ = utils_api_schema
    __field_names__ = ('pagination_property',)
    pagination_property = sgqlc.types.Field(sgqlc.types.non_null('ConceptPropertyPagination'), graphql_name='paginationProperty', args=sgqlc.types.ArgDict((
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(ConceptPropertyFilterSettings), graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
))
    )


class PropertyTypeTarget(sgqlc.types.Interface):
    __schema__ = utils_api_schema
    __field_names__ = ('list_property_type', 'pagination_property_type')
    list_property_type = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ConceptPropertyType'))), graphql_name='listPropertyType')
    pagination_property_type = sgqlc.types.Field(sgqlc.types.non_null('ConceptPropertyTypePagination'), graphql_name='paginationPropertyType', args=sgqlc.types.ArgDict((
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(ConceptPropertyTypeFilterSettings), graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('sort_direction', sgqlc.types.Arg(SortDirection, graphql_name='sortDirection', default='descending')),
        ('sorting', sgqlc.types.Arg(ConceptPropertyTypeSorting, graphql_name='sorting', default='name')),
))
    )


class RecordInterface(sgqlc.types.Interface):
    __schema__ = utils_api_schema
    __field_names__ = ('creator', 'last_updater', 'system_registration_date', 'system_update_date')
    creator = sgqlc.types.Field(sgqlc.types.non_null('User'), graphql_name='creator')
    last_updater = sgqlc.types.Field('User', graphql_name='lastUpdater')
    system_registration_date = sgqlc.types.Field(sgqlc.types.non_null(UnixTime), graphql_name='systemRegistrationDate')
    system_update_date = sgqlc.types.Field(UnixTime, graphql_name='systemUpdateDate')


class EntityType(sgqlc.types.Interface):
    __schema__ = utils_api_schema
    __field_names__ = ('full_dictionary', 'id', 'image', 'list_black_dictionary', 'list_black_regexp', 'list_concept_header_property_type', 'list_concept_link_type', 'list_concept_property_type', 'list_link_type', 'list_names_dictionary', 'list_property_type', 'list_type_black_search_element', 'list_type_search_element', 'list_white_dictionary', 'list_white_regexp', 'metric', 'name', 'non_configurable_dictionary', 'pagination_concept_link_type', 'pagination_concept_property_type', 'pagination_link_type', 'pagination_property_type', 'pretrained_nercmodels')
    full_dictionary = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))), graphql_name='fullDictionary')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    image = sgqlc.types.Field('Image', graphql_name='image')
    list_black_dictionary = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))), graphql_name='listBlackDictionary')
    list_black_regexp = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('NERCRegexp'))), graphql_name='listBlackRegexp')
    list_concept_header_property_type = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ConceptPropertyType'))), graphql_name='listConceptHeaderPropertyType')
    list_concept_link_type = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ConceptLinkType'))), graphql_name='listConceptLinkType')
    list_concept_property_type = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ConceptPropertyType'))), graphql_name='listConceptPropertyType')
    list_link_type = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ConceptLinkType'))), graphql_name='listLinkType')
    list_names_dictionary = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))), graphql_name='listNamesDictionary')
    list_property_type = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ConceptPropertyType'))), graphql_name='listPropertyType')
    list_type_black_search_element = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('TypeSearchElement'))), graphql_name='listTypeBlackSearchElement')
    list_type_search_element = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('TypeSearchElement'))), graphql_name='listTypeSearchElement')
    list_white_dictionary = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))), graphql_name='listWhiteDictionary')
    list_white_regexp = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('NERCRegexp'))), graphql_name='listWhiteRegexp')
    metric = sgqlc.types.Field(sgqlc.types.non_null('EntityTypeStatistics'), graphql_name='metric')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    non_configurable_dictionary = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))), graphql_name='nonConfigurableDictionary')
    pagination_concept_link_type = sgqlc.types.Field(sgqlc.types.non_null('ConceptLinkTypePagination'), graphql_name='paginationConceptLinkType', args=sgqlc.types.ArgDict((
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(ConceptLinkTypeFilterSettings), graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('sort_direction', sgqlc.types.Arg(SortDirection, graphql_name='sortDirection', default='descending')),
        ('sorting', sgqlc.types.Arg(ConceptLinkTypeSorting, graphql_name='sorting', default='id')),
))
    )
    pagination_concept_property_type = sgqlc.types.Field(sgqlc.types.non_null('ConceptPropertyTypePagination'), graphql_name='paginationConceptPropertyType', args=sgqlc.types.ArgDict((
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(ConceptPropertyTypeFilterSettings), graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('sort_direction', sgqlc.types.Arg(SortDirection, graphql_name='sortDirection', default='descending')),
        ('sorting', sgqlc.types.Arg(ConceptPropertyTypeSorting, graphql_name='sorting', default='name')),
))
    )
    pagination_link_type = sgqlc.types.Field(sgqlc.types.non_null('ConceptLinkTypePagination'), graphql_name='paginationLinkType', args=sgqlc.types.ArgDict((
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(ConceptLinkTypeFilterSettings), graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('sort_direction', sgqlc.types.Arg(SortDirection, graphql_name='sortDirection', default='descending')),
        ('sorting', sgqlc.types.Arg(ConceptLinkTypeSorting, graphql_name='sorting', default='id')),
))
    )
    pagination_property_type = sgqlc.types.Field(sgqlc.types.non_null('ConceptPropertyTypePagination'), graphql_name='paginationPropertyType', args=sgqlc.types.ArgDict((
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(ConceptPropertyTypeFilterSettings), graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('sort_direction', sgqlc.types.Arg(SortDirection, graphql_name='sortDirection', default='descending')),
        ('sorting', sgqlc.types.Arg(ConceptPropertyTypeSorting, graphql_name='sorting', default='name')),
))
    )
    pretrained_nercmodels = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))), graphql_name='pretrainedNERCModels')


class KBEntity(sgqlc.types.Interface):
    __schema__ = utils_api_schema
    __field_names__ = ('id', 'list_header_property', 'pagination_link', 'pagination_property')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    list_header_property = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('HeaderProperty'))), graphql_name='listHeaderProperty')
    pagination_link = sgqlc.types.Field(sgqlc.types.non_null('ConceptLinkPagination'), graphql_name='paginationLink', args=sgqlc.types.ArgDict((
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(ConceptLinkFilterSettings), graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
))
    )
    pagination_property = sgqlc.types.Field(sgqlc.types.non_null('ConceptPropertyPagination'), graphql_name='paginationProperty', args=sgqlc.types.ArgDict((
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(ConceptPropertyFilterSettings), graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
))
    )


class AccessLevel(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('id', 'name', 'order')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    order = sgqlc.types.Field(sgqlc.types.non_null(Long), graphql_name='order')


class AccessLevelPagination(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('list_access_level', 'total')
    list_access_level = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(AccessLevel))), graphql_name='listAccessLevel')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class AccountPagination(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('list_account', 'total', 'total_platforms')
    list_account = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('Account'))), graphql_name='listAccount')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')
    total_platforms = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='totalPlatforms')


class AccountStatistics(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('count_doc',)
    count_doc = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='countDoc')


class Annotation(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('end', 'start', 'value')
    end = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='end')
    start = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='start')
    value = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='value')


class CompositePropertyValueTemplatePagination(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('list_composite_property_value_template', 'total')
    list_composite_property_value_template = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('CompositePropertyValueTemplate'))), graphql_name='listCompositePropertyValueTemplate')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class CompositePropertyValueType(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('id', 'is_required', 'name', 'value_type', 'view')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    is_required = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isRequired')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    value_type = sgqlc.types.Field(sgqlc.types.non_null('ConceptPropertyValueType'), graphql_name='valueType')
    view = sgqlc.types.Field(sgqlc.types.non_null(ComponentView), graphql_name='view')


class CompositeValue(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('list_value',)
    list_value = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('NamedValue'))), graphql_name='listValue')


class ConceptDedupTask(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('id',)
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')


class ConceptDuplicate(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('concept', 'group', 'id')
    concept = sgqlc.types.Field(sgqlc.types.non_null('Concept'), graphql_name='concept')
    group = sgqlc.types.Field(sgqlc.types.non_null('ConceptDuplicateGroup'), graphql_name='group')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')


class ConceptDuplicateGroup(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('id', 'main_concept', 'metric', 'pagination_concept_duplicate', 'report')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    main_concept = sgqlc.types.Field(sgqlc.types.non_null('Concept'), graphql_name='mainConcept')
    metric = sgqlc.types.Field(sgqlc.types.non_null('ConceptDuplicateGroupMetrics'), graphql_name='metric')
    pagination_concept_duplicate = sgqlc.types.Field(sgqlc.types.non_null('ConceptDuplicatePagination'), graphql_name='paginationConceptDuplicate', args=sgqlc.types.ArgDict((
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(ConceptDuplicateFilterSettings), graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
))
    )
    report = sgqlc.types.Field(sgqlc.types.non_null('ConceptDuplicateReport'), graphql_name='report')


class ConceptDuplicateGroupMetrics(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('concept_duplicate_count',)
    concept_duplicate_count = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='conceptDuplicateCount')


class ConceptDuplicateGroupPagination(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('list_concept_duplicate_group', 'total')
    list_concept_duplicate_group = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ConceptDuplicateGroup))), graphql_name='listConceptDuplicateGroup')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class ConceptDuplicatePagination(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('list_concept_duplicate', 'total')
    list_concept_duplicate = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ConceptDuplicate))), graphql_name='listConceptDuplicate')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class ConceptDuplicateReportMetrics(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('group_count',)
    group_count = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='groupCount')


class ConceptFactPagination(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('list_concept_fact', 'total')
    list_concept_fact = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ConceptFact'))), graphql_name='listConceptFact')
    total = sgqlc.types.Field(sgqlc.types.non_null(Long), graphql_name='total')


class ConceptLinkFactPagination(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('list_concept_link_fact', 'total')
    list_concept_link_fact = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ConceptLinkFact'))), graphql_name='listConceptLinkFact')
    total = sgqlc.types.Field(sgqlc.types.non_null(Long), graphql_name='total')


class ConceptLinkPagination(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('list_concept_link', 'total')
    list_concept_link = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ConceptLink'))), graphql_name='listConceptLink')
    total = sgqlc.types.Field(sgqlc.types.non_null(Long), graphql_name='total')


class ConceptLinkTypePagination(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('list_concept_link_type', 'total')
    list_concept_link_type = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ConceptLinkType'))), graphql_name='listConceptLinkType')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class ConceptLinkTypePath(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('fixed', 'link_type')
    fixed = sgqlc.types.Field(ConceptLinkDirection, graphql_name='fixed')
    link_type = sgqlc.types.Field(sgqlc.types.non_null('ConceptLinkType'), graphql_name='linkType')


class ConceptLinkTypeStatistics(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('count_property_type',)
    count_property_type = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='countPropertyType')


class ConceptMetrics(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('facts', 'links', 'merged_concepts', 'not_approved_facts', 'not_approved_links', 'not_approved_properties', 'properties', 'research_maps')
    facts = sgqlc.types.Field(Int, graphql_name='facts')
    links = sgqlc.types.Field(Int, graphql_name='links')
    merged_concepts = sgqlc.types.Field(Int, graphql_name='mergedConcepts')
    not_approved_facts = sgqlc.types.Field(Int, graphql_name='notApprovedFacts')
    not_approved_links = sgqlc.types.Field(Int, graphql_name='notApprovedLinks')
    not_approved_properties = sgqlc.types.Field(Int, graphql_name='notApprovedProperties')
    properties = sgqlc.types.Field(Int, graphql_name='properties')
    research_maps = sgqlc.types.Field(Int, graphql_name='researchMaps')


class ConceptPagination(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('list_concept', 'precise_total', 'show_total', 'total')
    list_concept = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('Concept'))), graphql_name='listConcept')
    precise_total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='preciseTotal')
    show_total = sgqlc.types.Field(sgqlc.types.non_null(Long), graphql_name='showTotal')
    total = sgqlc.types.Field(sgqlc.types.non_null(Long), graphql_name='total')


class ConceptPropertyPagination(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('list_concept_property', 'total')
    list_concept_property = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ConceptProperty'))), graphql_name='listConceptProperty')
    total = sgqlc.types.Field(sgqlc.types.non_null(Long), graphql_name='total')


class ConceptPropertyTypePagination(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('list_concept_property_type', 'total')
    list_concept_property_type = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ConceptPropertyType'))), graphql_name='listConceptPropertyType')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class ConceptPropertyValueStatistics(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('count_concept_type', 'count_dictionary', 'count_link_type', 'count_regexp')
    count_concept_type = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='countConceptType')
    count_dictionary = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='countDictionary')
    count_link_type = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='countLinkType')
    count_regexp = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='countRegexp')


class ConceptPropertyValueTypePagination(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('list_concept_property_value_type', 'total')
    list_concept_property_value_type = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ConceptPropertyValueType'))), graphql_name='listConceptPropertyValueType')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class ConceptSubscriptions(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('count_users', 'list_user', 'subscriptions')
    count_users = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='countUsers')
    list_user = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('User'))), graphql_name='listUser')
    subscriptions = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ConceptUpdate))), graphql_name='subscriptions')


class ConceptTypePagination(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('list_concept_type', 'total')
    list_concept_type = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ConceptType'))), graphql_name='listConceptType')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class ConceptTypePresentationWidgetTypeColumn(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('concept_link_types_path', 'id', 'is_main_properties', 'link_metadata', 'link_property_type', 'list_values', 'metadata', 'name', 'property_type', 'sort_by_column', 'sort_direction', 'sortable')
    concept_link_types_path = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ConceptLinkTypePath))), graphql_name='conceptLinkTypesPath')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    is_main_properties = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isMainProperties')
    link_metadata = sgqlc.types.Field(ConceptTypeLinkMetadata, graphql_name='linkMetadata')
    link_property_type = sgqlc.types.Field('ConceptPropertyType', graphql_name='linkPropertyType')
    list_values = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='listValues')
    metadata = sgqlc.types.Field(ConceptTypeMetadata, graphql_name='metadata')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    property_type = sgqlc.types.Field('ConceptPropertyType', graphql_name='propertyType')
    sort_by_column = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='sortByColumn')
    sort_direction = sgqlc.types.Field(SortDirection, graphql_name='sortDirection')
    sortable = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='sortable')


class ConceptTypePresentationWidgetTypePagination(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('list_concept_type_presentation_widget', 'total')
    list_concept_type_presentation_widget = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ConceptTypePresentationWidgetType'))), graphql_name='listConceptTypePresentationWidget')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class ConceptTypeViewPagination(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('list_concept_type_view', 'total')
    list_concept_type_view = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ConceptTypeView'))), graphql_name='listConceptTypeView')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class ConceptView(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('concept', 'rows')
    concept = sgqlc.types.Field(sgqlc.types.non_null('Concept'), graphql_name='concept')
    rows = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ConceptViewValue'))))), graphql_name='rows')


class ConceptViewPagination(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('list_concept_view', 'total')
    list_concept_view = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ConceptView))), graphql_name='listConceptView')
    total = sgqlc.types.Field(sgqlc.types.non_null(Long), graphql_name='total')


class ConceptWithConfidence(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('concept', 'confidence')
    concept = sgqlc.types.Field(sgqlc.types.non_null('Concept'), graphql_name='concept')
    confidence = sgqlc.types.Field(Float, graphql_name='confidence')


class Coordinates(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('latitude', 'longitude')
    latitude = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='latitude')
    longitude = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='longitude')


class Date(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('day', 'month', 'year')
    day = sgqlc.types.Field(Int, graphql_name='day')
    month = sgqlc.types.Field(Int, graphql_name='month')
    year = sgqlc.types.Field(Int, graphql_name='year')


class DateTimeInterval(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('end', 'start')
    end = sgqlc.types.Field('DateTimeValue', graphql_name='end')
    start = sgqlc.types.Field('DateTimeValue', graphql_name='start')


class DateTimeValue(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('date', 'time')
    date = sgqlc.types.Field(sgqlc.types.non_null(Date), graphql_name='date')
    time = sgqlc.types.Field('Time', graphql_name='time')


class DictValue(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('value',)
    value = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='value')


class DocumentFacets(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('approved_entities_facets', 'calculated_at', 'document_metadata_facets', 'id', 'not_approved_entities_facets')
    approved_entities_facets = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(DocumentGroupFacet)), graphql_name='approvedEntitiesFacets')
    calculated_at = sgqlc.types.Field(UnixTime, graphql_name='calculatedAt')
    document_metadata_facets = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(DocumentGroupFacet)), graphql_name='documentMetadataFacets')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    not_approved_entities_facets = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(DocumentGroupFacet)), graphql_name='notApprovedEntitiesFacets')


class DocumentLink(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('child_id', 'parent_id')
    child_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='childId')
    parent_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='parentId')


class DocumentMetadata(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('access_time', 'account', 'created_time', 'file_name', 'file_type', 'job_id', 'language', 'modified_time', 'periodic_job_id', 'periodic_task_id', 'platform', 'size', 'source', 'task_id')
    access_time = sgqlc.types.Field(sgqlc.types.non_null(UnixTime), graphql_name='accessTime')
    account = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('Account'))), graphql_name='account')
    created_time = sgqlc.types.Field(sgqlc.types.non_null(UnixTime), graphql_name='createdTime')
    file_name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='fileName')
    file_type = sgqlc.types.Field(String, graphql_name='fileType')
    job_id = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='jobId')
    language = sgqlc.types.Field('Language', graphql_name='language')
    modified_time = sgqlc.types.Field(sgqlc.types.non_null(UnixTime), graphql_name='modifiedTime')
    periodic_job_id = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='periodicJobId')
    periodic_task_id = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='periodicTaskId')
    platform = sgqlc.types.Field('Platform', graphql_name='platform')
    size = sgqlc.types.Field(sgqlc.types.non_null(Long), graphql_name='size')
    source = sgqlc.types.Field(String, graphql_name='source')
    task_id = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='taskId')


class DocumentMetrics(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('child_documents', 'concepts', 'facts', 'links', 'not_approved_concepts', 'not_approved_links', 'not_approved_properties', 'properties', 'research_maps')
    child_documents = sgqlc.types.Field(Int, graphql_name='childDocuments')
    concepts = sgqlc.types.Field(Int, graphql_name='concepts')
    facts = sgqlc.types.Field(Int, graphql_name='facts')
    links = sgqlc.types.Field(Int, graphql_name='links')
    not_approved_concepts = sgqlc.types.Field(Int, graphql_name='notApprovedConcepts')
    not_approved_links = sgqlc.types.Field(Int, graphql_name='notApprovedLinks')
    not_approved_properties = sgqlc.types.Field(Int, graphql_name='notApprovedProperties')
    properties = sgqlc.types.Field(Int, graphql_name='properties')
    research_maps = sgqlc.types.Field(Int, graphql_name='researchMaps')


class DocumentPagination(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('list_document', 'total')
    list_document = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('Document'))), graphql_name='listDocument')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class DocumentSubscriptions(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('count_users', 'list_user', 'subscriptions')
    count_users = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='countUsers')
    list_user = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('User'))), graphql_name='listUser')
    subscriptions = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(DocumentUpdate))), graphql_name='subscriptions')


class DocumentTextPagination(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('pagination_text', 'total')
    pagination_text = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('FlatDocumentStructure'))))), graphql_name='paginationText')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class DocumentTypePagination(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('list_document_type', 'total')
    list_document_type = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('DocumentType'))), graphql_name='listDocumentType')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class DomainUpdateInfo(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('name', 'update_date')
    name = sgqlc.types.Field(sgqlc.types.non_null(DomainName), graphql_name='name')
    update_date = sgqlc.types.Field(UnixTime, graphql_name='updateDate')


class DoubleValue(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('value',)
    value = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='value')


class EntityTypePresentationStatistics(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('count_concept_types', 'count_document_types', 'count_entity_types')
    count_concept_types = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='countConceptTypes')
    count_document_types = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='countDocumentTypes')
    count_entity_types = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='countEntityTypes')


class EntityTypeStatistics(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('count_dictionary', 'count_link_type', 'count_property_type', 'count_regexp')
    count_dictionary = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='countDictionary')
    count_link_type = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='countLinkType')
    count_property_type = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='countPropertyType')
    count_regexp = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='countRegexp')


class FlatDocumentStructure(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('annotations', 'document_id', 'hierarchy_level', 'id', 'is_main', 'language', 'metadata', 'node_id', 'text', 'translated_text', 'translation_mention')
    annotations = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(Annotation))), graphql_name='annotations')
    document_id = sgqlc.types.Field(ID, graphql_name='documentId')
    hierarchy_level = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='hierarchyLevel')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    is_main = sgqlc.types.Field(Boolean, graphql_name='isMain')
    language = sgqlc.types.Field('Language', graphql_name='language')
    metadata = sgqlc.types.Field(sgqlc.types.non_null('ParagraphMetadata'), graphql_name='metadata')
    node_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='nodeId')
    text = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='text')
    translated_text = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='translatedText')
    translation_mention = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('MentionUnion'))), graphql_name='translationMention')


class GeoConceptProperty(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('concept', 'concept_property')
    concept = sgqlc.types.Field(sgqlc.types.non_null('Concept'), graphql_name='concept')
    concept_property = sgqlc.types.Field(sgqlc.types.non_null('ConceptProperty'), graphql_name='conceptProperty')


class GeoPointValue(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('name', 'point')
    name = sgqlc.types.Field(String, graphql_name='name')
    point = sgqlc.types.Field(Coordinates, graphql_name='point')


class Group(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('annotation', 'collapsed', 'id', 'layout', 'name', 'x_coordinate', 'y_coordinate')
    annotation = sgqlc.types.Field('MapAnnotation', graphql_name='annotation')
    collapsed = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='collapsed')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    layout = sgqlc.types.Field(String, graphql_name='layout')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    x_coordinate = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='xCoordinate')
    y_coordinate = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='yCoordinate')


class HLAnnotation(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('end', 'start')
    end = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='end')
    start = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='start')


class HeaderProperty(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('property_type', 'values')
    property_type = sgqlc.types.Field(sgqlc.types.non_null('ConceptPropertyType'), graphql_name='propertyType')
    values = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('AnyValue'))), graphql_name='values')


class Highlighting(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('annotations', 'highlighting')
    annotations = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(HLAnnotation))), graphql_name='annotations')
    highlighting = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='highlighting')


class Image(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('bucket_name', 'object_name')
    bucket_name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='bucketName')
    object_name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='objectName')


class IntValue(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('value',)
    value = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='value')


class Language(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('id',)
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')


class LinkValue(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('link',)
    link = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='link')


class MapDrawing(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('annotation', 'dashed', 'geo', 'id', 'opacity', 'stroke_color', 'stroke_width', 'x_coordinate', 'y_coordinate')
    annotation = sgqlc.types.Field('MapAnnotation', graphql_name='annotation')
    dashed = sgqlc.types.Field(Boolean, graphql_name='dashed')
    geo = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='geo')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    opacity = sgqlc.types.Field(Float, graphql_name='opacity')
    stroke_color = sgqlc.types.Field(String, graphql_name='strokeColor')
    stroke_width = sgqlc.types.Field(String, graphql_name='strokeWidth')
    x_coordinate = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='xCoordinate')
    y_coordinate = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='yCoordinate')


class MapEdge(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('annotation', 'from_id', 'id', 'link', 'link_type', 'to_id')
    annotation = sgqlc.types.Field('MapAnnotation', graphql_name='annotation')
    from_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='fromID')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    link = sgqlc.types.Field(sgqlc.types.non_null('EntityLink'), graphql_name='link')
    link_type = sgqlc.types.Field(sgqlc.types.non_null(MapEdgeType), graphql_name='linkType')
    to_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='toID')


class MapNode(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('annotation', 'entity', 'group_id', 'id', 'node_type', 'x_coordinate', 'y_coordinate')
    annotation = sgqlc.types.Field('MapAnnotation', graphql_name='annotation')
    entity = sgqlc.types.Field(sgqlc.types.non_null('Entity'), graphql_name='entity')
    group_id = sgqlc.types.Field(ID, graphql_name='groupId')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    node_type = sgqlc.types.Field(sgqlc.types.non_null(MapNodeType), graphql_name='nodeType')
    x_coordinate = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='xCoordinate')
    y_coordinate = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='yCoordinate')


class MentionLink(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('id', 'mention_link_type', 'source', 'target')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    mention_link_type = sgqlc.types.Field(sgqlc.types.non_null(MentionLinkType), graphql_name='mentionLinkType')
    source = sgqlc.types.Field(sgqlc.types.non_null('MentionUnion'), graphql_name='source')
    target = sgqlc.types.Field(sgqlc.types.non_null('MentionUnion'), graphql_name='target')


class MergedConcept(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('concept', 'merge_author', 'merge_date')
    concept = sgqlc.types.Field(sgqlc.types.non_null('Concept'), graphql_name='concept')
    merge_author = sgqlc.types.Field(sgqlc.types.non_null('User'), graphql_name='mergeAuthor')
    merge_date = sgqlc.types.Field(sgqlc.types.non_null(UnixTime), graphql_name='mergeDate')


class MergedConceptPagination(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('list_merged_concept', 'total')
    list_merged_concept = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(MergedConcept))), graphql_name='listMergedConcept')
    total = sgqlc.types.Field(sgqlc.types.non_null(Long), graphql_name='total')


class Mutation(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('add_document_to_original_document_internal', 'get_or_add_account_internal', 'get_or_add_concept_internal', 'get_or_add_concept_new_internal', 'get_or_add_platform_internal', 'reserve_concept_uuidv7', 'update_document_facts_internal')
    add_document_to_original_document_internal = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='addDocumentToOriginalDocumentInternal', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(AddDocumentToOriginalDocumentInput), graphql_name='input', default=None)),
))
    )
    get_or_add_account_internal = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='getOrAddAccountInternal', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(AccountGetOrCreateInput), graphql_name='form', default=None)),
))
    )
    get_or_add_concept_internal = sgqlc.types.Field(sgqlc.types.non_null('Concept'), graphql_name='getOrAddConceptInternal', args=sgqlc.types.ArgDict((
        ('file', sgqlc.types.Arg(S3FileInput, graphql_name='file', default=None)),
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(ConceptFilterSettings), graphql_name='filterSettings', default=None)),
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(ConceptMutationInput), graphql_name='form', default=None)),
        ('take_first_result', sgqlc.types.Arg(Boolean, graphql_name='takeFirstResult', default=False)),
))
    )
    get_or_add_concept_new_internal = sgqlc.types.Field(sgqlc.types.non_null('Concept'), graphql_name='getOrAddConceptNewInternal', args=sgqlc.types.ArgDict((
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(ConceptFilterSettings), graphql_name='filterSettings', default=None)),
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(ConceptFactsCreationInput), graphql_name='form', default=None)),
        ('take_first_result', sgqlc.types.Arg(Boolean, graphql_name='takeFirstResult', default=False)),
))
    )
    get_or_add_platform_internal = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='getOrAddPlatformInternal', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(PlatformGetOrCreateInput), graphql_name='form', default=None)),
))
    )
    reserve_concept_uuidv7 = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='reserveConceptUUIDv7', args=sgqlc.types.ArgDict((
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(ConceptFilterSettings), graphql_name='filterSettings', default=None)),
))
    )
    update_document_facts_internal = sgqlc.types.Field(sgqlc.types.non_null('StateWithErrors'), graphql_name='updateDocumentFactsInternal', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(BatchUpdateFactInput), graphql_name='form', default=None)),
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )


class NERCRegexp(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('auto_create', 'context_regexp', 'regexp')
    auto_create = sgqlc.types.Field(Boolean, graphql_name='autoCreate')
    context_regexp = sgqlc.types.Field(String, graphql_name='contextRegexp')
    regexp = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='regexp')


class NamedValue(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('id', 'property_value_type', 'value')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    property_value_type = sgqlc.types.Field(sgqlc.types.non_null(CompositePropertyValueType), graphql_name='propertyValueType')
    value = sgqlc.types.Field(sgqlc.types.non_null('Value'), graphql_name='value')


class ParagraphMetadata(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('bullet', 'colspan', 'content_type', 'duration', 'header', 'height', 'hidden', 'language', 'line_id', 'md5', 'name', 'original_text', 'page_id', 'paragraph_type', 'rowspan', 'size', 'width')
    bullet = sgqlc.types.Field(String, graphql_name='bullet')
    colspan = sgqlc.types.Field(Int, graphql_name='colspan')
    content_type = sgqlc.types.Field(String, graphql_name='contentType')
    duration = sgqlc.types.Field(Int, graphql_name='duration')
    header = sgqlc.types.Field(Boolean, graphql_name='header')
    height = sgqlc.types.Field(Int, graphql_name='height')
    hidden = sgqlc.types.Field(Boolean, graphql_name='hidden')
    language = sgqlc.types.Field(String, graphql_name='language')
    line_id = sgqlc.types.Field(Int, graphql_name='lineId')
    md5 = sgqlc.types.Field(String, graphql_name='md5')
    name = sgqlc.types.Field(String, graphql_name='name')
    original_text = sgqlc.types.Field(String, graphql_name='originalText')
    page_id = sgqlc.types.Field(Int, graphql_name='pageId')
    paragraph_type = sgqlc.types.Field(sgqlc.types.non_null(NodeType), graphql_name='paragraphType')
    rowspan = sgqlc.types.Field(Int, graphql_name='rowspan')
    size = sgqlc.types.Field(Int, graphql_name='size')
    width = sgqlc.types.Field(Int, graphql_name='width')


class Parameter(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('key', 'value')
    key = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='key')
    value = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='value')


class PlatformPagination(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('list_platform', 'total')
    list_platform = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('Platform'))), graphql_name='listPlatform')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class PlatformStatistics(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('count_account', 'count_doc')
    count_account = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='countAccount')
    count_doc = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='countDoc')


class Query(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('document_uuid_internal', 'domain_update_info_internal', 'pagination_access_level_internal', 'pagination_account_internal', 'pagination_composite_property_value_template_internal', 'pagination_concept_internal', 'pagination_concept_link_property_type_internal', 'pagination_concept_link_type_internal', 'pagination_concept_property_internal', 'pagination_concept_property_type_internal', 'pagination_concept_property_value_type_internal', 'pagination_concept_type_internal', 'pagination_document_type_internal', 'pagination_platform_internal', 'pagination_property_type_internal', 'tdm_internal', 'tdm_new_internal')
    document_uuid_internal = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='documentUuidInternal', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    domain_update_info_internal = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(DomainUpdateInfo))), graphql_name='domainUpdateInfoInternal')
    pagination_access_level_internal = sgqlc.types.Field(sgqlc.types.non_null(AccessLevelPagination), graphql_name='paginationAccessLevelInternal', args=sgqlc.types.ArgDict((
        ('direction', sgqlc.types.Arg(SortDirection, graphql_name='direction', default='descending')),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('query', sgqlc.types.Arg(String, graphql_name='query', default=None)),
        ('sort_field', sgqlc.types.Arg(AccessLevelSorting, graphql_name='sortField', default='id')),
))
    )
    pagination_account_internal = sgqlc.types.Field(sgqlc.types.non_null(AccountPagination), graphql_name='paginationAccountInternal', args=sgqlc.types.ArgDict((
        ('direction', sgqlc.types.Arg(SortDirection, graphql_name='direction', default='descending')),
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(AccountFilterSettings), graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('sort_field', sgqlc.types.Arg(AccountSorting, graphql_name='sortField', default='id')),
))
    )
    pagination_composite_property_value_template_internal = sgqlc.types.Field(sgqlc.types.non_null(CompositePropertyValueTemplatePagination), graphql_name='paginationCompositePropertyValueTemplateInternal', args=sgqlc.types.ArgDict((
        ('direction', sgqlc.types.Arg(SortDirection, graphql_name='direction', default='descending')),
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(CompositePropertyValueTemplateFilterSettings), graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('sort_field', sgqlc.types.Arg(CompositePropertyValueTemplateSorting, graphql_name='sortField', default='id')),
))
    )
    pagination_concept_internal = sgqlc.types.Field(ConceptPagination, graphql_name='paginationConceptInternal', args=sgqlc.types.ArgDict((
        ('direction', sgqlc.types.Arg(SortDirection, graphql_name='direction', default='descending')),
        ('filter_settings', sgqlc.types.Arg(ConceptFilterSettings, graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('sort_field', sgqlc.types.Arg(ConceptSorting, graphql_name='sortField', default='score')),
))
    )
    pagination_concept_link_property_type_internal = sgqlc.types.Field(sgqlc.types.non_null(ConceptPropertyTypePagination), graphql_name='paginationConceptLinkPropertyTypeInternal', args=sgqlc.types.ArgDict((
        ('direction', sgqlc.types.Arg(SortDirection, graphql_name='direction', default='descending')),
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(ConceptPropertyTypeFilterSettings), graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('sort_field', sgqlc.types.Arg(ConceptPropertyTypeSorting, graphql_name='sortField', default='name')),
))
    )
    pagination_concept_link_type_internal = sgqlc.types.Field(sgqlc.types.non_null(ConceptLinkTypePagination), graphql_name='paginationConceptLinkTypeInternal', args=sgqlc.types.ArgDict((
        ('direction', sgqlc.types.Arg(SortDirection, graphql_name='direction', default='descending')),
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(ConceptLinkTypeFilterSettings), graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('sort_field', sgqlc.types.Arg(ConceptLinkTypeSorting, graphql_name='sortField', default='id')),
))
    )
    pagination_concept_property_internal = sgqlc.types.Field(sgqlc.types.non_null(ConceptPropertyPagination), graphql_name='paginationConceptPropertyInternal', args=sgqlc.types.ArgDict((
        ('concept_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='conceptId', default=None)),
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(ConceptPropertyFilterSettings), graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
))
    )
    pagination_concept_property_type_internal = sgqlc.types.Field(sgqlc.types.non_null(ConceptPropertyTypePagination), graphql_name='paginationConceptPropertyTypeInternal', args=sgqlc.types.ArgDict((
        ('direction', sgqlc.types.Arg(SortDirection, graphql_name='direction', default='descending')),
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(ConceptPropertyTypeFilterSettings), graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('sort_field', sgqlc.types.Arg(ConceptPropertyTypeSorting, graphql_name='sortField', default='name')),
))
    )
    pagination_concept_property_value_type_internal = sgqlc.types.Field(sgqlc.types.non_null(ConceptPropertyValueTypePagination), graphql_name='paginationConceptPropertyValueTypeInternal', args=sgqlc.types.ArgDict((
        ('direction', sgqlc.types.Arg(SortDirection, graphql_name='direction', default='descending')),
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(ConceptPropertyValueTypeFilterSettings), graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('sort_field', sgqlc.types.Arg(ConceptPropertyValueTypeSorting, graphql_name='sortField', default='id')),
))
    )
    pagination_concept_type_internal = sgqlc.types.Field(sgqlc.types.non_null(ConceptTypePagination), graphql_name='paginationConceptTypeInternal', args=sgqlc.types.ArgDict((
        ('direction', sgqlc.types.Arg(SortDirection, graphql_name='direction', default='descending')),
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(ConceptTypeFilterSettings), graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('sort_field', sgqlc.types.Arg(ConceptTypeSorting, graphql_name='sortField', default='id')),
))
    )
    pagination_document_type_internal = sgqlc.types.Field(sgqlc.types.non_null(DocumentTypePagination), graphql_name='paginationDocumentTypeInternal', args=sgqlc.types.ArgDict((
        ('direction', sgqlc.types.Arg(SortDirection, graphql_name='direction', default='descending')),
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(DocumentTypeFilterSettings), graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('sort_field', sgqlc.types.Arg(DocumentTypeSorting, graphql_name='sortField', default='id')),
))
    )
    pagination_platform_internal = sgqlc.types.Field(sgqlc.types.non_null(PlatformPagination), graphql_name='paginationPlatformInternal', args=sgqlc.types.ArgDict((
        ('direction', sgqlc.types.Arg(SortDirection, graphql_name='direction', default='descending')),
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(PlatformFilterSettings), graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('sort_field', sgqlc.types.Arg(PlatformSorting, graphql_name='sortField', default='id')),
))
    )
    pagination_property_type_internal = sgqlc.types.Field(sgqlc.types.non_null(ConceptPropertyTypePagination), graphql_name='paginationPropertyTypeInternal', args=sgqlc.types.ArgDict((
        ('direction', sgqlc.types.Arg(SortDirection, graphql_name='direction', default='descending')),
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(ConceptPropertyTypeFilterSettings), graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('sort_field', sgqlc.types.Arg(ConceptPropertyTypeSorting, graphql_name='sortField', default='name')),
))
    )
    tdm_internal = sgqlc.types.Field(sgqlc.types.non_null(JSON), graphql_name='tdmInternal', args=sgqlc.types.ArgDict((
        ('hide_new', sgqlc.types.Arg(sgqlc.types.non_null(Boolean), graphql_name='hideNew', default=False)),
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    tdm_new_internal = sgqlc.types.Field(sgqlc.types.non_null(JSON), graphql_name='tdmNewInternal', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )


class RelExtModel(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('invert_direction', 'relation_type', 'source_annotation_type', 'target_annotation_type')
    invert_direction = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='invertDirection')
    relation_type = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='relationType')
    source_annotation_type = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='sourceAnnotationType')
    target_annotation_type = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='targetAnnotationType')


class ResearchMapPagination(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('list_research_map', 'total')
    list_research_map = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ResearchMap'))), graphql_name='listResearchMap')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class ResearchMapStatistics(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('concept_and_document_num', 'concept_num', 'document_num', 'event_num', 'object_num')
    concept_and_document_num = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='conceptAndDocumentNum')
    concept_num = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='conceptNum')
    document_num = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='documentNum')
    event_num = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='eventNum')
    object_num = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='objectNum')


class RubricFacet(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('list_child_rubric_facet', 'own_documents_count', 'rubric', 'subtree_documents_count')
    list_child_rubric_facet = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('RubricFacet'))), graphql_name='listChildRubricFacet')
    own_documents_count = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='ownDocumentsCount')
    rubric = sgqlc.types.Field(sgqlc.types.non_null('Rubric'), graphql_name='rubric')
    subtree_documents_count = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='subtreeDocumentsCount')


class RubricationFacets(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('calculated_at', 'id', 'list_rubricator_facet')
    calculated_at = sgqlc.types.Field(UnixTime, graphql_name='calculatedAt')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    list_rubricator_facet = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('RubricatorFacet')), graphql_name='listRubricatorFacet')


class RubricatorFacet(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('list_rubric_facet', 'rubricator')
    list_rubric_facet = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(RubricFacet))), graphql_name='listRubricFacet')
    rubricator = sgqlc.types.Field(sgqlc.types.non_null('Rubricator'), graphql_name='rubricator')


class S3File(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('bucket_name', 'object_name')
    bucket_name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='bucketName')
    object_name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='objectName')


class Score(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('name', 'score')
    name = sgqlc.types.Field(sgqlc.types.non_null(Name), graphql_name='name')
    score = sgqlc.types.Field(Float, graphql_name='score')


class State(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('is_success',)
    is_success = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isSuccess')


class StateWithErrors(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('info', 'state')
    info = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(State)), graphql_name='info')
    state = sgqlc.types.Field(sgqlc.types.non_null(State), graphql_name='state')


class Story(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('access_level', 'count_doc', 'highlighting', 'id', 'list_document', 'main', 'preview', 'system_registration_date', 'system_update_date', 'title')
    access_level = sgqlc.types.Field(sgqlc.types.non_null(AccessLevel), graphql_name='accessLevel')
    count_doc = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='countDoc')
    highlighting = sgqlc.types.Field(Highlighting, graphql_name='highlighting')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    list_document = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('Document'))), graphql_name='listDocument')
    main = sgqlc.types.Field(sgqlc.types.non_null('Document'), graphql_name='main')
    preview = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='preview')
    system_registration_date = sgqlc.types.Field(sgqlc.types.non_null(UnixTime), graphql_name='systemRegistrationDate')
    system_update_date = sgqlc.types.Field(UnixTime, graphql_name='systemUpdateDate')
    title = sgqlc.types.Field(String, graphql_name='title')


class StoryPagination(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('document_facets', 'list_story', 'precise_total', 'rubrication_facets', 'show_total', 'total')
    document_facets = sgqlc.types.Field(sgqlc.types.non_null(DocumentFacets), graphql_name='documentFacets')
    list_story = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(Story))), graphql_name='listStory')
    precise_total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='preciseTotal')
    rubrication_facets = sgqlc.types.Field(sgqlc.types.non_null(RubricationFacets), graphql_name='rubricationFacets')
    show_total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='showTotal')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class StringLocaleValue(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('locale', 'value')
    locale = sgqlc.types.Field(sgqlc.types.non_null(Locale), graphql_name='locale')
    value = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='value')


class StringValue(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('value',)
    value = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='value')


class Time(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('hour', 'minute', 'second')
    hour = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='hour')
    minute = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='minute')
    second = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='second')


class TimestampValue(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('value',)
    value = sgqlc.types.Field(sgqlc.types.non_null(UnixTime), graphql_name='value')


class Translation(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('language', 'text')
    language = sgqlc.types.Field(sgqlc.types.non_null(Language), graphql_name='language')
    text = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='text')


class User(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('id',)
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')


class ValueWithConfidence(sgqlc.types.Type):
    __schema__ = utils_api_schema
    __field_names__ = ('confidence', 'value')
    confidence = sgqlc.types.Field(Float, graphql_name='confidence')
    value = sgqlc.types.Field(sgqlc.types.non_null('Value'), graphql_name='value')


class Account(sgqlc.types.Type, RecordInterface):
    __schema__ = utils_api_schema
    __field_names__ = ('country', 'id', 'image', 'key', 'markers', 'metric', 'name', 'params', 'period', 'platform', 'url')
    country = sgqlc.types.Field(String, graphql_name='country')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    image = sgqlc.types.Field(Image, graphql_name='image')
    key = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='key')
    markers = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))), graphql_name='markers')
    metric = sgqlc.types.Field(AccountStatistics, graphql_name='metric')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    params = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(Parameter))), graphql_name='params')
    period = sgqlc.types.Field(DateTimeInterval, graphql_name='period')
    platform = sgqlc.types.Field(sgqlc.types.non_null('Platform'), graphql_name='platform')
    url = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='url')


class AudioNodeMention(sgqlc.types.Type, MentionInterface, RecordInterface):
    __schema__ = utils_api_schema
    __field_names__ = ('end', 'node_id', 'start')
    end = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='end')
    node_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='nodeId')
    start = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='start')


class CompositePropertyValueCandidateFact(sgqlc.types.Type, FactInterface):
    __schema__ = utils_api_schema
    __field_names__ = ('fact_from', 'property_value_type', 'value_slot_fact')
    fact_from = sgqlc.types.Field('AnyCompositePropertyFact', graphql_name='factFrom')
    property_value_type = sgqlc.types.Field(sgqlc.types.non_null('CompositePropertyValueTemplate'), graphql_name='propertyValueType')
    value_slot_fact = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('CompositePropertyValueComponentCandidateFact'))), graphql_name='valueSlotFact')


class CompositePropertyValueComponentCandidateFact(sgqlc.types.Type, FactInterface):
    __schema__ = utils_api_schema
    __field_names__ = ('component_value_type', 'fact_from', 'fact_to')
    component_value_type = sgqlc.types.Field(sgqlc.types.non_null(CompositePropertyValueType), graphql_name='componentValueType')
    fact_from = sgqlc.types.Field(sgqlc.types.non_null(CompositePropertyValueCandidateFact), graphql_name='factFrom')
    fact_to = sgqlc.types.Field(sgqlc.types.non_null('ConceptPropertyValueCandidateFact'), graphql_name='factTo')


class CompositePropertyValueTemplate(sgqlc.types.Type, RecordInterface):
    __schema__ = utils_api_schema
    __field_names__ = ('component_value_types', 'id', 'name')
    component_value_types = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(CompositePropertyValueType))), graphql_name='componentValueTypes')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')


class Concept(sgqlc.types.Type, KBEntity, LinkTarget, PropertyTarget, RecordInterface):
    __schema__ = utils_api_schema
    __field_names__ = ('access_level', 'avatar_document', 'concept_type', 'end_date', 'image', 'is_actual', 'links_with_concepts_and_documents', 'links_with_concepts_and_documents_on_research_map', 'list_alias', 'list_concept_candidate_fact', 'list_concept_fact', 'list_header_concept_property', 'list_subscription', 'markers', 'metric', 'name', 'notes', 'pagination_alias', 'pagination_concept_duplicate_group', 'pagination_concept_fact', 'pagination_concept_link', 'pagination_concept_link_documents', 'pagination_concept_property', 'pagination_concept_property_documents', 'pagination_merged_concept', 'pagination_research_map', 'start_date', 'status')
    access_level = sgqlc.types.Field(sgqlc.types.non_null(AccessLevel), graphql_name='accessLevel')
    avatar_document = sgqlc.types.Field('Document', graphql_name='avatarDocument')
    concept_type = sgqlc.types.Field(sgqlc.types.non_null('ConceptType'), graphql_name='conceptType')
    end_date = sgqlc.types.Field(DateTimeValue, graphql_name='endDate')
    image = sgqlc.types.Field(Image, graphql_name='image')
    is_actual = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isActual')
    links_with_concepts_and_documents = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='linksWithConceptsAndDocuments')
    links_with_concepts_and_documents_on_research_map = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='linksWithConceptsAndDocumentsOnResearchMap')
    list_alias = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ConceptProperty'))), graphql_name='listAlias')
    list_concept_candidate_fact = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ConceptCandidateFact'))), graphql_name='listConceptCandidateFact')
    list_concept_fact = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ConceptFact'))), graphql_name='listConceptFact')
    list_header_concept_property = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ConceptProperty'))), graphql_name='listHeaderConceptProperty')
    list_subscription = sgqlc.types.Field(sgqlc.types.non_null(ConceptSubscriptions), graphql_name='listSubscription')
    markers = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))), graphql_name='markers')
    metric = sgqlc.types.Field(sgqlc.types.non_null(ConceptMetrics), graphql_name='metric')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    notes = sgqlc.types.Field(String, graphql_name='notes')
    pagination_alias = sgqlc.types.Field(sgqlc.types.non_null(ConceptPropertyPagination), graphql_name='paginationAlias', args=sgqlc.types.ArgDict((
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
))
    )
    pagination_concept_duplicate_group = sgqlc.types.Field(sgqlc.types.non_null(ConceptDuplicateGroupPagination), graphql_name='paginationConceptDuplicateGroup', args=sgqlc.types.ArgDict((
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(ConceptDuplicateGroupFilterSettings), graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
))
    )
    pagination_concept_fact = sgqlc.types.Field(sgqlc.types.non_null(ConceptFactPagination), graphql_name='paginationConceptFact', args=sgqlc.types.ArgDict((
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(LinkedDocumentFilterSettings), graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
))
    )
    pagination_concept_link = sgqlc.types.Field(sgqlc.types.non_null(ConceptLinkPagination), graphql_name='paginationConceptLink', args=sgqlc.types.ArgDict((
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(ConceptLinkFilterSettings), graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
))
    )
    pagination_concept_link_documents = sgqlc.types.Field(sgqlc.types.non_null(DocumentPagination), graphql_name='paginationConceptLinkDocuments', args=sgqlc.types.ArgDict((
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(ConceptLinkFilterSettings), graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
))
    )
    pagination_concept_property = sgqlc.types.Field(sgqlc.types.non_null(ConceptPropertyPagination), graphql_name='paginationConceptProperty', args=sgqlc.types.ArgDict((
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(ConceptPropertyFilterSettings), graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
))
    )
    pagination_concept_property_documents = sgqlc.types.Field(sgqlc.types.non_null(DocumentPagination), graphql_name='paginationConceptPropertyDocuments', args=sgqlc.types.ArgDict((
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(ConceptPropertyFilterSettings), graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
))
    )
    pagination_merged_concept = sgqlc.types.Field(sgqlc.types.non_null(MergedConceptPagination), graphql_name='paginationMergedConcept', args=sgqlc.types.ArgDict((
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
))
    )
    pagination_research_map = sgqlc.types.Field(sgqlc.types.non_null(ResearchMapPagination), graphql_name='paginationResearchMap', args=sgqlc.types.ArgDict((
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(ResearchMapFilterSettings), graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('sort_direction', sgqlc.types.Arg(sgqlc.types.non_null(SortDirection), graphql_name='sortDirection', default=None)),
        ('sorting', sgqlc.types.Arg(sgqlc.types.non_null(ResearchMapSorting), graphql_name='sorting', default=None)),
))
    )
    start_date = sgqlc.types.Field(DateTimeValue, graphql_name='startDate')
    status = sgqlc.types.Field(sgqlc.types.non_null(KbFactStatus), graphql_name='status')


class ConceptCandidateFact(sgqlc.types.Type, FactInterface):
    __schema__ = utils_api_schema
    __field_names__ = ('concept_type', 'list_concept', 'name')
    concept_type = sgqlc.types.Field(sgqlc.types.non_null('ConceptType'), graphql_name='conceptType')
    list_concept = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ConceptWithConfidence))), graphql_name='listConcept')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')


class ConceptCompositePropertyCandidateFact(sgqlc.types.Type, FactInterface):
    __schema__ = utils_api_schema
    __field_names__ = ('concept_property_type', 'fact_from', 'fact_to')
    concept_property_type = sgqlc.types.Field(sgqlc.types.non_null('ConceptPropertyType'), graphql_name='conceptPropertyType')
    fact_from = sgqlc.types.Field('ConceptLikeFact', graphql_name='factFrom')
    fact_to = sgqlc.types.Field(sgqlc.types.non_null(CompositePropertyValueCandidateFact), graphql_name='factTo')


class ConceptDuplicateReport(sgqlc.types.Type, RecordInterface):
    __schema__ = utils_api_schema
    __field_names__ = ('id', 'metric', 'pagination_concept_duplicate_group', 'task')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    metric = sgqlc.types.Field(sgqlc.types.non_null(ConceptDuplicateReportMetrics), graphql_name='metric')
    pagination_concept_duplicate_group = sgqlc.types.Field(sgqlc.types.non_null(ConceptDuplicateGroupPagination), graphql_name='paginationConceptDuplicateGroup', args=sgqlc.types.ArgDict((
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(ConceptDuplicateGroupFilterSettings), graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
))
    )
    task = sgqlc.types.Field(ConceptDedupTask, graphql_name='task')


class ConceptFact(sgqlc.types.Type, FactInterface, RecordInterface):
    __schema__ = utils_api_schema
    __field_names__ = ('access_level', 'concept')
    access_level = sgqlc.types.Field(sgqlc.types.non_null(AccessLevel), graphql_name='accessLevel')
    concept = sgqlc.types.Field(sgqlc.types.non_null(Concept), graphql_name='concept')


class ConceptGroupFacet(sgqlc.types.Type, DocumentGroupFacet):
    __schema__ = utils_api_schema
    __field_names__ = ('concept',)
    concept = sgqlc.types.Field(sgqlc.types.non_null(Concept), graphql_name='concept')


class ConceptLink(sgqlc.types.Type, PropertyTarget, RecordInterface):
    __schema__ = utils_api_schema
    __field_names__ = ('access_level', 'concept_from', 'concept_from_id', 'concept_link_type', 'concept_to', 'concept_to_id', 'end_date', 'from_', 'id', 'list_concept_link_fact', 'notes', 'pagination_concept_link_property', 'pagination_concept_link_property_documents', 'pagination_document', 'start_date', 'status', 'to')
    access_level = sgqlc.types.Field(sgqlc.types.non_null(AccessLevel), graphql_name='accessLevel')
    concept_from = sgqlc.types.Field(sgqlc.types.non_null(Concept), graphql_name='conceptFrom')
    concept_from_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='conceptFromId')
    concept_link_type = sgqlc.types.Field(sgqlc.types.non_null('ConceptLinkType'), graphql_name='conceptLinkType')
    concept_to = sgqlc.types.Field(sgqlc.types.non_null(Concept), graphql_name='conceptTo')
    concept_to_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='conceptToId')
    end_date = sgqlc.types.Field(DateTimeValue, graphql_name='endDate')
    from_ = sgqlc.types.Field(sgqlc.types.non_null(LinkTarget), graphql_name='from')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    list_concept_link_fact = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ConceptLinkFact'))), graphql_name='listConceptLinkFact')
    notes = sgqlc.types.Field(String, graphql_name='notes')
    pagination_concept_link_property = sgqlc.types.Field(sgqlc.types.non_null(ConceptPropertyPagination), graphql_name='paginationConceptLinkProperty', args=sgqlc.types.ArgDict((
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(ConceptPropertyFilterSettings), graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
))
    )
    pagination_concept_link_property_documents = sgqlc.types.Field(sgqlc.types.non_null(DocumentPagination), graphql_name='paginationConceptLinkPropertyDocuments', args=sgqlc.types.ArgDict((
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(ConceptPropertyFilterSettings), graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
))
    )
    pagination_document = sgqlc.types.Field(sgqlc.types.non_null(DocumentPagination), graphql_name='paginationDocument', args=sgqlc.types.ArgDict((
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
))
    )
    start_date = sgqlc.types.Field(DateTimeValue, graphql_name='startDate')
    status = sgqlc.types.Field(sgqlc.types.non_null(KbFactStatus), graphql_name='status')
    to = sgqlc.types.Field(sgqlc.types.non_null(LinkTarget), graphql_name='to')


class ConceptLinkCandidateFact(sgqlc.types.Type, FactInterface):
    __schema__ = utils_api_schema
    __field_names__ = ('concept_link_type', 'fact_from', 'fact_to')
    concept_link_type = sgqlc.types.Field(sgqlc.types.non_null('ConceptLinkType'), graphql_name='conceptLinkType')
    fact_from = sgqlc.types.Field('ConceptLikeFact', graphql_name='factFrom')
    fact_to = sgqlc.types.Field('ConceptLikeFact', graphql_name='factTo')


class ConceptLinkCompositePropertyCandidateFact(sgqlc.types.Type, FactInterface):
    __schema__ = utils_api_schema
    __field_names__ = ('concept_link_property_type', 'fact_from', 'fact_to')
    concept_link_property_type = sgqlc.types.Field(sgqlc.types.non_null('ConceptPropertyType'), graphql_name='conceptLinkPropertyType')
    fact_from = sgqlc.types.Field('ConceptLinkLikeFact', graphql_name='factFrom')
    fact_to = sgqlc.types.Field(sgqlc.types.non_null(CompositePropertyValueCandidateFact), graphql_name='factTo')


class ConceptLinkFact(sgqlc.types.Type, FactInterface, RecordInterface):
    __schema__ = utils_api_schema
    __field_names__ = ('access_level', 'concept_link')
    access_level = sgqlc.types.Field(sgqlc.types.non_null(AccessLevel), graphql_name='accessLevel')
    concept_link = sgqlc.types.Field(sgqlc.types.non_null(ConceptLink), graphql_name='conceptLink')


class ConceptLinkPropertyCandidateFact(sgqlc.types.Type, FactInterface):
    __schema__ = utils_api_schema
    __field_names__ = ('concept_link_property_type', 'fact_from', 'fact_to')
    concept_link_property_type = sgqlc.types.Field(sgqlc.types.non_null('ConceptPropertyType'), graphql_name='conceptLinkPropertyType')
    fact_from = sgqlc.types.Field('ConceptLinkLikeFact', graphql_name='factFrom')
    fact_to = sgqlc.types.Field(sgqlc.types.non_null('ConceptPropertyValueCandidateFact'), graphql_name='factTo')


class ConceptLinkPropertyFact(sgqlc.types.Type, FactInterface, RecordInterface):
    __schema__ = utils_api_schema
    __field_names__ = ('access_level', 'concept_link_property', 'fact_from', 'mention', 'parent_concept_link')
    access_level = sgqlc.types.Field(sgqlc.types.non_null(AccessLevel), graphql_name='accessLevel')
    concept_link_property = sgqlc.types.Field(sgqlc.types.non_null('ConceptProperty'), graphql_name='conceptLinkProperty')
    fact_from = sgqlc.types.Field('ConceptLinkLikeFact', graphql_name='factFrom')
    mention = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('MentionUnion'))), graphql_name='mention')
    parent_concept_link = sgqlc.types.Field(sgqlc.types.non_null(ConceptLink), graphql_name='parentConceptLink')


class ConceptLinkType(sgqlc.types.Type, PropertyTypeTarget, RecordInterface):
    __schema__ = utils_api_schema
    __field_names__ = ('concept_from_type', 'concept_to_type', 'from_type', 'id', 'is_directed', 'is_hierarchical', 'list_concept_link_property_type', 'metric', 'name', 'notify_on_update', 'pagination_concept_link_property_type', 'pretrained_rel_ext_models', 'to_type')
    concept_from_type = sgqlc.types.Field(sgqlc.types.non_null(EntityType), graphql_name='conceptFromType')
    concept_to_type = sgqlc.types.Field(sgqlc.types.non_null(EntityType), graphql_name='conceptToType')
    from_type = sgqlc.types.Field(sgqlc.types.non_null(LinkTypeTarget), graphql_name='fromType')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    is_directed = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isDirected')
    is_hierarchical = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isHierarchical')
    list_concept_link_property_type = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ConceptPropertyType'))), graphql_name='listConceptLinkPropertyType')
    metric = sgqlc.types.Field(sgqlc.types.non_null(ConceptLinkTypeStatistics), graphql_name='metric')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    notify_on_update = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='notifyOnUpdate')
    pagination_concept_link_property_type = sgqlc.types.Field(sgqlc.types.non_null(ConceptPropertyTypePagination), graphql_name='paginationConceptLinkPropertyType', args=sgqlc.types.ArgDict((
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(ConceptPropertyTypeFilterSettings), graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('sort_direction', sgqlc.types.Arg(sgqlc.types.non_null(SortDirection), graphql_name='sortDirection', default=None)),
        ('sorting', sgqlc.types.Arg(sgqlc.types.non_null(ConceptTypeSorting), graphql_name='sorting', default=None)),
))
    )
    pretrained_rel_ext_models = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(RelExtModel))), graphql_name='pretrainedRelExtModels')
    to_type = sgqlc.types.Field(sgqlc.types.non_null(LinkTypeTarget), graphql_name='toType')


class ConceptLinkTypeGroupFacet(sgqlc.types.Type, DocumentGroupFacet):
    __schema__ = utils_api_schema
    __field_names__ = ('concept_link_type',)
    concept_link_type = sgqlc.types.Field(sgqlc.types.non_null(ConceptLinkType), graphql_name='conceptLinkType')


class ConceptProperty(sgqlc.types.Type, RecordInterface):
    __schema__ = utils_api_schema
    __field_names__ = ('access_level', 'end_date', 'id', 'is_main', 'list_concept_property_fact', 'notes', 'pagination_document', 'property_type', 'start_date', 'status', 'value')
    access_level = sgqlc.types.Field(sgqlc.types.non_null(AccessLevel), graphql_name='accessLevel')
    end_date = sgqlc.types.Field(DateTimeValue, graphql_name='endDate')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    is_main = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isMain')
    list_concept_property_fact = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ConceptPropertyLikeFact'))), graphql_name='listConceptPropertyFact')
    notes = sgqlc.types.Field(String, graphql_name='notes')
    pagination_document = sgqlc.types.Field(sgqlc.types.non_null(DocumentPagination), graphql_name='paginationDocument', args=sgqlc.types.ArgDict((
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
))
    )
    property_type = sgqlc.types.Field(sgqlc.types.non_null('ConceptPropertyType'), graphql_name='propertyType')
    start_date = sgqlc.types.Field(DateTimeValue, graphql_name='startDate')
    status = sgqlc.types.Field(sgqlc.types.non_null(KbFactStatus), graphql_name='status')
    value = sgqlc.types.Field(sgqlc.types.non_null('AnyValue'), graphql_name='value')


class ConceptPropertyCandidateFact(sgqlc.types.Type, FactInterface):
    __schema__ = utils_api_schema
    __field_names__ = ('concept_property_type', 'fact_from', 'fact_to')
    concept_property_type = sgqlc.types.Field(sgqlc.types.non_null('ConceptPropertyType'), graphql_name='conceptPropertyType')
    fact_from = sgqlc.types.Field('ConceptLikeFact', graphql_name='factFrom')
    fact_to = sgqlc.types.Field(sgqlc.types.non_null('ConceptPropertyValueCandidateFact'), graphql_name='factTo')


class ConceptPropertyFact(sgqlc.types.Type, FactInterface, RecordInterface):
    __schema__ = utils_api_schema
    __field_names__ = ('access_level', 'concept_property', 'fact_from', 'mention', 'parent_concept')
    access_level = sgqlc.types.Field(sgqlc.types.non_null(AccessLevel), graphql_name='accessLevel')
    concept_property = sgqlc.types.Field(sgqlc.types.non_null(ConceptProperty), graphql_name='conceptProperty')
    fact_from = sgqlc.types.Field('ConceptLikeFact', graphql_name='factFrom')
    mention = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('MentionUnion'))), graphql_name='mention')
    parent_concept = sgqlc.types.Field(sgqlc.types.non_null(Concept), graphql_name='parentConcept')


class ConceptPropertyType(sgqlc.types.Type, RecordInterface):
    __schema__ = utils_api_schema
    __field_names__ = ('deprecated', 'id', 'is_identifying', 'name', 'notify_on_update', 'parent_concept_link_type', 'parent_concept_type', 'parent_type', 'pretrained_rel_ext_models', 'use_for_auto_rubricator', 'value_type')
    deprecated = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='deprecated')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    is_identifying = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isIdentifying')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    notify_on_update = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='notifyOnUpdate')
    parent_concept_link_type = sgqlc.types.Field(ConceptLinkType, graphql_name='parentConceptLinkType')
    parent_concept_type = sgqlc.types.Field(EntityType, graphql_name='parentConceptType')
    parent_type = sgqlc.types.Field(sgqlc.types.non_null(PropertyTypeTarget), graphql_name='parentType')
    pretrained_rel_ext_models = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(RelExtModel))), graphql_name='pretrainedRelExtModels')
    use_for_auto_rubricator = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='useForAutoRubricator')
    value_type = sgqlc.types.Field(sgqlc.types.non_null('AnyValueType'), graphql_name='valueType')


class ConceptPropertyTypeGroupFacet(sgqlc.types.Type, DocumentGroupFacet):
    __schema__ = utils_api_schema
    __field_names__ = ('concept_property_type',)
    concept_property_type = sgqlc.types.Field(sgqlc.types.non_null(ConceptPropertyType), graphql_name='conceptPropertyType')


class ConceptPropertyValueCandidateFact(sgqlc.types.Type, FactInterface):
    __schema__ = utils_api_schema
    __field_names__ = ('concept_property_value_type', 'fact_from', 'meanings')
    concept_property_value_type = sgqlc.types.Field(sgqlc.types.non_null('ConceptPropertyValueType'), graphql_name='conceptPropertyValueType')
    fact_from = sgqlc.types.Field('AnyPropertyOrValueComponentFact', graphql_name='factFrom')
    meanings = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ValueWithConfidence))), graphql_name='meanings')


class ConceptPropertyValueGroupFacet(sgqlc.types.Type, DocumentGroupFacet):
    __schema__ = utils_api_schema
    __field_names__ = ('concept_property_type', 'concept_property_value')
    concept_property_type = sgqlc.types.Field(sgqlc.types.non_null(ConceptPropertyType), graphql_name='conceptPropertyType')
    concept_property_value = sgqlc.types.Field(sgqlc.types.non_null('AnyValue'), graphql_name='conceptPropertyValue')


class ConceptPropertyValueType(sgqlc.types.Type, HasTypeSearchElements, RecordInterface):
    __schema__ = utils_api_schema
    __field_names__ = ('id', 'list_concept_link_type', 'list_concept_type', 'metric', 'name', 'pagination_concept_link_type', 'pagination_concept_type', 'use_for_auto_rubricator', 'value_restriction', 'value_type')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    list_concept_link_type = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ConceptLinkType))), graphql_name='listConceptLinkType')
    list_concept_type = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ConceptType'))), graphql_name='listConceptType')
    metric = sgqlc.types.Field(sgqlc.types.non_null(ConceptPropertyValueStatistics), graphql_name='metric')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    pagination_concept_link_type = sgqlc.types.Field(sgqlc.types.non_null(ConceptLinkTypePagination), graphql_name='paginationConceptLinkType', args=sgqlc.types.ArgDict((
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
))
    )
    pagination_concept_type = sgqlc.types.Field(sgqlc.types.non_null(ConceptTypePagination), graphql_name='paginationConceptType', args=sgqlc.types.ArgDict((
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
))
    )
    use_for_auto_rubricator = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='useForAutoRubricator')
    value_restriction = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))), graphql_name='valueRestriction')
    value_type = sgqlc.types.Field(sgqlc.types.non_null(ValueType), graphql_name='valueType')


class ConceptType(sgqlc.types.Type, EntityType, HasTypeSearchElements, LinkTypeTarget, PropertyTypeTarget, RecordInterface):
    __schema__ = utils_api_schema
    __field_names__ = ('is_event', 'list_concept_type_presentation', 'pagination_concept_type_view', 'use_for_auto_rubricator')
    is_event = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isEvent')
    list_concept_type_presentation = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ConceptTypePresentation'))), graphql_name='listConceptTypePresentation')
    pagination_concept_type_view = sgqlc.types.Field(sgqlc.types.non_null(ConceptTypeViewPagination), graphql_name='paginationConceptTypeView', args=sgqlc.types.ArgDict((
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
))
    )
    use_for_auto_rubricator = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='useForAutoRubricator')


class ConceptTypeGroupFacet(sgqlc.types.Type, DocumentGroupFacet):
    __schema__ = utils_api_schema
    __field_names__ = ('concept_type',)
    concept_type = sgqlc.types.Field(sgqlc.types.non_null(ConceptType), graphql_name='conceptType')


class ConceptTypePresentation(sgqlc.types.Type, EntityTypePresentation, RecordInterface):
    __schema__ = utils_api_schema
    __field_names__ = ('has_header_information', 'has_supporting_documents', 'hide_empty_rows', 'id', 'internal_url', 'is_default', 'layout', 'list_widget_type', 'name', 'pagination_widget_type', 'root_concept_type', 'root_type')
    has_header_information = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='hasHeaderInformation')
    has_supporting_documents = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='hasSupportingDocuments')
    hide_empty_rows = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='hideEmptyRows')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    internal_url = sgqlc.types.Field(String, graphql_name='internalUrl')
    is_default = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isDefault')
    layout = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='layout')
    list_widget_type = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ConceptTypePresentationWidgetType'))), graphql_name='listWidgetType')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    pagination_widget_type = sgqlc.types.Field(sgqlc.types.non_null(ConceptTypePresentationWidgetTypePagination), graphql_name='paginationWidgetType', args=sgqlc.types.ArgDict((
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('sort_direction', sgqlc.types.Arg(SortDirection, graphql_name='sortDirection', default='ascending')),
        ('sorting', sgqlc.types.Arg(ConceptTypePresentationWidgetTypeSorting, graphql_name='sorting', default='order')),
))
    )
    root_concept_type = sgqlc.types.Field(sgqlc.types.non_null(ConceptType), graphql_name='rootConceptType')
    root_type = sgqlc.types.Field(sgqlc.types.non_null(EntityType), graphql_name='rootType')


class ConceptTypePresentationWidgetType(sgqlc.types.Type, RecordInterface):
    __schema__ = utils_api_schema
    __field_names__ = ('columns_info', 'concept_type_presentation', 'hierarchy', 'id', 'name', 'table_type')
    columns_info = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ConceptTypePresentationWidgetTypeColumn))), graphql_name='columnsInfo')
    concept_type_presentation = sgqlc.types.Field(sgqlc.types.non_null(ConceptTypePresentation), graphql_name='conceptTypePresentation')
    hierarchy = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ConceptLinkTypePath))))), graphql_name='hierarchy')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    table_type = sgqlc.types.Field(sgqlc.types.non_null(WidgetTypeTableType), graphql_name='tableType')


class ConceptTypeView(sgqlc.types.Type, RecordInterface):
    __schema__ = utils_api_schema
    __field_names__ = ('columns', 'concept_type', 'id', 'name', 'pagination_concept', 'show_in_menu')
    columns = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ConceptTypePresentationWidgetTypeColumn))), graphql_name='columns')
    concept_type = sgqlc.types.Field(sgqlc.types.non_null(ConceptType), graphql_name='conceptType')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    pagination_concept = sgqlc.types.Field(sgqlc.types.non_null(ConceptViewPagination), graphql_name='paginationConcept', args=sgqlc.types.ArgDict((
        ('filter_settings', sgqlc.types.Arg(ConceptFilterSettings, graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('sort_column', sgqlc.types.Arg(ID, graphql_name='sortColumn', default=None)),
        ('sort_direction', sgqlc.types.Arg(SortDirection, graphql_name='sortDirection', default='descending')),
))
    )
    show_in_menu = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='showInMenu')


class Document(sgqlc.types.Type, KBEntity, LinkTarget, PropertyTarget, RecordInterface):
    __schema__ = utils_api_schema
    __field_names__ = ('access_level', 'additional_text', 'avatar', 'content_types', 'document_content_type', 'document_type', 'external_url', 'fact', 'handling_status', 'has_text', 'highlightings', 'internal_file', 'internal_url', 'is_processed', 'is_read', 'list_child', 'list_concept_fact', 'list_concept_link_document_fact', 'list_fact', 'list_fact_with_mention', 'list_mention', 'list_mention_link', 'list_subscription', 'markers', 'metadata', 'metadata_concept', 'metric', 'node', 'notes', 'pagination_child', 'pagination_concept_fact', 'pagination_concept_link_fact', 'pagination_similar_documents', 'pagination_text', 'parent', 'preview', 'publication_author', 'publication_date', 'score', 'story', 'text', 'text_translations', 'title', 'trust_level', 'uuid')
    access_level = sgqlc.types.Field(sgqlc.types.non_null(AccessLevel), graphql_name='accessLevel')
    additional_text = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(FlatDocumentStructure))))), graphql_name='additionalText', args=sgqlc.types.ArgDict((
        ('show_hidden', sgqlc.types.Arg(Boolean, graphql_name='showHidden', default=False)),
))
    )
    avatar = sgqlc.types.Field(Image, graphql_name='avatar')
    content_types = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(DocumentContentType))), graphql_name='contentTypes')
    document_content_type = sgqlc.types.Field(sgqlc.types.non_null(DocumentContentType), graphql_name='documentContentType')
    document_type = sgqlc.types.Field(sgqlc.types.non_null('DocumentType'), graphql_name='documentType')
    external_url = sgqlc.types.Field(String, graphql_name='externalUrl')
    fact = sgqlc.types.Field('Fact', graphql_name='fact', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    handling_status = sgqlc.types.Field(sgqlc.types.non_null(TdmHandlingStatus), graphql_name='handlingStatus')
    has_text = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='hasText')
    highlightings = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(Highlighting))), graphql_name='highlightings')
    internal_file = sgqlc.types.Field(S3File, graphql_name='internalFile')
    internal_url = sgqlc.types.Field(String, graphql_name='internalUrl')
    is_processed = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isProcessed')
    is_read = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isRead')
    list_child = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('Document'))), graphql_name='listChild')
    list_concept_fact = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ConceptFact))), graphql_name='listConceptFact')
    list_concept_link_document_fact = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ConceptLinkFact))), graphql_name='listConceptLinkDocumentFact')
    list_fact = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('Fact'))), graphql_name='listFact')
    list_fact_with_mention = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(FactInterface))), graphql_name='listFactWithMention', args=sgqlc.types.ArgDict((
        ('node_id', sgqlc.types.Arg(String, graphql_name='nodeId', default=None)),
))
    )
    list_mention = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('MentionUnion'))), graphql_name='listMention')
    list_mention_link = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(MentionLink))), graphql_name='listMentionLink', args=sgqlc.types.ArgDict((
        ('mention_link_type', sgqlc.types.Arg(MentionLinkType, graphql_name='mentionLinkType', default=None)),
))
    )
    list_subscription = sgqlc.types.Field(sgqlc.types.non_null(DocumentSubscriptions), graphql_name='listSubscription')
    markers = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))), graphql_name='markers')
    metadata = sgqlc.types.Field(DocumentMetadata, graphql_name='metadata')
    metadata_concept = sgqlc.types.Field(Concept, graphql_name='metadataConcept')
    metric = sgqlc.types.Field(sgqlc.types.non_null(DocumentMetrics), graphql_name='metric')
    node = sgqlc.types.Field(FlatDocumentStructure, graphql_name='node', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    notes = sgqlc.types.Field(String, graphql_name='notes')
    pagination_child = sgqlc.types.Field(sgqlc.types.non_null(DocumentPagination), graphql_name='paginationChild', args=sgqlc.types.ArgDict((
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(LinkedDocumentFilterSettings), graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
))
    )
    pagination_concept_fact = sgqlc.types.Field(sgqlc.types.non_null(ConceptFactPagination), graphql_name='paginationConceptFact', args=sgqlc.types.ArgDict((
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
))
    )
    pagination_concept_link_fact = sgqlc.types.Field(sgqlc.types.non_null(ConceptLinkFactPagination), graphql_name='paginationConceptLinkFact', args=sgqlc.types.ArgDict((
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
))
    )
    pagination_similar_documents = sgqlc.types.Field(sgqlc.types.non_null(DocumentPagination), graphql_name='paginationSimilarDocuments', args=sgqlc.types.ArgDict((
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
))
    )
    pagination_text = sgqlc.types.Field(sgqlc.types.non_null(DocumentTextPagination), graphql_name='paginationText', args=sgqlc.types.ArgDict((
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('show_hidden', sgqlc.types.Arg(Boolean, graphql_name='showHidden', default=False)),
))
    )
    parent = sgqlc.types.Field('Document', graphql_name='parent')
    preview = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='preview')
    publication_author = sgqlc.types.Field(String, graphql_name='publicationAuthor')
    publication_date = sgqlc.types.Field(UnixTime, graphql_name='publicationDate')
    score = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(Score))), graphql_name='score')
    story = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='story')
    text = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(FlatDocumentStructure))), graphql_name='text', args=sgqlc.types.ArgDict((
        ('show_hidden', sgqlc.types.Arg(Boolean, graphql_name='showHidden', default=False)),
))
    )
    text_translations = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(Translation))), graphql_name='textTranslations', args=sgqlc.types.ArgDict((
        ('node_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='nodeId', default=None)),
))
    )
    title = sgqlc.types.Field(String, graphql_name='title')
    trust_level = sgqlc.types.Field(TrustLevel, graphql_name='trustLevel')
    uuid = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='uuid')


class DocumentAccountGroupFacet(sgqlc.types.Type, DocumentGroupFacet):
    __schema__ = utils_api_schema
    __field_names__ = ('account',)
    account = sgqlc.types.Field(sgqlc.types.non_null(Account), graphql_name='account')


class DocumentPlatformGroupFacet(sgqlc.types.Type, DocumentGroupFacet):
    __schema__ = utils_api_schema
    __field_names__ = ('platform',)
    platform = sgqlc.types.Field(sgqlc.types.non_null('Platform'), graphql_name='platform')


class DocumentPlatformTypeGroupFacet(sgqlc.types.Type, DocumentGroupFacet):
    __schema__ = utils_api_schema
    __field_names__ = ('platform_type',)
    platform_type = sgqlc.types.Field(sgqlc.types.non_null(PlatformType), graphql_name='platformType')


class DocumentPropertyGroupFacet(sgqlc.types.Type, DocumentGroupFacet):
    __schema__ = utils_api_schema
    __field_names__ = ('value',)
    value = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='value')


class DocumentType(sgqlc.types.Type, EntityType, HasTypeSearchElements, LinkTypeTarget, PropertyTypeTarget, RecordInterface):
    __schema__ = utils_api_schema
    __field_names__ = ('list_document_type_presentation',)
    list_document_type_presentation = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('DocumentTypePresentation'))), graphql_name='listDocumentTypePresentation')


class DocumentTypePresentation(sgqlc.types.Type, EntityTypePresentation, RecordInterface):
    __schema__ = utils_api_schema
    __field_names__ = ('columns_info', 'hierarchy', 'id', 'is_default', 'name', 'root_document_type', 'root_type')
    columns_info = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ConceptTypePresentationWidgetTypeColumn))), graphql_name='columnsInfo')
    hierarchy = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ConceptLinkTypePath))))), graphql_name='hierarchy')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    is_default = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isDefault')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    root_document_type = sgqlc.types.Field(sgqlc.types.non_null(DocumentType), graphql_name='rootDocumentType')
    root_type = sgqlc.types.Field(sgqlc.types.non_null(EntityType), graphql_name='rootType')


class ImageNodeMention(sgqlc.types.Type, MentionInterface, RecordInterface):
    __schema__ = utils_api_schema
    __field_names__ = ('bottom', 'left', 'node_id', 'right', 'top')
    bottom = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='bottom')
    left = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='left')
    node_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='nodeId')
    right = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='right')
    top = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='top')


class MapAnnotation(sgqlc.types.Type, RecordInterface):
    __schema__ = utils_api_schema
    __field_names__ = ('annotation', 'id')
    annotation = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='annotation')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')


class NodeMention(sgqlc.types.Type, MentionInterface, RecordInterface):
    __schema__ = utils_api_schema
    __field_names__ = ('node_id',)
    node_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='nodeId')


class Platform(sgqlc.types.Type, RecordInterface):
    __schema__ = utils_api_schema
    __field_names__ = ('accounts', 'country', 'id', 'image', 'key', 'language', 'markers', 'metric', 'name', 'params', 'period', 'platform_type', 'url')
    accounts = sgqlc.types.Field(sgqlc.types.non_null(AccountPagination), graphql_name='accounts', args=sgqlc.types.ArgDict((
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(AccountFilterSettings), graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('sort_direction', sgqlc.types.Arg(SortDirection, graphql_name='sortDirection', default='descending')),
        ('sorting', sgqlc.types.Arg(AccountSorting, graphql_name='sorting', default='id')),
))
    )
    country = sgqlc.types.Field(String, graphql_name='country')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    image = sgqlc.types.Field(Image, graphql_name='image')
    key = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='key')
    language = sgqlc.types.Field(String, graphql_name='language')
    markers = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))), graphql_name='markers')
    metric = sgqlc.types.Field(PlatformStatistics, graphql_name='metric')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    params = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(Parameter))), graphql_name='params')
    period = sgqlc.types.Field(DateTimeInterval, graphql_name='period')
    platform_type = sgqlc.types.Field(sgqlc.types.non_null(PlatformType), graphql_name='platformType')
    url = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='url')


class PropertyValueMentionCandidateFact(sgqlc.types.Type, FactInterface):
    __schema__ = utils_api_schema
    __field_names__ = ('mention', 'value_fact')
    mention = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('MentionUnion'))), graphql_name='mention')
    value_fact = sgqlc.types.Field(sgqlc.types.non_null(ConceptPropertyValueCandidateFact), graphql_name='valueFact')


class ResearchMap(sgqlc.types.Type, RecordInterface):
    __schema__ = utils_api_schema
    __field_names__ = ('access_level', 'description', 'id', 'is_active', 'is_temporary', 'list_drawing', 'list_edge', 'list_geo_concept_properties', 'list_group', 'list_node', 'markers', 'name', 'pagination_concept', 'pagination_research_map', 'pagination_story', 'research_map_statistics')
    access_level = sgqlc.types.Field(sgqlc.types.non_null(AccessLevel), graphql_name='accessLevel')
    description = sgqlc.types.Field(String, graphql_name='description')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    is_active = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isActive')
    is_temporary = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isTemporary')
    list_drawing = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(MapDrawing))), graphql_name='listDrawing')
    list_edge = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(MapEdge))), graphql_name='listEdge', args=sgqlc.types.ArgDict((
        ('default_view', sgqlc.types.Arg(Boolean, graphql_name='defaultView', default=True)),
        ('filter_settings', sgqlc.types.Arg(MapEdgeFilterSettings, graphql_name='filterSettings', default=None)),
))
    )
    list_geo_concept_properties = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(GeoConceptProperty))), graphql_name='listGeoConceptProperties')
    list_group = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(Group))), graphql_name='listGroup')
    list_node = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(MapNode))), graphql_name='listNode', args=sgqlc.types.ArgDict((
        ('default_view', sgqlc.types.Arg(Boolean, graphql_name='defaultView', default=True)),
        ('filter_settings', sgqlc.types.Arg(MapNodeFilterSettings, graphql_name='filterSettings', default=None)),
))
    )
    markers = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))), graphql_name='markers')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    pagination_concept = sgqlc.types.Field(sgqlc.types.non_null(ConceptPagination), graphql_name='paginationConcept', args=sgqlc.types.ArgDict((
        ('direction', sgqlc.types.Arg(SortDirection, graphql_name='direction', default='descending')),
        ('extra_settings', sgqlc.types.Arg(sgqlc.types.non_null(ConceptExtraSettings), graphql_name='extraSettings', default=None)),
        ('filter_settings', sgqlc.types.Arg(ConceptFilterSettings, graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=1000)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('sort_field', sgqlc.types.Arg(ConceptSorting, graphql_name='sortField', default=None)),
))
    )
    pagination_research_map = sgqlc.types.Field(sgqlc.types.non_null(ResearchMapPagination), graphql_name='paginationResearchMap', args=sgqlc.types.ArgDict((
        ('research_map_content_select_input', sgqlc.types.Arg(ResearchMapContentUpdateInput, graphql_name='ResearchMapContentSelectInput', default=None)),
        ('direction', sgqlc.types.Arg(SortDirection, graphql_name='direction', default='descending')),
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(ResearchMapFilterSettings), graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('sort_field', sgqlc.types.Arg(ResearchMapSorting, graphql_name='sortField', default='conceptAndDocumentLink')),
))
    )
    pagination_story = sgqlc.types.Field(sgqlc.types.non_null(StoryPagination), graphql_name='paginationStory', args=sgqlc.types.ArgDict((
        ('direction', sgqlc.types.Arg(SortDirection, graphql_name='direction', default='descending')),
        ('extra_settings', sgqlc.types.Arg(sgqlc.types.non_null(ExtraSettings), graphql_name='extraSettings', default=None)),
        ('filter_settings', sgqlc.types.Arg(DocumentFilterSettings, graphql_name='filterSettings', default=None)),
        ('grouping', sgqlc.types.Arg(DocumentGrouping, graphql_name='grouping', default='none')),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=1000)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('relevance', sgqlc.types.Arg(DocumentRelevanceMetricsInput, graphql_name='relevance', default=None)),
        ('sort_field', sgqlc.types.Arg(DocumentSorting, graphql_name='sortField', default=None)),
))
    )
    research_map_statistics = sgqlc.types.Field(sgqlc.types.non_null(ResearchMapStatistics), graphql_name='researchMapStatistics')


class Rubric(sgqlc.types.Type, RecordInterface):
    __schema__ = utils_api_schema
    __field_names__ = ('count_child', 'id', 'linked_type', 'list_child', 'name', 'notes', 'parent_rubric', 'rubric_power', 'transformator_id')
    count_child = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='countChild')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    linked_type = sgqlc.types.Field('RubricLinkedType', graphql_name='linkedType')
    list_child = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('Rubric'))), graphql_name='listChild')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    notes = sgqlc.types.Field(String, graphql_name='notes')
    parent_rubric = sgqlc.types.Field('Rubric', graphql_name='parentRubric')
    rubric_power = sgqlc.types.Field(Int, graphql_name='rubricPower')
    transformator_id = sgqlc.types.Field(ID, graphql_name='transformatorId')


class Rubricator(sgqlc.types.Type, RecordInterface):
    __schema__ = utils_api_schema
    __field_names__ = ('id', 'name', 'notes', 'rubricator_type', 'transformator_id')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    notes = sgqlc.types.Field(String, graphql_name='notes')
    rubricator_type = sgqlc.types.Field(sgqlc.types.non_null(RubricatorType), graphql_name='rubricatorType')
    transformator_id = sgqlc.types.Field(ID, graphql_name='transformatorId')


class TextNodeMention(sgqlc.types.Type, MentionInterface, RecordInterface):
    __schema__ = utils_api_schema
    __field_names__ = ('end', 'node_id', 'start')
    end = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='end')
    node_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='nodeId')
    start = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='start')


class VideoNodeMention(sgqlc.types.Type, MentionInterface, RecordInterface):
    __schema__ = utils_api_schema
    __field_names__ = ('bottom', 'end', 'left', 'node_id', 'right', 'start', 'top')
    bottom = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='bottom')
    end = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='end')
    left = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='left')
    node_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='nodeId')
    right = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='right')
    start = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='start')
    top = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='top')



########################################################################
# Unions
########################################################################
class AnyCompositePropertyFact(sgqlc.types.Union):
    __schema__ = utils_api_schema
    __types__ = (ConceptCompositePropertyCandidateFact, ConceptLinkCompositePropertyCandidateFact)


class AnyPropertyOrValueComponentFact(sgqlc.types.Union):
    __schema__ = utils_api_schema
    __types__ = (CompositePropertyValueComponentCandidateFact, ConceptLinkPropertyCandidateFact, ConceptLinkPropertyFact, ConceptPropertyCandidateFact, ConceptPropertyFact)


class AnyValue(sgqlc.types.Union):
    __schema__ = utils_api_schema
    __types__ = (CompositeValue, DateTimeValue, DoubleValue, GeoPointValue, IntValue, LinkValue, StringLocaleValue, StringValue, TimestampValue)


class AnyValueType(sgqlc.types.Union):
    __schema__ = utils_api_schema
    __types__ = (CompositePropertyValueTemplate, ConceptPropertyValueType)


class ConceptLikeFact(sgqlc.types.Union):
    __schema__ = utils_api_schema
    __types__ = (ConceptCandidateFact, ConceptFact)


class ConceptLinkLikeFact(sgqlc.types.Union):
    __schema__ = utils_api_schema
    __types__ = (ConceptLinkCandidateFact, ConceptLinkFact)


class ConceptPropertyLikeFact(sgqlc.types.Union):
    __schema__ = utils_api_schema
    __types__ = (ConceptLinkPropertyFact, ConceptPropertyFact)


class ConceptViewValue(sgqlc.types.Union):
    __schema__ = utils_api_schema
    __types__ = (CompositeValue, Concept, ConceptLinkType, ConceptType, DateTimeValue, DoubleValue, GeoPointValue, Image, IntValue, LinkValue, StringLocaleValue, StringValue, TimestampValue, User)


class Entity(sgqlc.types.Union):
    __schema__ = utils_api_schema
    __types__ = (Concept, ConceptType, Document, DocumentType)


class EntityLink(sgqlc.types.Union):
    __schema__ = utils_api_schema
    __types__ = (ConceptCandidateFact, ConceptFact, ConceptLink, ConceptLinkType, DocumentLink)


class Fact(sgqlc.types.Union):
    __schema__ = utils_api_schema
    __types__ = (CompositePropertyValueCandidateFact, CompositePropertyValueComponentCandidateFact, ConceptCandidateFact, ConceptCompositePropertyCandidateFact, ConceptFact, ConceptLinkCandidateFact, ConceptLinkCompositePropertyCandidateFact, ConceptLinkFact, ConceptLinkPropertyCandidateFact, ConceptLinkPropertyFact, ConceptPropertyCandidateFact, ConceptPropertyFact, ConceptPropertyValueCandidateFact, PropertyValueMentionCandidateFact)


class MentionUnion(sgqlc.types.Union):
    __schema__ = utils_api_schema
    __types__ = (AudioNodeMention, ImageNodeMention, NodeMention, TextNodeMention, VideoNodeMention)


class RubricLinkedType(sgqlc.types.Union):
    __schema__ = utils_api_schema
    __types__ = (ConceptPropertyType, ConceptPropertyValueType, ConceptType)


class TypeSearchElement(sgqlc.types.Union):
    __schema__ = utils_api_schema
    __types__ = (DictValue, NERCRegexp)


class Value(sgqlc.types.Union):
    __schema__ = utils_api_schema
    __types__ = (DateTimeValue, DoubleValue, GeoPointValue, IntValue, LinkValue, StringLocaleValue, StringValue, TimestampValue)



########################################################################
# Schema Entry Points
########################################################################
utils_api_schema.query_type = Query
utils_api_schema.mutation_type = Mutation
utils_api_schema.subscription_type = None

