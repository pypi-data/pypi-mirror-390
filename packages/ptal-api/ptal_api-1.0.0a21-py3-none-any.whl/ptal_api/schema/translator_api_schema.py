import sgqlc.types


translator_api_schema = sgqlc.types.Schema()



########################################################################
# Scalars and Enumerations
########################################################################
Boolean = sgqlc.types.Boolean

ID = sgqlc.types.ID

String = sgqlc.types.String


########################################################################
# Input Objects
########################################################################

########################################################################
# Output Objects and Interfaces
########################################################################
class Language(sgqlc.types.Type):
    __schema__ = translator_api_schema
    __field_names__ = ('id', 'iso6391', 'iso6392', 'name', 'russian_name', 'english_name', 'target_languages')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    iso6391 = sgqlc.types.Field(String, graphql_name='iso6391')
    iso6392 = sgqlc.types.Field(String, graphql_name='iso6392')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    russian_name = sgqlc.types.Field(String, graphql_name='russianName')
    english_name = sgqlc.types.Field(String, graphql_name='englishName')
    target_languages = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('Language'))), graphql_name='targetLanguages')


class Query(sgqlc.types.Type):
    __schema__ = translator_api_schema
    __field_names__ = ('language', 'language_list_by_id', 'detect_language', 'translate_str', 'source_languages', 'default_language')
    language = sgqlc.types.Field(Language, graphql_name='language', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    language_list_by_id = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(Language)), graphql_name='languageListById', args=sgqlc.types.ArgDict((
        ('ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='ids', default=None)),
))
    )
    detect_language = sgqlc.types.Field(sgqlc.types.non_null(Language), graphql_name='detectLanguage', args=sgqlc.types.ArgDict((
        ('text', sgqlc.types.Arg(String, graphql_name='text', default=None)),
))
    )
    translate_str = sgqlc.types.Field(String, graphql_name='translateStr', args=sgqlc.types.ArgDict((
        ('text', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='text', default=None)),
        ('source', sgqlc.types.Arg(ID, graphql_name='source', default=None)),
        ('target', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='target', default=None)),
))
    )
    source_languages = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(Language))), graphql_name='sourceLanguages')
    default_language = sgqlc.types.Field(Language, graphql_name='defaultLanguage')



########################################################################
# Unions
########################################################################

########################################################################
# Schema Entry Points
########################################################################
translator_api_schema.query_type = Query
translator_api_schema.mutation_type = None
translator_api_schema.subscription_type = None

