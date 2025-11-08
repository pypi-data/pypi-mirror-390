import sgqlc.types


api_schema = sgqlc.types.Schema()



########################################################################
# Scalars and Enumerations
########################################################################
class AccessLevelSorting(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ('id', 'name', 'order')


class AccountSorting(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ('creator', 'id', 'key', 'lastUpdater', 'name', 'platformKey', 'systemRegistrationDate', 'systemUpdateDate', 'url')


class AutocompleteConceptDestination(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ('markers',)


class AutocompleteDocumentDestination(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ('links', 'markers')


Boolean = sgqlc.types.Boolean

class BulkType(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ('account', 'concept', 'document', 'map', 'platform')


class ChildVisibility(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ('all', 'childrenOnly')


class ComponentView(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ('keyValue', 'value')


class CompositePropertyTypeSorting(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ('id', 'name', 'registrationDate')


class CompositePropertyValueTemplateSorting(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ('id', 'name', 'registrationDate')


class ConceptLinkDirection(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ('from', 'to')


class ConceptLinkTypeSorting(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ('conceptType', 'id', 'name')


class ConceptPropertyTypeSorting(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ('name', 'registrationDate')


class ConceptPropertyValueTypeSorting(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ('id', 'name')


class ConceptSorting(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ('id', 'name', 'score', 'status', 'systemRegistrationDate', 'systemUpdateDate')


class ConceptTypeLinkMetadata(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ('creator', 'endDate', 'lastUpdater', 'linkType', 'registrationDate', 'startDate', 'updateDate')


class ConceptTypeMetadata(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ('concept', 'conceptType', 'creator', 'endDate', 'image', 'lastUpdater', 'markers', 'name', 'notes', 'startDate', 'systemRegistrationDate', 'systemUpdateDate')


class ConceptTypePresentationSorting(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ('id', 'name')


class ConceptTypePresentationWidgetTypeSorting(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ('id', 'name', 'order')


class ConceptTypeSorting(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ('dictionary', 'id', 'name', 'regexp')


class ConceptUpdate(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ('link', 'linkProperty', 'metadata', 'property')


class ConceptVariant(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ('event', 'obj')


class ConceptViewColumnType(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ('accessLevel', 'conceptType', 'creator', 'id', 'image', 'lastUpdater', 'metrics', 'name', 'systemRegistrationDate', 'systemUpdateDate')


class ConceptViewMetricType(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ('facts', 'links', 'mergedConcepts', 'notApprovedFacts', 'notApprovedLinks', 'notApprovedProperties', 'properties', 'researchMaps')


class CountryTarget(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ('account', 'platform')


class DocumentContentType(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ('audio', 'image', 'text', 'video')


class DocumentDuplicateComparisonField(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ('accessLevel', 'account', 'externalUrl', 'fileName', 'fileType', 'language', 'markers', 'platform', 'publicationAuthor', 'publicationDate', 'size', 'story', 'text', 'title', 'trustLevel')


class DocumentDuplicateReportStatus(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ('Error', 'InProgress', 'Pending', 'Success')


class DocumentDuplicateTaskStatus(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ('Declined', 'Deleted', 'Error', 'InProgress', 'New', 'Pending')


class DocumentFeedMode(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ('all', 'deleted', 'favorites')


class DocumentFeedNotificationEvent(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ('documentFeedUpdated', 'newDeletedDocuments', 'newDocuments', 'newFavoriteDocuments')


class DocumentFeedSorting(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ('creator', 'id', 'lastUpdater', 'name', 'systemRegistrationDate', 'systemUpdateDate')


class DocumentGrouping(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ('none', 'story')


class DocumentGroupingCategory(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ('account', 'accountCountry', 'concept', 'conceptLinkType', 'conceptPropertyType', 'conceptPropertyValue', 'conceptType', 'documentLanguage', 'marker', 'platform', 'platformCountry', 'platformLanguage', 'platformType', 'publicationAuthor')


class DocumentInFeedSorting(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ('addedToFeedDate', 'publicationDate', 'registrationDate', 'relevance')


class DocumentRubricSorting(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ('id', 'rubricName', 'systemRegistrationDate', 'systemUpdateDate')


class DocumentRubricStatus(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ('approved', 'new')


class DocumentSorting(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ('countLinks', 'countNamedEntities', 'id', 'publicationDate', 'registrationDate', 'relevance', 'score', 'title', 'updateDate')


class DocumentSourceType(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ('external', 'internal')


class DocumentTypePresentationSorting(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ('id', 'name')


class DocumentTypeSorting(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ('dictionary', 'id', 'name', 'regexp')


class DocumentUpdate(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ('content', 'markup', 'metadata')


class DocumentViewColumnType(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ('accessLevel', 'creator', 'externalUrl', 'lastUpdater', 'publicationAuthor', 'publicationDate', 'systemRegistrationDate', 'systemUpdateDate', 'trustLevel')


class DocumentViewMetricType(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ('childDocuments', 'concepts', 'facts', 'links', 'notApprovedConcepts', 'notApprovedLinks', 'notApprovedProperties', 'properties', 'researchMaps')


class ElementType(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ('blackList', 'whiteList')


Float = sgqlc.types.Float

ID = sgqlc.types.ID

Int = sgqlc.types.Int

class KbFactStatus(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ('approved', 'notApproved')


class KbFactStatusFilter(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ('all', 'approved', 'notApproved')


class LinkDirection(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ('in', 'out', 'undirected')


class Locale(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ('eng', 'other', 'ru')


class Long(sgqlc.types.Scalar):
    __schema__ = api_schema


class MapEdgeType(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ('conceptCandidateFactLink', 'conceptFactLink', 'conceptLink', 'conceptTypeLink', 'documentLink')


class MapNodeType(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ('accountType', 'concept', 'conceptType', 'document', 'documentType', 'platformType', 'storyType')


class MentionLinkType(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ('equivalent', 'reference', 'translation')


class Name(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ('approvedPropsRelevance', 'conceptApprovedPropsRelevance', 'conceptFactRelevance', 'conceptMeaningPropsRelevance', 'conceptNercRelevance', 'conceptNercSearchRelevance', 'conceptPropsRelevance', 'conceptSubstituteRelevance', 'factRelevance', 'mapApprovedPropsRelevance', 'mapFactRelevance', 'mapMeaningPropsRelevance', 'mapNercRelevance', 'mapNercSearchRelevance', 'mapPropsRelevance', 'meaningPropsRelevance', 'nercRelevance', 'nercSearchRelevance', 'propsRelevance', 'queryScore', 'significantTextRelevance', 'totalRelevance')


class NodeType(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ('audio', 'base64', 'cell', 'file', 'header', 'image', 'json', 'key', 'list', 'other', 'row', 'table', 'text', 'video')


class PlatformSorting(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ('creator', 'id', 'key', 'lastUpdater', 'name', 'platformType', 'systemRegistrationDate', 'systemUpdateDate', 'url')


class PropertyParent(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ('concept', 'conceptLink', 'document')


class RelatedDocumentSorting(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ('publicationDate', 'registrationDate', 'updateDate')


class ResearchMapSorting(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ('accessLevel', 'conceptAndDocumentLink', 'conceptLink', 'creator', 'documentLink', 'id', 'lastUpdater', 'name', 'systemRegistrationDate', 'systemUpdateDate')


class RubricSorting(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ('id', 'name', 'rubricPower', 'systemRegistrationDate', 'systemUpdateDate', 'transformatorId')


class RubricatorSorting(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ('id', 'name', 'systemRegistrationDate', 'systemUpdateDate')


class RubricatorType(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ('auto', 'manual')


class SortDirection(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ('ascending', 'descending')


class StoryTypeSorting(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ('dictionary', 'id', 'name', 'regexp')


String = sgqlc.types.String

class TDMProcessStage(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ('all', 'preprocessed', 'processed')


class TdmHandlingStatus(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ('Failed', 'Pending', 'Success', 'WithErrors')


class TrustLevel(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ('high', 'low', 'medium')


class UnixTime(sgqlc.types.Scalar):
    __schema__ = api_schema


class ValueType(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ('Date', 'Double', 'Geo', 'Int', 'Link', 'String', 'StringLocale', 'Timestamp')


class WidgetTypeTableType(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ('horizontal', 'vertical')



########################################################################
# Input Objects
########################################################################
class AccessLevelCreationInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('name', 'order')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    order = sgqlc.types.Field(Long, graphql_name='order')


class AccessLevelUpdateInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('name',)
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')


class AccountCreationInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('access_level_id', 'account_type_id', 'country', 'end_date', 'key', 'language', 'markers', 'name', 'platform_id', 'start_date', 'url')
    access_level_id = sgqlc.types.Field(ID, graphql_name='accessLevelId')
    account_type_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='accountTypeId')
    country = sgqlc.types.Field(String, graphql_name='country')
    end_date = sgqlc.types.Field('DateTimeInput', graphql_name='endDate')
    key = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='key')
    language = sgqlc.types.Field(String, graphql_name='language')
    markers = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='markers')
    name = sgqlc.types.Field(String, graphql_name='name')
    platform_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='platformId')
    start_date = sgqlc.types.Field('DateTimeInput', graphql_name='startDate')
    url = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='url')


class AccountFilterSettings(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('account_type_ids', 'country', 'creator', 'ids', 'keys', 'last_updater', 'markers', 'platform_ids', 'platform_type_ids', 'property_filter_settings', 'registration_date', 'search_string', 'status', 'update_date')
    account_type_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='accountTypeIds')
    country = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='country')
    creator = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='creator')
    ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='ids')
    keys = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='keys')
    last_updater = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='lastUpdater')
    markers = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='markers')
    platform_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='platformIds')
    platform_type_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='platformTypeIds')
    property_filter_settings = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('PropertyFilterSettings')), graphql_name='propertyFilterSettings')
    registration_date = sgqlc.types.Field('TimestampIntervalInput', graphql_name='registrationDate')
    search_string = sgqlc.types.Field(String, graphql_name='searchString')
    status = sgqlc.types.Field(KbFactStatusFilter, graphql_name='status')
    update_date = sgqlc.types.Field('TimestampIntervalInput', graphql_name='updateDate')


class AccountTypeFilterSettings(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('creator', 'dictionary_exists', 'last_updater', 'name', 'pretrained_nercmodels', 'regexp_exists', 'registration_date', 'update_date')
    creator = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='creator')
    dictionary_exists = sgqlc.types.Field(Boolean, graphql_name='dictionaryExists')
    last_updater = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='lastUpdater')
    name = sgqlc.types.Field(String, graphql_name='name')
    pretrained_nercmodels = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='pretrainedNERCModels')
    regexp_exists = sgqlc.types.Field(Boolean, graphql_name='regexpExists')
    registration_date = sgqlc.types.Field('TimestampIntervalInput', graphql_name='registrationDate')
    update_date = sgqlc.types.Field('TimestampIntervalInput', graphql_name='updateDate')


class AccountTypeInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('description', 'domain_map_coordinate', 'name', 'platform_type_id', 'pretrained_nercmodels')
    description = sgqlc.types.Field(String, graphql_name='description')
    domain_map_coordinate = sgqlc.types.Field('Coordinate', graphql_name='domainMapCoordinate')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    platform_type_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='platformTypeId')
    pretrained_nercmodels = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='pretrainedNERCModels')


class AccountUpdateInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('access_level_id', 'account_type_id', 'country', 'end_date', 'id', 'key', 'language', 'markers', 'name', 'platform_id', 'start_date', 'url')
    access_level_id = sgqlc.types.Field(ID, graphql_name='accessLevelId')
    account_type_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='accountTypeId')
    country = sgqlc.types.Field(String, graphql_name='country')
    end_date = sgqlc.types.Field('DateTimeInput', graphql_name='endDate')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    key = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='key')
    language = sgqlc.types.Field(String, graphql_name='language')
    markers = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))), graphql_name='markers')
    name = sgqlc.types.Field(String, graphql_name='name')
    platform_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='platformId')
    start_date = sgqlc.types.Field('DateTimeInput', graphql_name='startDate')
    url = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='url')


class AddConceptNodeInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('concept_id', 'x_coordinate', 'y_coordinate')
    concept_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='conceptId')
    x_coordinate = sgqlc.types.Field(Float, graphql_name='xCoordinate')
    y_coordinate = sgqlc.types.Field(Float, graphql_name='yCoordinate')


class AddDocumentNodeInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('document_id', 'x_coordinate', 'y_coordinate')
    document_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='documentId')
    x_coordinate = sgqlc.types.Field(Float, graphql_name='xCoordinate')
    y_coordinate = sgqlc.types.Field(Float, graphql_name='yCoordinate')


class AddDocumentRubricInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('document_id', 'list_rubric_ids')
    document_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='documentId')
    list_rubric_ids = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='listRubricIds')


class AddRubricInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('name', 'notes', 'parent_rubric_id', 'rubric_power', 'rubricator_id', 'transformator_id')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    notes = sgqlc.types.Field(String, graphql_name='notes')
    parent_rubric_id = sgqlc.types.Field(ID, graphql_name='parentRubricId')
    rubric_power = sgqlc.types.Field(Int, graphql_name='rubricPower')
    rubricator_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='rubricatorId')
    transformator_id = sgqlc.types.Field(ID, graphql_name='transformatorId')


class AddRubricatorInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('name', 'notes', 'transformator_id')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    notes = sgqlc.types.Field(String, graphql_name='notes')
    transformator_id = sgqlc.types.Field(ID, graphql_name='transformatorId')


class AnnotationInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('end', 'node_id', 'start')
    end = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='end')
    node_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='nodeId')
    start = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='start')


class ApproveResearchMapEntitiesInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('concept_fact_ids', 'concept_ids', 'link_ids')
    concept_fact_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='conceptFactIds')
    concept_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='conceptIds')
    link_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='linkIds')


class BatchUpdateFactInput(sgqlc.types.Input):
    __schema__ = api_schema
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


class BulkDocumentUpdateInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('access_level_id', 'account', 'clear_access_level_id', 'clear_account', 'clear_external_url', 'clear_notes', 'clear_platform', 'clear_publication_author', 'clear_publication_date', 'clear_trust_level', 'external_url', 'notes', 'platform', 'publication_author', 'publication_date', 'trust_level')
    access_level_id = sgqlc.types.Field(ID, graphql_name='accessLevelId')
    account = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='account')
    clear_access_level_id = sgqlc.types.Field(Boolean, graphql_name='clearAccessLevelId')
    clear_account = sgqlc.types.Field(Boolean, graphql_name='clearAccount')
    clear_external_url = sgqlc.types.Field(Boolean, graphql_name='clearExternalUrl')
    clear_notes = sgqlc.types.Field(Boolean, graphql_name='clearNotes')
    clear_platform = sgqlc.types.Field(Boolean, graphql_name='clearPlatform')
    clear_publication_author = sgqlc.types.Field(Boolean, graphql_name='clearPublicationAuthor')
    clear_publication_date = sgqlc.types.Field(Boolean, graphql_name='clearPublicationDate')
    clear_trust_level = sgqlc.types.Field(Boolean, graphql_name='clearTrustLevel')
    external_url = sgqlc.types.Field(String, graphql_name='externalUrl')
    notes = sgqlc.types.Field(String, graphql_name='notes')
    platform = sgqlc.types.Field(ID, graphql_name='platform')
    publication_author = sgqlc.types.Field(String, graphql_name='publicationAuthor')
    publication_date = sgqlc.types.Field(UnixTime, graphql_name='publicationDate')
    trust_level = sgqlc.types.Field(TrustLevel, graphql_name='trustLevel')


class BulkMarkersInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('bulk_type', 'ids')
    bulk_type = sgqlc.types.Field(sgqlc.types.non_null(BulkType), graphql_name='bulkType')
    ids = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='ids')


class BulkMarkersUpdateInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('bulk_type', 'ids', 'markers_to_add', 'markers_to_delete')
    bulk_type = sgqlc.types.Field(sgqlc.types.non_null(BulkType), graphql_name='bulkType')
    ids = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='ids')
    markers_to_add = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))), graphql_name='markersToAdd')
    markers_to_delete = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))), graphql_name='markersToDelete')


class BulkUpdateDocumentMetadataInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('access_level_id', 'clear_access_level_id', 'clear_notes', 'clear_trust_level', 'notes', 'trust_level')
    access_level_id = sgqlc.types.Field(ID, graphql_name='accessLevelId')
    clear_access_level_id = sgqlc.types.Field(Boolean, graphql_name='clearAccessLevelId')
    clear_notes = sgqlc.types.Field(Boolean, graphql_name='clearNotes')
    clear_trust_level = sgqlc.types.Field(Boolean, graphql_name='clearTrustLevel')
    notes = sgqlc.types.Field(String, graphql_name='notes')
    trust_level = sgqlc.types.Field(TrustLevel, graphql_name='trustLevel')


class ComponentValueInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('id', 'value')
    id = sgqlc.types.Field(ID, graphql_name='id')
    value = sgqlc.types.Field(sgqlc.types.non_null('ValueInput'), graphql_name='value')


class CompositePropertyTypeFilterSettings(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('concept_type_id', 'link_type_id', 'name')
    concept_type_id = sgqlc.types.Field(ID, graphql_name='conceptTypeId')
    link_type_id = sgqlc.types.Field(ID, graphql_name='linkTypeId')
    name = sgqlc.types.Field(String, graphql_name='name')


class CompositePropertyValueComponentFactInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('component_value_type_id', 'composite_property_value_fact_id', 'id', 'reject', 'value_fact_id')
    component_value_type_id = sgqlc.types.Field(ID, graphql_name='componentValueTypeId')
    composite_property_value_fact_id = sgqlc.types.Field(ID, graphql_name='compositePropertyValueFactId')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    reject = sgqlc.types.Field(Boolean, graphql_name='reject')
    value_fact_id = sgqlc.types.Field(ID, graphql_name='valueFactId')


class CompositePropertyValueFactInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('composite_value_type_id', 'id', 'reject')
    composite_value_type_id = sgqlc.types.Field(ID, graphql_name='compositeValueTypeId')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    reject = sgqlc.types.Field(Boolean, graphql_name='reject')


class CompositePropertyValueTemplateCreateInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('component_value_types', 'id', 'name')
    component_value_types = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('NamedValueType'))), graphql_name='componentValueTypes')
    id = sgqlc.types.Field(ID, graphql_name='id')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')


class CompositePropertyValueTemplateFilterSettings(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('creator', 'last_updater', 'name', 'registration_date', 'update_date')
    creator = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='creator')
    last_updater = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='lastUpdater')
    name = sgqlc.types.Field(String, graphql_name='name')
    registration_date = sgqlc.types.Field('TimestampIntervalInput', graphql_name='registrationDate')
    update_date = sgqlc.types.Field('TimestampIntervalInput', graphql_name='updateDate')


class ConceptAddImplicitLinkInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('first_node_id', 'second_node_id')
    first_node_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='firstNodeId')
    second_node_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='secondNodeId')


class ConceptDuplicateFilterSettings(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('concept_id', 'group_id', 'input_value')
    concept_id = sgqlc.types.Field(ID, graphql_name='conceptId')
    group_id = sgqlc.types.Field(ID, graphql_name='groupId')
    input_value = sgqlc.types.Field(String, graphql_name='inputValue')


class ConceptDuplicateGroupFilterSettings(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('concept_type_ids', 'contains_concept_id', 'creators', 'input_value', 'report_id', 'task_created_at', 'task_ids', 'task_method_ids')
    concept_type_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='conceptTypeIds')
    contains_concept_id = sgqlc.types.Field(ID, graphql_name='containsConceptId')
    creators = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='creators')
    input_value = sgqlc.types.Field(String, graphql_name='inputValue')
    report_id = sgqlc.types.Field(ID, graphql_name='reportId')
    task_created_at = sgqlc.types.Field('TimestampIntervalInput', graphql_name='taskCreatedAt')
    task_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='taskIds')
    task_method_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='taskMethodIds')


class ConceptDuplicateReportFilterSettings(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('created_at', 'creators', 'input_value', 'task_created_at', 'task_ids', 'task_method_ids', 'updated_at', 'updaters')
    created_at = sgqlc.types.Field('TimestampIntervalInput', graphql_name='createdAt')
    creators = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='creators')
    input_value = sgqlc.types.Field(String, graphql_name='inputValue')
    task_created_at = sgqlc.types.Field('TimestampIntervalInput', graphql_name='taskCreatedAt')
    task_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='taskIds')
    task_method_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='taskMethodIds')
    updated_at = sgqlc.types.Field('TimestampIntervalInput', graphql_name='updatedAt')
    updaters = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='updaters')


class ConceptExtraSettings(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('search_on_map', 'selected_content')
    search_on_map = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='searchOnMap')
    selected_content = sgqlc.types.Field('ResearchMapContentSelectInput', graphql_name='selectedContent')


class ConceptFactInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('approved', 'concept_id', 'concept_type_id', 'id', 'reject')
    approved = sgqlc.types.Field(Boolean, graphql_name='approved')
    concept_id = sgqlc.types.Field(ID, graphql_name='conceptId')
    concept_type_id = sgqlc.types.Field(ID, graphql_name='conceptTypeId')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    reject = sgqlc.types.Field(Boolean, graphql_name='reject')


class ConceptFilterSettings(sgqlc.types.Input):
    __schema__ = api_schema
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


class ConceptLinkCreationMutationInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('access_level_id', 'concept_from_id', 'concept_to_id', 'end_date', 'entity_from_id', 'entity_to_id', 'fact_info', 'link_type_id', 'notes', 'start_date')
    access_level_id = sgqlc.types.Field(ID, graphql_name='accessLevelId')
    concept_from_id = sgqlc.types.Field(ID, graphql_name='conceptFromId')
    concept_to_id = sgqlc.types.Field(ID, graphql_name='conceptToId')
    end_date = sgqlc.types.Field('DateTimeInput', graphql_name='endDate')
    entity_from_id = sgqlc.types.Field(ID, graphql_name='entityFromId')
    entity_to_id = sgqlc.types.Field(ID, graphql_name='entityToId')
    fact_info = sgqlc.types.Field('FactInput', graphql_name='factInfo')
    link_type_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='linkTypeId')
    notes = sgqlc.types.Field(String, graphql_name='notes')
    start_date = sgqlc.types.Field('DateTimeInput', graphql_name='startDate')


class ConceptLinkFactInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('approved', 'concept_from_fact_id', 'concept_to_fact_id', 'id', 'link_type_id', 'reject')
    approved = sgqlc.types.Field(Boolean, graphql_name='approved')
    concept_from_fact_id = sgqlc.types.Field(ID, graphql_name='conceptFromFactId')
    concept_to_fact_id = sgqlc.types.Field(ID, graphql_name='conceptToFactId')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    link_type_id = sgqlc.types.Field(ID, graphql_name='linkTypeId')
    reject = sgqlc.types.Field(Boolean, graphql_name='reject')


class ConceptLinkFilterSettings(sgqlc.types.Input):
    __schema__ = api_schema
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
    __schema__ = api_schema
    __field_names__ = ('approved', 'concept_link_fact_id', 'id', 'link_property_type_id', 'reject', 'value_fact_id')
    approved = sgqlc.types.Field(Boolean, graphql_name='approved')
    concept_link_fact_id = sgqlc.types.Field(ID, graphql_name='conceptLinkFactId')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    link_property_type_id = sgqlc.types.Field(ID, graphql_name='linkPropertyTypeId')
    reject = sgqlc.types.Field(Boolean, graphql_name='reject')
    value_fact_id = sgqlc.types.Field(ID, graphql_name='valueFactId')


class ConceptLinkPropertyInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('access_level_id', 'end_date', 'fact_info', 'is_main', 'link_id', 'notes', 'property_type_id', 'start_date', 'value_input')
    access_level_id = sgqlc.types.Field(ID, graphql_name='accessLevelId')
    end_date = sgqlc.types.Field('DateTimeInput', graphql_name='endDate')
    fact_info = sgqlc.types.Field('FactInput', graphql_name='factInfo')
    is_main = sgqlc.types.Field(Boolean, graphql_name='isMain')
    link_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='linkId')
    notes = sgqlc.types.Field(String, graphql_name='notes')
    property_type_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='propertyTypeId')
    start_date = sgqlc.types.Field('DateTimeInput', graphql_name='startDate')
    value_input = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ComponentValueInput))), graphql_name='valueInput')


class ConceptLinkPropertyTypeCreationInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('link_type_id', 'name', 'notify_on_update', 'pretrained_rel_ext_models', 'value_type_id')
    link_type_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='linkTypeId')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    notify_on_update = sgqlc.types.Field(Boolean, graphql_name='notifyOnUpdate')
    pretrained_rel_ext_models = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('RelExtModelInput')), graphql_name='pretrainedRelExtModels')
    value_type_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='valueTypeId')


class ConceptLinkPropertyTypeUpdateInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('computable_formula', 'deprecated', 'id', 'name', 'notify_on_update', 'pretrained_rel_ext_models', 'value_type_id')
    computable_formula = sgqlc.types.Field(String, graphql_name='computableFormula')
    deprecated = sgqlc.types.Field(Boolean, graphql_name='deprecated')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    notify_on_update = sgqlc.types.Field(Boolean, graphql_name='notifyOnUpdate')
    pretrained_rel_ext_models = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('RelExtModelInput')), graphql_name='pretrainedRelExtModels')
    value_type_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='valueTypeId')


class ConceptLinkTypeCreationInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('concept_from_type_id', 'concept_to_type_id', 'is_directed', 'is_hierarchical', 'name', 'notify_on_update', 'pretrained_rel_ext_models')
    concept_from_type_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='conceptFromTypeId')
    concept_to_type_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='conceptToTypeId')
    is_directed = sgqlc.types.Field(Boolean, graphql_name='isDirected')
    is_hierarchical = sgqlc.types.Field(Boolean, graphql_name='isHierarchical')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    notify_on_update = sgqlc.types.Field(Boolean, graphql_name='notifyOnUpdate')
    pretrained_rel_ext_models = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('RelExtModelInput')), graphql_name='pretrainedRelExtModels')


class ConceptLinkTypeFilterSettings(sgqlc.types.Input):
    __schema__ = api_schema
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


class ConceptLinkTypePathInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('fixed', 'link_type_id')
    fixed = sgqlc.types.Field(ConceptLinkDirection, graphql_name='fixed')
    link_type_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='linkTypeId')


class ConceptLinkTypeUpdateInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('concept_from_type_id', 'concept_to_type_id', 'id', 'is_directed', 'is_hierarchical', 'name', 'notify_on_update', 'pretrained_rel_ext_models')
    concept_from_type_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='conceptFromTypeId')
    concept_to_type_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='conceptToTypeId')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    is_directed = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isDirected')
    is_hierarchical = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isHierarchical')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    notify_on_update = sgqlc.types.Field(Boolean, graphql_name='notifyOnUpdate')
    pretrained_rel_ext_models = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('RelExtModelInput')), graphql_name='pretrainedRelExtModels')


class ConceptLinkUpdateMutationInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('access_level_id', 'approved', 'end_date', 'id', 'notes', 'start_date')
    access_level_id = sgqlc.types.Field(ID, graphql_name='accessLevelId')
    approved = sgqlc.types.Field(Boolean, graphql_name='approved')
    end_date = sgqlc.types.Field('DateTimeInput', graphql_name='endDate')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    notes = sgqlc.types.Field(String, graphql_name='notes')
    start_date = sgqlc.types.Field('DateTimeInput', graphql_name='startDate')


class ConceptMergeInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('main_concept_id', 'merged_concept_id')
    main_concept_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='mainConceptId')
    merged_concept_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='mergedConceptId')


class ConceptMutationInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('access_level_id', 'concept_type_id', 'end_date', 'fact_info', 'markers', 'name', 'notes', 'start_date')
    access_level_id = sgqlc.types.Field(ID, graphql_name='accessLevelId')
    concept_type_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='conceptTypeId')
    end_date = sgqlc.types.Field('DateTimeInput', graphql_name='endDate')
    fact_info = sgqlc.types.Field('FactInput', graphql_name='factInfo')
    markers = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='markers')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    notes = sgqlc.types.Field(String, graphql_name='notes')
    start_date = sgqlc.types.Field('DateTimeInput', graphql_name='startDate')


class ConceptPresentationFilterSettings(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('access_level_id', 'concept_type_presentation_ids', 'concept_variant', 'creation_date', 'creator', 'exact_name', 'last_updater', 'link_filter_settings', 'markers', 'name', 'property_filter_settings', 'status', 'substring', 'update_date')
    access_level_id = sgqlc.types.Field(ID, graphql_name='accessLevelId')
    concept_type_presentation_ids = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='conceptTypePresentationIds')
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


class ConceptPropertyCreateInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('access_level_id', 'concept_id', 'end_date', 'fact_info', 'is_main', 'notes', 'property_type_id', 'start_date', 'value_input')
    access_level_id = sgqlc.types.Field(ID, graphql_name='accessLevelId')
    concept_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='conceptId')
    end_date = sgqlc.types.Field('DateTimeInput', graphql_name='endDate')
    fact_info = sgqlc.types.Field('FactInput', graphql_name='factInfo')
    is_main = sgqlc.types.Field(Boolean, graphql_name='isMain')
    notes = sgqlc.types.Field(String, graphql_name='notes')
    property_type_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='propertyTypeId')
    start_date = sgqlc.types.Field('DateTimeInput', graphql_name='startDate')
    value_input = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ComponentValueInput))), graphql_name='valueInput')


class ConceptPropertyFactInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('approved', 'concept_fact_id', 'id', 'property_type_id', 'reject', 'value_fact_id')
    approved = sgqlc.types.Field(Boolean, graphql_name='approved')
    concept_fact_id = sgqlc.types.Field(ID, graphql_name='conceptFactId')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    property_type_id = sgqlc.types.Field(ID, graphql_name='propertyTypeId')
    reject = sgqlc.types.Field(Boolean, graphql_name='reject')
    value_fact_id = sgqlc.types.Field(ID, graphql_name='valueFactId')


class ConceptPropertyFilterSettings(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('document_id', 'only_main', 'property_type', 'status', 'value', 'value_type')
    document_id = sgqlc.types.Field(ID, graphql_name='documentId')
    only_main = sgqlc.types.Field(Boolean, graphql_name='onlyMain')
    property_type = sgqlc.types.Field(ID, graphql_name='propertyType')
    status = sgqlc.types.Field(KbFactStatusFilter, graphql_name='status')
    value = sgqlc.types.Field('ValueFilterInput', graphql_name='value')
    value_type = sgqlc.types.Field(ValueType, graphql_name='valueType')


class ConceptPropertyTypeCreationInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('concept_type_id', 'name', 'notify_on_update', 'pretrained_rel_ext_models', 'use_for_auto_rubricator', 'value_type_id')
    concept_type_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='conceptTypeId')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    notify_on_update = sgqlc.types.Field(Boolean, graphql_name='notifyOnUpdate')
    pretrained_rel_ext_models = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('RelExtModelInput')), graphql_name='pretrainedRelExtModels')
    use_for_auto_rubricator = sgqlc.types.Field(Boolean, graphql_name='useForAutoRubricator')
    value_type_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='valueTypeId')


class ConceptPropertyTypeFilterSettings(sgqlc.types.Input):
    __schema__ = api_schema
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


class ConceptPropertyTypeUpdateInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('deprecated', 'id', 'name', 'notify_on_update', 'pretrained_rel_ext_models', 'use_for_auto_rubricator', 'value_type_id')
    deprecated = sgqlc.types.Field(Boolean, graphql_name='deprecated')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    notify_on_update = sgqlc.types.Field(Boolean, graphql_name='notifyOnUpdate')
    pretrained_rel_ext_models = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('RelExtModelInput')), graphql_name='pretrainedRelExtModels')
    use_for_auto_rubricator = sgqlc.types.Field(Boolean, graphql_name='useForAutoRubricator')
    value_type_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='valueTypeId')


class ConceptPropertyUpdateInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('access_level_id', 'approved', 'computable_value', 'end_date', 'is_main', 'notes', 'property_id', 'start_date', 'value_input')
    access_level_id = sgqlc.types.Field(ID, graphql_name='accessLevelId')
    approved = sgqlc.types.Field(Boolean, graphql_name='approved')
    computable_value = sgqlc.types.Field(String, graphql_name='computableValue')
    end_date = sgqlc.types.Field('DateTimeInput', graphql_name='endDate')
    is_main = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isMain')
    notes = sgqlc.types.Field(String, graphql_name='notes')
    property_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='propertyId')
    start_date = sgqlc.types.Field('DateTimeInput', graphql_name='startDate')
    value_input = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ComponentValueInput))), graphql_name='valueInput')


class ConceptPropertyValueTypeCreationInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('name', 'pretrained_nercmodels', 'use_for_auto_rubricator', 'value_restriction', 'value_type')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    pretrained_nercmodels = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='pretrainedNERCModels')
    use_for_auto_rubricator = sgqlc.types.Field(Boolean, graphql_name='useForAutoRubricator')
    value_restriction = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='valueRestriction')
    value_type = sgqlc.types.Field(sgqlc.types.non_null(ValueType), graphql_name='valueType')


class ConceptPropertyValueTypeFilterSettings(sgqlc.types.Input):
    __schema__ = api_schema
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


class ConceptPropertyValueTypeUpdateInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('id', 'name', 'pretrained_nercmodels', 'use_for_auto_rubricator', 'value_restriction', 'value_type')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    pretrained_nercmodels = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))), graphql_name='pretrainedNERCModels')
    use_for_auto_rubricator = sgqlc.types.Field(Boolean, graphql_name='useForAutoRubricator')
    value_restriction = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))), graphql_name='valueRestriction')
    value_type = sgqlc.types.Field(sgqlc.types.non_null(ValueType), graphql_name='valueType')


class ConceptRegistryViewInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('columns', 'metrics', 'sorting')
    columns = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ConceptViewColumnType)), graphql_name='columns')
    metrics = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ConceptViewMetricType)), graphql_name='metrics')
    sorting = sgqlc.types.Field('ConceptRegistryViewSortingInput', graphql_name='sorting')


class ConceptRegistryViewSortingInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('sort_direction', 'sorting_type')
    sort_direction = sgqlc.types.Field(sgqlc.types.non_null(SortDirection), graphql_name='sortDirection')
    sorting_type = sgqlc.types.Field(sgqlc.types.non_null(ConceptSorting), graphql_name='sortingType')


class ConceptTypeFilterSettings(sgqlc.types.Input):
    __schema__ = api_schema
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


class ConceptTypeInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('domain_map_coordinate', 'is_event', 'name', 'pretrained_nercmodels', 'use_for_auto_rubricator')
    domain_map_coordinate = sgqlc.types.Field('Coordinate', graphql_name='domainMapCoordinate')
    is_event = sgqlc.types.Field(Boolean, graphql_name='isEvent')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    pretrained_nercmodels = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='pretrainedNERCModels')
    use_for_auto_rubricator = sgqlc.types.Field(Boolean, graphql_name='useForAutoRubricator')


class ConceptTypePresentationAddInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('has_header_information', 'has_supporting_documents', 'hide_empty_rows', 'is_default', 'layout', 'name', 'root_concept_type_id', 'show_in_menu')
    has_header_information = sgqlc.types.Field(Boolean, graphql_name='hasHeaderInformation')
    has_supporting_documents = sgqlc.types.Field(Boolean, graphql_name='hasSupportingDocuments')
    hide_empty_rows = sgqlc.types.Field(Boolean, graphql_name='hideEmptyRows')
    is_default = sgqlc.types.Field(Boolean, graphql_name='isDefault')
    layout = sgqlc.types.Field(String, graphql_name='layout')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    root_concept_type_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='rootConceptTypeId')
    show_in_menu = sgqlc.types.Field(Boolean, graphql_name='showInMenu')


class ConceptTypePresentationFilterSettings(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('creator', 'last_updater', 'name', 'registration_date', 'update_date')
    creator = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='creator')
    last_updater = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='lastUpdater')
    name = sgqlc.types.Field(String, graphql_name='name')
    registration_date = sgqlc.types.Field('TimestampIntervalInput', graphql_name='registrationDate')
    update_date = sgqlc.types.Field('TimestampIntervalInput', graphql_name='updateDate')


class ConceptTypePresentationUpdateInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('has_header_information', 'has_supporting_documents', 'hide_empty_rows', 'id', 'is_default', 'layout', 'name', 'show_in_menu')
    has_header_information = sgqlc.types.Field(Boolean, graphql_name='hasHeaderInformation')
    has_supporting_documents = sgqlc.types.Field(Boolean, graphql_name='hasSupportingDocuments')
    hide_empty_rows = sgqlc.types.Field(Boolean, graphql_name='hideEmptyRows')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    is_default = sgqlc.types.Field(Boolean, graphql_name='isDefault')
    layout = sgqlc.types.Field(String, graphql_name='layout')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    show_in_menu = sgqlc.types.Field(Boolean, graphql_name='showInMenu')


class ConceptTypePresentationUpdateTemplateFilenameInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('bucket', 'filename', 'id')
    bucket = sgqlc.types.Field(String, graphql_name='bucket')
    filename = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='filename')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')


class ConceptTypePresentationViewInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('concept_type_id', 'concept_type_presentation_id')
    concept_type_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='conceptTypeId')
    concept_type_presentation_id = sgqlc.types.Field(ID, graphql_name='conceptTypePresentationId')


class ConceptTypePresentationWidgetTypeAddInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('columns', 'concept_type_presentation_id', 'name', 'table_type')
    columns = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ConceptTypePresentationWidgetTypeColumnInput'))), graphql_name='columns')
    concept_type_presentation_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='conceptTypePresentationId')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    table_type = sgqlc.types.Field(sgqlc.types.non_null(WidgetTypeTableType), graphql_name='tableType')


class ConceptTypePresentationWidgetTypeColumnInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('concept_link_type_ids_path', 'is_main_properties', 'list_values', 'name', 'sort_by_column', 'sort_direction', 'value_info')
    concept_link_type_ids_path = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ConceptLinkTypePathInput)), graphql_name='conceptLinkTypeIdsPath')
    is_main_properties = sgqlc.types.Field(Boolean, graphql_name='isMainProperties')
    list_values = sgqlc.types.Field(Boolean, graphql_name='listValues')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    sort_by_column = sgqlc.types.Field(Boolean, graphql_name='sortByColumn')
    sort_direction = sgqlc.types.Field(SortDirection, graphql_name='sortDirection')
    value_info = sgqlc.types.Field(sgqlc.types.non_null('ConceptTypePresentationWidgetTypeColumnValueInfoInput'), graphql_name='valueInfo')


class ConceptTypePresentationWidgetTypeColumnValueInfoInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('link_metadata', 'link_property_type_id', 'metadata', 'property_type_id')
    link_metadata = sgqlc.types.Field(ConceptTypeLinkMetadata, graphql_name='linkMetadata')
    link_property_type_id = sgqlc.types.Field(ID, graphql_name='linkPropertyTypeId')
    metadata = sgqlc.types.Field(ConceptTypeMetadata, graphql_name='metadata')
    property_type_id = sgqlc.types.Field(ID, graphql_name='propertyTypeId')


class ConceptTypePresentationWidgetTypeUpdateInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('columns', 'id', 'name', 'table_type')
    columns = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ConceptTypePresentationWidgetTypeColumnInput))), graphql_name='columns')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    table_type = sgqlc.types.Field(sgqlc.types.non_null(WidgetTypeTableType), graphql_name='tableType')


class ConceptTypePresentationWidgetTypeUpdateOrderInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('concept_type_presentation_id', 'ids')
    concept_type_presentation_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='conceptTypePresentationId')
    ids = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='ids')


class ConceptTypeViewCreationInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('columns', 'concept_type_id', 'name', 'show_in_menu')
    columns = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ConceptTypePresentationWidgetTypeColumnInput))), graphql_name='columns')
    concept_type_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='conceptTypeId')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    show_in_menu = sgqlc.types.Field(Boolean, graphql_name='showInMenu')


class ConceptTypeViewUpdateInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('columns', 'id', 'name', 'show_in_menu')
    columns = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ConceptTypePresentationWidgetTypeColumnInput))), graphql_name='columns')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    show_in_menu = sgqlc.types.Field(Boolean, graphql_name='showInMenu')


class ConceptUnmergeInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('main_concept_id', 'merged_concept_id')
    main_concept_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='mainConceptId')
    merged_concept_id = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='mergedConceptId')


class ConceptUpdateInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('access_level_id', 'approved', 'concept_id', 'concept_type_id', 'document_input', 'end_date', 'markers', 'name', 'notes', 'start_date')
    access_level_id = sgqlc.types.Field(ID, graphql_name='accessLevelId')
    approved = sgqlc.types.Field(Boolean, graphql_name='approved')
    concept_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='conceptId')
    concept_type_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='conceptTypeId')
    document_input = sgqlc.types.Field('FactInput', graphql_name='documentInput')
    end_date = sgqlc.types.Field('DateTimeInput', graphql_name='endDate')
    markers = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='markers')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    notes = sgqlc.types.Field(String, graphql_name='notes')
    start_date = sgqlc.types.Field('DateTimeInput', graphql_name='startDate')


class Coordinate(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('x', 'y')
    x = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='x')
    y = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='y')


class CoordinatesInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('latitude', 'longitude')
    latitude = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='latitude')
    longitude = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='longitude')


class CountryFilterSettings(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('search_string', 'target')
    search_string = sgqlc.types.Field(String, graphql_name='searchString')
    target = sgqlc.types.Field(CountryTarget, graphql_name='target')


class DateInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('day', 'month', 'year')
    day = sgqlc.types.Field(Int, graphql_name='day')
    month = sgqlc.types.Field(Int, graphql_name='month')
    year = sgqlc.types.Field(Int, graphql_name='year')


class DateTimeInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('date', 'time')
    date = sgqlc.types.Field(sgqlc.types.non_null(DateInput), graphql_name='date')
    time = sgqlc.types.Field('TimeInput', graphql_name='time')


class DateTimeIntervalInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('end', 'start')
    end = sgqlc.types.Field(DateTimeInput, graphql_name='end')
    start = sgqlc.types.Field(DateTimeInput, graphql_name='start')


class DocumentAllKBFactsRemoveInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('document_id', 'kb_entity_id')
    document_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='documentId')
    kb_entity_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='kbEntityId')


class DocumentAvatarUpdateInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('children_document_id', 'id')
    children_document_id = sgqlc.types.Field(ID, graphql_name='childrenDocumentId')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')


class DocumentDeleteCandidateFactInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('document_id', 'fact_id')
    document_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='documentId')
    fact_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='factId')


class DocumentDuplicateReportFilterSettings(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('created_at', 'creators', 'input_value', 'status')
    created_at = sgqlc.types.Field('TimestampIntervalInput', graphql_name='createdAt')
    creators = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='creators')
    input_value = sgqlc.types.Field(String, graphql_name='inputValue')
    status = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(DocumentDuplicateReportStatus)), graphql_name='status')


class DocumentDuplicateReportInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('auto_delete', 'comparison_fields', 'filter_setting', 'ignore_markup')
    auto_delete = sgqlc.types.Field(Boolean, graphql_name='autoDelete')
    comparison_fields = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(DocumentDuplicateComparisonField))), graphql_name='comparisonFields')
    filter_setting = sgqlc.types.Field(sgqlc.types.non_null('DocumentFilterSettings'), graphql_name='filterSetting')
    ignore_markup = sgqlc.types.Field(Boolean, graphql_name='ignoreMarkup')


class DocumentDuplicateTaskFilterSettings(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('query', 'report_id', 'status')
    query = sgqlc.types.Field(String, graphql_name='query')
    report_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='reportId')
    status = sgqlc.types.Field(DocumentDuplicateTaskStatus, graphql_name='status')


class DocumentFeedCreationInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('filter_settings', 'is_refresh_locked', 'name', 'query')
    filter_settings = sgqlc.types.Field('DocumentFilterSettings', graphql_name='filterSettings')
    is_refresh_locked = sgqlc.types.Field(Boolean, graphql_name='isRefreshLocked')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    query = sgqlc.types.Field(String, graphql_name='query')


class DocumentFeedFilterSettings(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('creator', 'id', 'last_updater', 'registration_date', 'search_string', 'update_date')
    creator = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='creator')
    id = sgqlc.types.Field(ID, graphql_name='id')
    last_updater = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='lastUpdater')
    registration_date = sgqlc.types.Field('TimestampIntervalInput', graphql_name='registrationDate')
    search_string = sgqlc.types.Field(String, graphql_name='searchString')
    update_date = sgqlc.types.Field('TimestampIntervalInput', graphql_name='updateDate')


class DocumentFeedUpdateInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('filter_settings', 'is_refresh_locked', 'name')
    filter_settings = sgqlc.types.Field('DocumentFilterSettings', graphql_name='filterSettings')
    is_refresh_locked = sgqlc.types.Field(Boolean, graphql_name='isRefreshLocked')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')


class DocumentFeedViewInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('columns', 'metrics', 'sorting')
    columns = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(DocumentViewColumnType)), graphql_name='columns')
    metrics = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(DocumentViewMetricType)), graphql_name='metrics')
    sorting = sgqlc.types.Field('DocumentFeedViewSortingInput', graphql_name='sorting')


class DocumentFeedViewSortingInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('sort_direction', 'sorting_type')
    sort_direction = sgqlc.types.Field(sgqlc.types.non_null(SortDirection), graphql_name='sortDirection')
    sorting_type = sgqlc.types.Field(sgqlc.types.non_null(DocumentInFeedSorting), graphql_name='sortingType')


class DocumentFilterSettings(sgqlc.types.Input):
    __schema__ = api_schema
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


class DocumentNodeUpdateInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('id', 'language', 'node_id', 'translation')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    language = sgqlc.types.Field('LanguageUpdateInput', graphql_name='language')
    node_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='nodeId')
    translation = sgqlc.types.Field('TranslationInput', graphql_name='translation')


class DocumentRegistryViewInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('columns', 'metrics', 'relevance_metrics', 'sorting')
    columns = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(DocumentViewColumnType)), graphql_name='columns')
    metrics = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(DocumentViewMetricType)), graphql_name='metrics')
    relevance_metrics = sgqlc.types.Field('DocumentRelevanceMetricsInput', graphql_name='relevanceMetrics')
    sorting = sgqlc.types.Field('DocumentRegistryViewSortingInput', graphql_name='sorting')


class DocumentRegistryViewSortingInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('sort_direction', 'sorting_type')
    sort_direction = sgqlc.types.Field(sgqlc.types.non_null(SortDirection), graphql_name='sortDirection')
    sorting_type = sgqlc.types.Field(sgqlc.types.non_null(DocumentSorting), graphql_name='sortingType')


class DocumentRelevanceMetricsInput(sgqlc.types.Input):
    __schema__ = api_schema
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


class DocumentRubricFilterSettings(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('created_at', 'creator_ids', 'document_id', 'input_value', 'rubric_ids', 'rubricator_ids', 'statuses', 'updated_at', 'updater_ids')
    created_at = sgqlc.types.Field('TimestampIntervalInput', graphql_name='createdAt')
    creator_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='creatorIds')
    document_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='documentId')
    input_value = sgqlc.types.Field(String, graphql_name='inputValue')
    rubric_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='rubricIds')
    rubricator_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='rubricatorIds')
    statuses = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(DocumentRubricStatus)), graphql_name='statuses')
    updated_at = sgqlc.types.Field('TimestampIntervalInput', graphql_name='updatedAt')
    updater_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='updaterIds')


class DocumentTypeFilterSettings(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('creator', 'dictionary_exists', 'last_updater', 'name', 'pretrained_nercmodels', 'regexp_exists', 'registration_date', 'update_date')
    creator = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='creator')
    dictionary_exists = sgqlc.types.Field(Boolean, graphql_name='dictionaryExists')
    last_updater = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='lastUpdater')
    name = sgqlc.types.Field(String, graphql_name='name')
    pretrained_nercmodels = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='pretrainedNERCModels')
    regexp_exists = sgqlc.types.Field(Boolean, graphql_name='regexpExists')
    registration_date = sgqlc.types.Field('TimestampIntervalInput', graphql_name='registrationDate')
    update_date = sgqlc.types.Field('TimestampIntervalInput', graphql_name='updateDate')


class DocumentTypeInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('domain_map_coordinate', 'name', 'pretrained_nercmodels')
    domain_map_coordinate = sgqlc.types.Field(Coordinate, graphql_name='domainMapCoordinate')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    pretrained_nercmodels = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='pretrainedNERCModels')


class DocumentTypePresentationAddInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('columns', 'document_type_id', 'is_default', 'name', 'show_in_menu')
    columns = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ConceptTypePresentationWidgetTypeColumnInput))), graphql_name='columns')
    document_type_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='documentTypeId')
    is_default = sgqlc.types.Field(Boolean, graphql_name='isDefault')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    show_in_menu = sgqlc.types.Field(Boolean, graphql_name='showInMenu')


class DocumentTypePresentationFilterSettings(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('creator', 'last_updater', 'name', 'registration_date', 'update_date')
    creator = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='creator')
    last_updater = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='lastUpdater')
    name = sgqlc.types.Field(String, graphql_name='name')
    registration_date = sgqlc.types.Field('TimestampIntervalInput', graphql_name='registrationDate')
    update_date = sgqlc.types.Field('TimestampIntervalInput', graphql_name='updateDate')


class DocumentTypePresentationUpdateInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('columns', 'id', 'is_default', 'name')
    columns = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ConceptTypePresentationWidgetTypeColumnInput))), graphql_name='columns')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    is_default = sgqlc.types.Field(Boolean, graphql_name='isDefault')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')


class DocumentTypePresentationViewInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('document_type_id', 'document_type_presentation_id')
    document_type_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='documentTypeId')
    document_type_presentation_id = sgqlc.types.Field(ID, graphql_name='documentTypePresentationId')


class DocumentUpdateInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('access_level_id', 'account', 'external_url', 'id', 'language', 'markers', 'notes', 'platform', 'preview_text', 'publication_author', 'publication_date', 'title', 'trust_level')
    access_level_id = sgqlc.types.Field(ID, graphql_name='accessLevelId')
    account = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='account')
    external_url = sgqlc.types.Field(String, graphql_name='externalUrl')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    language = sgqlc.types.Field(String, graphql_name='language')
    markers = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='markers')
    notes = sgqlc.types.Field(String, graphql_name='notes')
    platform = sgqlc.types.Field(ID, graphql_name='platform')
    preview_text = sgqlc.types.Field(String, graphql_name='previewText')
    publication_author = sgqlc.types.Field(String, graphql_name='publicationAuthor')
    publication_date = sgqlc.types.Field(Long, graphql_name='publicationDate')
    title = sgqlc.types.Field(String, graphql_name='title')
    trust_level = sgqlc.types.Field(TrustLevel, graphql_name='trustLevel')


class DoubleIntervalInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('end', 'start')
    end = sgqlc.types.Field(Float, graphql_name='end')
    start = sgqlc.types.Field(Float, graphql_name='start')


class DoubleValueInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('double',)
    double = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='double')


class ExtraSettings(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('ranking_script', 'search_on_map', 'selected_content', 'target_languages')
    ranking_script = sgqlc.types.Field(String, graphql_name='rankingScript')
    search_on_map = sgqlc.types.Field(Boolean, graphql_name='searchOnMap')
    selected_content = sgqlc.types.Field('ResearchMapContentSelectInput', graphql_name='selectedContent')
    target_languages = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='targetLanguages')


class FactInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('add_as_name', 'annotations', 'document_id', 'fact_id')
    add_as_name = sgqlc.types.Field(Boolean, graphql_name='addAsName')
    annotations = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('TextBoundingInput')), graphql_name='annotations')
    document_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='documentId')
    fact_id = sgqlc.types.Field(ID, graphql_name='factId')


class GeoCircularAreaInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('latitude_center', 'longitude_center', 'radius')
    latitude_center = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='latitudeCenter')
    longitude_center = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='longitudeCenter')
    radius = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='radius')


class GeoPointInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('name', 'point')
    name = sgqlc.types.Field(String, graphql_name='name')
    point = sgqlc.types.Field(CoordinatesInput, graphql_name='point')


class GeoPointWithNameInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('circular_area', 'name', 'rectangular_area')
    circular_area = sgqlc.types.Field(GeoCircularAreaInput, graphql_name='circularArea')
    name = sgqlc.types.Field(String, graphql_name='name')
    rectangular_area = sgqlc.types.Field('GeoRectangularAreaInput', graphql_name='rectangularArea')


class GeoRectangularAreaInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('latitude_max', 'latitude_min', 'longitude_max', 'longitude_min')
    latitude_max = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='latitudeMax')
    latitude_min = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='latitudeMin')
    longitude_max = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='longitudeMax')
    longitude_min = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='longitudeMin')


class GroupCreationInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('collapsed', 'layout', 'name', 'research_map_id', 'x_coordinate', 'y_coordinate')
    collapsed = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='collapsed')
    layout = sgqlc.types.Field(String, graphql_name='layout')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    research_map_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='researchMapId')
    x_coordinate = sgqlc.types.Field(Float, graphql_name='xCoordinate')
    y_coordinate = sgqlc.types.Field(Float, graphql_name='yCoordinate')


class GroupUpdateInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('collapsed', 'layout', 'name', 'x_coordinate', 'y_coordinate')
    collapsed = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='collapsed')
    layout = sgqlc.types.Field(String, graphql_name='layout')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    x_coordinate = sgqlc.types.Field(Float, graphql_name='xCoordinate')
    y_coordinate = sgqlc.types.Field(Float, graphql_name='yCoordinate')


class IntIntervalInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('end', 'start')
    end = sgqlc.types.Field(Int, graphql_name='end')
    start = sgqlc.types.Field(Int, graphql_name='start')


class IntValueInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('int',)
    int = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='int')


class InterestObjectMainPropertiesOrderUpdateInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('concept_type_id', 'ordered_main_property_type_ids')
    concept_type_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='conceptTypeId')
    ordered_main_property_type_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='orderedMainPropertyTypeIds')


class LanguageFilterSettings(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('search_string',)
    search_string = sgqlc.types.Field(String, graphql_name='searchString')


class LanguageInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('id',)
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')


class LanguageUpdateInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('id',)
    id = sgqlc.types.Field(ID, graphql_name='id')


class LinkFilterSettings(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('link_direction', 'link_type_id', 'other_concept_id', 'status')
    link_direction = sgqlc.types.Field(LinkDirection, graphql_name='linkDirection')
    link_type_id = sgqlc.types.Field(ID, graphql_name='linkTypeId')
    other_concept_id = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='otherConceptId')
    status = sgqlc.types.Field(KbFactStatusFilter, graphql_name='status')


class LinkValueInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('link',)
    link = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='link')


class LinkedConceptListFilterSettings(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('concept_template_name', 'status')
    concept_template_name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='conceptTemplateName')
    status = sgqlc.types.Field(KbFactStatusFilter, graphql_name='status')


class LinkedDocumentFilterSettings(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('document_content_type',)
    document_content_type = sgqlc.types.Field(DocumentContentType, graphql_name='documentContentType')


class MapDrawingAddInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('dashed', 'geo', 'opacity', 'research_map_id', 'stroke_color', 'stroke_width', 'x_coordinate', 'y_coordinate')
    dashed = sgqlc.types.Field(Boolean, graphql_name='dashed')
    geo = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='geo')
    opacity = sgqlc.types.Field(Float, graphql_name='opacity')
    research_map_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='researchMapId')
    stroke_color = sgqlc.types.Field(String, graphql_name='strokeColor')
    stroke_width = sgqlc.types.Field(String, graphql_name='strokeWidth')
    x_coordinate = sgqlc.types.Field(Float, graphql_name='xCoordinate')
    y_coordinate = sgqlc.types.Field(Float, graphql_name='yCoordinate')


class MapDrawingUpdateInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('dashed', 'geo', 'opacity', 'stroke_color', 'stroke_width', 'x_coordinate', 'y_coordinate')
    dashed = sgqlc.types.Field(Boolean, graphql_name='dashed')
    geo = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='geo')
    opacity = sgqlc.types.Field(Float, graphql_name='opacity')
    stroke_color = sgqlc.types.Field(String, graphql_name='strokeColor')
    stroke_width = sgqlc.types.Field(String, graphql_name='strokeWidth')
    x_coordinate = sgqlc.types.Field(Float, graphql_name='xCoordinate')
    y_coordinate = sgqlc.types.Field(Float, graphql_name='yCoordinate')


class MapEdgeFilterSettings(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('edge_type',)
    edge_type = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(MapEdgeType)), graphql_name='edgeType')


class MapNodeFilterSettings(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('node_type',)
    node_type = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(MapNodeType)), graphql_name='nodeType')


class MentionInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('annotation', 'id')
    annotation = sgqlc.types.Field(AnnotationInput, graphql_name='annotation')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')


class NERCRegexpInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('auto_create', 'context_regexp', 'regexp')
    auto_create = sgqlc.types.Field(Boolean, graphql_name='autoCreate')
    context_regexp = sgqlc.types.Field(String, graphql_name='contextRegexp')
    regexp = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='regexp')


class NamedValueType(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('is_required', 'name', 'value_type_id', 'view')
    is_required = sgqlc.types.Field(Boolean, graphql_name='isRequired')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    value_type_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='valueTypeId')
    view = sgqlc.types.Field(ComponentView, graphql_name='view')


class NodeMoveInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('id', 'x_coordinate', 'y_coordinate')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    x_coordinate = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='xCoordinate')
    y_coordinate = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='yCoordinate')


class NormalizationInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('type_id', 'value')
    type_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='typeId')
    value = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='value')


class PerformSynchronously(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('perform_synchronously',)
    perform_synchronously = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='performSynchronously')


class PlatformCreationInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('access_level_id', 'country', 'end_date', 'key', 'language', 'markers', 'name', 'platform_type_id', 'start_date', 'url')
    access_level_id = sgqlc.types.Field(ID, graphql_name='accessLevelId')
    country = sgqlc.types.Field(String, graphql_name='country')
    end_date = sgqlc.types.Field(DateTimeInput, graphql_name='endDate')
    key = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='key')
    language = sgqlc.types.Field(String, graphql_name='language')
    markers = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='markers')
    name = sgqlc.types.Field(String, graphql_name='name')
    platform_type_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='platformTypeId')
    start_date = sgqlc.types.Field(DateTimeInput, graphql_name='startDate')
    url = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='url')


class PlatformFilterSettings(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('country', 'creator', 'ids', 'keys', 'language', 'last_updater', 'markers', 'platform_type_ids', 'property_filter_settings', 'registration_date', 'search_string', 'status', 'update_date')
    country = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='country')
    creator = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='creator')
    ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='ids')
    keys = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='keys')
    language = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='language')
    last_updater = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='lastUpdater')
    markers = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='markers')
    platform_type_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='platformTypeIds')
    property_filter_settings = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('PropertyFilterSettings')), graphql_name='propertyFilterSettings')
    registration_date = sgqlc.types.Field('TimestampIntervalInput', graphql_name='registrationDate')
    search_string = sgqlc.types.Field(String, graphql_name='searchString')
    status = sgqlc.types.Field(KbFactStatusFilter, graphql_name='status')
    update_date = sgqlc.types.Field('TimestampIntervalInput', graphql_name='updateDate')


class PlatformTypeFilterSettings(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('creator', 'dictionary_exists', 'last_updater', 'name', 'pretrained_nercmodels', 'regexp_exists', 'registration_date', 'update_date')
    creator = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='creator')
    dictionary_exists = sgqlc.types.Field(Boolean, graphql_name='dictionaryExists')
    last_updater = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='lastUpdater')
    name = sgqlc.types.Field(String, graphql_name='name')
    pretrained_nercmodels = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='pretrainedNERCModels')
    regexp_exists = sgqlc.types.Field(Boolean, graphql_name='regexpExists')
    registration_date = sgqlc.types.Field('TimestampIntervalInput', graphql_name='registrationDate')
    update_date = sgqlc.types.Field('TimestampIntervalInput', graphql_name='updateDate')


class PlatformTypeInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('description', 'domain_map_coordinate', 'name', 'pretrained_nercmodels')
    description = sgqlc.types.Field(String, graphql_name='description')
    domain_map_coordinate = sgqlc.types.Field(Coordinate, graphql_name='domainMapCoordinate')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    pretrained_nercmodels = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='pretrainedNERCModels')


class PlatformUpdateInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('access_level_id', 'country', 'end_date', 'id', 'key', 'language', 'markers', 'name', 'platform_type_id', 'start_date', 'url')
    access_level_id = sgqlc.types.Field(ID, graphql_name='accessLevelId')
    country = sgqlc.types.Field(String, graphql_name='country')
    end_date = sgqlc.types.Field(DateTimeInput, graphql_name='endDate')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    key = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='key')
    language = sgqlc.types.Field(String, graphql_name='language')
    markers = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))), graphql_name='markers')
    name = sgqlc.types.Field(String, graphql_name='name')
    platform_type_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='platformTypeId')
    start_date = sgqlc.types.Field(DateTimeInput, graphql_name='startDate')
    url = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='url')


class PropertyAddInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('access_level_id', 'end_date', 'fact_info', 'is_main', 'notes', 'property_type_id', 'start_date', 'target_id', 'value_input')
    access_level_id = sgqlc.types.Field(ID, graphql_name='accessLevelId')
    end_date = sgqlc.types.Field(DateTimeInput, graphql_name='endDate')
    fact_info = sgqlc.types.Field(FactInput, graphql_name='factInfo')
    is_main = sgqlc.types.Field(Boolean, graphql_name='isMain')
    notes = sgqlc.types.Field(String, graphql_name='notes')
    property_type_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='propertyTypeId')
    start_date = sgqlc.types.Field(DateTimeInput, graphql_name='startDate')
    target_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='targetId')
    value_input = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ComponentValueInput))), graphql_name='valueInput')


class PropertyFilterSettings(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('component_id', 'date_time_filter', 'double_filter', 'geo_filter', 'int_filter', 'property_type_id', 'status', 'string_filter')
    component_id = sgqlc.types.Field(ID, graphql_name='componentId')
    date_time_filter = sgqlc.types.Field(DateTimeIntervalInput, graphql_name='dateTimeFilter')
    double_filter = sgqlc.types.Field(DoubleIntervalInput, graphql_name='doubleFilter')
    geo_filter = sgqlc.types.Field(GeoPointWithNameInput, graphql_name='geoFilter')
    int_filter = sgqlc.types.Field(IntIntervalInput, graphql_name='intFilter')
    property_type_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='propertyTypeId')
    status = sgqlc.types.Field(KbFactStatusFilter, graphql_name='status')
    string_filter = sgqlc.types.Field('StringFilterInput', graphql_name='stringFilter')


class PropertyUpdateInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('access_level_id', 'approved', 'computable_value', 'end_date', 'is_main', 'notes', 'property_id', 'start_date', 'value_input')
    access_level_id = sgqlc.types.Field(ID, graphql_name='accessLevelId')
    approved = sgqlc.types.Field(Boolean, graphql_name='approved')
    computable_value = sgqlc.types.Field(String, graphql_name='computableValue')
    end_date = sgqlc.types.Field(DateTimeInput, graphql_name='endDate')
    is_main = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isMain')
    notes = sgqlc.types.Field(String, graphql_name='notes')
    property_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='propertyId')
    start_date = sgqlc.types.Field(DateTimeInput, graphql_name='startDate')
    value_input = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ComponentValueInput))), graphql_name='valueInput')


class PropertyValueFactInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('id', 'reject', 'value')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    reject = sgqlc.types.Field(Boolean, graphql_name='reject')
    value = sgqlc.types.Field('ValueInput', graphql_name='value')


class PropertyValueMentionFactInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('id', 'mention_id', 'reject', 'value_fact_id')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    mention_id = sgqlc.types.Field(ID, graphql_name='mentionId')
    reject = sgqlc.types.Field(Boolean, graphql_name='reject')
    value_fact_id = sgqlc.types.Field(ID, graphql_name='valueFactId')


class RegexpToUpdate(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('regexp_to_insert', 'regexp_to_replace')
    regexp_to_insert = sgqlc.types.Field(NERCRegexpInput, graphql_name='regexpToInsert')
    regexp_to_replace = sgqlc.types.Field(NERCRegexpInput, graphql_name='regexpToReplace')


class RelExtModelInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('invert_direction', 'relation_type', 'source_annotation_type', 'target_annotation_type')
    invert_direction = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='invertDirection')
    relation_type = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='relationType')
    source_annotation_type = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='sourceAnnotationType')
    target_annotation_type = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='targetAnnotationType')


class RelatedDocumentFilterSettings(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('document_content_type', 'publication_date', 'registration_date', 'update_date', 'view_only_approved_documents')
    document_content_type = sgqlc.types.Field(DocumentContentType, graphql_name='documentContentType')
    publication_date = sgqlc.types.Field('TimestampIntervalInput', graphql_name='publicationDate')
    registration_date = sgqlc.types.Field('TimestampIntervalInput', graphql_name='registrationDate')
    update_date = sgqlc.types.Field('TimestampIntervalInput', graphql_name='updateDate')
    view_only_approved_documents = sgqlc.types.Field(Boolean, graphql_name='viewOnlyApprovedDocuments')


class ResearchMapBatchMoveInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('node_move_input',)
    node_move_input = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(NodeMoveInput))), graphql_name='nodeMoveInput')


class ResearchMapBatchUpdateGroupInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('group_id', 'node_ids')
    group_id = sgqlc.types.Field(ID, graphql_name='groupId')
    node_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='nodeIds')


class ResearchMapContentSelectInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('nodes',)
    nodes = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='nodes')


class ResearchMapContentUpdateInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('nodes',)
    nodes = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='nodes')


class ResearchMapCreationInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('access_level_id', 'concepts', 'description', 'documents', 'markers', 'name')
    access_level_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='accessLevelId')
    concepts = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='concepts')
    description = sgqlc.types.Field(String, graphql_name='description')
    documents = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='documents')
    markers = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='markers')
    name = sgqlc.types.Field(String, graphql_name='name')


class ResearchMapFilterSettings(sgqlc.types.Input):
    __schema__ = api_schema
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


class ResearchMapUpdateInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('access_level_id', 'description', 'markers', 'name')
    access_level_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='accessLevelId')
    description = sgqlc.types.Field(String, graphql_name='description')
    markers = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='markers')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')


class RubricFilterSettings(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('concept_type_ids', 'created_at', 'creator_ids', 'input_value', 'property_type_ids', 'property_value_type_ids', 'rubricator_ids', 'updated_at', 'updater_ids')
    concept_type_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='conceptTypeIds')
    created_at = sgqlc.types.Field('TimestampIntervalInput', graphql_name='createdAt')
    creator_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='creatorIds')
    input_value = sgqlc.types.Field(String, graphql_name='inputValue')
    property_type_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='propertyTypeIds')
    property_value_type_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='propertyValueTypeIds')
    rubricator_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='rubricatorIds')
    updated_at = sgqlc.types.Field('TimestampIntervalInput', graphql_name='updatedAt')
    updater_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='updaterIds')


class RubricatorFilterSettings(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('created_at', 'creator_ids', 'input_value', 'rubric_ids', 'rubricator_types', 'updated_at', 'updater_ids')
    created_at = sgqlc.types.Field('TimestampIntervalInput', graphql_name='createdAt')
    creator_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='creatorIds')
    input_value = sgqlc.types.Field(String, graphql_name='inputValue')
    rubric_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='rubricIds')
    rubricator_types = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(RubricatorType)), graphql_name='rubricatorTypes')
    updated_at = sgqlc.types.Field('TimestampIntervalInput', graphql_name='updatedAt')
    updater_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='updaterIds')


class S3FileInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('bucket_name', 'object_name')
    bucket_name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='bucketName')
    object_name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='objectName')


class SearchElementToUpdate(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('dict', 'regexp')
    dict = sgqlc.types.Field('WordsToUpdate', graphql_name='dict')
    regexp = sgqlc.types.Field(RegexpToUpdate, graphql_name='regexp')


class StoryTypeFilterSettings(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('creator', 'dictionary_exists', 'last_updater', 'name', 'pretrained_nercmodels', 'regexp_exists', 'registration_date', 'update_date')
    creator = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='creator')
    dictionary_exists = sgqlc.types.Field(Boolean, graphql_name='dictionaryExists')
    last_updater = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='lastUpdater')
    name = sgqlc.types.Field(String, graphql_name='name')
    pretrained_nercmodels = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='pretrainedNERCModels')
    regexp_exists = sgqlc.types.Field(Boolean, graphql_name='regexpExists')
    registration_date = sgqlc.types.Field('TimestampIntervalInput', graphql_name='registrationDate')
    update_date = sgqlc.types.Field('TimestampIntervalInput', graphql_name='updateDate')


class StoryTypeInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('domain_map_coordinate', 'name', 'pretrained_nercmodels')
    domain_map_coordinate = sgqlc.types.Field(Coordinate, graphql_name='domainMapCoordinate')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    pretrained_nercmodels = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='pretrainedNERCModels')


class StringFilterInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('exact', 'str')
    exact = sgqlc.types.Field(Boolean, graphql_name='exact')
    str = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='str')


class StringLocaleValueInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('locale', 'str')
    locale = sgqlc.types.Field(sgqlc.types.non_null(Locale), graphql_name='locale')
    str = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='str')


class StringValueInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('str',)
    str = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='str')


class TextBoundingInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('component_id', 'end', 'node_id', 'start')
    component_id = sgqlc.types.Field(ID, graphql_name='componentId')
    end = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='end')
    node_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='nodeId')
    start = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='start')


class TimeInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('hour', 'minute', 'second')
    hour = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='hour')
    minute = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='minute')
    second = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='second')


class TimestampIntervalInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('end', 'start')
    end = sgqlc.types.Field(UnixTime, graphql_name='end')
    start = sgqlc.types.Field(UnixTime, graphql_name='start')


class TimestampValueInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('value',)
    value = sgqlc.types.Field(sgqlc.types.non_null(UnixTime), graphql_name='value')


class TranslationInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('language', 'text')
    language = sgqlc.types.Field(sgqlc.types.non_null(LanguageInput), graphql_name='language')
    text = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='text')


class TypeSearchElementUpdateInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('elements_type', 'id', 'search_element_to_update')
    elements_type = sgqlc.types.Field(sgqlc.types.non_null(ElementType), graphql_name='elementsType')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    search_element_to_update = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(SearchElementToUpdate))), graphql_name='searchElementToUpdate')


class UpdateDocumentFeedSubscriptionsInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('events', 'send_document_link', 'send_document_title')
    events = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(DocumentFeedNotificationEvent))), graphql_name='events')
    send_document_link = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='sendDocumentLink')
    send_document_title = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='sendDocumentTitle')


class UpdateDocumentMetadataInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('access_level_id', 'id', 'markers', 'notes', 'title', 'trust_level')
    access_level_id = sgqlc.types.Field(ID, graphql_name='accessLevelId')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    markers = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='markers')
    notes = sgqlc.types.Field(String, graphql_name='notes')
    title = sgqlc.types.Field(String, graphql_name='title')
    trust_level = sgqlc.types.Field(TrustLevel, graphql_name='trustLevel')


class UpdateEdgeAnnotationInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('annotation', 'edge_id')
    annotation = sgqlc.types.Field(String, graphql_name='annotation')
    edge_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='edgeId')


class UpdateGroupAnnotationInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('annotation', 'group_id')
    annotation = sgqlc.types.Field(String, graphql_name='annotation')
    group_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='groupId')


class UpdateNodeAnnotationInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('annotation', 'node_id')
    annotation = sgqlc.types.Field(String, graphql_name='annotation')
    node_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='nodeId')


class UpdateRubricInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('name', 'notes', 'parent_rubric_id', 'rubric_power', 'rubricator_id', 'transformator_id')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    notes = sgqlc.types.Field(String, graphql_name='notes')
    parent_rubric_id = sgqlc.types.Field(ID, graphql_name='parentRubricId')
    rubric_power = sgqlc.types.Field(Int, graphql_name='rubricPower')
    rubricator_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='rubricatorId')
    transformator_id = sgqlc.types.Field(ID, graphql_name='transformatorId')


class UpdateRubricatorInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('name', 'notes', 'transformator_id')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    notes = sgqlc.types.Field(String, graphql_name='notes')
    transformator_id = sgqlc.types.Field(ID, graphql_name='transformatorId')


class ValueFilterInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('date_time_filter', 'double_filter', 'geo_filter', 'int_filter', 'string_filter')
    date_time_filter = sgqlc.types.Field(DateTimeIntervalInput, graphql_name='dateTimeFilter')
    double_filter = sgqlc.types.Field(DoubleIntervalInput, graphql_name='doubleFilter')
    geo_filter = sgqlc.types.Field(GeoPointWithNameInput, graphql_name='geoFilter')
    int_filter = sgqlc.types.Field(IntIntervalInput, graphql_name='intFilter')
    string_filter = sgqlc.types.Field(StringFilterInput, graphql_name='stringFilter')


class ValueInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('date_time_value_input', 'double_value_input', 'geo_point_value_input', 'int_value_input', 'link_value_input', 'string_locale_value_input', 'string_value_input', 'timestamp_value_input')
    date_time_value_input = sgqlc.types.Field(DateTimeInput, graphql_name='dateTimeValueInput')
    double_value_input = sgqlc.types.Field(DoubleValueInput, graphql_name='doubleValueInput')
    geo_point_value_input = sgqlc.types.Field(GeoPointInput, graphql_name='geoPointValueInput')
    int_value_input = sgqlc.types.Field(IntValueInput, graphql_name='intValueInput')
    link_value_input = sgqlc.types.Field(LinkValueInput, graphql_name='linkValueInput')
    string_locale_value_input = sgqlc.types.Field(StringLocaleValueInput, graphql_name='stringLocaleValueInput')
    string_value_input = sgqlc.types.Field(StringValueInput, graphql_name='stringValueInput')
    timestamp_value_input = sgqlc.types.Field(TimestampValueInput, graphql_name='timestampValueInput')


class WordsToUpdate(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('word_to_insert', 'word_to_replace')
    word_to_insert = sgqlc.types.Field(String, graphql_name='wordToInsert')
    word_to_replace = sgqlc.types.Field(String, graphql_name='wordToReplace')


class conceptTypeAndEventFilter(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ('full_type', 'is_event')
    full_type = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='fullType')
    is_event = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isEvent')



########################################################################
# Output Objects and Interfaces
########################################################################
class DocumentGroupFacet(sgqlc.types.Interface):
    __schema__ = api_schema
    __field_names__ = ('count', 'group')
    count = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='count')
    group = sgqlc.types.Field(sgqlc.types.non_null(DocumentGroupingCategory), graphql_name='group')


class EntityTypePresentation(sgqlc.types.Interface):
    __schema__ = api_schema
    __field_names__ = ('is_default', 'list_concept_link_type', 'metric', 'show_in_menu')
    is_default = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isDefault')
    list_concept_link_type = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ConceptLinkType'))), graphql_name='listConceptLinkType')
    metric = sgqlc.types.Field(sgqlc.types.non_null('EntityTypePresentationStatistics'), graphql_name='metric')
    show_in_menu = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='showInMenu')


class FactInterface(sgqlc.types.Interface):
    __schema__ = api_schema
    __field_names__ = ('document', 'id', 'system_registration_date', 'system_update_date')
    document = sgqlc.types.Field(sgqlc.types.non_null('Document'), graphql_name='document')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    system_registration_date = sgqlc.types.Field(sgqlc.types.non_null(UnixTime), graphql_name='systemRegistrationDate')
    system_update_date = sgqlc.types.Field(UnixTime, graphql_name='systemUpdateDate')


class HasTypeSearchElements(sgqlc.types.Interface):
    __schema__ = api_schema
    __field_names__ = ('list_black_dictionary', 'list_black_regexp', 'list_type_black_search_element', 'list_type_search_element', 'list_white_dictionary', 'list_white_regexp', 'pretrained_nercmodels')
    list_black_dictionary = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))), graphql_name='listBlackDictionary')
    list_black_regexp = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('NERCRegexp'))), graphql_name='listBlackRegexp')
    list_type_black_search_element = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('TypeSearchElement'))), graphql_name='listTypeBlackSearchElement')
    list_type_search_element = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('TypeSearchElement'))), graphql_name='listTypeSearchElement')
    list_white_dictionary = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))), graphql_name='listWhiteDictionary')
    list_white_regexp = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('NERCRegexp'))), graphql_name='listWhiteRegexp')
    pretrained_nercmodels = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))), graphql_name='pretrainedNERCModels')


class LinkTarget(sgqlc.types.Interface):
    __schema__ = api_schema
    __field_names__ = ('pagination_link',)
    pagination_link = sgqlc.types.Field(sgqlc.types.non_null('ConceptLinkPagination'), graphql_name='paginationLink', args=sgqlc.types.ArgDict((
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(ConceptLinkFilterSettings), graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
))
    )


class LinkTypeTarget(sgqlc.types.Interface):
    __schema__ = api_schema
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
    __schema__ = api_schema
    __field_names__ = ('document', 'id', 'mention_fact', 'system_registration_date', 'system_update_date')
    document = sgqlc.types.Field(sgqlc.types.non_null('Document'), graphql_name='document')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    mention_fact = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(FactInterface))), graphql_name='mentionFact')
    system_registration_date = sgqlc.types.Field(sgqlc.types.non_null(UnixTime), graphql_name='systemRegistrationDate')
    system_update_date = sgqlc.types.Field(UnixTime, graphql_name='systemUpdateDate')


class PropertyTarget(sgqlc.types.Interface):
    __schema__ = api_schema
    __field_names__ = ('pagination_property',)
    pagination_property = sgqlc.types.Field(sgqlc.types.non_null('ConceptPropertyPagination'), graphql_name='paginationProperty', args=sgqlc.types.ArgDict((
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(ConceptPropertyFilterSettings), graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
))
    )


class PropertyTypeTarget(sgqlc.types.Interface):
    __schema__ = api_schema
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
    __schema__ = api_schema
    __field_names__ = ('creator', 'last_updater', 'system_registration_date', 'system_update_date')
    creator = sgqlc.types.Field(sgqlc.types.non_null('User'), graphql_name='creator')
    last_updater = sgqlc.types.Field('User', graphql_name='lastUpdater')
    system_registration_date = sgqlc.types.Field(sgqlc.types.non_null(UnixTime), graphql_name='systemRegistrationDate')
    system_update_date = sgqlc.types.Field(UnixTime, graphql_name='systemUpdateDate')


class EntityType(sgqlc.types.Interface):
    __schema__ = api_schema
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
    __schema__ = api_schema
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
    __schema__ = api_schema
    __field_names__ = ('id', 'name', 'order')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    order = sgqlc.types.Field(sgqlc.types.non_null(Long), graphql_name='order')


class AccessLevelPagination(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('list_access_level', 'total')
    list_access_level = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(AccessLevel))), graphql_name='listAccessLevel')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class AccountPagination(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('list_account', 'total', 'total_platforms')
    list_account = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('Account'))), graphql_name='listAccount')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')
    total_platforms = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='totalPlatforms')


class AccountStatistics(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('count_doc',)
    count_doc = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='countDoc')


class AccountTypePagination(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('list_account_type', 'total')
    list_account_type = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('AccountType'))), graphql_name='listAccountType')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class Annotation(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('end', 'start', 'value')
    end = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='end')
    start = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='start')
    value = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='value')


class Autocomplete(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('autocomplete',)
    autocomplete = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))), graphql_name='autocomplete')


class CommonStringPagination(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('list_string', 'total')
    list_string = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))), graphql_name='listString')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class CompositePropertyValueTemplatePagination(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('list_composite_property_value_template', 'total')
    list_composite_property_value_template = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('CompositePropertyValueTemplate'))), graphql_name='listCompositePropertyValueTemplate')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class CompositePropertyValueType(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('id', 'is_required', 'name', 'value_type', 'view')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    is_required = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isRequired')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    value_type = sgqlc.types.Field(sgqlc.types.non_null('ConceptPropertyValueType'), graphql_name='valueType')
    view = sgqlc.types.Field(sgqlc.types.non_null(ComponentView), graphql_name='view')


class CompositeValue(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('list_value',)
    list_value = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('NamedValue'))), graphql_name='listValue')


class ConceptDedupTask(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('id',)
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')


class ConceptDuplicate(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('concept', 'group', 'id')
    concept = sgqlc.types.Field(sgqlc.types.non_null('Concept'), graphql_name='concept')
    group = sgqlc.types.Field(sgqlc.types.non_null('ConceptDuplicateGroup'), graphql_name='group')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')


class ConceptDuplicateGroup(sgqlc.types.Type):
    __schema__ = api_schema
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
    __schema__ = api_schema
    __field_names__ = ('concept_duplicate_count',)
    concept_duplicate_count = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='conceptDuplicateCount')


class ConceptDuplicateGroupPagination(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('list_concept_duplicate_group', 'total')
    list_concept_duplicate_group = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ConceptDuplicateGroup))), graphql_name='listConceptDuplicateGroup')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class ConceptDuplicatePagination(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('list_concept_duplicate', 'total')
    list_concept_duplicate = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ConceptDuplicate))), graphql_name='listConceptDuplicate')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class ConceptDuplicateReportMetrics(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('group_count',)
    group_count = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='groupCount')


class ConceptDuplicateReportPagination(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('list_concept_duplicate_report', 'total')
    list_concept_duplicate_report = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ConceptDuplicateReport'))), graphql_name='listConceptDuplicateReport')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class ConceptFactPagination(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('list_concept_fact', 'total')
    list_concept_fact = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ConceptFact'))), graphql_name='listConceptFact')
    total = sgqlc.types.Field(sgqlc.types.non_null(Long), graphql_name='total')


class ConceptLinkFactPagination(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('list_concept_link_fact', 'total')
    list_concept_link_fact = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ConceptLinkFact'))), graphql_name='listConceptLinkFact')
    total = sgqlc.types.Field(sgqlc.types.non_null(Long), graphql_name='total')


class ConceptLinkPagination(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('list_concept_link', 'total')
    list_concept_link = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ConceptLink'))), graphql_name='listConceptLink')
    total = sgqlc.types.Field(sgqlc.types.non_null(Long), graphql_name='total')


class ConceptLinkTypePagination(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('list_concept_link_type', 'total')
    list_concept_link_type = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ConceptLinkType'))), graphql_name='listConceptLinkType')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class ConceptLinkTypePath(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('fixed', 'link_type')
    fixed = sgqlc.types.Field(ConceptLinkDirection, graphql_name='fixed')
    link_type = sgqlc.types.Field(sgqlc.types.non_null('ConceptLinkType'), graphql_name='linkType')


class ConceptLinkTypeStatistics(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('count_property_type',)
    count_property_type = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='countPropertyType')


class ConceptMetrics(sgqlc.types.Type):
    __schema__ = api_schema
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
    __schema__ = api_schema
    __field_names__ = ('list_concept', 'precise_total', 'show_total', 'total')
    list_concept = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('Concept'))), graphql_name='listConcept')
    precise_total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='preciseTotal')
    show_total = sgqlc.types.Field(sgqlc.types.non_null(Long), graphql_name='showTotal')
    total = sgqlc.types.Field(sgqlc.types.non_null(Long), graphql_name='total')


class ConceptPresentation(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('concept_type_presentation', 'id', 'list_concept_mention', 'list_concepts', 'paginate_single_widget', 'pagination_concept_mention', 'root_concept')
    concept_type_presentation = sgqlc.types.Field(sgqlc.types.non_null('ConceptTypePresentation'), graphql_name='conceptTypePresentation')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    list_concept_mention = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('ConceptFact')), graphql_name='listConceptMention')
    list_concepts = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('Concept'))), graphql_name='listConcepts')
    paginate_single_widget = sgqlc.types.Field(sgqlc.types.non_null('ConceptPresentationWidgetRowPagination'), graphql_name='paginateSingleWidget', args=sgqlc.types.ArgDict((
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('sort_column', sgqlc.types.Arg(ID, graphql_name='sortColumn', default=None)),
        ('sort_direction', sgqlc.types.Arg(SortDirection, graphql_name='sortDirection', default='descending')),
        ('widget_type_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='widgetTypeId', default=None)),
))
    )
    pagination_concept_mention = sgqlc.types.Field(ConceptFactPagination, graphql_name='paginationConceptMention', args=sgqlc.types.ArgDict((
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(LinkedDocumentFilterSettings), graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
))
    )
    root_concept = sgqlc.types.Field(sgqlc.types.non_null('Concept'), graphql_name='rootConcept')


class ConceptPresentationPagination(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('list_concept_presentation', 'total')
    list_concept_presentation = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ConceptPresentation))), graphql_name='listConceptPresentation')
    total = sgqlc.types.Field(sgqlc.types.non_null(Long), graphql_name='total')


class ConceptPresentationWidgetRowPagination(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('rows', 'total', 'widget_type')
    rows = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ConceptViewValue'))))))), graphql_name='rows')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')
    widget_type = sgqlc.types.Field(sgqlc.types.non_null('ConceptTypePresentationWidgetType'), graphql_name='widgetType')


class ConceptPropertyPagination(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('list_concept_property', 'total')
    list_concept_property = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ConceptProperty'))), graphql_name='listConceptProperty')
    total = sgqlc.types.Field(sgqlc.types.non_null(Long), graphql_name='total')


class ConceptPropertyTypePagination(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('list_concept_property_type', 'total')
    list_concept_property_type = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ConceptPropertyType'))), graphql_name='listConceptPropertyType')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class ConceptPropertyValueStatistics(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('count_concept_type', 'count_dictionary', 'count_link_type', 'count_regexp')
    count_concept_type = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='countConceptType')
    count_dictionary = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='countDictionary')
    count_link_type = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='countLinkType')
    count_regexp = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='countRegexp')


class ConceptPropertyValueTypePagination(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('list_concept_property_value_type', 'total')
    list_concept_property_value_type = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ConceptPropertyValueType'))), graphql_name='listConceptPropertyValueType')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class ConceptRegistryView(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('columns', 'metrics', 'sorting')
    columns = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ConceptRegistryViewColumn'))), graphql_name='columns')
    metrics = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ConceptRegistryViewMetric'))), graphql_name='metrics')
    sorting = sgqlc.types.Field('ConceptRegistryViewSorting', graphql_name='sorting')


class ConceptRegistryViewColumn(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('column_type',)
    column_type = sgqlc.types.Field(sgqlc.types.non_null(ConceptViewColumnType), graphql_name='columnType')


class ConceptRegistryViewMetric(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('metric_type',)
    metric_type = sgqlc.types.Field(sgqlc.types.non_null(ConceptViewMetricType), graphql_name='metricType')


class ConceptRegistryViewSorting(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('sort_direction', 'sorting_type')
    sort_direction = sgqlc.types.Field(sgqlc.types.non_null(SortDirection), graphql_name='sortDirection')
    sorting_type = sgqlc.types.Field(sgqlc.types.non_null(ConceptSorting), graphql_name='sortingType')


class ConceptSubscriptions(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('count_users', 'list_user', 'subscriptions')
    count_users = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='countUsers')
    list_user = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('User'))), graphql_name='listUser')
    subscriptions = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ConceptUpdate))), graphql_name='subscriptions')


class ConceptTypePagination(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('list_concept_type', 'total')
    list_concept_type = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ConceptType'))), graphql_name='listConceptType')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class ConceptTypePresentationPagination(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('list_concept_type_presentation', 'total')
    list_concept_type_presentation = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ConceptTypePresentation'))), graphql_name='listConceptTypePresentation')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class ConceptTypePresentationWidgetTypeColumn(sgqlc.types.Type):
    __schema__ = api_schema
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
    __schema__ = api_schema
    __field_names__ = ('list_concept_type_presentation_widget', 'total')
    list_concept_type_presentation_widget = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ConceptTypePresentationWidgetType'))), graphql_name='listConceptTypePresentationWidget')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class ConceptTypeViewPagination(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('list_concept_type_view', 'total')
    list_concept_type_view = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ConceptTypeView'))), graphql_name='listConceptTypeView')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class ConceptView(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('concept', 'rows')
    concept = sgqlc.types.Field(sgqlc.types.non_null('Concept'), graphql_name='concept')
    rows = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ConceptViewValue'))))), graphql_name='rows')


class ConceptViewPagination(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('list_concept_view', 'total')
    list_concept_view = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ConceptView))), graphql_name='listConceptView')
    total = sgqlc.types.Field(sgqlc.types.non_null(Long), graphql_name='total')


class ConceptWithConfidence(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('concept', 'confidence')
    concept = sgqlc.types.Field(sgqlc.types.non_null('Concept'), graphql_name='concept')
    confidence = sgqlc.types.Field(Float, graphql_name='confidence')


class ConceptWithNeighbors(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('concept', 'num_of_neighbors')
    concept = sgqlc.types.Field(sgqlc.types.non_null('Concept'), graphql_name='concept')
    num_of_neighbors = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='numOfNeighbors')


class Coordinates(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('latitude', 'longitude')
    latitude = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='latitude')
    longitude = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='longitude')


class CountryPagination(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('list_country', 'total')
    list_country = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))), graphql_name='listCountry')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class Date(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('day', 'month', 'year')
    day = sgqlc.types.Field(Int, graphql_name='day')
    month = sgqlc.types.Field(Int, graphql_name='month')
    year = sgqlc.types.Field(Int, graphql_name='year')


class DateTimeInterval(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('end', 'start')
    end = sgqlc.types.Field('DateTimeValue', graphql_name='end')
    start = sgqlc.types.Field('DateTimeValue', graphql_name='start')


class DateTimeValue(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('date', 'time')
    date = sgqlc.types.Field(sgqlc.types.non_null(Date), graphql_name='date')
    time = sgqlc.types.Field('Time', graphql_name='time')


class DeleteDrawing(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('id',)
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')


class DeleteEdge(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('id',)
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')


class DeleteGroup(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('id',)
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')


class DeleteNode(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('id',)
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')


class DictValue(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('value',)
    value = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='value')


class DocumentDuplicateReportMetrics(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('deleted_count', 'documents_count', 'duplicates_count')
    deleted_count = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='deletedCount')
    documents_count = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='documentsCount')
    duplicates_count = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='duplicatesCount')


class DocumentDuplicateReportPagination(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('list_document_duplicate_report', 'total')
    list_document_duplicate_report = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('DocumentDuplicateReport'))), graphql_name='listDocumentDuplicateReport')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class DocumentDuplicateTask(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('duplicate_document_id', 'id', 'original_document_id', 'report_id', 'status')
    duplicate_document_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='duplicateDocumentId')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    original_document_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='originalDocumentId')
    report_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='reportId')
    status = sgqlc.types.Field(sgqlc.types.non_null(DocumentDuplicateTaskStatus), graphql_name='status')


class DocumentDuplicateTaskPagination(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('list_document_duplicate_task', 'total')
    list_document_duplicate_task = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(DocumentDuplicateTask))), graphql_name='listDocumentDuplicateTask')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class DocumentFacets(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('approved_entities_facets', 'calculated_at', 'document_metadata_facets', 'id', 'not_approved_entities_facets')
    approved_entities_facets = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(DocumentGroupFacet)), graphql_name='approvedEntitiesFacets')
    calculated_at = sgqlc.types.Field(UnixTime, graphql_name='calculatedAt')
    document_metadata_facets = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(DocumentGroupFacet)), graphql_name='documentMetadataFacets')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    not_approved_entities_facets = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(DocumentGroupFacet)), graphql_name='notApprovedEntitiesFacets')


class DocumentFeedPagination(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('list_document_feed', 'total')
    list_document_feed = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('DocumentFeed'))), graphql_name='listDocumentFeed')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class DocumentFeedSubscriptions(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('count_users', 'list_user', 'send_document_link', 'send_document_title', 'subscriptions')
    count_users = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='countUsers')
    list_user = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('User'))), graphql_name='listUser')
    send_document_link = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='sendDocumentLink')
    send_document_title = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='sendDocumentTitle')
    subscriptions = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(DocumentFeedNotificationEvent))), graphql_name='subscriptions')


class DocumentFeedView(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('columns', 'metrics', 'sorting')
    columns = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('DocumentRegistryViewColumn'))), graphql_name='columns')
    metrics = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('DocumentViewMetric'))), graphql_name='metrics')
    sorting = sgqlc.types.Field('DocumentFeedViewSorting', graphql_name='sorting')


class DocumentFeedViewSorting(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('sort_direction', 'sorting_type')
    sort_direction = sgqlc.types.Field(sgqlc.types.non_null(SortDirection), graphql_name='sortDirection')
    sorting_type = sgqlc.types.Field(sgqlc.types.non_null(DocumentInFeedSorting), graphql_name='sortingType')


class DocumentFromDocumentFeed(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('document', 'is_from_deleted', 'is_from_favorites')
    document = sgqlc.types.Field(sgqlc.types.non_null('Document'), graphql_name='document')
    is_from_deleted = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isFromDeleted')
    is_from_favorites = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isFromFavorites')


class DocumentFromDocumentFeedPagination(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('list_document', 'total')
    list_document = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(DocumentFromDocumentFeed))), graphql_name='listDocument')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class DocumentLink(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('child_id', 'parent_id')
    child_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='childId')
    parent_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='parentId')


class DocumentMetadata(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('access_time', 'created_time', 'file_name', 'file_type', 'job_id', 'language', 'modified_time', 'periodic_job_id', 'periodic_task_id', 'size', 'source', 'task_id')
    access_time = sgqlc.types.Field(sgqlc.types.non_null(UnixTime), graphql_name='accessTime')
    created_time = sgqlc.types.Field(sgqlc.types.non_null(UnixTime), graphql_name='createdTime')
    file_name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='fileName')
    file_type = sgqlc.types.Field(String, graphql_name='fileType')
    job_id = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='jobId')
    language = sgqlc.types.Field('Language', graphql_name='language')
    modified_time = sgqlc.types.Field(sgqlc.types.non_null(UnixTime), graphql_name='modifiedTime')
    periodic_job_id = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='periodicJobId')
    periodic_task_id = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='periodicTaskId')
    size = sgqlc.types.Field(sgqlc.types.non_null(Long), graphql_name='size')
    source = sgqlc.types.Field(String, graphql_name='source')
    task_id = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='taskId')


class DocumentMetrics(sgqlc.types.Type):
    __schema__ = api_schema
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
    __schema__ = api_schema
    __field_names__ = ('list_document', 'total')
    list_document = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('Document'))), graphql_name='listDocument')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class DocumentRegistryView(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('columns', 'metrics', 'relevance', 'sorting')
    columns = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('DocumentRegistryViewColumn'))), graphql_name='columns')
    metrics = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('DocumentViewMetric'))), graphql_name='metrics')
    relevance = sgqlc.types.Field('DocumentRelevanceMetrics', graphql_name='relevance')
    sorting = sgqlc.types.Field('DocumentRegistryViewSorting', graphql_name='sorting')


class DocumentRegistryViewColumn(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('column_type',)
    column_type = sgqlc.types.Field(sgqlc.types.non_null(DocumentViewColumnType), graphql_name='columnType')


class DocumentRegistryViewSorting(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('sort_direction', 'sorting_type')
    sort_direction = sgqlc.types.Field(sgqlc.types.non_null(SortDirection), graphql_name='sortDirection')
    sorting_type = sgqlc.types.Field(sgqlc.types.non_null(DocumentSorting), graphql_name='sortingType')


class DocumentRelevanceMetrics(sgqlc.types.Type):
    __schema__ = api_schema
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


class DocumentRubricPagination(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('list_document_rubric', 'total')
    list_document_rubric = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('DocumentRubric'))), graphql_name='listDocumentRubric')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class DocumentSubscriptions(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('count_users', 'list_user', 'subscriptions')
    count_users = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='countUsers')
    list_user = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('User'))), graphql_name='listUser')
    subscriptions = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(DocumentUpdate))), graphql_name='subscriptions')


class DocumentTextPagination(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('pagination_text', 'total')
    pagination_text = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('FlatDocumentStructure'))))), graphql_name='paginationText')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class DocumentTypePagination(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('list_document_type', 'total')
    list_document_type = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('DocumentType'))), graphql_name='listDocumentType')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class DocumentTypePresentationPagination(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('list_document_type_presentation', 'total')
    list_document_type_presentation = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('DocumentTypePresentation'))), graphql_name='listDocumentTypePresentation')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class DocumentViewMetric(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('metric_type',)
    metric_type = sgqlc.types.Field(sgqlc.types.non_null(DocumentViewMetricType), graphql_name='metricType')


class DomainMap(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('list_edge', 'list_node')
    list_edge = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('MapEdge'))), graphql_name='listEdge')
    list_node = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('MapNode'))), graphql_name='listNode')


class DoubleValue(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('value',)
    value = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='value')


class EntityTypePresentationStatistics(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('count_concept_types', 'count_document_types', 'count_entity_types')
    count_concept_types = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='countConceptTypes')
    count_document_types = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='countDocumentTypes')
    count_entity_types = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='countEntityTypes')


class EntityTypeStatistics(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('count_dictionary', 'count_link_type', 'count_property_type', 'count_regexp')
    count_dictionary = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='countDictionary')
    count_link_type = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='countLinkType')
    count_property_type = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='countPropertyType')
    count_regexp = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='countRegexp')


class FlatDocumentStructure(sgqlc.types.Type):
    __schema__ = api_schema
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
    __schema__ = api_schema
    __field_names__ = ('concept', 'concept_property')
    concept = sgqlc.types.Field(sgqlc.types.non_null('Concept'), graphql_name='concept')
    concept_property = sgqlc.types.Field(sgqlc.types.non_null('ConceptProperty'), graphql_name='conceptProperty')


class GeoPointValue(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('name', 'point')
    name = sgqlc.types.Field(String, graphql_name='name')
    point = sgqlc.types.Field(Coordinates, graphql_name='point')


class Group(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('annotation', 'collapsed', 'id', 'layout', 'name', 'x_coordinate', 'y_coordinate')
    annotation = sgqlc.types.Field('MapAnnotation', graphql_name='annotation')
    collapsed = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='collapsed')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    layout = sgqlc.types.Field(String, graphql_name='layout')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    x_coordinate = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='xCoordinate')
    y_coordinate = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='yCoordinate')


class HLAnnotation(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('end', 'start')
    end = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='end')
    start = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='start')


class HeaderProperty(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('property_type', 'values')
    property_type = sgqlc.types.Field(sgqlc.types.non_null('ConceptPropertyType'), graphql_name='propertyType')
    values = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('AnyValue'))), graphql_name='values')


class Highlighting(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('annotations', 'highlighting')
    annotations = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(HLAnnotation))), graphql_name='annotations')
    highlighting = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='highlighting')


class Image(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('bucket_name', 'object_name')
    bucket_name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='bucketName')
    object_name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='objectName')


class IntValue(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('value',)
    value = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='value')


class Language(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('id',)
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')


class LanguagePagination(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('list_language', 'total')
    list_language = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))), graphql_name='listLanguage')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class LinkValue(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('link',)
    link = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='link')


class MapDrawing(sgqlc.types.Type):
    __schema__ = api_schema
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
    __schema__ = api_schema
    __field_names__ = ('annotation', 'from_id', 'id', 'link', 'link_type', 'to_id')
    annotation = sgqlc.types.Field('MapAnnotation', graphql_name='annotation')
    from_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='fromID')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    link = sgqlc.types.Field(sgqlc.types.non_null('EntityLink'), graphql_name='link')
    link_type = sgqlc.types.Field(sgqlc.types.non_null(MapEdgeType), graphql_name='linkType')
    to_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='toID')


class MapEvents(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('event_list',)
    event_list = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('MapEvent'))), graphql_name='eventList')


class MapNode(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('annotation', 'entity', 'group_id', 'id', 'node_type', 'x_coordinate', 'y_coordinate')
    annotation = sgqlc.types.Field('MapAnnotation', graphql_name='annotation')
    entity = sgqlc.types.Field(sgqlc.types.non_null('Entity'), graphql_name='entity')
    group_id = sgqlc.types.Field(ID, graphql_name='groupId')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    node_type = sgqlc.types.Field(sgqlc.types.non_null(MapNodeType), graphql_name='nodeType')
    x_coordinate = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='xCoordinate')
    y_coordinate = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='yCoordinate')


class Markers(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('markers',)
    markers = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))), graphql_name='markers')


class MentionLink(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('id', 'mention_link_type', 'source', 'target')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    mention_link_type = sgqlc.types.Field(sgqlc.types.non_null(MentionLinkType), graphql_name='mentionLinkType')
    source = sgqlc.types.Field(sgqlc.types.non_null('MentionUnion'), graphql_name='source')
    target = sgqlc.types.Field(sgqlc.types.non_null('MentionUnion'), graphql_name='target')


class MergedConcept(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('concept', 'merge_author', 'merge_date')
    concept = sgqlc.types.Field(sgqlc.types.non_null('Concept'), graphql_name='concept')
    merge_author = sgqlc.types.Field(sgqlc.types.non_null('User'), graphql_name='mergeAuthor')
    merge_date = sgqlc.types.Field(sgqlc.types.non_null(UnixTime), graphql_name='mergeDate')


class MergedConceptPagination(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('list_merged_concept', 'total')
    list_merged_concept = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(MergedConcept))), graphql_name='listMergedConcept')
    total = sgqlc.types.Field(sgqlc.types.non_null(Long), graphql_name='total')


class Mutation(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('add_access_level', 'add_account', 'add_account_type', 'add_approved_concepts_by_document_node', 'add_approved_linked_concepts_by_concept_node', 'add_composite_property_value_template', 'add_concept', 'add_concept_fact', 'add_concept_link', 'add_concept_link_fact', 'add_concept_link_property', 'add_concept_link_property_fact', 'add_concept_link_property_type', 'add_concept_link_type', 'add_concept_node_on_research_map', 'add_concept_property', 'add_concept_property_fact', 'add_concept_property_type', 'add_concept_property_value_type', 'add_concept_type', 'add_concept_type_presentation', 'add_concept_type_presentation_template', 'add_concept_type_presentation_widget_type', 'add_concept_type_view', 'add_concepts_from_approved_facts_by_document_node', 'add_concepts_from_not_approved_facts_by_document_node', 'add_document_duplicate_report', 'add_document_feed', 'add_document_node_on_research_map', 'add_document_nodes_by_concept_node', 'add_document_rubric', 'add_document_to_document_feed_favorites', 'add_document_type', 'add_document_type_presentation', 'add_drawing', 'add_group', 'add_not_approved_concepts_by_document_node', 'add_not_approved_linked_concepts_by_concept_node', 'add_platform', 'add_platform_type', 'add_property', 'add_research_map', 'add_research_map_from_files', 'add_rubric', 'add_rubricator', 'add_story_type', 'add_template_docx', 'approve_document_rubric', 'approve_kb_fact', 'approve_research_map_entities', 'batch_move_nodes_on_domain_map', 'batch_move_nodes_on_map', 'batch_update_group_on_map', 'bulk_delete_research_map', 'decline_concept_duplicate', 'decline_document_duplicate_task', 'delete_access_level', 'delete_account', 'delete_account_type', 'delete_all_document_duplicate_task', 'delete_bulk', 'delete_composite_property_value_template', 'delete_concept', 'delete_concept_by_research_map', 'delete_concept_duplicate_report', 'delete_concept_fact', 'delete_concept_link', 'delete_concept_link_fact', 'delete_concept_link_property', 'delete_concept_link_property_fact', 'delete_concept_link_property_type', 'delete_concept_link_type', 'delete_concept_property', 'delete_concept_property_fact', 'delete_concept_property_type', 'delete_concept_property_value_type', 'delete_concept_type', 'delete_concept_type_avatar', 'delete_concept_type_presentation', 'delete_concept_type_presentation_widget_type', 'delete_concept_type_view', 'delete_content_from_research_map', 'delete_document_duplicate_report', 'delete_document_duplicate_task', 'delete_document_feed', 'delete_document_from_document_feed', 'delete_document_from_document_feed_favorites', 'delete_document_rubric', 'delete_document_type', 'delete_document_type_presentation', 'delete_documents', 'delete_drawing', 'delete_fact', 'delete_group', 'delete_platform', 'delete_platform_type', 'delete_property', 'delete_research_map', 'delete_rubric', 'delete_rubricator', 'delete_story_type', 'find_shortest_path_on_map', 'force_handle_document', 'mark_document_as_read', 'mark_document_as_unread', 'merge_concepts', 'normalize_value', 'remove_all_candidate_facts_from_document', 'remove_all_kbfacts_from_document', 'remove_candidate_fact_from_document', 'restore_document_to_document_feed', 'reverse_concept_link', 'set_concept_type_default_view', 'set_document_type_default_view', 'set_research_map_active', 'toggle_concept_type_presentation_visibility_in_menu', 'toggle_concept_type_view_visibility_in_menu', 'translate_tql', 'unmerge_concepts', 'update_access_level', 'update_account', 'update_account_type', 'update_composite_property_value_template', 'update_concept', 'update_concept_avatar', 'update_concept_link', 'update_concept_link_property_type', 'update_concept_link_type', 'update_concept_main_property_type_order', 'update_concept_property', 'update_concept_property_type', 'update_concept_property_value_type', 'update_concept_registry_view', 'update_concept_subscriptions', 'update_concept_type', 'update_concept_type_presentation', 'update_concept_type_presentation_template_filename', 'update_concept_type_presentation_widget_type', 'update_concept_type_presentation_widget_types_order', 'update_concept_type_view', 'update_document', 'update_document_avatar', 'update_document_bulk', 'update_document_facets', 'update_document_facts', 'update_document_feed', 'update_document_feed_subscriptions', 'update_document_feed_view', 'update_document_metadata', 'update_document_metadata_bulk', 'update_document_node', 'update_document_registry_view', 'update_document_subscriptions', 'update_document_type', 'update_document_type_presentation', 'update_drawing', 'update_edge_annotation', 'update_group', 'update_group_annotation', 'update_markers_bulk', 'update_node_annotation', 'update_platform', 'update_platform_type', 'update_property', 'update_research_map', 'update_rubric', 'update_rubrication_facets', 'update_rubricator', 'update_story_type', 'update_type_search_element')
    add_access_level = sgqlc.types.Field(sgqlc.types.non_null(AccessLevel), graphql_name='addAccessLevel', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(AccessLevelCreationInput), graphql_name='form', default=None)),
))
    )
    add_account = sgqlc.types.Field(sgqlc.types.non_null('Account'), graphql_name='addAccount', args=sgqlc.types.ArgDict((
        ('file', sgqlc.types.Arg(S3FileInput, graphql_name='file', default=None)),
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(AccountCreationInput), graphql_name='form', default=None)),
))
    )
    add_account_type = sgqlc.types.Field(sgqlc.types.non_null('AccountType'), graphql_name='addAccountType', args=sgqlc.types.ArgDict((
        ('file', sgqlc.types.Arg(S3FileInput, graphql_name='file', default=None)),
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(AccountTypeInput), graphql_name='form', default=None)),
))
    )
    add_approved_concepts_by_document_node = sgqlc.types.Field(sgqlc.types.non_null('StateWithCount'), graphql_name='addApprovedConceptsByDocumentNode', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(ResearchMapContentSelectInput), graphql_name='form', default=None)),
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
        ('quantity', sgqlc.types.Arg(Int, graphql_name='quantity', default=10)),
))
    )
    add_approved_linked_concepts_by_concept_node = sgqlc.types.Field(sgqlc.types.non_null('StateWithCount'), graphql_name='addApprovedLinkedConceptsByConceptNode', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(ResearchMapContentSelectInput), graphql_name='form', default=None)),
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
        ('quantity', sgqlc.types.Arg(Int, graphql_name='quantity', default=10)),
))
    )
    add_composite_property_value_template = sgqlc.types.Field(sgqlc.types.non_null('CompositePropertyValueTemplate'), graphql_name='addCompositePropertyValueTemplate', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(CompositePropertyValueTemplateCreateInput), graphql_name='form', default=None)),
))
    )
    add_concept = sgqlc.types.Field(sgqlc.types.non_null('Concept'), graphql_name='addConcept', args=sgqlc.types.ArgDict((
        ('file', sgqlc.types.Arg(S3FileInput, graphql_name='file', default=None)),
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(ConceptMutationInput), graphql_name='form', default=None)),
        ('performance_control', sgqlc.types.Arg(PerformSynchronously, graphql_name='performanceControl', default={'performSynchronously': True})),
))
    )
    add_concept_fact = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='addConceptFact', args=sgqlc.types.ArgDict((
        ('fact', sgqlc.types.Arg(sgqlc.types.non_null(FactInput), graphql_name='fact', default=None)),
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
        ('performance_control', sgqlc.types.Arg(PerformSynchronously, graphql_name='performanceControl', default={'performSynchronously': True})),
))
    )
    add_concept_link = sgqlc.types.Field(sgqlc.types.non_null('ConceptLink'), graphql_name='addConceptLink', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(ConceptLinkCreationMutationInput), graphql_name='form', default=None)),
        ('performance_control', sgqlc.types.Arg(PerformSynchronously, graphql_name='performanceControl', default={'performSynchronously': True})),
))
    )
    add_concept_link_fact = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='addConceptLinkFact', args=sgqlc.types.ArgDict((
        ('fact', sgqlc.types.Arg(sgqlc.types.non_null(FactInput), graphql_name='fact', default=None)),
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
        ('performance_control', sgqlc.types.Arg(PerformSynchronously, graphql_name='performanceControl', default={'performSynchronously': True})),
))
    )
    add_concept_link_property = sgqlc.types.Field(sgqlc.types.non_null('ConceptProperty'), graphql_name='addConceptLinkProperty', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(ConceptLinkPropertyInput), graphql_name='form', default=None)),
        ('performance_control', sgqlc.types.Arg(PerformSynchronously, graphql_name='performanceControl', default={'performSynchronously': True})),
))
    )
    add_concept_link_property_fact = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='addConceptLinkPropertyFact', args=sgqlc.types.ArgDict((
        ('fact', sgqlc.types.Arg(sgqlc.types.non_null(FactInput), graphql_name='fact', default=None)),
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
        ('performance_control', sgqlc.types.Arg(PerformSynchronously, graphql_name='performanceControl', default={'performSynchronously': True})),
))
    )
    add_concept_link_property_type = sgqlc.types.Field(sgqlc.types.non_null('ConceptPropertyType'), graphql_name='addConceptLinkPropertyType', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(ConceptLinkPropertyTypeCreationInput), graphql_name='form', default=None)),
))
    )
    add_concept_link_type = sgqlc.types.Field(sgqlc.types.non_null('ConceptLinkType'), graphql_name='addConceptLinkType', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(ConceptLinkTypeCreationInput), graphql_name='form', default=None)),
))
    )
    add_concept_node_on_research_map = sgqlc.types.Field(sgqlc.types.non_null('StateWithCount'), graphql_name='addConceptNodeOnResearchMap', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
        ('nodes', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(AddConceptNodeInput))), graphql_name='nodes', default=None)),
))
    )
    add_concept_property = sgqlc.types.Field(sgqlc.types.non_null('ConceptProperty'), graphql_name='addConceptProperty', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(ConceptPropertyCreateInput), graphql_name='form', default=None)),
        ('performance_control', sgqlc.types.Arg(PerformSynchronously, graphql_name='performanceControl', default={'performSynchronously': True})),
))
    )
    add_concept_property_fact = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='addConceptPropertyFact', args=sgqlc.types.ArgDict((
        ('fact', sgqlc.types.Arg(sgqlc.types.non_null(FactInput), graphql_name='fact', default=None)),
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
        ('performance_control', sgqlc.types.Arg(PerformSynchronously, graphql_name='performanceControl', default={'performSynchronously': True})),
))
    )
    add_concept_property_type = sgqlc.types.Field(sgqlc.types.non_null('ConceptPropertyType'), graphql_name='addConceptPropertyType', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(ConceptPropertyTypeCreationInput), graphql_name='form', default=None)),
))
    )
    add_concept_property_value_type = sgqlc.types.Field(sgqlc.types.non_null('ConceptPropertyValueType'), graphql_name='addConceptPropertyValueType', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(ConceptPropertyValueTypeCreationInput), graphql_name='form', default=None)),
))
    )
    add_concept_type = sgqlc.types.Field(sgqlc.types.non_null('ConceptType'), graphql_name='addConceptType', args=sgqlc.types.ArgDict((
        ('file', sgqlc.types.Arg(S3FileInput, graphql_name='file', default=None)),
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(ConceptTypeInput), graphql_name='form', default=None)),
))
    )
    add_concept_type_presentation = sgqlc.types.Field(sgqlc.types.non_null('ConceptTypePresentation'), graphql_name='addConceptTypePresentation', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(ConceptTypePresentationAddInput), graphql_name='form', default=None)),
))
    )
    add_concept_type_presentation_template = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='addConceptTypePresentationTemplate', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
        ('s3_file_input', sgqlc.types.Arg(sgqlc.types.non_null(S3FileInput), graphql_name='s3FileInput', default=None)),
))
    )
    add_concept_type_presentation_widget_type = sgqlc.types.Field(sgqlc.types.non_null('ConceptTypePresentationWidgetType'), graphql_name='addConceptTypePresentationWidgetType', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(ConceptTypePresentationWidgetTypeAddInput), graphql_name='form', default=None)),
))
    )
    add_concept_type_view = sgqlc.types.Field(sgqlc.types.non_null('ConceptTypeView'), graphql_name='addConceptTypeView', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(ConceptTypeViewCreationInput), graphql_name='form', default=None)),
))
    )
    add_concepts_from_approved_facts_by_document_node = sgqlc.types.Field(sgqlc.types.non_null('StateWithCount'), graphql_name='addConceptsFromApprovedFactsByDocumentNode', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(ResearchMapContentSelectInput), graphql_name='form', default=None)),
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
        ('quantity', sgqlc.types.Arg(Int, graphql_name='quantity', default=10)),
))
    )
    add_concepts_from_not_approved_facts_by_document_node = sgqlc.types.Field(sgqlc.types.non_null('StateWithCount'), graphql_name='addConceptsFromNotApprovedFactsByDocumentNode', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(ResearchMapContentSelectInput), graphql_name='form', default=None)),
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
        ('quantity', sgqlc.types.Arg(Int, graphql_name='quantity', default=10)),
))
    )
    add_document_duplicate_report = sgqlc.types.Field(sgqlc.types.non_null('DocumentDuplicateReport'), graphql_name='addDocumentDuplicateReport', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(DocumentDuplicateReportInput), graphql_name='input', default=None)),
))
    )
    add_document_feed = sgqlc.types.Field(sgqlc.types.non_null('DocumentFeed'), graphql_name='addDocumentFeed', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(DocumentFeedCreationInput), graphql_name='form', default=None)),
))
    )
    add_document_node_on_research_map = sgqlc.types.Field(sgqlc.types.non_null('StateWithCount'), graphql_name='addDocumentNodeOnResearchMap', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
        ('nodes', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(AddDocumentNodeInput))), graphql_name='nodes', default=None)),
))
    )
    add_document_nodes_by_concept_node = sgqlc.types.Field(sgqlc.types.non_null('StateWithCount'), graphql_name='addDocumentNodesByConceptNode', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(ResearchMapContentSelectInput), graphql_name='form', default=None)),
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
        ('quantity', sgqlc.types.Arg(Int, graphql_name='quantity', default=10)),
))
    )
    add_document_rubric = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('DocumentRubric'))), graphql_name='addDocumentRubric', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(AddDocumentRubricInput), graphql_name='form', default=None)),
))
    )
    add_document_to_document_feed_favorites = sgqlc.types.Field(sgqlc.types.non_null('DocumentFeed'), graphql_name='addDocumentToDocumentFeedFavorites', args=sgqlc.types.ArgDict((
        ('document_feed_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='documentFeedId', default=None)),
        ('document_ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='documentIds', default=None)),
))
    )
    add_document_type = sgqlc.types.Field(sgqlc.types.non_null('DocumentType'), graphql_name='addDocumentType', args=sgqlc.types.ArgDict((
        ('file', sgqlc.types.Arg(S3FileInput, graphql_name='file', default=None)),
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(DocumentTypeInput), graphql_name='form', default=None)),
))
    )
    add_document_type_presentation = sgqlc.types.Field(sgqlc.types.non_null('DocumentTypePresentation'), graphql_name='addDocumentTypePresentation', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(DocumentTypePresentationAddInput), graphql_name='form', default=None)),
))
    )
    add_drawing = sgqlc.types.Field(sgqlc.types.non_null(MapDrawing), graphql_name='addDrawing', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(MapDrawingAddInput), graphql_name='form', default=None)),
))
    )
    add_group = sgqlc.types.Field(sgqlc.types.non_null(Group), graphql_name='addGroup', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(GroupCreationInput), graphql_name='form', default=None)),
))
    )
    add_not_approved_concepts_by_document_node = sgqlc.types.Field(sgqlc.types.non_null('StateWithCount'), graphql_name='addNotApprovedConceptsByDocumentNode', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(ResearchMapContentSelectInput), graphql_name='form', default=None)),
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
        ('quantity', sgqlc.types.Arg(Int, graphql_name='quantity', default=10)),
))
    )
    add_not_approved_linked_concepts_by_concept_node = sgqlc.types.Field(sgqlc.types.non_null('StateWithCount'), graphql_name='addNotApprovedLinkedConceptsByConceptNode', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(ResearchMapContentSelectInput), graphql_name='form', default=None)),
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
        ('quantity', sgqlc.types.Arg(Int, graphql_name='quantity', default=10)),
))
    )
    add_platform = sgqlc.types.Field(sgqlc.types.non_null('Platform'), graphql_name='addPlatform', args=sgqlc.types.ArgDict((
        ('file', sgqlc.types.Arg(S3FileInput, graphql_name='file', default=None)),
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(PlatformCreationInput), graphql_name='form', default=None)),
))
    )
    add_platform_type = sgqlc.types.Field(sgqlc.types.non_null('PlatformType'), graphql_name='addPlatformType', args=sgqlc.types.ArgDict((
        ('file', sgqlc.types.Arg(S3FileInput, graphql_name='file', default=None)),
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(PlatformTypeInput), graphql_name='form', default=None)),
))
    )
    add_property = sgqlc.types.Field(sgqlc.types.non_null('ConceptProperty'), graphql_name='addProperty', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(PropertyAddInput), graphql_name='form', default=None)),
        ('performance_control', sgqlc.types.Arg(PerformSynchronously, graphql_name='performanceControl', default={'performSynchronously': True})),
))
    )
    add_research_map = sgqlc.types.Field(sgqlc.types.non_null('ResearchMap'), graphql_name='addResearchMap', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(ResearchMapCreationInput), graphql_name='form', default=None)),
))
    )
    add_research_map_from_files = sgqlc.types.Field(sgqlc.types.non_null('ResearchMapFromFilesType'), graphql_name='addResearchMapFromFiles', args=sgqlc.types.ArgDict((
        ('files', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(S3FileInput)), graphql_name='files', default=None)),
))
    )
    add_rubric = sgqlc.types.Field(sgqlc.types.non_null('Rubric'), graphql_name='addRubric', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(AddRubricInput), graphql_name='form', default=None)),
))
    )
    add_rubricator = sgqlc.types.Field(sgqlc.types.non_null('Rubricator'), graphql_name='addRubricator', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(AddRubricatorInput), graphql_name='form', default=None)),
))
    )
    add_story_type = sgqlc.types.Field(sgqlc.types.non_null('StoryType'), graphql_name='addStoryType', args=sgqlc.types.ArgDict((
        ('file', sgqlc.types.Arg(S3FileInput, graphql_name='file', default=None)),
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(StoryTypeInput), graphql_name='form', default=None)),
))
    )
    add_template_docx = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='addTemplateDocx', args=sgqlc.types.ArgDict((
        ('file', sgqlc.types.Arg(S3FileInput, graphql_name='file', default=None)),
))
    )
    approve_document_rubric = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='approveDocumentRubric', args=sgqlc.types.ArgDict((
        ('ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='ids', default=None)),
))
    )
    approve_kb_fact = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='approveKbFact', args=sgqlc.types.ArgDict((
        ('ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='ids', default=None)),
))
    )
    approve_research_map_entities = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='approveResearchMapEntities', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(ApproveResearchMapEntitiesInput), graphql_name='form', default=None)),
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    batch_move_nodes_on_domain_map = sgqlc.types.Field(sgqlc.types.non_null(DomainMap), graphql_name='batchMoveNodesOnDomainMap', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(ResearchMapBatchMoveInput), graphql_name='form', default=None)),
))
    )
    batch_move_nodes_on_map = sgqlc.types.Field(sgqlc.types.non_null('ResearchMap'), graphql_name='batchMoveNodesOnMap', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(ResearchMapBatchMoveInput), graphql_name='form', default=None)),
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    batch_update_group_on_map = sgqlc.types.Field(sgqlc.types.non_null('ResearchMap'), graphql_name='batchUpdateGroupOnMap', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(ResearchMapBatchUpdateGroupInput), graphql_name='form', default=None)),
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    bulk_delete_research_map = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='bulkDeleteResearchMap', args=sgqlc.types.ArgDict((
        ('ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='ids', default=None)),
))
    )
    decline_concept_duplicate = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='declineConceptDuplicate', args=sgqlc.types.ArgDict((
        ('ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='ids', default=None)),
))
    )
    decline_document_duplicate_task = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='declineDocumentDuplicateTask', args=sgqlc.types.ArgDict((
        ('report_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='reportId', default=None)),
        ('task_ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='taskIds', default=None)),
))
    )
    delete_access_level = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='deleteAccessLevel', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    delete_account = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='deleteAccount', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    delete_account_type = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='deleteAccountType', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    delete_all_document_duplicate_task = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='deleteAllDocumentDuplicateTask', args=sgqlc.types.ArgDict((
        ('report_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='reportId', default=None)),
))
    )
    delete_bulk = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of('State')), graphql_name='deleteBulk', args=sgqlc.types.ArgDict((
        ('ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='ids', default=None)),
))
    )
    delete_composite_property_value_template = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='deleteCompositePropertyValueTemplate', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    delete_concept = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='deleteConcept', args=sgqlc.types.ArgDict((
        ('ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='ids', default=None)),
        ('performance_control', sgqlc.types.Arg(PerformSynchronously, graphql_name='performanceControl', default={'performSynchronously': False})),
))
    )
    delete_concept_by_research_map = sgqlc.types.Field(sgqlc.types.non_null('StateWithCount'), graphql_name='deleteConceptByResearchMap', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(ResearchMapContentSelectInput), graphql_name='form', default=None)),
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    delete_concept_duplicate_report = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='deleteConceptDuplicateReport', args=sgqlc.types.ArgDict((
        ('ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='ids', default=None)),
))
    )
    delete_concept_fact = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='deleteConceptFact', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    delete_concept_link = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='deleteConceptLink', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    delete_concept_link_fact = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='deleteConceptLinkFact', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    delete_concept_link_property = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='deleteConceptLinkProperty', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    delete_concept_link_property_fact = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='deleteConceptLinkPropertyFact', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    delete_concept_link_property_type = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='deleteConceptLinkPropertyType', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    delete_concept_link_type = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='deleteConceptLinkType', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    delete_concept_property = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='deleteConceptProperty', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    delete_concept_property_fact = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='deleteConceptPropertyFact', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    delete_concept_property_type = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='deleteConceptPropertyType', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    delete_concept_property_value_type = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='deleteConceptPropertyValueType', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    delete_concept_type = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='deleteConceptType', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    delete_concept_type_avatar = sgqlc.types.Field(sgqlc.types.non_null('ConceptType'), graphql_name='deleteConceptTypeAvatar', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    delete_concept_type_presentation = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='deleteConceptTypePresentation', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    delete_concept_type_presentation_widget_type = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='deleteConceptTypePresentationWidgetType', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    delete_concept_type_view = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='deleteConceptTypeView', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    delete_content_from_research_map = sgqlc.types.Field(sgqlc.types.non_null('ResearchMap'), graphql_name='deleteContentFromResearchMap', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(ResearchMapContentUpdateInput), graphql_name='form', default=None)),
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    delete_document_duplicate_report = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='deleteDocumentDuplicateReport', args=sgqlc.types.ArgDict((
        ('report_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='reportId', default=None)),
))
    )
    delete_document_duplicate_task = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='deleteDocumentDuplicateTask', args=sgqlc.types.ArgDict((
        ('report_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='reportId', default=None)),
        ('task_ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='taskIds', default=None)),
))
    )
    delete_document_feed = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='deleteDocumentFeed', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    delete_document_from_document_feed = sgqlc.types.Field(sgqlc.types.non_null('DocumentFeed'), graphql_name='deleteDocumentFromDocumentFeed', args=sgqlc.types.ArgDict((
        ('document_feed_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='documentFeedId', default=None)),
        ('document_ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='documentIds', default=None)),
))
    )
    delete_document_from_document_feed_favorites = sgqlc.types.Field(sgqlc.types.non_null('DocumentFeed'), graphql_name='deleteDocumentFromDocumentFeedFavorites', args=sgqlc.types.ArgDict((
        ('document_feed_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='documentFeedId', default=None)),
        ('document_ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='documentIds', default=None)),
))
    )
    delete_document_rubric = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='deleteDocumentRubric', args=sgqlc.types.ArgDict((
        ('ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='ids', default=None)),
))
    )
    delete_document_type = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='deleteDocumentType', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    delete_document_type_presentation = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='deleteDocumentTypePresentation', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    delete_documents = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='deleteDocuments', args=sgqlc.types.ArgDict((
        ('ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='ids', default=None)),
        ('performance_control', sgqlc.types.Arg(PerformSynchronously, graphql_name='performanceControl', default={'performSynchronously': False})),
))
    )
    delete_drawing = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='deleteDrawing', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    delete_fact = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='deleteFact', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    delete_group = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='deleteGroup', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    delete_platform = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='deletePlatform', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    delete_platform_type = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='deletePlatformType', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    delete_property = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='deleteProperty', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    delete_research_map = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='deleteResearchMap', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    delete_rubric = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='deleteRubric', args=sgqlc.types.ArgDict((
        ('ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='ids', default=None)),
))
    )
    delete_rubricator = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='deleteRubricator', args=sgqlc.types.ArgDict((
        ('ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='ids', default=None)),
))
    )
    delete_story_type = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='deleteStoryType', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    find_shortest_path_on_map = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='findShortestPathOnMap', args=sgqlc.types.ArgDict((
        ('concept_node_ids', sgqlc.types.Arg(sgqlc.types.non_null(ConceptAddImplicitLinkInput), graphql_name='conceptNodeIds', default=None)),
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    force_handle_document = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='forceHandleDocument', args=sgqlc.types.ArgDict((
        ('ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='ids', default=None)),
))
    )
    mark_document_as_read = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='markDocumentAsRead', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    mark_document_as_unread = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='markDocumentAsUnread', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    merge_concepts = sgqlc.types.Field(sgqlc.types.non_null('Concept'), graphql_name='mergeConcepts', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(ConceptMergeInput), graphql_name='form', default=None)),
))
    )
    normalize_value = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('AnyValue'))), graphql_name='normalizeValue', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(NormalizationInput), graphql_name='input', default=None)),
))
    )
    remove_all_candidate_facts_from_document = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='removeAllCandidateFactsFromDocument', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    remove_all_kbfacts_from_document = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='removeAllKBFactsFromDocument', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(DocumentAllKBFactsRemoveInput), graphql_name='form', default=None)),
))
    )
    remove_candidate_fact_from_document = sgqlc.types.Field(sgqlc.types.non_null('Document'), graphql_name='removeCandidateFactFromDocument', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(DocumentDeleteCandidateFactInput), graphql_name='form', default=None)),
))
    )
    restore_document_to_document_feed = sgqlc.types.Field(sgqlc.types.non_null('DocumentFeed'), graphql_name='restoreDocumentToDocumentFeed', args=sgqlc.types.ArgDict((
        ('document_feed_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='documentFeedId', default=None)),
        ('document_ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='documentIds', default=None)),
))
    )
    reverse_concept_link = sgqlc.types.Field(sgqlc.types.non_null('ConceptLink'), graphql_name='reverseConceptLink', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    set_concept_type_default_view = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='setConceptTypeDefaultView', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(ConceptTypePresentationViewInput), graphql_name='form', default=None)),
))
    )
    set_document_type_default_view = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='setDocumentTypeDefaultView', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(DocumentTypePresentationViewInput), graphql_name='form', default=None)),
))
    )
    set_research_map_active = sgqlc.types.Field(sgqlc.types.non_null('ResearchMap'), graphql_name='setResearchMapActive', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    toggle_concept_type_presentation_visibility_in_menu = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='toggleConceptTypePresentationVisibilityInMenu', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    toggle_concept_type_view_visibility_in_menu = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='toggleConceptTypeViewVisibilityInMenu', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    translate_tql = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='translateTQL', args=sgqlc.types.ArgDict((
        ('query', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='query', default=None)),
        ('source_language', sgqlc.types.Arg(String, graphql_name='sourceLanguage', default=None)),
        ('target_language', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='targetLanguage', default=None)),
))
    )
    unmerge_concepts = sgqlc.types.Field(sgqlc.types.non_null('Concept'), graphql_name='unmergeConcepts', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(ConceptUnmergeInput), graphql_name='form', default=None)),
))
    )
    update_access_level = sgqlc.types.Field(sgqlc.types.non_null(AccessLevel), graphql_name='updateAccessLevel', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(AccessLevelUpdateInput), graphql_name='form', default=None)),
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    update_account = sgqlc.types.Field(sgqlc.types.non_null('Account'), graphql_name='updateAccount', args=sgqlc.types.ArgDict((
        ('delete_image', sgqlc.types.Arg(Boolean, graphql_name='deleteImage', default=False)),
        ('file', sgqlc.types.Arg(S3FileInput, graphql_name='file', default=None)),
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(AccountUpdateInput), graphql_name='form', default=None)),
))
    )
    update_account_type = sgqlc.types.Field(sgqlc.types.non_null('AccountType'), graphql_name='updateAccountType', args=sgqlc.types.ArgDict((
        ('delete_image', sgqlc.types.Arg(Boolean, graphql_name='deleteImage', default=False)),
        ('file', sgqlc.types.Arg(S3FileInput, graphql_name='file', default=None)),
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(AccountTypeInput), graphql_name='form', default=None)),
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    update_composite_property_value_template = sgqlc.types.Field(sgqlc.types.non_null('CompositePropertyValueTemplate'), graphql_name='updateCompositePropertyValueTemplate', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(CompositePropertyValueTemplateCreateInput), graphql_name='form', default=None)),
))
    )
    update_concept = sgqlc.types.Field(sgqlc.types.non_null('Concept'), graphql_name='updateConcept', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(ConceptUpdateInput), graphql_name='form', default=None)),
        ('performance_control', sgqlc.types.Arg(PerformSynchronously, graphql_name='performanceControl', default={'performSynchronously': True})),
))
    )
    update_concept_avatar = sgqlc.types.Field(sgqlc.types.non_null('Concept'), graphql_name='updateConceptAvatar', args=sgqlc.types.ArgDict((
        ('document_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='documentId', default=None)),
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    update_concept_link = sgqlc.types.Field(sgqlc.types.non_null('ConceptLink'), graphql_name='updateConceptLink', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(ConceptLinkUpdateMutationInput), graphql_name='form', default=None)),
))
    )
    update_concept_link_property_type = sgqlc.types.Field(sgqlc.types.non_null('ConceptPropertyType'), graphql_name='updateConceptLinkPropertyType', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(ConceptLinkPropertyTypeUpdateInput), graphql_name='form', default=None)),
))
    )
    update_concept_link_type = sgqlc.types.Field(sgqlc.types.non_null('ConceptLinkType'), graphql_name='updateConceptLinkType', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(ConceptLinkTypeUpdateInput), graphql_name='form', default=None)),
))
    )
    update_concept_main_property_type_order = sgqlc.types.Field(sgqlc.types.non_null('ConceptType'), graphql_name='updateConceptMainPropertyTypeOrder', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(InterestObjectMainPropertiesOrderUpdateInput), graphql_name='form', default=None)),
))
    )
    update_concept_property = sgqlc.types.Field(sgqlc.types.non_null('ConceptProperty'), graphql_name='updateConceptProperty', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(ConceptPropertyUpdateInput), graphql_name='form', default=None)),
))
    )
    update_concept_property_type = sgqlc.types.Field(sgqlc.types.non_null('ConceptPropertyType'), graphql_name='updateConceptPropertyType', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(ConceptPropertyTypeUpdateInput), graphql_name='form', default=None)),
))
    )
    update_concept_property_value_type = sgqlc.types.Field(sgqlc.types.non_null('ConceptPropertyValueType'), graphql_name='updateConceptPropertyValueType', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(ConceptPropertyValueTypeUpdateInput), graphql_name='form', default=None)),
))
    )
    update_concept_registry_view = sgqlc.types.Field(sgqlc.types.non_null(ConceptRegistryView), graphql_name='updateConceptRegistryView', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(ConceptRegistryViewInput), graphql_name='form', default=None)),
))
    )
    update_concept_subscriptions = sgqlc.types.Field(sgqlc.types.non_null('Concept'), graphql_name='updateConceptSubscriptions', args=sgqlc.types.ArgDict((
        ('events', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ConceptUpdate))), graphql_name='events', default=None)),
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    update_concept_type = sgqlc.types.Field(sgqlc.types.non_null('ConceptType'), graphql_name='updateConceptType', args=sgqlc.types.ArgDict((
        ('delete_image', sgqlc.types.Arg(Boolean, graphql_name='deleteImage', default=False)),
        ('file', sgqlc.types.Arg(S3FileInput, graphql_name='file', default=None)),
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(ConceptTypeInput), graphql_name='form', default=None)),
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    update_concept_type_presentation = sgqlc.types.Field(sgqlc.types.non_null('ConceptTypePresentation'), graphql_name='updateConceptTypePresentation', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(ConceptTypePresentationUpdateInput), graphql_name='form', default=None)),
))
    )
    update_concept_type_presentation_template_filename = sgqlc.types.Field(sgqlc.types.non_null('ConceptTypePresentation'), graphql_name='updateConceptTypePresentationTemplateFilename', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(ConceptTypePresentationUpdateTemplateFilenameInput), graphql_name='form', default=None)),
))
    )
    update_concept_type_presentation_widget_type = sgqlc.types.Field(sgqlc.types.non_null('ConceptTypePresentationWidgetType'), graphql_name='updateConceptTypePresentationWidgetType', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(ConceptTypePresentationWidgetTypeUpdateInput), graphql_name='form', default=None)),
))
    )
    update_concept_type_presentation_widget_types_order = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='updateConceptTypePresentationWidgetTypesOrder', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(ConceptTypePresentationWidgetTypeUpdateOrderInput), graphql_name='form', default=None)),
))
    )
    update_concept_type_view = sgqlc.types.Field(sgqlc.types.non_null('ConceptTypeView'), graphql_name='updateConceptTypeView', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(ConceptTypeViewUpdateInput), graphql_name='form', default=None)),
))
    )
    update_document = sgqlc.types.Field(sgqlc.types.non_null('Document'), graphql_name='updateDocument', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(DocumentUpdateInput), graphql_name='form', default=None)),
))
    )
    update_document_avatar = sgqlc.types.Field(sgqlc.types.non_null('Document'), graphql_name='updateDocumentAvatar', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(DocumentAvatarUpdateInput), graphql_name='form', default=None)),
))
    )
    update_document_bulk = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='updateDocumentBulk', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(BulkDocumentUpdateInput), graphql_name='form', default=None)),
        ('ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='ids', default=None)),
))
    )
    update_document_facets = sgqlc.types.Field(sgqlc.types.non_null(DocumentFacets), graphql_name='updateDocumentFacets', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    update_document_facts = sgqlc.types.Field(sgqlc.types.non_null('StateWithErrors'), graphql_name='updateDocumentFacts', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(BatchUpdateFactInput), graphql_name='form', default=None)),
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    update_document_feed = sgqlc.types.Field(sgqlc.types.non_null('DocumentFeed'), graphql_name='updateDocumentFeed', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(DocumentFeedUpdateInput), graphql_name='form', default=None)),
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    update_document_feed_subscriptions = sgqlc.types.Field(sgqlc.types.non_null('DocumentFeed'), graphql_name='updateDocumentFeedSubscriptions', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(UpdateDocumentFeedSubscriptionsInput), graphql_name='form', default=None)),
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    update_document_feed_view = sgqlc.types.Field(sgqlc.types.non_null(DocumentFeedView), graphql_name='updateDocumentFeedView', args=sgqlc.types.ArgDict((
        ('document_feed_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='documentFeedId', default=None)),
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(DocumentFeedViewInput), graphql_name='form', default=None)),
))
    )
    update_document_metadata = sgqlc.types.Field(sgqlc.types.non_null('Document'), graphql_name='updateDocumentMetadata', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(UpdateDocumentMetadataInput), graphql_name='form', default=None)),
))
    )
    update_document_metadata_bulk = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='updateDocumentMetadataBulk', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(BulkUpdateDocumentMetadataInput), graphql_name='form', default=None)),
        ('ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='ids', default=None)),
))
    )
    update_document_node = sgqlc.types.Field(sgqlc.types.non_null('Document'), graphql_name='updateDocumentNode', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(DocumentNodeUpdateInput), graphql_name='form', default=None)),
))
    )
    update_document_registry_view = sgqlc.types.Field(sgqlc.types.non_null(DocumentRegistryView), graphql_name='updateDocumentRegistryView', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(DocumentRegistryViewInput), graphql_name='form', default=None)),
))
    )
    update_document_subscriptions = sgqlc.types.Field(sgqlc.types.non_null('Document'), graphql_name='updateDocumentSubscriptions', args=sgqlc.types.ArgDict((
        ('events', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(DocumentUpdate))), graphql_name='events', default=None)),
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    update_document_type = sgqlc.types.Field(sgqlc.types.non_null('DocumentType'), graphql_name='updateDocumentType', args=sgqlc.types.ArgDict((
        ('delete_image', sgqlc.types.Arg(Boolean, graphql_name='deleteImage', default=False)),
        ('file', sgqlc.types.Arg(S3FileInput, graphql_name='file', default=None)),
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(DocumentTypeInput), graphql_name='form', default=None)),
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    update_document_type_presentation = sgqlc.types.Field(sgqlc.types.non_null('DocumentTypePresentation'), graphql_name='updateDocumentTypePresentation', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(DocumentTypePresentationUpdateInput), graphql_name='form', default=None)),
))
    )
    update_drawing = sgqlc.types.Field(sgqlc.types.non_null(MapDrawing), graphql_name='updateDrawing', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(MapDrawingUpdateInput), graphql_name='form', default=None)),
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    update_edge_annotation = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='updateEdgeAnnotation', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(UpdateEdgeAnnotationInput), graphql_name='form', default=None)),
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    update_group = sgqlc.types.Field(sgqlc.types.non_null(Group), graphql_name='updateGroup', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(GroupUpdateInput), graphql_name='form', default=None)),
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    update_group_annotation = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='updateGroupAnnotation', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(UpdateGroupAnnotationInput), graphql_name='form', default=None)),
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    update_markers_bulk = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='updateMarkersBulk', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(BulkMarkersUpdateInput), graphql_name='form', default=None)),
))
    )
    update_node_annotation = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='updateNodeAnnotation', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(UpdateNodeAnnotationInput), graphql_name='form', default=None)),
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    update_platform = sgqlc.types.Field(sgqlc.types.non_null('Platform'), graphql_name='updatePlatform', args=sgqlc.types.ArgDict((
        ('delete_image', sgqlc.types.Arg(Boolean, graphql_name='deleteImage', default=False)),
        ('file', sgqlc.types.Arg(S3FileInput, graphql_name='file', default=None)),
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(PlatformUpdateInput), graphql_name='form', default=None)),
))
    )
    update_platform_type = sgqlc.types.Field(sgqlc.types.non_null('PlatformType'), graphql_name='updatePlatformType', args=sgqlc.types.ArgDict((
        ('delete_image', sgqlc.types.Arg(Boolean, graphql_name='deleteImage', default=False)),
        ('file', sgqlc.types.Arg(S3FileInput, graphql_name='file', default=None)),
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(PlatformTypeInput), graphql_name='form', default=None)),
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    update_property = sgqlc.types.Field(sgqlc.types.non_null('ConceptProperty'), graphql_name='updateProperty', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(PropertyUpdateInput), graphql_name='form', default=None)),
))
    )
    update_research_map = sgqlc.types.Field(sgqlc.types.non_null('ResearchMap'), graphql_name='updateResearchMap', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(ResearchMapUpdateInput), graphql_name='form', default=None)),
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    update_rubric = sgqlc.types.Field(sgqlc.types.non_null('Rubric'), graphql_name='updateRubric', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(UpdateRubricInput), graphql_name='form', default=None)),
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    update_rubrication_facets = sgqlc.types.Field(sgqlc.types.non_null('RubricationFacets'), graphql_name='updateRubricationFacets', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    update_rubricator = sgqlc.types.Field(sgqlc.types.non_null('Rubricator'), graphql_name='updateRubricator', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(UpdateRubricatorInput), graphql_name='form', default=None)),
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    update_story_type = sgqlc.types.Field(sgqlc.types.non_null('StoryType'), graphql_name='updateStoryType', args=sgqlc.types.ArgDict((
        ('delete_image', sgqlc.types.Arg(Boolean, graphql_name='deleteImage', default=False)),
        ('file', sgqlc.types.Arg(S3FileInput, graphql_name='file', default=None)),
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(StoryTypeInput), graphql_name='form', default=None)),
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    update_type_search_element = sgqlc.types.Field(sgqlc.types.non_null('State'), graphql_name='updateTypeSearchElement', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(TypeSearchElementUpdateInput), graphql_name='form', default=None)),
))
    )


class NERCRegexp(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('auto_create', 'context_regexp', 'regexp')
    auto_create = sgqlc.types.Field(Boolean, graphql_name='autoCreate')
    context_regexp = sgqlc.types.Field(String, graphql_name='contextRegexp')
    regexp = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='regexp')


class NamedValue(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('id', 'property_value_type', 'value')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    property_value_type = sgqlc.types.Field(sgqlc.types.non_null(CompositePropertyValueType), graphql_name='propertyValueType')
    value = sgqlc.types.Field(sgqlc.types.non_null('Value'), graphql_name='value')


class ParagraphMetadata(sgqlc.types.Type):
    __schema__ = api_schema
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


class PlatformPagination(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('list_platform', 'total')
    list_platform = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('Platform'))), graphql_name='listPlatform')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class PlatformStatistics(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('count_account', 'count_doc')
    count_account = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='countAccount')
    count_doc = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='countDoc')


class PlatformTypePagination(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('list_platform_type', 'total')
    list_platform_type = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('PlatformType'))), graphql_name='listPlatformType')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class PotentialDocumentFactUpdates(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('concept_facts_to_approve_count', 'concept_facts_to_change_count', 'concept_facts_to_reject_count', 'concept_facts_to_update_count', 'concept_link_facts_to_reject_count', 'concept_link_facts_to_update_count', 'concept_property_facts_to_reject_count', 'concept_property_facts_to_update_count', 'link_property_facts_to_reject_count', 'link_property_facts_to_update_count')
    concept_facts_to_approve_count = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='conceptFactsToApproveCount')
    concept_facts_to_change_count = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='conceptFactsToChangeCount')
    concept_facts_to_reject_count = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='conceptFactsToRejectCount')
    concept_facts_to_update_count = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='conceptFactsToUpdateCount')
    concept_link_facts_to_reject_count = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='conceptLinkFactsToRejectCount')
    concept_link_facts_to_update_count = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='conceptLinkFactsToUpdateCount')
    concept_property_facts_to_reject_count = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='conceptPropertyFactsToRejectCount')
    concept_property_facts_to_update_count = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='conceptPropertyFactsToUpdateCount')
    link_property_facts_to_reject_count = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='linkPropertyFactsToRejectCount')
    link_property_facts_to_update_count = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='linkPropertyFactsToUpdateCount')


class Query(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('access_level', 'account', 'account_type', 'active_research_map', 'check_potential_document_fact_updates', 'composite_concept_property_type', 'composite_link_property_type', 'composite_property_value_template', 'concept', 'concept_autocomplete', 'concept_duplicate_group', 'concept_duplicate_report', 'concept_fs2_query', 'concept_link', 'concept_link_type', 'concept_presentation', 'concept_property', 'concept_property_type', 'concept_property_value_type', 'concept_registry_view', 'concept_type', 'concept_type_presentation', 'concept_type_view', 'document', 'document_autocomplete', 'document_duplicate_report', 'document_duplicate_task', 'document_facets', 'document_feed', 'document_feed_view', 'document_registry_view', 'document_rubric', 'document_type', 'document_type_presentation', 'domain_map', 'entity_type', 'get_osm_coordinates', 'get_osm_place_name', 'linked_concept_autocomplete', 'list_access_level', 'list_account_by_id', 'list_account_type', 'list_child_rubric_facet_by_parent_id', 'list_composite_concept_property_type', 'list_composite_link_property_type', 'list_composite_property_value_template', 'list_concept_by_id', 'list_concept_duplicate_report', 'list_concept_link', 'list_concept_link_between_fixed_concepts', 'list_concept_link_type', 'list_concept_property_type', 'list_concept_property_type_by_id', 'list_concept_property_value_type', 'list_concept_type', 'list_document_by_id', 'list_document_by_uuid', 'list_document_type', 'list_last_research_map', 'list_platform_by_id', 'list_platform_type', 'list_research_map_by_id', 'list_rubric_by_rubricator', 'list_story_type', 'list_top_neighbors_on_map', 'list_user_menu_type', 'markers_bulk', 'pagination_access_level', 'pagination_account', 'pagination_account_type', 'pagination_composite_concept_property_type', 'pagination_composite_link_property_type', 'pagination_composite_property_value_template', 'pagination_concept', 'pagination_concept_duplicate', 'pagination_concept_duplicate_group', 'pagination_concept_duplicate_report', 'pagination_concept_link', 'pagination_concept_link_property_type', 'pagination_concept_link_type', 'pagination_concept_presentation', 'pagination_concept_property_type', 'pagination_concept_property_value_type', 'pagination_concept_related_document', 'pagination_concept_type', 'pagination_concept_type_presentation', 'pagination_country', 'pagination_document_duplicate_report', 'pagination_document_duplicate_task', 'pagination_document_feed', 'pagination_document_markers', 'pagination_document_rubric', 'pagination_document_type', 'pagination_document_type_presentation', 'pagination_language', 'pagination_link_property_related_document', 'pagination_link_related_document', 'pagination_platform', 'pagination_platform_type', 'pagination_property_related_document', 'pagination_property_type', 'pagination_research_map', 'pagination_rubric', 'pagination_rubricator', 'pagination_story', 'pagination_story_type', 'platform', 'platform_type', 'research_map', 'rubric', 'rubric_by_transformator_id', 'rubrication_facets', 'rubricator', 'story', 'story_fs2_query', 'story_type')
    access_level = sgqlc.types.Field(sgqlc.types.non_null(AccessLevel), graphql_name='accessLevel', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    account = sgqlc.types.Field(sgqlc.types.non_null('Account'), graphql_name='account', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    account_type = sgqlc.types.Field(sgqlc.types.non_null('AccountType'), graphql_name='accountType', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    active_research_map = sgqlc.types.Field('ResearchMap', graphql_name='activeResearchMap')
    check_potential_document_fact_updates = sgqlc.types.Field(sgqlc.types.non_null(PotentialDocumentFactUpdates), graphql_name='checkPotentialDocumentFactUpdates', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(BatchUpdateFactInput), graphql_name='form', default=None)),
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    composite_concept_property_type = sgqlc.types.Field(sgqlc.types.non_null('ConceptPropertyType'), graphql_name='compositeConceptPropertyType', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    composite_link_property_type = sgqlc.types.Field(sgqlc.types.non_null('ConceptPropertyType'), graphql_name='compositeLinkPropertyType', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    composite_property_value_template = sgqlc.types.Field(sgqlc.types.non_null('CompositePropertyValueTemplate'), graphql_name='compositePropertyValueTemplate', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    concept = sgqlc.types.Field('Concept', graphql_name='concept', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    concept_autocomplete = sgqlc.types.Field(sgqlc.types.non_null(Autocomplete), graphql_name='conceptAutocomplete', args=sgqlc.types.ArgDict((
        ('destination', sgqlc.types.Arg(sgqlc.types.non_null(AutocompleteConceptDestination), graphql_name='destination', default=None)),
        ('query', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='query', default=None)),
))
    )
    concept_duplicate_group = sgqlc.types.Field(sgqlc.types.non_null(ConceptDuplicateGroup), graphql_name='conceptDuplicateGroup', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    concept_duplicate_report = sgqlc.types.Field(sgqlc.types.non_null('ConceptDuplicateReport'), graphql_name='conceptDuplicateReport', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    concept_fs2_query = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='conceptFs2Query', args=sgqlc.types.ArgDict((
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(ConceptFilterSettings), graphql_name='filterSettings', default=None)),
))
    )
    concept_link = sgqlc.types.Field(sgqlc.types.non_null('ConceptLink'), graphql_name='conceptLink', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    concept_link_type = sgqlc.types.Field(sgqlc.types.non_null('ConceptLinkType'), graphql_name='conceptLinkType', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    concept_presentation = sgqlc.types.Field(sgqlc.types.non_null(ConceptPresentation), graphql_name='conceptPresentation', args=sgqlc.types.ArgDict((
        ('concept_type_presentation_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='conceptTypePresentationId', default=None)),
        ('root_concept_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='rootConceptId', default=None)),
))
    )
    concept_property = sgqlc.types.Field('ConceptProperty', graphql_name='conceptProperty', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    concept_property_type = sgqlc.types.Field(sgqlc.types.non_null('ConceptPropertyType'), graphql_name='conceptPropertyType', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    concept_property_value_type = sgqlc.types.Field(sgqlc.types.non_null('ConceptPropertyValueType'), graphql_name='conceptPropertyValueType', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    concept_registry_view = sgqlc.types.Field(sgqlc.types.non_null(ConceptRegistryView), graphql_name='conceptRegistryView')
    concept_type = sgqlc.types.Field(sgqlc.types.non_null('ConceptType'), graphql_name='conceptType', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    concept_type_presentation = sgqlc.types.Field(sgqlc.types.non_null('ConceptTypePresentation'), graphql_name='conceptTypePresentation', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    concept_type_view = sgqlc.types.Field(sgqlc.types.non_null('ConceptTypeView'), graphql_name='conceptTypeView', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    document = sgqlc.types.Field('Document', graphql_name='document', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    document_autocomplete = sgqlc.types.Field(sgqlc.types.non_null(Autocomplete), graphql_name='documentAutocomplete', args=sgqlc.types.ArgDict((
        ('destination', sgqlc.types.Arg(sgqlc.types.non_null(AutocompleteDocumentDestination), graphql_name='destination', default=None)),
        ('query', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='query', default=None)),
))
    )
    document_duplicate_report = sgqlc.types.Field(sgqlc.types.non_null('DocumentDuplicateReport'), graphql_name='documentDuplicateReport', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    document_duplicate_task = sgqlc.types.Field(sgqlc.types.non_null(DocumentDuplicateTask), graphql_name='documentDuplicateTask', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
        ('report_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='reportId', default=None)),
))
    )
    document_facets = sgqlc.types.Field(sgqlc.types.non_null(DocumentFacets), graphql_name='documentFacets', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    document_feed = sgqlc.types.Field(sgqlc.types.non_null('DocumentFeed'), graphql_name='documentFeed', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    document_feed_view = sgqlc.types.Field(sgqlc.types.non_null(DocumentFeedView), graphql_name='documentFeedView', args=sgqlc.types.ArgDict((
        ('document_feed_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='documentFeedId', default=None)),
))
    )
    document_registry_view = sgqlc.types.Field(sgqlc.types.non_null(DocumentRegistryView), graphql_name='documentRegistryView')
    document_rubric = sgqlc.types.Field(sgqlc.types.non_null('DocumentRubric'), graphql_name='documentRubric', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    document_type = sgqlc.types.Field(sgqlc.types.non_null('DocumentType'), graphql_name='documentType', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    document_type_presentation = sgqlc.types.Field(sgqlc.types.non_null('DocumentTypePresentation'), graphql_name='documentTypePresentation', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    domain_map = sgqlc.types.Field(sgqlc.types.non_null(DomainMap), graphql_name='domainMap')
    entity_type = sgqlc.types.Field(sgqlc.types.non_null(EntityType), graphql_name='entityType', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    get_osm_coordinates = sgqlc.types.Field(sgqlc.types.non_null(GeoPointValue), graphql_name='getOsmCoordinates', args=sgqlc.types.ArgDict((
        ('name', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='name', default=None)),
))
    )
    get_osm_place_name = sgqlc.types.Field(sgqlc.types.non_null(GeoPointValue), graphql_name='getOsmPlaceName', args=sgqlc.types.ArgDict((
        ('latitude', sgqlc.types.Arg(sgqlc.types.non_null(Float), graphql_name='latitude', default=None)),
        ('longitude', sgqlc.types.Arg(sgqlc.types.non_null(Float), graphql_name='longitude', default=None)),
))
    )
    linked_concept_autocomplete = sgqlc.types.Field(sgqlc.types.non_null(Autocomplete), graphql_name='linkedConceptAutocomplete', args=sgqlc.types.ArgDict((
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(LinkedConceptListFilterSettings), graphql_name='filterSettings', default=None)),
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
))
    )
    list_access_level = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(AccessLevel))), graphql_name='listAccessLevel', args=sgqlc.types.ArgDict((
        ('ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='ids', default=None)),
))
    )
    list_account_by_id = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('Account'))), graphql_name='listAccountById', args=sgqlc.types.ArgDict((
        ('ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='ids', default=None)),
))
    )
    list_account_type = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('AccountType'))), graphql_name='listAccountType')
    list_child_rubric_facet_by_parent_id = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('RubricFacet'))), graphql_name='listChildRubricFacetByParentId', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
        ('parent_rubric_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='parentRubricId', default=None)),
))
    )
    list_composite_concept_property_type = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ConceptPropertyType'))), graphql_name='listCompositeConceptPropertyType')
    list_composite_link_property_type = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ConceptPropertyType'))), graphql_name='listCompositeLinkPropertyType')
    list_composite_property_value_template = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('CompositePropertyValueTemplate'))), graphql_name='listCompositePropertyValueTemplate')
    list_concept_by_id = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of('Concept')), graphql_name='listConceptById', args=sgqlc.types.ArgDict((
        ('ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='ids', default=None)),
))
    )
    list_concept_duplicate_report = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of('ConceptDuplicateReport')), graphql_name='listConceptDuplicateReport', args=sgqlc.types.ArgDict((
        ('ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='ids', default=None)),
))
    )
    list_concept_link = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of('ConceptLink')), graphql_name='listConceptLink', args=sgqlc.types.ArgDict((
        ('ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='ids', default=None)),
))
    )
    list_concept_link_between_fixed_concepts = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ConceptLink'))), graphql_name='listConceptLinkBetweenFixedConcepts', args=sgqlc.types.ArgDict((
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(ConceptLinkFilterSettings), graphql_name='filterSettings', default=None)),
        ('ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='ids', default=None)),
))
    )
    list_concept_link_type = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ConceptLinkType'))), graphql_name='listConceptLinkType')
    list_concept_property_type = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ConceptPropertyType'))), graphql_name='listConceptPropertyType')
    list_concept_property_type_by_id = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of('ConceptPropertyType')), graphql_name='listConceptPropertyTypeById', args=sgqlc.types.ArgDict((
        ('ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='ids', default=None)),
))
    )
    list_concept_property_value_type = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ConceptPropertyValueType'))), graphql_name='listConceptPropertyValueType')
    list_concept_type = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ConceptType'))), graphql_name='listConceptType')
    list_document_by_id = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of('Document')), graphql_name='listDocumentById', args=sgqlc.types.ArgDict((
        ('ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='ids', default=None)),
))
    )
    list_document_by_uuid = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of('Document')), graphql_name='listDocumentByUUID', args=sgqlc.types.ArgDict((
        ('ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='ids', default=None)),
))
    )
    list_document_type = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('DocumentType'))), graphql_name='listDocumentType')
    list_last_research_map = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ResearchMap'))), graphql_name='listLastResearchMap')
    list_platform_by_id = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('Platform'))), graphql_name='listPlatformById', args=sgqlc.types.ArgDict((
        ('ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='ids', default=None)),
))
    )
    list_platform_type = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('PlatformType'))), graphql_name='listPlatformType')
    list_research_map_by_id = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of('ResearchMap')), graphql_name='listResearchMapById', args=sgqlc.types.ArgDict((
        ('ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='ids', default=None)),
))
    )
    list_rubric_by_rubricator = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('Rubric'))), graphql_name='listRubricByRubricator', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    list_story_type = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('StoryType'))), graphql_name='listStoryType')
    list_top_neighbors_on_map = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ConceptWithNeighbors))), graphql_name='listTopNeighborsOnMap', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(ResearchMapContentSelectInput), graphql_name='form', default=None)),
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
        ('quantity', sgqlc.types.Arg(Int, graphql_name='quantity', default=10)),
))
    )
    list_user_menu_type = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('UserMenuType'))), graphql_name='listUserMenuType')
    markers_bulk = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(Markers)), graphql_name='markersBulk', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(BulkMarkersInput), graphql_name='form', default=None)),
))
    )
    pagination_access_level = sgqlc.types.Field(sgqlc.types.non_null(AccessLevelPagination), graphql_name='paginationAccessLevel', args=sgqlc.types.ArgDict((
        ('direction', sgqlc.types.Arg(SortDirection, graphql_name='direction', default='descending')),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('query', sgqlc.types.Arg(String, graphql_name='query', default=None)),
        ('sort_field', sgqlc.types.Arg(AccessLevelSorting, graphql_name='sortField', default='id')),
))
    )
    pagination_account = sgqlc.types.Field(sgqlc.types.non_null(AccountPagination), graphql_name='paginationAccount', args=sgqlc.types.ArgDict((
        ('direction', sgqlc.types.Arg(SortDirection, graphql_name='direction', default='descending')),
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(AccountFilterSettings), graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('sort_field', sgqlc.types.Arg(AccountSorting, graphql_name='sortField', default='id')),
))
    )
    pagination_account_type = sgqlc.types.Field(sgqlc.types.non_null(AccountTypePagination), graphql_name='paginationAccountType', args=sgqlc.types.ArgDict((
        ('direction', sgqlc.types.Arg(SortDirection, graphql_name='direction', default='descending')),
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(AccountTypeFilterSettings), graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('sort_field', sgqlc.types.Arg(DocumentTypeSorting, graphql_name='sortField', default='id')),
))
    )
    pagination_composite_concept_property_type = sgqlc.types.Field(sgqlc.types.non_null(ConceptPropertyTypePagination), graphql_name='paginationCompositeConceptPropertyType', args=sgqlc.types.ArgDict((
        ('direction', sgqlc.types.Arg(SortDirection, graphql_name='direction', default='descending')),
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(CompositePropertyTypeFilterSettings), graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('sort_field', sgqlc.types.Arg(CompositePropertyTypeSorting, graphql_name='sortField', default='name')),
))
    )
    pagination_composite_link_property_type = sgqlc.types.Field(sgqlc.types.non_null(ConceptPropertyTypePagination), graphql_name='paginationCompositeLinkPropertyType', args=sgqlc.types.ArgDict((
        ('direction', sgqlc.types.Arg(SortDirection, graphql_name='direction', default='descending')),
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(CompositePropertyTypeFilterSettings), graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('sort_field', sgqlc.types.Arg(CompositePropertyTypeSorting, graphql_name='sortField', default='name')),
))
    )
    pagination_composite_property_value_template = sgqlc.types.Field(sgqlc.types.non_null(CompositePropertyValueTemplatePagination), graphql_name='paginationCompositePropertyValueTemplate', args=sgqlc.types.ArgDict((
        ('direction', sgqlc.types.Arg(SortDirection, graphql_name='direction', default='descending')),
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(CompositePropertyValueTemplateFilterSettings), graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('sort_field', sgqlc.types.Arg(CompositePropertyValueTemplateSorting, graphql_name='sortField', default='id')),
))
    )
    pagination_concept = sgqlc.types.Field(ConceptPagination, graphql_name='paginationConcept', args=sgqlc.types.ArgDict((
        ('direction', sgqlc.types.Arg(SortDirection, graphql_name='direction', default='descending')),
        ('filter_settings', sgqlc.types.Arg(ConceptFilterSettings, graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('sort_field', sgqlc.types.Arg(ConceptSorting, graphql_name='sortField', default='score')),
))
    )
    pagination_concept_duplicate = sgqlc.types.Field(sgqlc.types.non_null(ConceptDuplicatePagination), graphql_name='paginationConceptDuplicate', args=sgqlc.types.ArgDict((
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(ConceptDuplicateFilterSettings), graphql_name='filterSettings', default=None)),
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
    pagination_concept_duplicate_report = sgqlc.types.Field(sgqlc.types.non_null(ConceptDuplicateReportPagination), graphql_name='paginationConceptDuplicateReport', args=sgqlc.types.ArgDict((
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(ConceptDuplicateReportFilterSettings), graphql_name='filterSettings', default=None)),
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
    pagination_concept_link_property_type = sgqlc.types.Field(sgqlc.types.non_null(ConceptPropertyTypePagination), graphql_name='paginationConceptLinkPropertyType', args=sgqlc.types.ArgDict((
        ('direction', sgqlc.types.Arg(SortDirection, graphql_name='direction', default='descending')),
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(ConceptPropertyTypeFilterSettings), graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('sort_field', sgqlc.types.Arg(ConceptPropertyTypeSorting, graphql_name='sortField', default='name')),
))
    )
    pagination_concept_link_type = sgqlc.types.Field(sgqlc.types.non_null(ConceptLinkTypePagination), graphql_name='paginationConceptLinkType', args=sgqlc.types.ArgDict((
        ('direction', sgqlc.types.Arg(SortDirection, graphql_name='direction', default='descending')),
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(ConceptLinkTypeFilterSettings), graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('sort_field', sgqlc.types.Arg(ConceptLinkTypeSorting, graphql_name='sortField', default='id')),
))
    )
    pagination_concept_presentation = sgqlc.types.Field(sgqlc.types.non_null(ConceptPresentationPagination), graphql_name='paginationConceptPresentation', args=sgqlc.types.ArgDict((
        ('direction', sgqlc.types.Arg(SortDirection, graphql_name='direction', default='descending')),
        ('filter_settings', sgqlc.types.Arg(ConceptPresentationFilterSettings, graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('sort_field', sgqlc.types.Arg(ConceptSorting, graphql_name='sortField', default='score')),
))
    )
    pagination_concept_property_type = sgqlc.types.Field(sgqlc.types.non_null(ConceptPropertyTypePagination), graphql_name='paginationConceptPropertyType', args=sgqlc.types.ArgDict((
        ('direction', sgqlc.types.Arg(SortDirection, graphql_name='direction', default='descending')),
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(ConceptPropertyTypeFilterSettings), graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('sort_field', sgqlc.types.Arg(ConceptPropertyTypeSorting, graphql_name='sortField', default='name')),
))
    )
    pagination_concept_property_value_type = sgqlc.types.Field(sgqlc.types.non_null(ConceptPropertyValueTypePagination), graphql_name='paginationConceptPropertyValueType', args=sgqlc.types.ArgDict((
        ('direction', sgqlc.types.Arg(SortDirection, graphql_name='direction', default='descending')),
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(ConceptPropertyValueTypeFilterSettings), graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('sort_field', sgqlc.types.Arg(ConceptPropertyValueTypeSorting, graphql_name='sortField', default='id')),
))
    )
    pagination_concept_related_document = sgqlc.types.Field(DocumentPagination, graphql_name='paginationConceptRelatedDocument', args=sgqlc.types.ArgDict((
        ('direction', sgqlc.types.Arg(SortDirection, graphql_name='direction', default='descending')),
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(RelatedDocumentFilterSettings), graphql_name='filterSettings', default=None)),
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('sort_field', sgqlc.types.Arg(RelatedDocumentSorting, graphql_name='sortField', default='registrationDate')),
))
    )
    pagination_concept_type = sgqlc.types.Field(sgqlc.types.non_null(ConceptTypePagination), graphql_name='paginationConceptType', args=sgqlc.types.ArgDict((
        ('direction', sgqlc.types.Arg(SortDirection, graphql_name='direction', default='descending')),
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(ConceptTypeFilterSettings), graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('sort_field', sgqlc.types.Arg(ConceptTypeSorting, graphql_name='sortField', default='id')),
))
    )
    pagination_concept_type_presentation = sgqlc.types.Field(sgqlc.types.non_null(ConceptTypePresentationPagination), graphql_name='paginationConceptTypePresentation', args=sgqlc.types.ArgDict((
        ('direction', sgqlc.types.Arg(SortDirection, graphql_name='direction', default='descending')),
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(ConceptTypePresentationFilterSettings), graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('sort_field', sgqlc.types.Arg(ConceptTypePresentationSorting, graphql_name='sortField', default='id')),
))
    )
    pagination_country = sgqlc.types.Field(sgqlc.types.non_null(CountryPagination), graphql_name='paginationCountry', args=sgqlc.types.ArgDict((
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(CountryFilterSettings), graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
))
    )
    pagination_document_duplicate_report = sgqlc.types.Field(sgqlc.types.non_null(DocumentDuplicateReportPagination), graphql_name='paginationDocumentDuplicateReport', args=sgqlc.types.ArgDict((
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(DocumentDuplicateReportFilterSettings), graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
))
    )
    pagination_document_duplicate_task = sgqlc.types.Field(sgqlc.types.non_null(DocumentDuplicateTaskPagination), graphql_name='paginationDocumentDuplicateTask', args=sgqlc.types.ArgDict((
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(DocumentDuplicateTaskFilterSettings), graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
))
    )
    pagination_document_feed = sgqlc.types.Field(sgqlc.types.non_null(DocumentFeedPagination), graphql_name='paginationDocumentFeed', args=sgqlc.types.ArgDict((
        ('direction', sgqlc.types.Arg(SortDirection, graphql_name='direction', default='descending')),
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(DocumentFeedFilterSettings), graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('sort_field', sgqlc.types.Arg(DocumentFeedSorting, graphql_name='sortField', default='id')),
))
    )
    pagination_document_markers = sgqlc.types.Field(sgqlc.types.non_null(CommonStringPagination), graphql_name='paginationDocumentMarkers', args=sgqlc.types.ArgDict((
        ('direction', sgqlc.types.Arg(SortDirection, graphql_name='direction', default='descending')),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
))
    )
    pagination_document_rubric = sgqlc.types.Field(sgqlc.types.non_null(DocumentRubricPagination), graphql_name='paginationDocumentRubric', args=sgqlc.types.ArgDict((
        ('direction', sgqlc.types.Arg(SortDirection, graphql_name='direction', default='descending')),
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(DocumentRubricFilterSettings), graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('sort_field', sgqlc.types.Arg(DocumentRubricSorting, graphql_name='sortField', default='id')),
))
    )
    pagination_document_type = sgqlc.types.Field(sgqlc.types.non_null(DocumentTypePagination), graphql_name='paginationDocumentType', args=sgqlc.types.ArgDict((
        ('direction', sgqlc.types.Arg(SortDirection, graphql_name='direction', default='descending')),
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(DocumentTypeFilterSettings), graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('sort_field', sgqlc.types.Arg(DocumentTypeSorting, graphql_name='sortField', default='id')),
))
    )
    pagination_document_type_presentation = sgqlc.types.Field(sgqlc.types.non_null(DocumentTypePresentationPagination), graphql_name='paginationDocumentTypePresentation', args=sgqlc.types.ArgDict((
        ('direction', sgqlc.types.Arg(SortDirection, graphql_name='direction', default='descending')),
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(DocumentTypePresentationFilterSettings), graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('sort_field', sgqlc.types.Arg(DocumentTypePresentationSorting, graphql_name='sortField', default='id')),
))
    )
    pagination_language = sgqlc.types.Field(sgqlc.types.non_null(LanguagePagination), graphql_name='paginationLanguage', args=sgqlc.types.ArgDict((
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(LanguageFilterSettings), graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
))
    )
    pagination_link_property_related_document = sgqlc.types.Field(DocumentPagination, graphql_name='paginationLinkPropertyRelatedDocument', args=sgqlc.types.ArgDict((
        ('direction', sgqlc.types.Arg(SortDirection, graphql_name='direction', default='descending')),
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(RelatedDocumentFilterSettings), graphql_name='filterSettings', default=None)),
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('sort_field', sgqlc.types.Arg(RelatedDocumentSorting, graphql_name='sortField', default='registrationDate')),
))
    )
    pagination_link_related_document = sgqlc.types.Field(DocumentPagination, graphql_name='paginationLinkRelatedDocument', args=sgqlc.types.ArgDict((
        ('direction', sgqlc.types.Arg(SortDirection, graphql_name='direction', default='descending')),
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(RelatedDocumentFilterSettings), graphql_name='filterSettings', default=None)),
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('sort_field', sgqlc.types.Arg(RelatedDocumentSorting, graphql_name='sortField', default='registrationDate')),
))
    )
    pagination_platform = sgqlc.types.Field(sgqlc.types.non_null(PlatformPagination), graphql_name='paginationPlatform', args=sgqlc.types.ArgDict((
        ('direction', sgqlc.types.Arg(SortDirection, graphql_name='direction', default='descending')),
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(PlatformFilterSettings), graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('sort_field', sgqlc.types.Arg(PlatformSorting, graphql_name='sortField', default='id')),
))
    )
    pagination_platform_type = sgqlc.types.Field(sgqlc.types.non_null(PlatformTypePagination), graphql_name='paginationPlatformType', args=sgqlc.types.ArgDict((
        ('direction', sgqlc.types.Arg(SortDirection, graphql_name='direction', default='descending')),
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(PlatformTypeFilterSettings), graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('sort_field', sgqlc.types.Arg(DocumentTypeSorting, graphql_name='sortField', default='id')),
))
    )
    pagination_property_related_document = sgqlc.types.Field(DocumentPagination, graphql_name='paginationPropertyRelatedDocument', args=sgqlc.types.ArgDict((
        ('direction', sgqlc.types.Arg(SortDirection, graphql_name='direction', default='descending')),
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(RelatedDocumentFilterSettings), graphql_name='filterSettings', default=None)),
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('sort_field', sgqlc.types.Arg(RelatedDocumentSorting, graphql_name='sortField', default='registrationDate')),
))
    )
    pagination_property_type = sgqlc.types.Field(sgqlc.types.non_null(ConceptPropertyTypePagination), graphql_name='paginationPropertyType', args=sgqlc.types.ArgDict((
        ('direction', sgqlc.types.Arg(SortDirection, graphql_name='direction', default='descending')),
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(ConceptPropertyTypeFilterSettings), graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('sort_field', sgqlc.types.Arg(ConceptPropertyTypeSorting, graphql_name='sortField', default='name')),
))
    )
    pagination_research_map = sgqlc.types.Field(sgqlc.types.non_null('ResearchMapPagination'), graphql_name='paginationResearchMap', args=sgqlc.types.ArgDict((
        ('direction', sgqlc.types.Arg(SortDirection, graphql_name='direction', default='descending')),
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(ResearchMapFilterSettings), graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('sort_field', sgqlc.types.Arg(ResearchMapSorting, graphql_name='sortField', default='id')),
))
    )
    pagination_rubric = sgqlc.types.Field(sgqlc.types.non_null('RubricPagination'), graphql_name='paginationRubric', args=sgqlc.types.ArgDict((
        ('direction', sgqlc.types.Arg(SortDirection, graphql_name='direction', default='descending')),
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(RubricFilterSettings), graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('sort_field', sgqlc.types.Arg(RubricSorting, graphql_name='sortField', default='id')),
))
    )
    pagination_rubricator = sgqlc.types.Field(sgqlc.types.non_null('RubricatorPagination'), graphql_name='paginationRubricator', args=sgqlc.types.ArgDict((
        ('direction', sgqlc.types.Arg(SortDirection, graphql_name='direction', default='descending')),
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(RubricatorFilterSettings), graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('sort_field', sgqlc.types.Arg(RubricatorSorting, graphql_name='sortField', default='id')),
))
    )
    pagination_story = sgqlc.types.Field(sgqlc.types.non_null('StoryPagination'), graphql_name='paginationStory', args=sgqlc.types.ArgDict((
        ('direction', sgqlc.types.Arg(SortDirection, graphql_name='direction', default='descending')),
        ('extra_settings', sgqlc.types.Arg(sgqlc.types.non_null(ExtraSettings), graphql_name='extraSettings', default=None)),
        ('filter_settings', sgqlc.types.Arg(DocumentFilterSettings, graphql_name='filterSettings', default=None)),
        ('grouping', sgqlc.types.Arg(DocumentGrouping, graphql_name='grouping', default='none')),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('relevance', sgqlc.types.Arg(DocumentRelevanceMetricsInput, graphql_name='relevance', default=None)),
        ('sort_field', sgqlc.types.Arg(DocumentSorting, graphql_name='sortField', default='score')),
))
    )
    pagination_story_type = sgqlc.types.Field(sgqlc.types.non_null('StoryTypePagination'), graphql_name='paginationStoryType', args=sgqlc.types.ArgDict((
        ('direction', sgqlc.types.Arg(SortDirection, graphql_name='direction', default='descending')),
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(StoryTypeFilterSettings), graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('sort_field', sgqlc.types.Arg(StoryTypeSorting, graphql_name='sortField', default='id')),
))
    )
    platform = sgqlc.types.Field(sgqlc.types.non_null('Platform'), graphql_name='platform', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    platform_type = sgqlc.types.Field(sgqlc.types.non_null('PlatformType'), graphql_name='platformType', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    research_map = sgqlc.types.Field(sgqlc.types.non_null('ResearchMap'), graphql_name='researchMap', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    rubric = sgqlc.types.Field(sgqlc.types.non_null('Rubric'), graphql_name='rubric', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    rubric_by_transformator_id = sgqlc.types.Field('Rubric', graphql_name='rubricByTransformatorId', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    rubrication_facets = sgqlc.types.Field(sgqlc.types.non_null('RubricationFacets'), graphql_name='rubricationFacets', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    rubricator = sgqlc.types.Field(sgqlc.types.non_null('Rubricator'), graphql_name='rubricator', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    story = sgqlc.types.Field('Story', graphql_name='story', args=sgqlc.types.ArgDict((
        ('ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='ids', default=None)),
))
    )
    story_fs2_query = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='storyFs2Query', args=sgqlc.types.ArgDict((
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(DocumentFilterSettings), graphql_name='filterSettings', default=None)),
))
    )
    story_type = sgqlc.types.Field(sgqlc.types.non_null('StoryType'), graphql_name='storyType', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )


class RelExtModel(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('invert_direction', 'relation_type', 'source_annotation_type', 'target_annotation_type')
    invert_direction = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='invertDirection')
    relation_type = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='relationType')
    source_annotation_type = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='sourceAnnotationType')
    target_annotation_type = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='targetAnnotationType')


class ResearchMapFromFilesType(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('info', 'research_maps')
    info = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of('State')), graphql_name='info')
    research_maps = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ResearchMap'))), graphql_name='researchMaps')


class ResearchMapPagination(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('list_research_map', 'total')
    list_research_map = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ResearchMap'))), graphql_name='listResearchMap')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class ResearchMapStatistics(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('concept_and_document_num', 'concept_num', 'document_num', 'event_num', 'object_num')
    concept_and_document_num = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='conceptAndDocumentNum')
    concept_num = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='conceptNum')
    document_num = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='documentNum')
    event_num = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='eventNum')
    object_num = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='objectNum')


class RubricFacet(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('list_child_rubric_facet', 'own_documents_count', 'rubric', 'subtree_documents_count')
    list_child_rubric_facet = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('RubricFacet'))), graphql_name='listChildRubricFacet')
    own_documents_count = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='ownDocumentsCount')
    rubric = sgqlc.types.Field(sgqlc.types.non_null('Rubric'), graphql_name='rubric')
    subtree_documents_count = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='subtreeDocumentsCount')


class RubricPagination(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('list_rubric', 'total')
    list_rubric = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('Rubric'))), graphql_name='listRubric')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class RubricationFacets(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('calculated_at', 'id', 'list_rubricator_facet')
    calculated_at = sgqlc.types.Field(UnixTime, graphql_name='calculatedAt')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    list_rubricator_facet = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('RubricatorFacet')), graphql_name='listRubricatorFacet')


class RubricatorFacet(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('list_rubric_facet', 'rubricator')
    list_rubric_facet = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(RubricFacet))), graphql_name='listRubricFacet')
    rubricator = sgqlc.types.Field(sgqlc.types.non_null('Rubricator'), graphql_name='rubricator')


class RubricatorPagination(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('list_rubricator', 'total')
    list_rubricator = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('Rubricator'))), graphql_name='listRubricator')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class S3File(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('bucket_name', 'object_name')
    bucket_name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='bucketName')
    object_name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='objectName')


class Score(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('name', 'score')
    name = sgqlc.types.Field(sgqlc.types.non_null(Name), graphql_name='name')
    score = sgqlc.types.Field(Float, graphql_name='score')


class ShortestPath(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('path',)
    path = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ShortestPathEdge'))), graphql_name='path')


class ShortestPathEdge(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('link_id', 'node_id')
    link_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='linkId')
    node_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='nodeId')


class State(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('is_success',)
    is_success = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isSuccess')


class StateWithCount(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('count', 'state')
    count = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='count')
    state = sgqlc.types.Field(sgqlc.types.non_null(State), graphql_name='state')


class StateWithErrors(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('info', 'state')
    info = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(State)), graphql_name='info')
    state = sgqlc.types.Field(sgqlc.types.non_null(State), graphql_name='state')


class Story(sgqlc.types.Type):
    __schema__ = api_schema
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
    __schema__ = api_schema
    __field_names__ = ('document_facets', 'list_story', 'precise_total', 'rubrication_facets', 'show_total', 'total')
    document_facets = sgqlc.types.Field(sgqlc.types.non_null(DocumentFacets), graphql_name='documentFacets')
    list_story = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(Story))), graphql_name='listStory')
    precise_total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='preciseTotal')
    rubrication_facets = sgqlc.types.Field(sgqlc.types.non_null(RubricationFacets), graphql_name='rubricationFacets')
    show_total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='showTotal')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class StoryTypePagination(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('list_story_type', 'total')
    list_story_type = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('StoryType'))), graphql_name='listStoryType')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class StringLocaleValue(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('locale', 'value')
    locale = sgqlc.types.Field(sgqlc.types.non_null(Locale), graphql_name='locale')
    value = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='value')


class StringValue(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('value',)
    value = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='value')


class Subscription(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('domain_map_changed', 'research_map_changed')
    domain_map_changed = sgqlc.types.Field(sgqlc.types.non_null(MapEvents), graphql_name='domainMapChanged')
    research_map_changed = sgqlc.types.Field(sgqlc.types.non_null(MapEvents), graphql_name='researchMapChanged', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )


class Time(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('hour', 'minute', 'second')
    hour = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='hour')
    minute = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='minute')
    second = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='second')


class TimestampValue(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('value',)
    value = sgqlc.types.Field(sgqlc.types.non_null(UnixTime), graphql_name='value')


class Translation(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('language', 'text')
    language = sgqlc.types.Field(sgqlc.types.non_null(Language), graphql_name='language')
    text = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='text')


class UpsertDrawing(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('drawing',)
    drawing = sgqlc.types.Field(sgqlc.types.non_null(MapDrawing), graphql_name='drawing')


class UpsertEdge(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('edge',)
    edge = sgqlc.types.Field(sgqlc.types.non_null(MapEdge), graphql_name='edge')


class UpsertGroup(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('group',)
    group = sgqlc.types.Field(sgqlc.types.non_null(Group), graphql_name='group')


class UpsertNode(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('node',)
    node = sgqlc.types.Field(sgqlc.types.non_null(MapNode), graphql_name='node')


class User(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('id',)
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')


class ValueWithConfidence(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ('confidence', 'value')
    confidence = sgqlc.types.Field(Float, graphql_name='confidence')
    value = sgqlc.types.Field(sgqlc.types.non_null('Value'), graphql_name='value')


class Account(sgqlc.types.Type, KBEntity, LinkTarget, PropertyTarget, RecordInterface):
    __schema__ = api_schema
    __field_names__ = ('access_level', 'account_type', 'avatar_document', 'country', 'end_date', 'image', 'is_actual', 'key', 'language', 'links_with_concepts_and_documents', 'links_with_concepts_and_documents_on_research_map', 'list_alias', 'list_concept_candidate_fact', 'list_concept_fact', 'list_header_concept_property', 'list_subscription', 'markers', 'metric', 'name', 'notes', 'pagination_alias', 'pagination_concept_duplicate_group', 'pagination_concept_fact', 'pagination_concept_link', 'pagination_concept_link_documents', 'pagination_concept_property', 'pagination_concept_property_documents', 'pagination_merged_concept', 'pagination_research_map', 'period', 'platform', 'start_date', 'status', 'url')
    access_level = sgqlc.types.Field(sgqlc.types.non_null(AccessLevel), graphql_name='accessLevel')
    account_type = sgqlc.types.Field(sgqlc.types.non_null('AccountType'), graphql_name='accountType')
    avatar_document = sgqlc.types.Field('Document', graphql_name='avatarDocument')
    country = sgqlc.types.Field(String, graphql_name='country')
    end_date = sgqlc.types.Field(DateTimeValue, graphql_name='endDate')
    image = sgqlc.types.Field(Image, graphql_name='image')
    is_actual = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isActual')
    key = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='key')
    language = sgqlc.types.Field(String, graphql_name='language')
    links_with_concepts_and_documents = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='linksWithConceptsAndDocuments')
    links_with_concepts_and_documents_on_research_map = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='linksWithConceptsAndDocumentsOnResearchMap')
    list_alias = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ConceptProperty'))), graphql_name='listAlias')
    list_concept_candidate_fact = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ConceptCandidateFact'))), graphql_name='listConceptCandidateFact')
    list_concept_fact = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ConceptFact'))), graphql_name='listConceptFact')
    list_header_concept_property = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ConceptProperty'))), graphql_name='listHeaderConceptProperty')
    list_subscription = sgqlc.types.Field(sgqlc.types.non_null(ConceptSubscriptions), graphql_name='listSubscription')
    markers = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))), graphql_name='markers')
    metric = sgqlc.types.Field(AccountStatistics, graphql_name='metric')
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
    period = sgqlc.types.Field(DateTimeInterval, graphql_name='period')
    platform = sgqlc.types.Field(sgqlc.types.non_null('Platform'), graphql_name='platform')
    start_date = sgqlc.types.Field(DateTimeValue, graphql_name='startDate')
    status = sgqlc.types.Field(sgqlc.types.non_null(KbFactStatus), graphql_name='status')
    url = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='url')


class AccountType(sgqlc.types.Type, EntityType, HasTypeSearchElements, LinkTypeTarget, PropertyTypeTarget, RecordInterface):
    __schema__ = api_schema
    __field_names__ = ('description',)
    description = sgqlc.types.Field(String, graphql_name='description')


class AudioNodeMention(sgqlc.types.Type, MentionInterface, RecordInterface):
    __schema__ = api_schema
    __field_names__ = ('end', 'node_id', 'start')
    end = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='end')
    node_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='nodeId')
    start = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='start')


class CompositePropertyValueCandidateFact(sgqlc.types.Type, FactInterface):
    __schema__ = api_schema
    __field_names__ = ('fact_from', 'property_value_type', 'value_slot_fact')
    fact_from = sgqlc.types.Field('AnyCompositePropertyFact', graphql_name='factFrom')
    property_value_type = sgqlc.types.Field(sgqlc.types.non_null('CompositePropertyValueTemplate'), graphql_name='propertyValueType')
    value_slot_fact = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('CompositePropertyValueComponentCandidateFact'))), graphql_name='valueSlotFact')


class CompositePropertyValueComponentCandidateFact(sgqlc.types.Type, FactInterface):
    __schema__ = api_schema
    __field_names__ = ('component_value_type', 'fact_from', 'fact_to')
    component_value_type = sgqlc.types.Field(sgqlc.types.non_null(CompositePropertyValueType), graphql_name='componentValueType')
    fact_from = sgqlc.types.Field(sgqlc.types.non_null(CompositePropertyValueCandidateFact), graphql_name='factFrom')
    fact_to = sgqlc.types.Field(sgqlc.types.non_null('ConceptPropertyValueCandidateFact'), graphql_name='factTo')


class CompositePropertyValueTemplate(sgqlc.types.Type, RecordInterface):
    __schema__ = api_schema
    __field_names__ = ('component_value_types', 'id', 'name')
    component_value_types = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(CompositePropertyValueType))), graphql_name='componentValueTypes')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')


class Concept(sgqlc.types.Type, KBEntity, LinkTarget, PropertyTarget, RecordInterface):
    __schema__ = api_schema
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
    __schema__ = api_schema
    __field_names__ = ('concept_type', 'list_concept', 'name')
    concept_type = sgqlc.types.Field(sgqlc.types.non_null('ConceptType'), graphql_name='conceptType')
    list_concept = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ConceptWithConfidence))), graphql_name='listConcept')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')


class ConceptCompositePropertyCandidateFact(sgqlc.types.Type, FactInterface):
    __schema__ = api_schema
    __field_names__ = ('concept_property_type', 'fact_from', 'fact_to')
    concept_property_type = sgqlc.types.Field(sgqlc.types.non_null('ConceptPropertyType'), graphql_name='conceptPropertyType')
    fact_from = sgqlc.types.Field('ConceptLikeFact', graphql_name='factFrom')
    fact_to = sgqlc.types.Field(sgqlc.types.non_null(CompositePropertyValueCandidateFact), graphql_name='factTo')


class ConceptDuplicateReport(sgqlc.types.Type, RecordInterface):
    __schema__ = api_schema
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
    __schema__ = api_schema
    __field_names__ = ('access_level', 'concept')
    access_level = sgqlc.types.Field(sgqlc.types.non_null(AccessLevel), graphql_name='accessLevel')
    concept = sgqlc.types.Field(sgqlc.types.non_null(Concept), graphql_name='concept')


class ConceptGroupFacet(sgqlc.types.Type, DocumentGroupFacet):
    __schema__ = api_schema
    __field_names__ = ('concept',)
    concept = sgqlc.types.Field(sgqlc.types.non_null(Concept), graphql_name='concept')


class ConceptLink(sgqlc.types.Type, PropertyTarget, RecordInterface):
    __schema__ = api_schema
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
    __schema__ = api_schema
    __field_names__ = ('concept_link_type', 'fact_from', 'fact_to')
    concept_link_type = sgqlc.types.Field(sgqlc.types.non_null('ConceptLinkType'), graphql_name='conceptLinkType')
    fact_from = sgqlc.types.Field('ConceptLikeFact', graphql_name='factFrom')
    fact_to = sgqlc.types.Field('ConceptLikeFact', graphql_name='factTo')


class ConceptLinkCompositePropertyCandidateFact(sgqlc.types.Type, FactInterface):
    __schema__ = api_schema
    __field_names__ = ('concept_link_property_type', 'fact_from', 'fact_to')
    concept_link_property_type = sgqlc.types.Field(sgqlc.types.non_null('ConceptPropertyType'), graphql_name='conceptLinkPropertyType')
    fact_from = sgqlc.types.Field('ConceptLinkLikeFact', graphql_name='factFrom')
    fact_to = sgqlc.types.Field(sgqlc.types.non_null(CompositePropertyValueCandidateFact), graphql_name='factTo')


class ConceptLinkFact(sgqlc.types.Type, FactInterface, RecordInterface):
    __schema__ = api_schema
    __field_names__ = ('access_level', 'concept_link')
    access_level = sgqlc.types.Field(sgqlc.types.non_null(AccessLevel), graphql_name='accessLevel')
    concept_link = sgqlc.types.Field(sgqlc.types.non_null(ConceptLink), graphql_name='conceptLink')


class ConceptLinkPropertyCandidateFact(sgqlc.types.Type, FactInterface):
    __schema__ = api_schema
    __field_names__ = ('concept_link_property_type', 'fact_from', 'fact_to')
    concept_link_property_type = sgqlc.types.Field(sgqlc.types.non_null('ConceptPropertyType'), graphql_name='conceptLinkPropertyType')
    fact_from = sgqlc.types.Field('ConceptLinkLikeFact', graphql_name='factFrom')
    fact_to = sgqlc.types.Field(sgqlc.types.non_null('ConceptPropertyValueCandidateFact'), graphql_name='factTo')


class ConceptLinkPropertyFact(sgqlc.types.Type, FactInterface, RecordInterface):
    __schema__ = api_schema
    __field_names__ = ('access_level', 'concept_link_property', 'fact_from', 'mention', 'parent_concept_link')
    access_level = sgqlc.types.Field(sgqlc.types.non_null(AccessLevel), graphql_name='accessLevel')
    concept_link_property = sgqlc.types.Field(sgqlc.types.non_null('ConceptProperty'), graphql_name='conceptLinkProperty')
    fact_from = sgqlc.types.Field('ConceptLinkLikeFact', graphql_name='factFrom')
    mention = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('MentionUnion'))), graphql_name='mention')
    parent_concept_link = sgqlc.types.Field(sgqlc.types.non_null(ConceptLink), graphql_name='parentConceptLink')


class ConceptLinkType(sgqlc.types.Type, PropertyTypeTarget, RecordInterface):
    __schema__ = api_schema
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
    __schema__ = api_schema
    __field_names__ = ('concept_link_type',)
    concept_link_type = sgqlc.types.Field(sgqlc.types.non_null(ConceptLinkType), graphql_name='conceptLinkType')


class ConceptProperty(sgqlc.types.Type, RecordInterface):
    __schema__ = api_schema
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
    __schema__ = api_schema
    __field_names__ = ('concept_property_type', 'fact_from', 'fact_to')
    concept_property_type = sgqlc.types.Field(sgqlc.types.non_null('ConceptPropertyType'), graphql_name='conceptPropertyType')
    fact_from = sgqlc.types.Field('ConceptLikeFact', graphql_name='factFrom')
    fact_to = sgqlc.types.Field(sgqlc.types.non_null('ConceptPropertyValueCandidateFact'), graphql_name='factTo')


class ConceptPropertyFact(sgqlc.types.Type, FactInterface, RecordInterface):
    __schema__ = api_schema
    __field_names__ = ('access_level', 'concept_property', 'fact_from', 'mention', 'parent_concept')
    access_level = sgqlc.types.Field(sgqlc.types.non_null(AccessLevel), graphql_name='accessLevel')
    concept_property = sgqlc.types.Field(sgqlc.types.non_null(ConceptProperty), graphql_name='conceptProperty')
    fact_from = sgqlc.types.Field('ConceptLikeFact', graphql_name='factFrom')
    mention = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('MentionUnion'))), graphql_name='mention')
    parent_concept = sgqlc.types.Field(sgqlc.types.non_null(Concept), graphql_name='parentConcept')


class ConceptPropertyType(sgqlc.types.Type, RecordInterface):
    __schema__ = api_schema
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
    __schema__ = api_schema
    __field_names__ = ('concept_property_type',)
    concept_property_type = sgqlc.types.Field(sgqlc.types.non_null(ConceptPropertyType), graphql_name='conceptPropertyType')


class ConceptPropertyValueCandidateFact(sgqlc.types.Type, FactInterface):
    __schema__ = api_schema
    __field_names__ = ('concept_property_value_type', 'fact_from', 'meanings')
    concept_property_value_type = sgqlc.types.Field(sgqlc.types.non_null('ConceptPropertyValueType'), graphql_name='conceptPropertyValueType')
    fact_from = sgqlc.types.Field('AnyPropertyOrValueComponentFact', graphql_name='factFrom')
    meanings = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ValueWithConfidence))), graphql_name='meanings')


class ConceptPropertyValueGroupFacet(sgqlc.types.Type, DocumentGroupFacet):
    __schema__ = api_schema
    __field_names__ = ('concept_property_type', 'concept_property_value')
    concept_property_type = sgqlc.types.Field(sgqlc.types.non_null(ConceptPropertyType), graphql_name='conceptPropertyType')
    concept_property_value = sgqlc.types.Field(sgqlc.types.non_null('AnyValue'), graphql_name='conceptPropertyValue')


class ConceptPropertyValueType(sgqlc.types.Type, HasTypeSearchElements, RecordInterface):
    __schema__ = api_schema
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
    __schema__ = api_schema
    __field_names__ = ('is_event', 'list_concept_type_presentation', 'pagination_concept_type_view', 'use_for_auto_rubricator')
    is_event = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isEvent')
    list_concept_type_presentation = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ConceptTypePresentation'))), graphql_name='listConceptTypePresentation', args=sgqlc.types.ArgDict((
        ('is_for_user', sgqlc.types.Arg(Boolean, graphql_name='isForUser', default=False)),
))
    )
    pagination_concept_type_view = sgqlc.types.Field(sgqlc.types.non_null(ConceptTypeViewPagination), graphql_name='paginationConceptTypeView', args=sgqlc.types.ArgDict((
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
))
    )
    use_for_auto_rubricator = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='useForAutoRubricator')


class ConceptTypeGroupFacet(sgqlc.types.Type, DocumentGroupFacet):
    __schema__ = api_schema
    __field_names__ = ('concept_type',)
    concept_type = sgqlc.types.Field(sgqlc.types.non_null(ConceptType), graphql_name='conceptType')


class ConceptTypePresentation(sgqlc.types.Type, EntityTypePresentation, RecordInterface):
    __schema__ = api_schema
    __field_names__ = ('has_header_information', 'has_supporting_documents', 'hide_empty_rows', 'id', 'internal_url', 'layout', 'list_widget_type', 'name', 'pagination_widget_type', 'root_concept_type', 'root_type')
    has_header_information = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='hasHeaderInformation')
    has_supporting_documents = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='hasSupportingDocuments')
    hide_empty_rows = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='hideEmptyRows')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    internal_url = sgqlc.types.Field(String, graphql_name='internalUrl')
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
    __schema__ = api_schema
    __field_names__ = ('columns_info', 'concept_type_presentation', 'hierarchy', 'id', 'name', 'table_type')
    columns_info = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ConceptTypePresentationWidgetTypeColumn))), graphql_name='columnsInfo')
    concept_type_presentation = sgqlc.types.Field(sgqlc.types.non_null(ConceptTypePresentation), graphql_name='conceptTypePresentation')
    hierarchy = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ConceptLinkTypePath))))), graphql_name='hierarchy')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    table_type = sgqlc.types.Field(sgqlc.types.non_null(WidgetTypeTableType), graphql_name='tableType')


class ConceptTypeView(sgqlc.types.Type, RecordInterface):
    __schema__ = api_schema
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
    __schema__ = api_schema
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
    __schema__ = api_schema
    __field_names__ = ('account',)
    account = sgqlc.types.Field(sgqlc.types.non_null(Account), graphql_name='account')


class DocumentDuplicateReport(sgqlc.types.Type, RecordInterface):
    __schema__ = api_schema
    __field_names__ = ('auto_delete', 'error_message', 'fields', 'id', 'ignore_markup', 'metrics', 'search_query', 'status')
    auto_delete = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='autoDelete')
    error_message = sgqlc.types.Field(String, graphql_name='errorMessage')
    fields = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(DocumentDuplicateComparisonField))), graphql_name='fields')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    ignore_markup = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='ignoreMarkup')
    metrics = sgqlc.types.Field(DocumentDuplicateReportMetrics, graphql_name='metrics')
    search_query = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='searchQuery')
    status = sgqlc.types.Field(sgqlc.types.non_null(DocumentDuplicateReportStatus), graphql_name='status')


class DocumentFeed(sgqlc.types.Type, RecordInterface):
    __schema__ = api_schema
    __field_names__ = ('id', 'is_refresh_locked', 'list_subscription', 'name', 'pagination_document', 'search_string')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    is_refresh_locked = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isRefreshLocked')
    list_subscription = sgqlc.types.Field(sgqlc.types.non_null(DocumentFeedSubscriptions), graphql_name='listSubscription')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    pagination_document = sgqlc.types.Field(sgqlc.types.non_null(DocumentFromDocumentFeedPagination), graphql_name='paginationDocument', args=sgqlc.types.ArgDict((
        ('added_to_feed_date', sgqlc.types.Arg(TimestampIntervalInput, graphql_name='addedToFeedDate', default=None)),
        ('direction', sgqlc.types.Arg(SortDirection, graphql_name='direction', default='descending')),
        ('filter_search_string', sgqlc.types.Arg(String, graphql_name='filterSearchString', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('mode', sgqlc.types.Arg(DocumentFeedMode, graphql_name='mode', default='all')),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('sort_field', sgqlc.types.Arg(DocumentInFeedSorting, graphql_name='sortField', default='addedToFeedDate')),
))
    )
    search_string = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='searchString')


class DocumentPlatformGroupFacet(sgqlc.types.Type, DocumentGroupFacet):
    __schema__ = api_schema
    __field_names__ = ('platform',)
    platform = sgqlc.types.Field(sgqlc.types.non_null('Platform'), graphql_name='platform')


class DocumentPlatformTypeGroupFacet(sgqlc.types.Type, DocumentGroupFacet):
    __schema__ = api_schema
    __field_names__ = ('platform_type',)
    platform_type = sgqlc.types.Field(sgqlc.types.non_null('PlatformType'), graphql_name='platformType')


class DocumentPropertyGroupFacet(sgqlc.types.Type, DocumentGroupFacet):
    __schema__ = api_schema
    __field_names__ = ('value',)
    value = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='value')


class DocumentRubric(sgqlc.types.Type, RecordInterface):
    __schema__ = api_schema
    __field_names__ = ('creator_id', 'hierarchy', 'id', 'last_updater_id', 'rubric', 'rubricator', 'status')
    creator_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='creatorId')
    hierarchy = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='hierarchy')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    last_updater_id = sgqlc.types.Field(ID, graphql_name='lastUpdaterId')
    rubric = sgqlc.types.Field(sgqlc.types.non_null('Rubric'), graphql_name='rubric')
    rubricator = sgqlc.types.Field(sgqlc.types.non_null('Rubricator'), graphql_name='rubricator')
    status = sgqlc.types.Field(sgqlc.types.non_null(DocumentRubricStatus), graphql_name='status')


class DocumentType(sgqlc.types.Type, EntityType, HasTypeSearchElements, LinkTypeTarget, PropertyTypeTarget, RecordInterface):
    __schema__ = api_schema
    __field_names__ = ('list_document_type_presentation',)
    list_document_type_presentation = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('DocumentTypePresentation'))), graphql_name='listDocumentTypePresentation')


class DocumentTypePresentation(sgqlc.types.Type, EntityTypePresentation, RecordInterface):
    __schema__ = api_schema
    __field_names__ = ('columns_info', 'hierarchy', 'id', 'name', 'root_document_type', 'root_type')
    columns_info = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ConceptTypePresentationWidgetTypeColumn))), graphql_name='columnsInfo')
    hierarchy = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ConceptLinkTypePath))))), graphql_name='hierarchy')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    root_document_type = sgqlc.types.Field(sgqlc.types.non_null(DocumentType), graphql_name='rootDocumentType')
    root_type = sgqlc.types.Field(sgqlc.types.non_null(EntityType), graphql_name='rootType')


class ImageNodeMention(sgqlc.types.Type, MentionInterface, RecordInterface):
    __schema__ = api_schema
    __field_names__ = ('bottom', 'left', 'node_id', 'right', 'top')
    bottom = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='bottom')
    left = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='left')
    node_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='nodeId')
    right = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='right')
    top = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='top')


class MapAnnotation(sgqlc.types.Type, RecordInterface):
    __schema__ = api_schema
    __field_names__ = ('annotation', 'id')
    annotation = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='annotation')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')


class NodeMention(sgqlc.types.Type, MentionInterface, RecordInterface):
    __schema__ = api_schema
    __field_names__ = ('node_id',)
    node_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='nodeId')


class Platform(sgqlc.types.Type, KBEntity, LinkTarget, PropertyTarget, RecordInterface):
    __schema__ = api_schema
    __field_names__ = ('access_level', 'accounts', 'avatar_document', 'country', 'end_date', 'image', 'is_actual', 'key', 'language', 'links_with_concepts_and_documents', 'links_with_concepts_and_documents_on_research_map', 'list_alias', 'list_concept_candidate_fact', 'list_concept_fact', 'list_header_concept_property', 'list_subscription', 'markers', 'metric', 'name', 'notes', 'pagination_alias', 'pagination_concept_duplicate_group', 'pagination_concept_fact', 'pagination_concept_link', 'pagination_concept_link_documents', 'pagination_concept_property', 'pagination_concept_property_documents', 'pagination_merged_concept', 'pagination_research_map', 'period', 'platform_type', 'start_date', 'status', 'url')
    access_level = sgqlc.types.Field(sgqlc.types.non_null(AccessLevel), graphql_name='accessLevel')
    accounts = sgqlc.types.Field(sgqlc.types.non_null(AccountPagination), graphql_name='accounts', args=sgqlc.types.ArgDict((
        ('direction', sgqlc.types.Arg(SortDirection, graphql_name='direction', default='descending')),
        ('filter_settings', sgqlc.types.Arg(sgqlc.types.non_null(AccountFilterSettings), graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=20)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('sort_field', sgqlc.types.Arg(AccountSorting, graphql_name='sortField', default='id')),
))
    )
    avatar_document = sgqlc.types.Field(Document, graphql_name='avatarDocument')
    country = sgqlc.types.Field(String, graphql_name='country')
    end_date = sgqlc.types.Field(DateTimeValue, graphql_name='endDate')
    image = sgqlc.types.Field(Image, graphql_name='image')
    is_actual = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isActual')
    key = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='key')
    language = sgqlc.types.Field(String, graphql_name='language')
    links_with_concepts_and_documents = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='linksWithConceptsAndDocuments')
    links_with_concepts_and_documents_on_research_map = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='linksWithConceptsAndDocumentsOnResearchMap')
    list_alias = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ConceptProperty))), graphql_name='listAlias')
    list_concept_candidate_fact = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ConceptCandidateFact))), graphql_name='listConceptCandidateFact')
    list_concept_fact = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ConceptFact))), graphql_name='listConceptFact')
    list_header_concept_property = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ConceptProperty))), graphql_name='listHeaderConceptProperty')
    list_subscription = sgqlc.types.Field(sgqlc.types.non_null(ConceptSubscriptions), graphql_name='listSubscription')
    markers = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))), graphql_name='markers')
    metric = sgqlc.types.Field(PlatformStatistics, graphql_name='metric')
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
    period = sgqlc.types.Field(DateTimeInterval, graphql_name='period')
    platform_type = sgqlc.types.Field(sgqlc.types.non_null('PlatformType'), graphql_name='platformType')
    start_date = sgqlc.types.Field(DateTimeValue, graphql_name='startDate')
    status = sgqlc.types.Field(sgqlc.types.non_null(KbFactStatus), graphql_name='status')
    url = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='url')


class PlatformType(sgqlc.types.Type, EntityType, HasTypeSearchElements, LinkTypeTarget, PropertyTypeTarget, RecordInterface):
    __schema__ = api_schema
    __field_names__ = ('description',)
    description = sgqlc.types.Field(String, graphql_name='description')


class PropertyValueMentionCandidateFact(sgqlc.types.Type, FactInterface):
    __schema__ = api_schema
    __field_names__ = ('mention', 'value_fact')
    mention = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('MentionUnion'))), graphql_name='mention')
    value_fact = sgqlc.types.Field(sgqlc.types.non_null(ConceptPropertyValueCandidateFact), graphql_name='valueFact')


class ResearchMap(sgqlc.types.Type, RecordInterface):
    __schema__ = api_schema
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
    __schema__ = api_schema
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
    __schema__ = api_schema
    __field_names__ = ('id', 'name', 'notes', 'rubricator_type', 'transformator_id')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    notes = sgqlc.types.Field(String, graphql_name='notes')
    rubricator_type = sgqlc.types.Field(sgqlc.types.non_null(RubricatorType), graphql_name='rubricatorType')
    transformator_id = sgqlc.types.Field(ID, graphql_name='transformatorId')


class StoryType(sgqlc.types.Type, EntityType, HasTypeSearchElements, LinkTypeTarget, PropertyTypeTarget, RecordInterface):
    __schema__ = api_schema
    __field_names__ = ()


class TextNodeMention(sgqlc.types.Type, MentionInterface, RecordInterface):
    __schema__ = api_schema
    __field_names__ = ('end', 'node_id', 'start')
    end = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='end')
    node_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='nodeId')
    start = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='start')


class VideoNodeMention(sgqlc.types.Type, MentionInterface, RecordInterface):
    __schema__ = api_schema
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
    __schema__ = api_schema
    __types__ = (ConceptCompositePropertyCandidateFact, ConceptLinkCompositePropertyCandidateFact)


class AnyPropertyOrValueComponentFact(sgqlc.types.Union):
    __schema__ = api_schema
    __types__ = (CompositePropertyValueComponentCandidateFact, ConceptLinkPropertyCandidateFact, ConceptLinkPropertyFact, ConceptPropertyCandidateFact, ConceptPropertyFact)


class AnyValue(sgqlc.types.Union):
    __schema__ = api_schema
    __types__ = (CompositeValue, DateTimeValue, DoubleValue, GeoPointValue, IntValue, LinkValue, StringLocaleValue, StringValue, TimestampValue)


class AnyValueType(sgqlc.types.Union):
    __schema__ = api_schema
    __types__ = (CompositePropertyValueTemplate, ConceptPropertyValueType)


class ConceptLikeFact(sgqlc.types.Union):
    __schema__ = api_schema
    __types__ = (ConceptCandidateFact, ConceptFact)


class ConceptLinkLikeFact(sgqlc.types.Union):
    __schema__ = api_schema
    __types__ = (ConceptLinkCandidateFact, ConceptLinkFact)


class ConceptPropertyLikeFact(sgqlc.types.Union):
    __schema__ = api_schema
    __types__ = (ConceptLinkPropertyFact, ConceptPropertyFact)


class ConceptViewValue(sgqlc.types.Union):
    __schema__ = api_schema
    __types__ = (CompositeValue, Concept, ConceptLinkType, ConceptType, DateTimeValue, DoubleValue, GeoPointValue, Image, IntValue, LinkValue, StringLocaleValue, StringValue, TimestampValue, User)


class Entity(sgqlc.types.Union):
    __schema__ = api_schema
    __types__ = (Account, AccountType, Concept, ConceptType, Document, DocumentType, Platform, PlatformType, StoryType)


class EntityLink(sgqlc.types.Union):
    __schema__ = api_schema
    __types__ = (ConceptCandidateFact, ConceptFact, ConceptLink, ConceptLinkType, DocumentLink)


class Fact(sgqlc.types.Union):
    __schema__ = api_schema
    __types__ = (CompositePropertyValueCandidateFact, CompositePropertyValueComponentCandidateFact, ConceptCandidateFact, ConceptCompositePropertyCandidateFact, ConceptFact, ConceptLinkCandidateFact, ConceptLinkCompositePropertyCandidateFact, ConceptLinkFact, ConceptLinkPropertyCandidateFact, ConceptLinkPropertyFact, ConceptPropertyCandidateFact, ConceptPropertyFact, ConceptPropertyValueCandidateFact, PropertyValueMentionCandidateFact)


class MapEvent(sgqlc.types.Union):
    __schema__ = api_schema
    __types__ = (DeleteDrawing, DeleteEdge, DeleteGroup, DeleteNode, ShortestPath, UpsertDrawing, UpsertEdge, UpsertGroup, UpsertNode)


class MentionUnion(sgqlc.types.Union):
    __schema__ = api_schema
    __types__ = (AudioNodeMention, ImageNodeMention, NodeMention, TextNodeMention, VideoNodeMention)


class RubricLinkedType(sgqlc.types.Union):
    __schema__ = api_schema
    __types__ = (ConceptPropertyType, ConceptPropertyValueType, ConceptType)


class TypeSearchElement(sgqlc.types.Union):
    __schema__ = api_schema
    __types__ = (DictValue, NERCRegexp)


class UserMenuType(sgqlc.types.Union):
    __schema__ = api_schema
    __types__ = (ConceptTypePresentation, ConceptTypeView, DocumentTypePresentation)


class Value(sgqlc.types.Union):
    __schema__ = api_schema
    __types__ = (DateTimeValue, DoubleValue, GeoPointValue, IntValue, LinkValue, StringLocaleValue, StringValue, TimestampValue)



########################################################################
# Schema Entry Points
########################################################################
api_schema.query_type = Query
api_schema.mutation_type = Mutation
api_schema.subscription_type = Subscription

