import json
import logging
from copy import copy
from functools import wraps
from time import time
from typing import Any, Dict, Iterable, List, Optional, Sequence, Union

import graphql
from deprecation import deprecated
from sgqlc.operation import Fragment

from .core.kb_sync.kb_iterator_config import KBIteratorConfig
from .core.kb_sync.object_time_interval import ObjectTimeInterval
from .core.query_factory import make_operation
from .core.type_mapper.data_model.base_data_model import TypeMapping
from .core.type_mapper.modules.type_mapping_loader.type_mapping_loader import TypeMappingLoader
from .core.type_mapper.modules.type_mapping_loader.type_mapping_loader_interface import TypeMappingLoaderInterface
from .core.values.value_mapping import get_map_helper
from .pretty_adapter import object_types, objects
from .pretty_adapter.transformer import prettify
from .providers.gql_providers import AbstractGQLClient
from .schema import tcontroller_api_schema as tc
from .schema import translator_api_schema as ts
from .schema import utils_api_schema as uas
from .schema.api_schema import (
    Account,
    AccountFilterSettings,
    AccountPagination,
    AccountUpdateInput,
    ComponentValueInput,
    CompositePropertyTypeFilterSettings,
    CompositePropertyTypeSorting,
    CompositePropertyValueTemplate,
    CompositePropertyValueType,
    CompositeValue,
    Concept,
    ConceptCandidateFact,
    ConceptFact,
    ConceptFactPagination,
    ConceptFilterSettings,
    ConceptLink,
    ConceptLinkCreationMutationInput,
    ConceptLinkFilterSettings,
    ConceptLinkPagination,
    ConceptLinkPropertyInput,
    ConceptLinkPropertyTypeCreationInput,
    ConceptLinkPropertyTypeUpdateInput,
    ConceptLinkType,
    ConceptLinkTypeFilterSettings,
    ConceptLinkTypePagination,
    ConceptLinkTypeSorting,
    ConceptLinkUpdateMutationInput,
    ConceptMergeInput,
    ConceptMutationInput,
    ConceptPagination,
    ConceptPresentation,
    ConceptPresentationWidgetRowPagination,
    ConceptProperty,
    ConceptPropertyCandidateFact,
    ConceptPropertyCreateInput,
    ConceptPropertyFilterSettings,
    ConceptPropertyPagination,
    ConceptPropertyType,
    ConceptPropertyTypeCreationInput,
    ConceptPropertyTypeFilterSettings,
    ConceptPropertyTypePagination,
    ConceptPropertyTypeSorting,
    ConceptPropertyUpdateInput,
    ConceptPropertyValueType,
    ConceptPropertyValueTypeFilterSettings,
    ConceptPropertyValueTypePagination,
    ConceptPropertyValueTypeSorting,
    ConceptPropertyValueTypeUpdateInput,
    ConceptSorting,
    ConceptType,
    ConceptTypeFilterSettings,
    ConceptTypePagination,
    ConceptTypeSorting,
    ConceptUnmergeInput,
    ConceptUpdateInput,
    CoordinatesInput,
    DateInput,
    DateTimeInput,
    DateTimeValue,
    Document,
    DocumentFilterSettings,
    DocumentGrouping,
    DocumentNodeUpdateInput,
    DocumentPagination,
    DocumentSorting,
    DoubleValue,
    DoubleValueInput,
    ExtraSettings,
    FactInput,
    GeoPointInput,
    GeoPointValue,
    IntValue,
    IntValueInput,
    LanguageInput,
    LanguageUpdateInput,
    LinkedDocumentFilterSettings,
    LinkValue,
    LinkValueInput,
    Mutation,
    NodeMention,
    PerformSynchronously,
    Platform,
    PlatformFilterSettings,
    PlatformPagination,
    PlatformSorting,
    PlatformUpdateInput,
    PropertyFilterSettings,
    Query,
    SortDirection,
    State,
    Story,
    StoryPagination,
    StringLocaleValue,
    StringLocaleValueInput,
    StringValue,
    StringValueInput,
    TimeInput,
    TimestampValue,
    TimestampValueInput,
    TranslationInput,
    ValueInput,
    StringFilterInput,
    TimestampIntervalInput,
)
from .schema.auth_api_schema import User
from .schema.crawlers_api_schema import Crawler, CrawlerPagination
from .schema.crawlers_api_schema import Query as CrQuery
from .tdm_builder.tdm_builder import AbstractTdmBuilder

logger = logging.getLogger(__name__)


def check_utils_gql_client(f):
    @wraps(f)
    def wrapper(self: "TalismanAPIAdapter", *args, **kwargs):
        if self._utils_gql_client is None:
            raise Exception("Utils methods cannot be used because the corresponding gql_client is not specified.")
        return f(self, *args, **kwargs)

    return wrapper


class TalismanAPIAdapter:
    def __init__(
        self,
        gql_client: AbstractGQLClient,
        type_mapping: Optional[Union[str, dict, TypeMapping]] = None,
        type_mapping_loader: Optional[TypeMappingLoaderInterface] = None,
        tdm_builder: Optional[AbstractTdmBuilder] = None,
        utils_gql_client: Optional[AbstractGQLClient] = None,
        kb_iterator_config: Optional[KBIteratorConfig] = None,
        limit: int = 100,
        perform_synchronously: bool = True,
        prettify_output: bool = False,
    ) -> None:
        self._gql_client = gql_client
        self._utils_gql_client = utils_gql_client
        self._type_mapping_loader = type_mapping_loader if type_mapping_loader else TypeMappingLoader(logger)
        self._type_mapping = self._type_mapping_loader.load_type_mapping(type_mapping)
        self._limit = limit
        self._perform_synchronously = perform_synchronously
        self.prettify_output = prettify_output

        self.document_fields_truncated = (
            "id",
            "external_url",
            "uuid",
        )
        self.document_fields = (
            "id",
            "title",
            "external_url",
            "publication_author",
            "publication_date",
            "internal_url",
            "markers",
            "system_registration_date",
            "system_update_date",
            "notes",
            "access_level",
            "trust_level",
            "uuid",
        )
        self.document_text_fields = (
            "hierarchy_level",
            "node_id",
            "text",
        )
        self.document_additional_text_fields = (
            "node_id",
            "text",
        )
        self.document_text_metadata_fields = ("paragraph_type",)
        self.document_platform_fields = (
            "id",
            "name",
        )
        self.document_account_fields = (
            "id",
            "name",
        )
        self.document_avatar_fields = (
            "bucket_name",
            "object_name",
        )
        self.document_avatar_url_fields = ("url",)

        self.translation_node_mention_fields = (
            "id",
            "node_id",
        )

        self.user_fields_truncated = ("id",)
        self.user_fields = (
            "id",
            "first_name",
            "last_name",
            "fathers_name",
        )

        self.concept_fields = (
            "id",
            "name",
            "notes",
            "markers",
            "system_registration_date",
            "system_update_date",
        )
        self.concept_type_fields = ("id", "name")

        self.concept_property_fields = ("id", "is_main", "status", "system_registration_date")
        self.concept_property_type_fields = ("id", "name")
        self.cpvt_fields_truncated = ("id", "name", "value_type")
        self.cpvt_fields = ("id", "name", "value_type", "value_restriction", "pretrained_nercmodels")

        self.composite_property_value_template_fields = ("id", "name")
        self.component_value_types_fields = ("id", "name")

        self.concept_link_fields = ("id", "notes")
        self.concept_link_type_fields = ("id", "name", "is_directed", "is_hierarchical")
        self.concept_link_type_fields_truncated = ("id", "name", "is_directed")

        self.concept_fact_fields = ("id",)
        self.concept_candidate_fact_fields = ("id",)
        self.concept_candidate_fact_property_fields = ("id",)
        self.concept_candidate_fact_property_value_fields = ("id",)

        self.concept_presentation_widget_type = ("id", "name")
        self.concept_presentation_widget_type_columns_info = ("name",)

        self.date_time_value_date_fields = ("year", "month", "day")
        self.date_time_value_time_fields = ("hour", "minute", "second")
        self.geo_point_value_point_fields = ("latitude", "longitude")

        self.platform_fields = ("id", "name", "platform_type", "url", "country", "language", "markers", "params")
        self.account_fields = ("id", "name", "url", "country", "markers", "params")

        self.pipeline_config_fields = ("id", "description")

        self.pipeline_topic_fields = ("topic", "description", "stopped", "metrics", "pipeline")
        self.pipeline_metrics_fields = ("duplicate", "failed", "messages", "ok")

        self.tdm_builder = tdm_builder

        if kb_iterator_config:
            self.kb_iterator_config = kb_iterator_config
        else:
            self.kb_iterator_config = KBIteratorConfig(1000, 1609448400)  # Fri Jan 01 2021 00:00:00 GMT+0300

    @property
    def prettify_output(self) -> bool:
        return self._prettify_output

    @prettify_output.setter
    def prettify_output(self, value: bool) -> None:
        self._prettify_output = value

    def get_tdm_builder(self) -> Optional[AbstractTdmBuilder]:
        return self.tdm_builder

    @property
    def type_mapping(self):
        return self._type_mapping

    @type_mapping.setter
    def type_mapping(self, new_type_mapping: TypeMapping):
        self._type_mapping = new_type_mapping

    @property
    def limit(self):
        return self._limit

    @limit.setter
    def limit(self, new_limit: int):
        self._limit = new_limit

    @property
    def perform_synchronously(self):
        return self._perform_synchronously

    @perform_synchronously.setter
    def perform_synchronously(self, new_perform_synchronously: bool):
        self._perform_synchronously = new_perform_synchronously

    def get_take_value(self, take: Optional[int]) -> int:
        return self.limit if take is None else take

    def get_perform_synchronously_value(self, perform_synchronously: Optional[bool]) -> bool:
        return self.perform_synchronously if perform_synchronously is None else perform_synchronously

    def _configure_property_value_type_fields(self, graphql_value, truncated: bool = True):
        conpvt_frag: Fragment = Fragment(ConceptPropertyValueType, "ConceptPropertyValueType")
        for f in self.cpvt_fields_truncated if truncated else self.cpvt_fields:
            conpvt_frag.__getattr__(f)()

        compvt_frag = Fragment(CompositePropertyValueTemplate, "CompositePropertyValueTemplate")
        compvt_frag.__fields__("id", "name")
        compvt_frag.component_value_types()

        graphql_value.__fragment__(conpvt_frag)
        graphql_value.__fragment__(compvt_frag)

    def _configure_output_value_fields(
        self, graphql_value, with_composite_values: bool = False, with_object_values: bool = False
    ):
        dtv_frag = Fragment(DateTimeValue, "DateTimeFull")
        dtv_frag.date().__fields__(*self.date_time_value_date_fields)
        dtv_frag.time().__fields__(*self.date_time_value_time_fields)

        tv_frag = Fragment(TimestampValue, "TimestampFull")
        tv_frag.value(__alias__="unixtime")

        slv_frag = Fragment(StringLocaleValue, "StringLocaleFull")
        slv_frag.value()
        slv_frag.locale()

        sv_frag = Fragment(StringValue, "StringFull")
        sv_frag.value()

        lv_frag = Fragment(LinkValue, "LinkFull")
        lv_frag.link()

        dv_frag = Fragment(DoubleValue, "DoubleFull")
        dv_frag.value(__alias__="double")

        iv_frag = Fragment(IntValue, "IntFull")
        iv_frag.value(__alias__="number")

        gpv_frag = Fragment(GeoPointValue, "GeoPointFull")
        gpv_frag.name(__alias__="geo_name")
        gpv_frag.point().__fields__(*self.geo_point_value_point_fields)

        graphql_value.__fragment__(dtv_frag)
        graphql_value.__fragment__(tv_frag)
        graphql_value.__fragment__(slv_frag)
        graphql_value.__fragment__(sv_frag)
        graphql_value.__fragment__(lv_frag)
        graphql_value.__fragment__(dv_frag)
        graphql_value.__fragment__(iv_frag)
        graphql_value.__fragment__(gpv_frag)

        if with_composite_values:
            cv_frag = Fragment(CompositeValue, "CompFull")
            cv_frag.list_value().id()
            cv_frag.list_value().property_value_type()
            cv_frag.list_value().value().__fragment__(dtv_frag)
            cv_frag.list_value().value().__fragment__(tv_frag)
            cv_frag.list_value().value().__fragment__(slv_frag)
            cv_frag.list_value().value().__fragment__(sv_frag)
            cv_frag.list_value().value().__fragment__(lv_frag)
            cv_frag.list_value().value().__fragment__(dv_frag)
            cv_frag.list_value().value().__fragment__(iv_frag)
            cv_frag.list_value().value().__fragment__(gpv_frag)
            graphql_value.__fragment__(cv_frag)

        if with_object_values:
            u_frag = Fragment(User, "UserFull")
            u_frag.__fields__("first_name", "last_name", "login")

            c_frag = Fragment(Concept, "ConceptFull")
            c_frag.__fields__("id", "name")

            ct_frag = Fragment(ConceptType, "ConceptTypeFull")
            ct_frag.__fields__(*self.concept_type_fields)

            graphql_value.__fragment__(u_frag)
            graphql_value.__fragment__(c_frag)
            graphql_value.__fragment__(ct_frag)

    def _configure_output_properties_fields(
        self,
        property_object,
        with_documents=False,
        with_facts=False,
    ):
        property_object.__fields__(*self.concept_property_fields)
        property_object.access_level()
        pt = property_object.property_type()
        pt.__fields__(*self.concept_property_type_fields)
        vt = pt.value_type()

        cpvt_frag = Fragment(ConceptPropertyValueType, "ConceptPropertyValueType")
        cpvt_frag.__fields__(*self.cpvt_fields_truncated)

        comp_frag = Fragment(CompositePropertyValueTemplate, "CompositePropertyValueTemplate")
        comp_frag.__fields__(*self.composite_property_value_template_fields)
        comp_frag.component_value_types().__fields__(*self.component_value_types_fields)
        comp_frag.component_value_types().value_type().__fields__(*self.cpvt_fields_truncated)

        vt.__fragment__(cpvt_frag)
        vt.__fragment__(comp_frag)

        self._configure_output_value_fields(property_object.value, with_composite_values=True)
        if with_facts:
            property_object.__fields__("list_concept_property_fact")
        if with_documents:
            pd: DocumentPagination = property_object.pagination_document(offset=0, limit=10000)
            self._configure_output_document_fields(pd.list_document(), with_extended_information=True)

    def _configure_output_concept_candidate_fact_fields(
        self, document_object, with_candidate_fact_properties: bool = False
    ):
        lf = document_object.list_fact()

        ccf_frag = Fragment(ConceptCandidateFact, "ConceptCandidateFact")
        ccf_frag.__fields__(*self.concept_candidate_fact_fields)
        ccf_frag.concept_type().__fields__(*self.concept_type_fields)
        ccf_frag.list_concept().concept().__fields__("id")
        lf.__fragment__(ccf_frag)

        if with_candidate_fact_properties:
            cpcf_frag = Fragment(ConceptPropertyCandidateFact, "ConceptPropertyCandidateFact")
            cpcf_frag.__fields__(*self.concept_candidate_fact_property_fields)
            cpcf_frag.concept_property_type().__fields__(*self.concept_property_type_fields)
            cpcf_frag.fact_from().__as__(ConceptCandidateFact).__fields__("id")
            candidate_fact_property_value = cpcf_frag.fact_to()
            candidate_fact_property_value.__fields__(*self.concept_candidate_fact_property_value_fields)
            self._configure_output_value_fields(candidate_fact_property_value.meanings().value)
            lf.__fragment__(cpcf_frag)

    def _configure_output_concept_fields(
        self,
        concept_object,
        with_aliases=False,
        with_properties=False,
        with_property_documents=False,
        with_links=False,
        with_link_properties=False,
        with_facts=False,
        with_potential_facts=False,
        with_metrics=False,
        property_filter_settings=None,
    ):
        concept_object.__fields__(*self.concept_fields)
        concept_object.access_level()
        concept_object.concept_type.__fields__(*self.concept_type_fields)
        if with_aliases:
            sv_frag = Fragment(StringValue, "StringFull")
            sv_frag.value()
            concept_object.list_alias.value.__fragment__(sv_frag)
        if with_properties:
            property_filter_settings = property_filter_settings if property_filter_settings else {}
            pcp: ConceptPropertyPagination = concept_object.pagination_concept_property(
                offset=0, limit=10000, filter_settings=property_filter_settings
            )
            self._configure_output_properties_fields(
                pcp.list_concept_property(), with_documents=with_property_documents
            )
        if with_links:
            pcl: ConceptLinkPagination = concept_object.pagination_concept_link(
                offset=0, limit=10000, filter_settings={}
            )
            self._configure_output_link_fields(pcl.list_concept_link(), with_link_properties=with_link_properties)
        if with_facts:
            pcf: ConceptFactPagination = concept_object.pagination_concept_fact(
                offset=0, limit=10000, filter_settings={}
            )
            lcf = pcf.list_concept_fact()
            lcf.__fields__(*self.concept_fact_fields)
            self._configure_output_document_fields(
                doc_object=lcf.document(),
                with_extended_information=True,
                with_candidate_facts=True,
                with_candidate_fact_properties=True,
            )
        if with_potential_facts:
            lccf = concept_object.list_concept_candidate_fact()
            lccf.__fields__(*self.concept_fact_fields)
            self._configure_output_document_fields(
                doc_object=lccf.document(),
                with_extended_information=True,
                with_candidate_facts=True,
                with_candidate_fact_properties=True,
            )
        if with_metrics:
            concept_object.metric()

    def _configure_output_link_fields(self, link_object, with_link_properties=False, with_facts=False):
        link_object.__fields__(*self.concept_link_fields)
        link_object.concept_link_type().__fields__(*self.concept_link_type_fields_truncated)
        link_object.access_level()
        self._configure_output_concept_fields(link_object.concept_from())
        self._configure_output_concept_fields(link_object.concept_to())
        if with_link_properties:
            pcp: ConceptPropertyPagination = link_object.pagination_concept_link_property(
                offset=0, limit=10000, filter_settings={}
            )
            self._configure_output_properties_fields(pcp.list_concept_property())
        if with_facts:
            link_object.__fields__("list_concept_link_fact")

    def _configure_output_document_fields(  # noqa: C901
        self,
        doc_object,
        *,
        with_extended_information=False,
        with_text=False,
        with_text_metadata=False,
        with_text_preview=False,
        with_additional_text=False,
        with_translation_mentions=False,
        with_updater=False,
        with_creator=False,
        with_facts=False,
        with_candidate_facts=False,
        with_candidate_fact_properties=False,
        with_avatar=False,
        with_avatar_url=False,
        with_extended_user_information=False,
        with_children=False,
    ):
        doc_object.access_level()
        if with_extended_information:
            doc_object.__fields__(*self.document_fields)
            mdm = doc_object.metadata()
            mdm.platform().__fields__(*self.document_platform_fields)
            mdm.account().__fields__(*self.document_account_fields)
        else:
            doc_object.__fields__(*self.document_fields_truncated)
        if with_text:
            dt = doc_object.text(show_hidden=True)
            dt.__fields__(*self.document_text_fields)
            if with_text_metadata:
                dt.metadata().__fields__(*self.document_text_metadata_fields)
            if with_translation_mentions:
                dt.translation_mention().__as__(NodeMention).__fields__(*self.translation_node_mention_fields)
        if with_text_preview:
            doc_object.preview()
        if with_additional_text:
            dat = doc_object.additional_text(show_hidden=True)
            dat.__fields__(*self.document_additional_text_fields)
            dat.language().id()
        if with_updater:
            if with_extended_user_information:
                user_fragment = Fragment(User, "UserFragment")
                user_fragment.__fields__(*self.user_fields)
                doc_object.last_updater().__fragment__(user_fragment)
            else:
                doc_object.last_updater().__fields__(*self.user_fields_truncated)
        if with_creator:
            if with_extended_user_information:
                user_fragment = Fragment(User, "UserFragment")
                user_fragment.__fields__(*self.user_fields)
                doc_object.creator().__fragment__(user_fragment)
            else:
                doc_object.creator().__fields__(*self.user_fields_truncated)
        if with_facts:
            doc_object.list_concept_fact().__fields__(*self.concept_fact_fields)
        if with_candidate_facts:
            self._configure_output_concept_candidate_fact_fields(
                document_object=doc_object,
                with_candidate_fact_properties=with_candidate_fact_properties,
            )
        if with_avatar:
            doc_object.avatar().__fields__(*self.document_avatar_fields)
        if with_avatar_url:
            doc_object.avatar().__fields__(*self.document_avatar_url_fields)
        if with_children:
            self._configure_output_document_fields(
                doc_object.list_child(),
                with_extended_information=with_extended_information,
                with_text=with_text,
                with_text_metadata=with_text_metadata,
                with_text_preview=with_text_preview,
                with_additional_text=with_additional_text,
                with_translation_mentions=with_translation_mentions,
                with_updater=with_updater,
                with_creator=with_creator,
                with_avatar=with_avatar,
                with_avatar_url=with_avatar_url,
                with_extended_user_information=with_extended_user_information,
            )

    def _configure_output_platform_fields(
        self,
        platform_object,
        with_metric: bool = False,
    ):
        platform_object.__fields__(*self.platform_fields)
        platform_object.params()
        if with_metric:
            platform_object.metric()

    def _configure_output_account_fields(
        self,
        account_object,
        with_metric: bool = False,
    ):
        account_object.__fields__(*self.account_fields)
        account_object.params()
        if with_metric:
            account_object.metric()
        self._configure_output_platform_fields(account_object.platform(), with_metric)

    @prettify
    def _create_concept_with_input(
        self,
        form: ConceptMutationInput,
        with_properties=False,
        with_links=False,
        with_link_properties=False,
        with_metrics=False,
        perform_synchronously: Optional[bool] = None,
    ) -> Union[Concept, objects.Concept]:
        op = make_operation(Mutation, "create_concept_with_input")
        ac = op.add_concept(
            performance_control=PerformSynchronously(
                perform_synchronously=self.get_perform_synchronously_value(perform_synchronously)
            ),
            form=form,
        )
        self._configure_output_concept_fields(
            ac,
            with_properties=with_properties,
            with_links=with_links,
            with_link_properties=with_link_properties,
            with_metrics=with_metrics,
        )
        res = self._gql_client.execute(op)
        res = op + res

        if self.tdm_builder is not None:
            self.tdm_builder.add_concept_fact(res.add_concept)

        return res.add_concept

    def _get_components_mapping(
        self, component_values: Dict[str, str], component_value_types: List[CompositePropertyValueType]
    ) -> Dict[str, CompositePropertyValueType]:
        components_type_mapping = {}
        for component_value in component_values:
            for component_value_type in component_value_types:
                if component_value_type.name != component_values[component_value]:
                    continue
                components_type_mapping[component_value] = component_value_type
        return components_type_mapping

    def _get_value_input(
        self, values: dict, components_type_mapping: Dict[str, CompositePropertyValueType]
    ) -> List[ComponentValueInput]:
        value_input = []
        for field in values:
            if field not in components_type_mapping:
                continue
            value_id = components_type_mapping[field].id
            value_input.append(
                ComponentValueInput(
                    id=value_id,
                    value=get_map_helper(components_type_mapping[field].value_type.value_type).get_value_input(
                        values[field]
                    ),
                )
            )
        return value_input

    def _configure_pipeline_topic_fields(self, kafka_topic: tc.KafkaTopic):
        kafka_topic.__fields__(*self.pipeline_topic_fields)
        kafka_topic.metrics().__fields__(*self.pipeline_metrics_fields)
        kafka_topic.pipeline().pipeline_config().__fields__(*self.pipeline_config_fields)

    def raw_execute(self, query: str, variables: Optional[dict] = None):
        graphql.parse(query)
        return self._gql_client.execute(query=query, variables=variables)

    # @prettify
    def get_all_documents(
        self,
        grouping: DocumentGrouping = "none",
        filter_settings: Optional[DocumentFilterSettings] = None,
        direction: SortDirection = "descending",
        sort_field: DocumentSorting = "score",
        extra_settings: Optional[ExtraSettings] = None,
        with_extended_information: bool = False,
        with_text: bool = False,
        with_text_metadata: bool = False,
        with_text_preview: bool = False,
        with_additional_text: bool = False,
        with_translation_mentions: bool = False,
        with_updater: bool = False,
        with_creator: bool = False,
        with_facts: bool = False,
        with_candidate_facts: bool = False,
        with_candidate_fact_properties: bool = False,
        with_avatar: bool = False,
        with_avatar_url: bool = False,
        with_extended_user_information: bool = False,
        with_children: bool = False,
    ) -> Iterable[Story]:
        if filter_settings is None:
            filter_settings = DocumentFilterSettings()
        if extra_settings is None:
            extra_settings = ExtraSettings()

        total = self.get_documents_count(filter_settings=filter_settings)

        if total > self.kb_iterator_config.max_total_count:
            had_creation_date = hasattr(filter_settings, "registration_date")
            old_timestamp_interval = None
            if had_creation_date:
                old_timestamp_interval = copy(filter_settings.registration_date)
            start: int = getattr(old_timestamp_interval, "start", self.kb_iterator_config.earliest_created_time)
            end: int = getattr(old_timestamp_interval, "end", int(time()))
            middle: int = (end + start) // 2

            for next_start, next_end in (start, middle), (middle + 1, end):
                if next_start == start and next_end == end:
                    logger.info(
                        f"Processed only {self.kb_iterator_config.max_total_count} documents, "
                        f"{total - self.kb_iterator_config.max_total_count} ignored"
                    )
                    continue
                filter_settings.registration_date = TimestampIntervalInput(start=next_start, end=next_end)
                yield from self.get_all_documents(
                    grouping=grouping,
                    filter_settings=filter_settings,
                    direction=direction,
                    sort_field=sort_field,
                    extra_settings=extra_settings,
                    with_extended_information=with_extended_information,
                    with_text=with_text,
                    with_text_metadata=with_text_metadata,
                    with_text_preview=with_text_preview,
                    with_additional_text=with_additional_text,
                    with_translation_mentions=with_translation_mentions,
                    with_updater=with_updater,
                    with_creator=with_creator,
                    with_facts=with_facts,
                    with_candidate_facts=with_candidate_facts,
                    with_candidate_fact_properties=with_candidate_fact_properties,
                    with_avatar=with_avatar,
                    with_avatar_url=with_avatar_url,
                    with_extended_user_information=with_extended_user_information,
                    with_children=with_children,
                )

            if had_creation_date:
                filter_settings.registration_date = old_timestamp_interval
            else:
                delattr(filter_settings, "registration_date")
            return
        elif not total:
            return

        documents: Iterable = [None]
        i: int = 0
        while documents:
            documents = self.get_documents(
                skip=i * self._limit,
                take=self._limit,
                grouping=grouping,
                filter_settings=filter_settings,
                direction=direction,
                sort_field=sort_field,
                extra_settings=extra_settings,
                with_extended_information=with_extended_information,
                with_text=with_text,
                with_text_metadata=with_text_metadata,
                with_text_preview=with_text_preview,
                with_additional_text=with_additional_text,
                with_translation_mentions=with_translation_mentions,
                with_updater=with_updater,
                with_creator=with_creator,
                with_facts=with_facts,
                with_candidate_facts=with_candidate_facts,
                with_candidate_fact_properties=with_candidate_fact_properties,
                with_avatar=with_avatar,
                with_avatar_url=with_avatar_url,
                with_extended_user_information=with_extended_user_information,
                with_children=with_children,
            )
            yield from documents
            i += 1

    # @prettify
    def get_documents(
        self,
        skip: int = 0,
        take: Optional[int] = None,
        grouping: DocumentGrouping = "none",
        filter_settings: Optional[DocumentFilterSettings] = None,
        direction: SortDirection = "descending",
        sort_field: DocumentSorting = "score",
        extra_settings: Optional[ExtraSettings] = None,
        with_extended_information: bool = False,
        with_text: bool = False,
        with_text_metadata: bool = False,
        with_text_preview: bool = False,
        with_additional_text: bool = False,
        with_translation_mentions: bool = False,
        with_updater: bool = False,
        with_creator: bool = False,
        with_facts: bool = False,
        with_candidate_facts: bool = False,
        with_candidate_fact_properties: bool = False,
        with_avatar: bool = False,
        with_avatar_url: bool = False,
        with_extended_user_information: bool = False,
        with_children: bool = False,
    ) -> Sequence[Story]:
        op = make_operation(Query, "get_documents")
        take = self.get_take_value(take)
        pagination_story_kwargs = {}
        if filter_settings is None:
            filter_settings = DocumentFilterSettings()
        if extra_settings is None:
            extra_settings = ExtraSettings()
        ps: StoryPagination = op.pagination_story(
            offset=skip,
            limit=take,
            grouping=grouping,
            filter_settings=filter_settings,
            direction=direction,
            sort_field=sort_field,
            extra_settings=extra_settings,
            **pagination_story_kwargs,
        )
        self._configure_output_document_fields(ps.list_story().list_document())
        self._configure_output_document_fields(
            ps.list_story().main(),
            with_extended_information=with_extended_information,
            with_text=with_text,
            with_text_metadata=with_text_metadata,
            with_text_preview=with_text_preview,
            with_additional_text=with_additional_text,
            with_translation_mentions=with_translation_mentions,
            with_updater=with_updater,
            with_creator=with_creator,
            with_facts=with_facts,
            with_candidate_facts=with_candidate_facts,
            with_candidate_fact_properties=with_candidate_fact_properties,
            with_avatar=with_avatar,
            with_avatar_url=with_avatar_url,
            with_extended_user_information=with_extended_user_information,
            with_children=with_children,
        )

        res = self._gql_client.execute(op)
        res = op + res
        return res.pagination_story.list_story

    def get_documents_by_ids(
        self,
        document_ids: List[str],
        with_extended_information: bool = False,
        with_text: bool = False,
        with_text_metadata: bool = False,
        with_text_preview: bool = False,
        with_additional_text: bool = False,
        with_translation_mentions: bool = False,
        with_updater: bool = False,
        with_creator: bool = False,
        with_facts: bool = False,
        with_candidate_facts: bool = False,
        with_candidate_fact_properties: bool = False,
        with_avatar: bool = False,
        with_avatar_url: bool = False,
        with_extended_user_information: bool = False,
        with_children: bool = False,
    ) -> Sequence[Document]:
        op = make_operation(Query, "get_documents_by_ids")
        ld = op.list_document_by_id(ids=document_ids)
        self._configure_output_document_fields(
            ld,
            with_extended_information=with_extended_information,
            with_text=with_text,
            with_text_metadata=with_text_metadata,
            with_text_preview=with_text_preview,
            with_additional_text=with_additional_text,
            with_translation_mentions=with_translation_mentions,
            with_updater=with_updater,
            with_creator=with_creator,
            with_facts=with_facts,
            with_candidate_facts=with_candidate_facts,
            with_candidate_fact_properties=with_candidate_fact_properties,
            with_avatar=with_avatar,
            with_avatar_url=with_avatar_url,
            with_extended_user_information=with_extended_user_information,
            with_children=with_children,
        )

        res = self._gql_client.execute(op)
        res = op + res
        return res.list_document_by_id

    def get_documents_count(self, filter_settings: Optional[DocumentFilterSettings] = None) -> int:
        op = make_operation(Query, "get_documents_count")
        if filter_settings is None:
            filter_settings = DocumentFilterSettings()
        ps: StoryPagination = op.pagination_story(
            limit=1, filter_settings=filter_settings, extra_settings=ExtraSettings()
        )
        ps.show_total()
        res = self._gql_client.execute(op)
        res = op + res
        return res.pagination_story.show_total

    # @prettify
    def get_documents_by_limit_offset_filter_extra_settings(
        self,
        skip: int = 0,
        take: Optional[int] = None,
        filter_settings: Optional[DocumentFilterSettings] = None,
        extra_settings: Optional[ExtraSettings] = None,
    ) -> Sequence[Story]:
        op = make_operation(Query, "get_documents_by_limit_offset_filter_extra_settings")
        take = self.get_take_value(take)
        ps: StoryPagination = op.pagination_story(
            offset=skip,
            limit=take,
            extra_settings=extra_settings if extra_settings else ExtraSettings(),
            filter_settings=filter_settings if filter_settings else DocumentFilterSettings(),
        )
        self._configure_output_document_fields(ps.list_story().list_document())
        self._configure_output_document_fields(ps.list_story().main())

        res = self._gql_client.execute(op)
        res = op + res
        return res.pagination_story.list_story

    # @prettify
    def get_document(
        self, document_id: str, with_candidate_facts: bool = False, with_candidate_fact_properties: bool = False,
        with_avatar: bool = False, with_avatar_url: bool = False, with_extended_user_information: bool = False
    ) -> Document:
        op = make_operation(Query, "get_document")
        d: Document = op.document(id=document_id)
        self._configure_output_document_fields(
            d,
            with_extended_information=True,
            with_text=True,
            with_text_metadata=True,
            with_text_preview=True,
            with_additional_text=True,
            with_translation_mentions=True,
            with_updater=True,
            with_creator=True,
            with_facts=True,
            with_candidate_facts=with_candidate_facts,
            with_candidate_fact_properties=with_candidate_fact_properties,
            with_avatar=with_avatar,
            with_avatar_url=with_avatar_url,
            with_extended_user_information=with_extended_user_information,
            with_children=True,
        )

        res = self._gql_client.execute(op)
        res = op + res
        return res.document

    def get_concept_count(self, filter_settings: Optional[ConceptFilterSettings] = None) -> int:
        op = make_operation(Query, "get_concept_count")
        pc: ConceptPagination = op.pagination_concept(
            filter_settings=filter_settings if filter_settings else ConceptFilterSettings()
        )
        pc.show_total()
        res = self._gql_client.execute(op)
        res = op + res
        return res.pagination_concept.show_total

    def get_concept_link_count(self, filter_settings: Optional[ConceptLinkFilterSettings] = None) -> int:
        op = make_operation(Query, "get_concept_link_count")
        pcl: ConceptLinkPagination = op.pagination_concept_link(
            filter_settings=filter_settings if filter_settings else ConceptLinkFilterSettings()
        )
        pcl.total()
        res = self._gql_client.execute(op)
        res = op + res
        return res.pagination_concept_link.total

    @prettify
    def get_concept(
        self,
        concept_id: str,
        with_aliases: bool = False,
        with_properties: bool = True,
        with_property_documents: bool = False,
        with_links: bool = True,
        with_link_properties: bool = True,
        with_facts: bool = False,
        with_potential_facts: bool = False,
        with_metrics: bool = True,
        property_filter_settings: Optional[ConceptPropertyFilterSettings] = None,
    ) -> Union[Concept, objects.Concept]:
        return self._get_concept(
            concept_id,
            with_aliases,
            with_properties,
            with_property_documents,
            with_links,
            with_link_properties,
            with_facts,
            with_potential_facts,
            with_metrics,
            property_filter_settings,
        )

    def _get_concept(
        self,
        concept_id: str,
        with_aliases: bool = False,
        with_properties: bool = True,
        with_property_documents: bool = False,
        with_links: bool = True,
        with_link_properties: bool = True,
        with_facts: bool = False,
        with_potential_facts: bool = False,
        with_metrics: bool = True,
        property_filter_settings: Optional[ConceptPropertyFilterSettings] = None,
    ) -> Concept:
        op = make_operation(Query, "get_concept")
        c: Concept = op.concept(id=concept_id)
        self._configure_output_concept_fields(
            c,
            with_aliases=with_aliases,
            with_properties=with_properties,
            with_property_documents=with_property_documents,
            with_links=with_links,
            with_link_properties=with_link_properties,
            with_facts=with_facts,
            with_potential_facts=with_potential_facts,
            with_metrics=with_metrics,
            property_filter_settings=property_filter_settings,
        )
        res = self._gql_client.execute(op)
        res = op + res

        if self.tdm_builder is not None:
            self.tdm_builder.add_concept_fact(res.concept)

        return res.concept

    @prettify
    def get_concept_property(self, concept_property_id: str) -> Union[ConceptProperty, objects.Property]:
        op = make_operation(Query, "get_concept_property")
        cp: ConceptProperty = op.concept_property(id=concept_property_id)

        self._configure_output_properties_fields(cp)
        res = self._gql_client.execute(op)
        res = op + res

        return res.concept_property

    # @prettify
    def get_concept_facts(
        self, concept_id: str, filter_settings: Optional[LinkedDocumentFilterSettings] = None
    ) -> Sequence[ConceptFact]:
        op = make_operation(Query, "get_concept_facts")
        c: Concept = op.concept(id=concept_id)
        pcf: ConceptFactPagination = c.pagination_concept_fact(
            filter_settings=filter_settings if filter_settings else LinkedDocumentFilterSettings()
        )
        lcf = pcf.list_concept_fact()
        lcf.__fields__(*self.concept_fact_fields)
        self._configure_output_document_fields(lcf.document(), with_extended_information=True)

        res = self._gql_client.execute(op)
        res = op + res

        return res.concept.pagination_concept_fact.list_concept_fact

    def _get_concept_link(self, link_id: str, with_facts: bool = False) -> ConceptLink:
        op = make_operation(Query, "get_concept_link")
        cl: ConceptLink = op.concept_link(id=link_id)
        self._configure_output_link_fields(cl, with_facts=with_facts)
        res = self._gql_client.execute(op)
        res = op + res

        if self.tdm_builder is not None:
            self.tdm_builder.add_link_fact(res.concept_link)

        return res.concept_link

    @prettify
    def get_concept_link(self, link_id: str, with_facts: bool = False) -> Union[ConceptLink, objects.Link]:
        return self._get_concept_link(link_id, with_facts)

    @prettify
    def get_all_concepts(
        self,
        filter_settings: Optional[ConceptFilterSettings] = None,
        direction: SortDirection = "descending",
        sort_field: ConceptSorting = "score",
        with_aliases: bool = False,
        with_properties: bool = False,
        with_property_documents: bool = False,
        with_links: bool = False,
        with_link_properties: bool = False,
        with_facts: bool = False,
        with_potential_facts: bool = False,
        with_metrics: bool = False,
        property_filter_settings: Optional[ConceptPropertyFilterSettings] = None,
    ) -> Union[Iterable[Concept], Iterable[objects.Concept]]:
        if not filter_settings:
            filter_settings = ConceptFilterSettings()
        total = self.get_concept_count(filter_settings=filter_settings)

        if total > self.kb_iterator_config.max_total_count:
            had_creation_date = hasattr(filter_settings, "creation_date")
            old_timestamp_interval = None
            if had_creation_date:
                old_timestamp_interval = copy(filter_settings.creation_date)
            start: int = getattr(old_timestamp_interval, "start", self.kb_iterator_config.earliest_created_time)
            end: int = getattr(old_timestamp_interval, "end", int(time()))
            middle: int = (end + start) // 2

            for next_start, next_end in (start, middle), (middle + 1, end):
                if next_start == start and next_end == end:
                    logger.info(
                        f"Processed only {self.kb_iterator_config.max_total_count} concepts, "
                        f"{total - self.kb_iterator_config.max_total_count} ignored"
                    )
                    continue
                filter_settings.creation_date = TimestampIntervalInput(start=next_start, end=next_end)
                yield from self.get_all_concepts(
                    filter_settings=filter_settings,
                    direction=direction,
                    sort_field=sort_field,
                    with_aliases=with_aliases,
                    with_properties=with_properties,
                    with_property_documents=with_property_documents,
                    with_links=with_links,
                    with_link_properties=with_link_properties,
                    with_facts=with_facts,
                    with_potential_facts=with_potential_facts,
                    with_metrics=with_metrics,
                    property_filter_settings=property_filter_settings,
                )

            if had_creation_date:
                filter_settings.creation_date = old_timestamp_interval
            else:
                delattr(filter_settings, "creation_date")
            return
        elif not total:
            return

        concepts: Iterable = [None]
        i: int = 0
        while concepts:
            concepts = self.get_concepts(
                skip=i * self._limit,
                take=self._limit,
                filter_settings=filter_settings,
                direction=direction,
                sort_field=sort_field,
                with_aliases=with_aliases,
                with_properties=with_properties,
                with_property_documents=with_property_documents,
                with_links=with_links,
                with_link_properties=with_link_properties,
                with_facts=with_facts,
                with_potential_facts=with_potential_facts,
                with_metrics=with_metrics,
                property_filter_settings=property_filter_settings,
            )
            yield from concepts
            i += 1

    @prettify
    def get_concepts(
        self,
        skip: int = 0,
        take: Optional[int] = None,
        filter_settings: Optional[ConceptFilterSettings] = None,
        direction: SortDirection = "descending",
        sort_field: ConceptSorting = "score",
        with_aliases: bool = False,
        with_properties: bool = False,
        with_property_documents: bool = False,
        with_links: bool = False,
        with_link_properties: bool = False,
        with_facts: bool = False,
        with_potential_facts: bool = False,
        with_metrics: bool = False,
        property_filter_settings: Optional[ConceptPropertyFilterSettings] = None,
    ) -> Union[Sequence[Concept], Sequence[objects.Concept]]:
        op = make_operation(Query, "get_concepts")
        take = self.get_take_value(take)
        pagination_concept_kwargs = {}
        if not filter_settings:
            filter_settings = ConceptFilterSettings()
        cp: ConceptPagination = op.pagination_concept(
            limit=take,
            offset=skip,
            filter_settings=filter_settings,
            direction=direction,
            sort_field=sort_field,
            **pagination_concept_kwargs,
        )
        self._configure_output_concept_fields(
            cp.list_concept(),
            with_aliases=with_aliases,
            with_properties=with_properties,
            with_property_documents=with_property_documents,
            with_links=with_links,
            with_link_properties=with_link_properties,
            with_facts=with_facts,
            with_potential_facts=with_potential_facts,
            with_metrics=with_metrics,
            property_filter_settings=property_filter_settings,
        )
        res = self._gql_client.execute(op)
        res = op + res
        return res.pagination_concept.list_concept

    @deprecated(details="Use get_concepts method instead")
    def get_concepts_by_limit_offset_filter_settings(
        self,
        skip: int = 0,
        take: Optional[int] = None,
        filter_settings: Optional[ConceptFilterSettings] = None,
        with_aliases: bool = False,
        with_facts: bool = False,
        with_potential_facts=False,
    ) -> Union[Sequence[Concept], Sequence[objects.Concept]]:
        op = make_operation(Query, "get_concepts_by_limit_offset_filter_settings")
        take = self.get_take_value(take)
        cp: ConceptPagination = op.pagination_concept(
            filter_settings=filter_settings if filter_settings else ConceptFilterSettings(), offset=skip, limit=take
        )
        self._configure_output_concept_fields(
            cp.list_concept(),
            with_aliases=with_aliases,
            with_facts=with_facts,
            with_potential_facts=with_potential_facts,
        )
        res = self._gql_client.execute(op)
        res = op + res
        return res.pagination_concept.list_concept

    @prettify
    def get_all_concept_links(
        self, filter_settings: Optional[ConceptLinkFilterSettings] = None, with_link_properties: bool = False
    ) -> Union[Iterable[ConceptLink], Iterable[objects.Link]]:
        if not filter_settings:
            filter_settings = ConceptLinkFilterSettings()

        total = self.get_concept_link_count(filter_settings=filter_settings)

        if total > self.kb_iterator_config.max_total_count:
            had_creation_date = hasattr(filter_settings, "creation_date")
            old_timestamp_interval = None
            if had_creation_date:
                old_timestamp_interval = copy(filter_settings.creation_date)
            start: int = getattr(old_timestamp_interval, "start", self.kb_iterator_config.earliest_created_time)
            end: int = getattr(old_timestamp_interval, "end", int(time()))
            middle: int = (end + start) // 2

            for next_start, next_end in (start, middle), (middle + 1, end):
                if next_start == start and next_end == end:
                    logger.info(
                        f"Processed only {self.kb_iterator_config.max_total_count} links, "
                        f"{total - self.kb_iterator_config.max_total_count} ignored"
                    )
                    continue
                filter_settings.creation_date = TimestampIntervalInput(start=next_start, end=next_end)
                for c in self.get_all_concept_links(
                    filter_settings=filter_settings, with_link_properties=with_link_properties
                ):
                    yield c

            if had_creation_date:
                filter_settings.creation_date = old_timestamp_interval
            else:
                delattr(filter_settings, "creation_date")
            return
        elif not total:
            return

        links: Iterable = [None]
        i: int = 0
        while links:
            links = self.get_concept_links_by_limit_offset_filter_settings(
                skip=i * self._limit,
                take=self._limit,
                filter_settings=filter_settings,
                with_link_properties=with_link_properties,
            )
            yield from links
            i += 1

    @prettify
    def get_concept_links_by_limit_offset_filter_settings(
        self,
        skip: int = 0,
        take: Optional[int] = None,
        filter_settings: Optional[ConceptLinkFilterSettings] = None,
        with_link_properties: bool = False,
    ) -> Union[Sequence[ConceptLink], Sequence[objects.Link]]:
        op = make_operation(Query, "get_concept_links_by_limit_offset_filter_settings")
        take = self.get_take_value(take)
        pcl: ConceptLinkPagination = op.pagination_concept_link(
            filter_settings=filter_settings if filter_settings else ConceptLinkFilterSettings(), offset=skip, limit=take
        )
        self._configure_output_link_fields(pcl.list_concept_link(), with_link_properties=with_link_properties)
        res = self._gql_client.execute(op)
        res = op + res
        return res.pagination_concept_link.list_concept_link

    @deprecated(details="Use get_concepts method instead")
    def get_concepts_by_type_id_with_offset(
        self,
        type_id: str,
        skip: int,
        take: Optional[int] = None,
        direction="descending",
        sort_field="systemRegistrationDate",
        with_aliases: bool = False,
        with_properties: bool = False,
        with_links: bool = False,
        with_link_properties: bool = False,
        with_facts: bool = False,
        with_potential_facts=False,
    ) -> ConceptPagination:
        op = make_operation(Query, "get_concepts_by_type_id_with_offset")
        take = self.get_take_value(take)
        cp: ConceptPagination = op.pagination_concept(
            filter_settings=ConceptFilterSettings(concept_type_ids=[type_id]),
            limit=take,
            offset=skip,
            direction=direction,
            sort_field=sort_field,
        )
        cp.total()
        self._configure_output_concept_fields(
            cp.list_concept(),
            with_aliases=with_aliases,
            with_properties=with_properties,
            with_links=with_links,
            with_link_properties=with_link_properties,
            with_facts=with_facts,
            with_potential_facts=with_potential_facts,
        )
        res = self._gql_client.execute(op)
        res = op + res
        return res.pagination_concept

    @deprecated(details="Use get_concepts method instead")
    def get_concepts_by_type_id_with_offset_with_markers(
        self,
        type_id: str,
        skip: int = 0,
        take: Optional[int] = None,
        markers: Optional[List[str]] = None,
        direction="descending",
        sort_field="systemRegistrationDate",
        with_aliases: bool = False,
        with_facts: bool = False,
        with_potential_facts=False,
    ) -> ConceptPagination:
        op = make_operation(Query, "get_concepts_by_type_id_with_offset_with_markers")
        take = self.get_take_value(take)
        cp: ConceptPagination = op.pagination_concept(
            filter_settings=ConceptFilterSettings(
                concept_type_ids=[type_id],
                markers=markers,
            ),
            limit=take,
            offset=skip,
            direction=direction,
            sort_field=sort_field,
        )
        cp.total()
        self._configure_output_concept_fields(
            cp.list_concept(),
            with_aliases=with_aliases,
            with_facts=with_facts,
            with_potential_facts=with_potential_facts,
        )
        res = self._gql_client.execute(op)
        res = op + res
        return res.pagination_concept

    @prettify
    def get_concepts_by_name(
        self,
        name: str,
        type_id: Optional[str] = None,
        with_aliases: bool = False,
        with_facts: bool = False,
        with_potential_facts=False,
    ) -> Union[Sequence[Concept], Sequence[objects.Concept]]:
        op = make_operation(Query, "get_concepts_by_name")
        if type_id:
            concept_filter_settings: ConceptFilterSettings = ConceptFilterSettings(
                exact_name=name, concept_type_ids=[type_id]
            )
        else:
            concept_filter_settings: ConceptFilterSettings = ConceptFilterSettings(exact_name=name)
        cp: ConceptPagination = op.pagination_concept(filter_settings=concept_filter_settings)
        self._configure_output_concept_fields(
            cp.list_concept(),
            with_aliases=with_aliases,
            with_facts=with_facts,
            with_potential_facts=with_potential_facts,
        )
        res = self._gql_client.execute(op)
        res = op + res
        return res.pagination_concept.list_concept

    @prettify
    def get_concepts_by_near_name(
        self,
        name: str,
        type_id: Optional[str] = None,
        with_aliases: bool = False,
        with_facts: bool = False,
        with_potential_facts=False,
    ) -> Union[Sequence[Concept], Sequence[objects.Concept]]:
        op = make_operation(Query, "get_concepts_by_near_name")
        if type_id:
            concept_filter_settings: ConceptFilterSettings = ConceptFilterSettings(
                name=name, concept_type_ids=[type_id]
            )
        else:
            concept_filter_settings: ConceptFilterSettings = ConceptFilterSettings(name=name)
        cp: ConceptPagination = op.pagination_concept(filter_settings=concept_filter_settings)
        self._configure_output_concept_fields(
            cp.list_concept(),
            with_aliases=with_aliases,
            with_facts=with_facts,
            with_potential_facts=with_potential_facts,
        )
        res = self._gql_client.execute(op)
        res = op + res
        return res.pagination_concept.list_concept

    @prettify
    def get_concepts_by_property_name(
        self,
        property_type_id: str,
        string_filter: str,
        exact: bool = False,
        with_aliases: bool = False,
        with_facts: bool = False,
        with_potential_facts=False,
    ) -> Union[Sequence[Concept], Sequence[objects.Concept]]:
        op = make_operation(Query, "get_concepts_by_property_name")
        cp: ConceptPagination = op.pagination_concept(
            filter_settings=ConceptFilterSettings(
                property_filter_settings=[
                    PropertyFilterSettings(
                        property_type_id=property_type_id,
                        string_filter=StringFilterInput(str=string_filter, exact=exact),
                    )
                ]
            )
        )
        self._configure_output_concept_fields(
            cp.list_concept(),
            with_aliases=with_aliases,
            with_facts=with_facts,
            with_potential_facts=with_potential_facts,
        )
        res = self._gql_client.execute(op)
        res = op + res
        return res.pagination_concept.list_concept

    @prettify
    def get_concept_properties(
        self, concept_id: str, filter_settings: Optional[ConceptPropertyFilterSettings] = None,
        with_documents: bool = False, with_facts: bool = False
    ) -> Union[Sequence[ConceptProperty], Sequence[objects.Property]]:
        filter_settings = filter_settings if filter_settings else ConceptPropertyFilterSettings()

        op = make_operation(Query, "get_concept_properties")
        concept: Concept = op.concept(id=concept_id)
        pcp: ConceptPropertyPagination = concept.pagination_concept_property(
            offset=0, limit=10000, filter_settings=filter_settings
        )
        self._configure_output_properties_fields(
            pcp.list_concept_property(), with_documents=with_documents, with_facts=with_facts
        )

        res = self._gql_client.execute(op)
        res = op + res  # type: Query
        return res.concept.pagination_concept_property.list_concept_property

    @prettify
    def get_concept_links(
        self, concept_id: str, with_link_properties: bool = False
    ) -> Union[Sequence[ConceptLink], Sequence[objects.Link]]:
        op = make_operation(Query, "get_concept_links")

        concept: Concept = op.concept(id=concept_id)
        pcl: ConceptLinkPagination = concept.pagination_concept_link(
            offset=0, limit=10000, filter_settings=ConceptLinkFilterSettings()
        )
        self._configure_output_link_fields(pcl.list_concept_link(), with_link_properties=with_link_properties)
        res = self._gql_client.execute(op)
        res = op + res  # type: Query
        return res.concept.pagination_concept_link.list_concept_link

    @prettify
    def get_concept_links_concept(
        self, concept_id: str, link_type_id: str, with_link_properties: bool = False
    ) -> Union[Sequence[ConceptLink], Sequence[objects.Link]]:
        op = make_operation(Query, "get_concept_links_concept")

        concept = op.concept(id=concept_id)
        pcl = concept.pagination_concept_link(
            offset=0, limit=10000, filter_settings=ConceptLinkFilterSettings(concept_link_type=[link_type_id])
        )
        self._configure_output_link_fields(pcl.list_concept_link(), with_link_properties=with_link_properties)
        res = self._gql_client.execute(op)
        res = op + res  # type: Query
        return res.concept.pagination_concept_link.list_concept_link

    @prettify
    def get_link_properties(
        self, link_id: str, with_facts: bool = False
    ) -> Union[Sequence[ConceptProperty], Sequence[objects.Property]]:
        op = make_operation(Query, "get_link_properties")
        concept_link: ConceptLink = op.concept_link(id=link_id)
        pcp: ConceptPropertyPagination = concept_link.pagination_concept_link_property(
            offset=0, limit=10000, filter_settings=ConceptPropertyFilterSettings()
        )
        self._configure_output_properties_fields(pcp.list_concept_property(), with_facts=with_facts)

        res = self._gql_client.execute(op)
        res = op + res  # type: Query
        return res.concept_link.pagination_concept_link_property.list_concept_property

    def get_concept_time_intervals(
        self, filter_settings: Optional[ConceptFilterSettings] = None, max_interval_size: Optional[int] = None
    ) -> Iterable[ObjectTimeInterval]:
        if not filter_settings:
            filter_settings = ConceptFilterSettings()
        yield from self._get_object_time_intervals(filter_settings, max_interval_size)

    def get_concept_link_time_intervals(
        self, filter_settings: Optional[ConceptLinkFilterSettings] = None, max_interval_size: Optional[int] = None
    ) -> Iterable[ObjectTimeInterval]:
        if not filter_settings:
            filter_settings = ConceptLinkFilterSettings()
        yield from self._get_object_time_intervals(filter_settings, max_interval_size)

    def get_document_time_intervals(
        self, filter_settings: Optional[DocumentFilterSettings] = None, max_interval_size: Optional[int] = None
    ) -> Iterable[ObjectTimeInterval]:
        if not filter_settings:
            filter_settings = DocumentFilterSettings()
        yield from self._get_object_time_intervals(filter_settings, max_interval_size)

    def _get_object_time_intervals(
        self,
        filter_settings: Union[ConceptFilterSettings, ConceptLinkFilterSettings, DocumentFilterSettings],
        max_interval_size: Optional[int] = None,
    ) -> Iterable[ObjectTimeInterval]:
        max_interval_size = max_interval_size if max_interval_size else self.kb_iterator_config.max_total_count

        creation_date_field_name = "creation_date"
        if isinstance(filter_settings, ConceptFilterSettings):
            object_count = self.get_concept_count(filter_settings)
        elif isinstance(filter_settings, ConceptLinkFilterSettings):
            object_count = self.get_concept_link_count(filter_settings)
        elif isinstance(filter_settings, DocumentFilterSettings):
            object_count = self.get_documents_count(filter_settings)
            creation_date_field_name = "registration_date"
        else:
            raise Exception("Time division is only available for concepts, links and documents")
        creation_date = getattr(filter_settings, creation_date_field_name, None)
        start: int = getattr(creation_date, "start", self.kb_iterator_config.earliest_created_time)
        end: int = getattr(creation_date, "end", int(time()))

        if (object_count > max_interval_size) and (start < end):
            middle = (end + start) // 2

            for mod_start, mod_end in (start, middle), (middle + 1, end):
                setattr(filter_settings, creation_date_field_name, TimestampIntervalInput(start=mod_start, end=mod_end))
                for time_interval in self._get_object_time_intervals(filter_settings, max_interval_size):
                    yield time_interval
        elif object_count > 0:
            yield ObjectTimeInterval(
                start_time=start, end_time=end, object_count=object_count, max_interval_size=max_interval_size
            )

    @prettify
    def create_concept(
        self,
        name: str,
        type_id: str,
        notes: Optional[str] = None,
        with_properties: bool = False,
        with_links: bool = False,
        with_link_properties: bool = False,
        perform_synchronously: Optional[bool] = None,
    ) -> Union[Concept, objects.Concept]:
        cmi: ConceptMutationInput = ConceptMutationInput(name=name, concept_type_id=type_id, notes=notes)
        return self._create_concept_with_input(
            cmi,
            with_properties=with_properties,
            with_links=with_links,
            with_link_properties=with_link_properties,
            perform_synchronously=perform_synchronously,
        )

    def _update_concept(
        self,
        concept_id: str,
        name: str,
        concept_type_id: str,
        markers: List[str],
        notes: str,
        access_level_id: str,
        perform_synchronously: Optional[bool] = None,
    ) -> Concept:
        perform_synchronously = self.get_perform_synchronously_value(perform_synchronously)
        op = make_operation(Mutation, "update_concept")
        uc: Concept = op.update_concept(
            performance_control=PerformSynchronously(perform_synchronously=perform_synchronously),
            form=ConceptUpdateInput(
                concept_id=concept_id,
                name=name,
                concept_type_id=concept_type_id,
                markers=markers,
                notes=notes,
                access_level_id=access_level_id,
            ),
        )
        self._configure_output_concept_fields(uc)
        res = self._gql_client.execute(op)
        res = op + res

        return res.update_concept

    @prettify
    def update_concept(
        self,
        c: Concept,
        markers: Optional[List[str]] = None,
        notes: Optional[str] = None,
        perform_synchronously: Optional[bool] = None,
    ) -> Union[Concept, objects.Concept]:
        return self._update_concept(
            concept_id=c.id,
            name=c.name,
            concept_type_id=c.concept_type.id,
            markers=markers if markers is not None else c.markers,
            notes=notes if notes is not None else c.notes,
            access_level_id=c.access_level.id,
            perform_synchronously=perform_synchronously,
        )

    def _update_link(
        self,
        link_id: str,
        access_level_id: str,
        notes: str,
    ) -> ConceptLink:
        op = make_operation(Mutation, "update_link")
        ucl: Concept = op.update_concept_link(
            form=ConceptLinkUpdateMutationInput(
                id=link_id,
                notes=notes,
                access_level_id=access_level_id,
            ),
        )
        self._configure_output_link_fields(ucl)
        res = self._gql_client.execute(op)
        res = op + res

        return res.update_concept_link

    @prettify
    def update_link(
        self,
        link: ConceptLink,
        notes: Optional[str] = None,
    ) -> ConceptLink:
        return self._update_link(
            link_id=link.id, notes=notes if notes is not None else link.notes, access_level_id=link.access_level.id
        )

    @prettify
    def update_concept_property_value_types(
        self, cpvt: ConceptPropertyValueType
    ) -> Union[ConceptPropertyValueType, object_types.BaseValueType]:
        op = make_operation(Mutation, "update_concept_property_value_types")
        ucpvt = op.update_concept_property_value_type(
            form=ConceptPropertyValueTypeUpdateInput(
                id=cpvt.id,
                name=cpvt.name,
                value_type=cpvt.value_type,
                pretrained_nercmodels=cpvt.pretrained_nercmodels,
                value_restriction=cpvt.value_restriction,
            )
        )
        ucpvt.__fields__(*self.cpvt_fields_truncated)
        res = self._gql_client.execute(op)
        res = op + res

        return res.update_concept_property_value_type

    @prettify
    @deprecated(details="Use update_concept_property method instead")
    def update_concept_string_property(self, cp: ConceptProperty) -> Union[ConceptProperty, objects.Property]:
        return self.update_concept_property(cp)

    @prettify
    @deprecated(details="Use update_concept_property method instead")
    def update_concept_int_property(self, cp: ConceptProperty) -> Union[ConceptProperty, objects.Property]:
        return self.update_concept_property(cp)

    def _get_value_input_by_value(self, value: Any, named_value_id: Optional[str] = None) -> ComponentValueInput:
        if isinstance(value, (StringValue, uas.StringValue)):
            value_input = ComponentValueInput(value=ValueInput(string_value_input=StringValueInput(str=value.value)))
        elif isinstance(value, (IntValue, uas.IntValue)):
            value_input = ComponentValueInput(value=ValueInput(int_value_input=IntValueInput(int=value.number)))
        elif isinstance(value, (DateTimeValue, uas.DateTimeValue)):
            date_input = DateInput(
                year=getattr(value.date, "year", None),
                month=getattr(value.date, "month", None),
                day=getattr(value.date, "day", None),
            )
            if all(
                (
                    hasattr(value, "time"),
                    hasattr(value.time, "hour"),
                    hasattr(value.time, "minute"),
                    hasattr(value.time, "second"),
                )
            ):
                time_input = TimeInput(hour=value.time.hour, minute=value.time.minute, second=value.time.second)
            else:
                time_input = None
            value_input = ComponentValueInput(
                value=ValueInput(date_time_value_input=DateTimeInput(date=date_input, time=time_input))
            )
        elif isinstance(value, (TimestampValue, uas.TimestampValue)):
            value_input = ComponentValueInput(
                value=ValueInput(timestamp_value_input=TimestampValueInput(value=value.unixtime))
            )
        elif isinstance(value, (StringLocaleValue, uas.StringLocaleValue)):
            value_input = ComponentValueInput(
                value=ValueInput(string_locale_value_input=StringLocaleValueInput(str=value.value, locale=value.locale))
            )
        elif isinstance(value, (LinkValue, uas.LinkValue)):
            value_input = ComponentValueInput(value=ValueInput(link_value_input=LinkValueInput(link=value.link)))
        elif isinstance(value, (DoubleValue, uas.DoubleValue)):
            value_input = ComponentValueInput(
                value=ValueInput(double_value_input=DoubleValueInput(double=value.double))
            )
        elif isinstance(value, (GeoPointValue, uas.GeoPointValue)):
            coordinates_input: Optional[CoordinatesInput] = None
            if hasattr(value.point, "latitude") and hasattr(value.point, "longitude"):
                coordinates_input = CoordinatesInput(latitude=value.point.latitude, longitude=value.point.longitude)
            value_input = ComponentValueInput(
                value=ValueInput(geo_point_value_input=GeoPointInput(name=value.name, point=coordinates_input))
            )
        else:
            raise NotImplementedError(f"{type(value)} type is not supported")

        if named_value_id:
            value_input.id = named_value_id
        return value_input

    @prettify
    def update_concept_property(self, cp: ConceptProperty) -> Union[ConceptProperty, objects.Property]:
        value_input = []
        if hasattr(cp.value, "list_value"):
            for value in cp.value.list_value:
                value_input.append(self._get_value_input_by_value(value.value, value.id))
        else:
            value_input.append(self._get_value_input_by_value(cp.value))
        return self._update_concept_property_with_input(cp.id, cp.is_main, value_input, cp.access_level.id)

    @prettify
    @deprecated(details="Use update_concept_property method instead")
    def update_concept_composite_property(self, cp: ConceptProperty) -> Union[ConceptProperty, objects.Property]:
        return self.update_concept_property(cp)

    def _update_concept_property_with_input(
        self,
        property_id: str,
        is_main: bool,
        value_input: List[ComponentValueInput],
        access_level_id: str,
    ) -> ConceptProperty:
        op = make_operation(Mutation, "update_concept_property_with_input")
        ucp: ConceptProperty = op.update_concept_property(
            form=ConceptPropertyUpdateInput(
                property_id=property_id,
                is_main=is_main,
                value_input=value_input,
                access_level_id=access_level_id,
            )
        )
        self._configure_output_properties_fields(ucp)
        res = self._gql_client.execute(op)
        res = op + res

        return res.update_concept_property

    @prettify
    def update_concept_property_with_input(
        self,
        concept_property: ConceptProperty,
        value_input: List[ComponentValueInput],
    ) -> Union[ConceptProperty, objects.Property]:
        return self._update_concept_property_with_input(
            property_id=concept_property.id,
            is_main=concept_property.is_main,
            value_input=value_input,
            access_level_id=concept_property.access_level.id,
        )

    def delete_concept_property(self, cp_id: str) -> bool:
        op = make_operation(Mutation, "delete_concept_property")
        dcp = op.delete_concept_property(id=cp_id)
        dcp.__fields__("is_success")
        res = self._gql_client.execute(op)
        res = op + res

        return res.delete_concept_property.is_success

    @prettify
    def get_all_concept_types(
        self,
        filter_settings: Optional[ConceptTypeFilterSettings] = None,
        direction: SortDirection = "ascending",
        sort_field: ConceptTypeSorting = "id",
    ) -> Union[Iterable[ConceptType], Iterable[object_types.ConceptType]]:
        current_step = 0
        while True:
            concept_types = self.get_concept_types(
                skip=current_step,
                take=self.limit,
                filter_settings=filter_settings,
                direction=direction,
                sort_field=sort_field,
            )
            if len(concept_types) < 1:
                break
            current_step += self.limit
            yield from concept_types

    @prettify
    def get_concept_types(
        self,
        skip: int = 0,
        take: Optional[int] = None,
        filter_settings: Optional[ConceptTypeFilterSettings] = None,
        direction: SortDirection = "ascending",
        sort_field: ConceptTypeSorting = "id",
    ) -> Union[Sequence[ConceptType], Sequence[object_types.ConceptType]]:
        op = make_operation(Query, "get_concept_types")
        take = self.get_take_value(take)
        if not filter_settings:
            filter_settings = ConceptTypeFilterSettings()
        pct: ConceptTypePagination = op.pagination_concept_type(
            direction=direction, filter_settings=filter_settings, limit=take, offset=skip, sort_field=sort_field
        )
        pct.list_concept_type().__fields__(*self.concept_type_fields)
        res = self._gql_client.execute(op)
        res = op + res
        return res.pagination_concept_type.list_concept_type

    def _get_concept_types_by_name(self, name: str) -> Sequence[ConceptType]:
        op = make_operation(Query, "get_concept_types_by_name")
        ctp: ConceptTypePagination = op.pagination_concept_type(filter_settings=ConceptTypeFilterSettings(name=name))
        ctp.list_concept_type().__fields__(*self.concept_type_fields)
        res = self._gql_client.execute(op)
        res = op + res
        return res.pagination_concept_type.list_concept_type

    @prettify
    def get_concept_types_by_name(self, name: str) -> Union[Sequence[ConceptType], Sequence[object_types.ConceptType]]:
        return self._get_concept_types_by_name(name)

    @prettify
    def get_concept_type_info(self, concept_type_id: str) -> Union[ConceptType, object_types.ConceptType]:
        op = make_operation(Query, "get_concept_type_info")
        ct = op.concept_type(id=concept_type_id)
        ct.__fields__(*self.concept_type_fields)
        lcpt = ct.list_concept_property_type()
        lcpt.__fields__(*self.concept_property_type_fields)
        lclt = ct.list_concept_link_type()
        lclt.__fields__(*self.concept_link_type_fields)
        lclt.list_concept_link_property_type().__fields__(*self.concept_property_type_fields)

        res = self._gql_client.execute(op)
        res = op + res
        return res.concept_type

    def _get_concept_type(self, concept_type_code: str) -> Optional[ConceptType]:
        concept_type = self._type_mapping.get_concept_type(concept_type_code)
        if concept_type:
            return concept_type

        concept_type_name = self._type_mapping.get_concept_type_name(concept_type_code)
        concept_types = self._get_concept_types_by_name(concept_type_name)
        for concept_type in concept_types:
            if concept_type.name == concept_type_name:
                self._type_mapping.add_concept_type(concept_type_code, concept_type)
                return concept_type
        return None

    @prettify
    def get_concept_type(self, concept_type_code: str) -> Union[ConceptType, object_types.ConceptType, None]:
        return self._get_concept_type(concept_type_code)

    @prettify
    def get_all_concept_property_types(
        self,
        filter_settings: Optional[ConceptPropertyTypeFilterSettings] = None,
        direction: SortDirection = "ascending",
        sort_field: ConceptPropertyTypeSorting = "name",
    ) -> Union[Iterable[ConceptPropertyType], Iterable[object_types.PropertyType]]:
        current_step = 0
        while True:
            concept_property_types = self.get_concept_property_types(
                skip=current_step,
                take=self.limit,
                filter_settings=filter_settings,
                direction=direction,
                sort_field=sort_field,
            )
            if len(concept_property_types) < 1:
                break
            current_step += self.limit
            yield from concept_property_types

    @prettify
    def get_concept_property_types(
        self,
        skip: int = 0,
        take: Optional[int] = None,
        filter_settings: Optional[ConceptPropertyTypeFilterSettings] = None,
        direction: SortDirection = "ascending",
        sort_field: ConceptPropertyTypeSorting = "name",
    ) -> Union[Sequence[ConceptPropertyType], Sequence[object_types.PropertyType]]:
        op = make_operation(Query, "get_concept_property_types")
        take = self.get_take_value(take)
        if not filter_settings:
            filter_settings = ConceptPropertyTypeFilterSettings()
        pcpt: ConceptPropertyTypePagination = op.pagination_concept_property_type(
            direction=direction, filter_settings=filter_settings, limit=take, offset=skip, sort_field=sort_field
        )
        lcpt = pcpt.list_concept_property_type()
        lcpt.__fields__(*self.concept_property_type_fields)
        self._configure_property_value_type_fields(lcpt.value_type, True)
        res = self._gql_client.execute(op)
        res = op + res
        return res.pagination_concept_property_type.list_concept_property_type

    def _get_concept_properties_types_by_name(
        self, concept_type_id: str, prop_name: str
    ) -> Sequence[ConceptPropertyType]:
        op = make_operation(Query, "get_concept_properties_types_by_name")
        cptp: ConceptPropertyTypePagination = op.pagination_concept_property_type(
            filter_settings=ConceptPropertyTypeFilterSettings(name=prop_name, concept_type_id=concept_type_id)
        )
        lcpt = cptp.list_concept_property_type()
        lcpt.__fields__(*self.concept_property_type_fields)
        self._configure_property_value_type_fields(lcpt.value_type, True)
        res = self._gql_client.execute(op)
        res = op + res
        return res.pagination_concept_property_type.list_concept_property_type

    @prettify
    def get_concept_properties_types_by_name(
        self, concept_type_id: str, prop_name: str
    ) -> Union[Sequence[ConceptPropertyType], Sequence[object_types.PropertyType]]:
        return self._get_concept_properties_types_by_name(concept_type_id, prop_name)

    @prettify
    def get_all_concept_composite_property_types(
        self,
        filter_settings: Optional[CompositePropertyTypeFilterSettings] = None,
        direction: SortDirection = "ascending",
        sort_field: CompositePropertyTypeSorting = "name",
    ) -> Union[Iterable[ConceptPropertyType], Iterable[object_types.PropertyType]]:
        current_step = 0
        while True:
            concept_composite_property_types = self.get_concept_composite_property_types(
                skip=current_step,
                take=self.limit,
                filter_settings=filter_settings,
                direction=direction,
                sort_field=sort_field,
            )
            if len(concept_composite_property_types) < 1:
                break
            current_step += self.limit
            yield from concept_composite_property_types

    @prettify
    def get_concept_composite_property_types(
        self,
        skip: int = 0,
        take: Optional[int] = None,
        filter_settings: Optional[CompositePropertyTypeFilterSettings] = None,
        direction: SortDirection = "ascending",
        sort_field: CompositePropertyTypeSorting = "name",
    ) -> Union[Sequence[ConceptPropertyType], Sequence[object_types.PropertyType]]:
        op = make_operation(Query, "get_concept_composite_property_types")
        take = self.get_take_value(take)
        if not filter_settings:
            filter_settings = CompositePropertyTypeFilterSettings()
        pccpt: ConceptPropertyTypePagination = op.pagination_composite_concept_property_type(
            direction=direction, filter_settings=filter_settings, limit=take, offset=skip, sort_field=sort_field
        )
        lcpt = pccpt.list_concept_property_type()
        lcpt.__fields__(*self.concept_property_type_fields)
        self._configure_property_value_type_fields(lcpt.value_type, True)
        res = self._gql_client.execute(op)
        res = op + res
        return res.pagination_composite_concept_property_type.list_concept_property_type

    def _get_concept_property_type(
        self, concept_type_code: str, property_type_code: str
    ) -> Optional[ConceptPropertyType]:
        property_type = self._type_mapping.get_concept_property_type(concept_type_code, property_type_code)
        if property_type:
            return property_type

        concept_type = self._get_concept_type(concept_type_code)
        if not concept_type:
            raise Exception("Cannot get concept property type: no concept type id")

        property_type_name = self._type_mapping.get_concept_property_type_name(concept_type_code, property_type_code)
        property_types = self._get_concept_properties_types_by_name(concept_type.id, property_type_name)
        for property_type in property_types:
            if property_type.name == property_type_name:
                self._type_mapping.add_concept_property_type(concept_type_code, property_type_code, property_type)
                return property_type
        return None

    @prettify
    def get_concept_property_type(
        self, concept_type_code: str, property_type_code: str
    ) -> Union[ConceptPropertyType, object_types.PropertyType, None]:
        return self._get_concept_property_type(concept_type_code, property_type_code)

    @prettify
    def get_all_concept_property_value_types(
        self,
        filter_settings: Optional[ConceptPropertyValueTypeFilterSettings] = None,
        direction: SortDirection = "ascending",
        sort_field: ConceptPropertyValueTypeSorting = "id",
    ) -> Union[Iterable[ConceptPropertyValueType], Iterable[object_types.BaseValueType]]:
        current_step = 0
        while True:
            concept_property_value_types = self.get_concept_property_value_types(
                skip=current_step,
                take=self.limit,
                filter_settings=filter_settings,
                direction=direction,
                sort_field=sort_field,
            )
            if len(concept_property_value_types) < 1:
                break
            current_step += self.limit
            yield from concept_property_value_types

    @prettify
    def get_concept_property_value_types(
        self,
        skip: int = 0,
        take: Optional[int] = None,
        filter_settings: Optional[ConceptPropertyValueTypeFilterSettings] = None,
        direction: SortDirection = "ascending",
        sort_field: ConceptPropertyValueTypeSorting = "id",
    ) -> Union[Sequence[ConceptPropertyValueType], Sequence[object_types.BaseValueType]]:
        op = make_operation(Query, "get_concept_property_value_types")
        take = self.get_take_value(take)
        if not filter_settings:
            filter_settings = ConceptPropertyValueTypeFilterSettings()
        pcpvt: ConceptPropertyValueTypePagination = op.pagination_concept_property_value_type(
            direction=direction, filter_settings=filter_settings, limit=take, offset=skip, sort_field=sort_field
        )
        pcpvt.list_concept_property_value_type().__fields__(*self.cpvt_fields)
        res = self._gql_client.execute(op)
        res = op + res
        return res.pagination_concept_property_value_type.list_concept_property_value_type

    def _get_concept_property_value_types_by_name(
        self, prop_value_type_name: str, limit: int = 20, offset: int = 0
    ) -> Sequence[ConceptPropertyValueType]:
        op = make_operation(Query, "get_concept_property_value_types_by_name")
        cpvtp: ConceptPropertyValueTypePagination = op.pagination_concept_property_value_type(
            filter_settings=ConceptPropertyValueTypeFilterSettings(name=prop_value_type_name),
            limit=limit,
            offset=offset,
        )
        cpvtp.list_concept_property_value_type().__fields__(*self.cpvt_fields)
        res = self._gql_client.execute(op)
        res = op + res
        return res.pagination_concept_property_value_type.list_concept_property_value_type

    @prettify
    def get_concept_property_value_types_by_name(
        self, prop_value_type_name: str, limit: int = 20, offset: int = 0
    ) -> Union[Sequence[ConceptPropertyValueType], Sequence[object_types.BaseValueType]]:
        return self._get_concept_property_value_types_by_name(prop_value_type_name, limit, offset)

    @prettify
    def get_concept_property_value_type(
        self, concept_property_value_type_code: str
    ) -> Union[ConceptPropertyValueType, object_types.BaseValueType, None]:
        property_value_type = self._type_mapping.get_concept_property_value_type(concept_property_value_type_code)
        if property_value_type:
            return property_value_type

        value_type_name = self._type_mapping.get_concept_property_value_type_name(concept_property_value_type_code)
        value_types = self._get_concept_property_value_types_by_name(value_type_name)
        for value_type in value_types:
            if value_type.name == value_type_name:
                self._type_mapping.add_concept_property_value_type(concept_property_value_type_code, value_type)
                return value_type
        return None

    @prettify
    def get_all_concept_link_property_types(
        self,
        filter_settings: Optional[ConceptPropertyTypeFilterSettings] = None,
        direction: SortDirection = "ascending",
        sort_field: ConceptPropertyTypeSorting = "name",
    ) -> Union[Iterable[ConceptPropertyType], Iterable[object_types.PropertyType]]:
        current_step = 0
        while True:
            concept_link_property_types = self.get_link_property_types(
                skip=current_step,
                take=self.limit,
                filter_settings=filter_settings,
                direction=direction,
                sort_field=sort_field,
            )
            if len(concept_link_property_types) < 1:
                break
            current_step += self.limit
            yield from concept_link_property_types

    @prettify
    def get_link_property_types(
        self,
        skip: int = 0,
        take: Optional[int] = None,
        filter_settings: Optional[ConceptPropertyTypeFilterSettings] = None,
        direction: SortDirection = "ascending",
        sort_field: ConceptPropertyTypeSorting = "name",
    ) -> Union[Sequence[ConceptPropertyType], Sequence[object_types.PropertyType]]:
        op = make_operation(Query, "get_link_property_types")
        take = self.get_take_value(take)
        if not filter_settings:
            filter_settings = ConceptPropertyTypeFilterSettings()
        pclpt: ConceptPropertyTypePagination = op.pagination_concept_link_property_type(
            direction=direction, filter_settings=filter_settings, limit=take, offset=skip, sort_field=sort_field
        )
        lcpt = pclpt.list_concept_property_type()
        lcpt.__fields__(*self.concept_property_type_fields)
        self._configure_property_value_type_fields(lcpt.value_type, True)
        res = self._gql_client.execute(op)
        res = op + res
        return res.pagination_concept_link_property_type.list_concept_property_type

    def _get_link_properties_types_by_name(self, link_type_id: str, prop_name: str) -> Sequence[ConceptPropertyType]:
        op = make_operation(Query, "_get_link_properties_types_by_name")
        cptp: ConceptPropertyTypePagination = op.pagination_concept_link_property_type(
            filter_settings=ConceptPropertyTypeFilterSettings(name=prop_name, concept_link_type_id=link_type_id)
        )
        lcpt = cptp.list_concept_property_type()
        lcpt.__fields__(*self.concept_property_type_fields)
        self._configure_property_value_type_fields(lcpt.value_type, True)
        res = self._gql_client.execute(op)
        res = op + res
        return res.pagination_concept_link_property_type.list_concept_property_type

    @prettify
    def get_link_properties_types_by_name(
        self, link_type_id: str, prop_name: str
    ) -> Union[Sequence[ConceptPropertyType], Sequence[object_types.PropertyType]]:
        return self._get_link_properties_types_by_name(link_type_id, prop_name)

    @prettify
    def get_all_concept_link_composite_property_types(
        self,
        filter_settings: Optional[CompositePropertyTypeFilterSettings] = None,
        direction: SortDirection = "ascending",
        sort_field: CompositePropertyTypeSorting = "name",
    ) -> Union[Iterable[ConceptPropertyType], Iterable[object_types.PropertyType]]:
        current_step = 0
        while True:
            concept_link_composite_property_types = self.get_link_composite_property_types(
                skip=current_step,
                take=self.limit,
                filter_settings=filter_settings,
                direction=direction,
                sort_field=sort_field,
            )
            if len(concept_link_composite_property_types) < 1:
                break
            current_step += self.limit
            yield from concept_link_composite_property_types

    @prettify
    def get_link_composite_property_types(
        self,
        skip: int = 0,
        take: Optional[int] = None,
        filter_settings: Optional[CompositePropertyTypeFilterSettings] = None,
        direction: SortDirection = "ascending",
        sort_field: CompositePropertyTypeSorting = "name",
    ) -> Union[Sequence[ConceptPropertyType], Sequence[object_types.PropertyType]]:
        op = make_operation(Query, "get_link_composite_property_types")
        take = self.get_take_value(take)
        if not filter_settings:
            filter_settings = CompositePropertyTypeFilterSettings()
        pclpt: ConceptPropertyTypePagination = op.pagination_composite_link_property_type(
            direction=direction, filter_settings=filter_settings, limit=take, offset=skip, sort_field=sort_field
        )
        lcpt = pclpt.list_concept_property_type()
        lcpt.__fields__(*self.concept_property_type_fields)
        self._configure_property_value_type_fields(lcpt.value_type, True)
        res = self._gql_client.execute(op)
        res = op + res
        return res.pagination_composite_link_property_type.list_concept_property_type

    def _get_composite_link_properties_types_by_name(
        self, link_type_id: str, prop_name: str
    ) -> Sequence[ConceptPropertyType]:
        op = make_operation(Query, "get_composite_link_properties_types_by_name")
        cptp: ConceptPropertyTypePagination = op.pagination_composite_link_property_type(
            filter_settings=CompositePropertyTypeFilterSettings(name=prop_name, link_type_id=link_type_id)
        )
        lcpt = cptp.list_concept_property_type()
        lcpt.__fields__(*self.concept_property_type_fields)
        self._configure_property_value_type_fields(lcpt.value_type, True)
        res = self._gql_client.execute(op)
        res = op + res
        return res.pagination_composite_link_property_type.list_concept_property_type

    @prettify
    def get_composite_link_properties_types_by_name(
        self, link_type_id: str, prop_name: str
    ) -> Union[Sequence[ConceptPropertyType], Sequence[object_types.PropertyType]]:
        return self._get_composite_link_properties_types_by_name(link_type_id, prop_name)

    def _get_link_property_type(self, link_type_code: str, property_type_code: str) -> Optional[ConceptPropertyType]:
        property_type = self._type_mapping.get_concept_link_property_type(link_type_code, property_type_code)
        if property_type:
            return property_type
        link_type = self._get_link_type(link_type_code)

        property_type_name = self._type_mapping.get_concept_link_property_type_name(link_type_code, property_type_code)
        property_types = self._get_link_properties_types_by_name(link_type.id, property_type_name)
        for property_type in property_types:
            if property_type.name == property_type_name:
                self._type_mapping.add_concept_link_property_type(link_type_code, property_type_code, property_type)
                return property_type
        return None

    @prettify
    def get_link_property_type(
        self, link_type_code: str, property_type_code: str
    ) -> Union[ConceptPropertyType, object_types.PropertyType, None]:
        return self._get_link_property_type(link_type_code, property_type_code)

    def _get_link_composite_property_type(
        self, link_type_code: str, property_type_code: str
    ) -> Optional[ConceptPropertyType]:
        property_type = self._type_mapping.get_concept_link_composite_property_type(link_type_code, property_type_code)
        if property_type:
            return property_type
        link_type = self._get_link_type(link_type_code)

        property_type_name = self._type_mapping.get_concept_link_composite_property_type_name(
            link_type_code, property_type_code
        )
        property_types = self._get_composite_link_properties_types_by_name(link_type.id, property_type_name)
        for property_type in property_types:
            if property_type.name == property_type_name:
                self._type_mapping.add_concept_link_composite_property_type(
                    link_type_code, property_type_code, property_type
                )
                return property_type
        return None

    @prettify
    def get_link_composite_property_type(
        self, link_type_code: str, property_type_code: str
    ) -> Union[ConceptPropertyType, object_types.PropertyType, None]:
        return self._get_link_composite_property_type(link_type_code, property_type_code)

    def _add_property_by_id(
        self,
        id: str,
        type_id: str,
        value: Any,
        is_main: bool,
        value_type: str,
        perform_synchronously: Optional[bool] = None,
    ) -> ConceptProperty:
        op = make_operation(Mutation, "add_property_by_id")
        acp = op.add_concept_property(
            performance_control=PerformSynchronously(
                perform_synchronously=self.get_perform_synchronously_value(perform_synchronously)
            ),
            form=ConceptPropertyCreateInput(
                concept_id=id,
                property_type_id=type_id,
                is_main=is_main,
                value_input=[ComponentValueInput(value=get_map_helper(value_type).get_value_input(value))],
            ),
        )
        self._configure_output_properties_fields(acp)
        res = self._gql_client.execute(op)
        res = op + res

        return res.add_concept_property

    @prettify
    def add_property_by_id(
        self,
        id: str,
        type_id: str,
        value: Any,
        is_main: bool,
        value_type: str,
        perform_synchronously: Optional[bool] = None,
    ) -> Union[ConceptProperty, objects.Property]:
        return self._add_property_by_id(id, type_id, value, is_main, value_type, perform_synchronously)

    def _add_concept_property_with_input_by_id(
        self,
        concept_id: str,
        property_type_id: str,
        value_input: List[ComponentValueInput],
        is_main: bool,
        perform_synchronously: Optional[bool] = None,
    ) -> ConceptProperty:
        op = make_operation(Mutation, "_add_property_with_input_by_id")
        acp = op.add_concept_property(
            performance_control=PerformSynchronously(
                perform_synchronously=self.get_perform_synchronously_value(perform_synchronously)
            ),
            form=ConceptPropertyCreateInput(
                concept_id=concept_id,
                property_type_id=property_type_id,
                is_main=is_main,
                value_input=value_input,
            ),
        )
        self._configure_output_properties_fields(acp)
        res = self._gql_client.execute(op)
        res = op + res

        return res.add_concept_property

    def _add_property(
        self,
        concept_id: str,
        concept_type_code: str,
        property_type_code: str,
        value: Any,
        is_main: bool = False,
        perform_synchronously: Optional[bool] = None,
    ) -> ConceptProperty:
        property_type: ConceptPropertyType = self._get_concept_property_type(concept_type_code, property_type_code)
        if not property_type:
            raise Exception("Cannot add property: no property type id")
        if isinstance(property_type.value_type, (CompositePropertyValueTemplate, uas.CompositePropertyValueTemplate)):
            component_values = self._type_mapping.get_concept_composite_property_component_values(
                concept_type_code, property_type_code
            )
            components_type_mapping: Dict[str, CompositePropertyValueType] = self._get_components_mapping(
                component_values, property_type.value_type.component_value_types
            )
            prop = self._add_composite_property_by_id(
                concept_id, property_type.id, value, is_main, components_type_mapping, perform_synchronously
            )
        else:
            prop = self._add_property_by_id(
                concept_id, property_type.id, value, is_main, property_type.value_type.value_type, perform_synchronously
            )
        if self.tdm_builder is not None:
            self.tdm_builder.add_concept_property_fact(prop, self._get_concept(concept_id), value, property_type)

        return prop

    @prettify
    def add_property(
        self,
        concept_id: str,
        concept_type_code: str,
        property_type_code: str,
        value: Any,
        is_main: bool = False,
        perform_synchronously: Optional[bool] = None,
    ) -> Union[ConceptProperty, objects.Property]:
        return self._add_property(
            concept_id=concept_id,
            concept_type_code=concept_type_code,
            property_type_code=property_type_code,
            value=value,
            is_main=is_main,
            perform_synchronously=perform_synchronously,
        )

    def _add_link_property_by_id(
        self,
        link_id: str,
        type_id: str,
        value: str,
        is_main: bool,
        value_type: str,
        perform_synchronously: Optional[bool] = None,
    ) -> ConceptProperty:
        op = make_operation(Mutation, "add_link_property_by_id")
        aclp = op.add_concept_link_property(
            performance_control=PerformSynchronously(
                perform_synchronously=self.get_perform_synchronously_value(perform_synchronously)
            ),
            form=ConceptLinkPropertyInput(
                property_type_id=type_id,
                link_id=link_id,
                is_main=is_main,
                value_input=[ComponentValueInput(value=get_map_helper(value_type).get_value_input(value))],
            ),
        )
        self._configure_output_properties_fields(aclp)
        res = self._gql_client.execute(op)
        res = op + res

        return res.add_concept_link_property

    @prettify
    def add_link_property_by_id(
        self,
        link_id: str,
        type_id: str,
        value: str,
        is_main: bool,
        value_type: str,
        perform_synchronously: Optional[bool] = None,
    ) -> Union[ConceptProperty, objects.Property]:
        return self._add_link_property_by_id(link_id, type_id, value, is_main, value_type, perform_synchronously)

    @prettify
    def add_concept_link_property_type(
        self, link_type_id: str, name: str, value_type_id: str
    ) -> Union[ConceptPropertyType, object_types.PropertyType]:
        op = make_operation(Mutation, "add_concept_link_property_type")
        aclpt = op.add_concept_link_property_type(
            form=ConceptLinkPropertyTypeCreationInput(
                link_type_id=link_type_id,
                name=name,
                value_type_id=value_type_id,
            )
        )
        aclpt.__fields__(*self.concept_property_type_fields)
        res = self._gql_client.execute(op)
        res = op + res

        return res.add_concept_link_property_type

    @prettify
    def update_concept_link_property_type(
        self, link_property_type_id: str, name: str, value_type_id: str
    ) -> Union[ConceptPropertyType, object_types.PropertyType]:
        op = make_operation(Mutation, "update_concept_link_property_type")
        acpt = op.update_concept_link_property_type(
            form=ConceptLinkPropertyTypeUpdateInput(
                id=link_property_type_id,
                name=name,
                value_type_id=value_type_id,
            )
        )
        acpt.__fields__(*self.concept_property_type_fields)
        res = self._gql_client.execute(op)
        res = op + res

        return res.update_concept_link_property_type

    def delete_concept_link_property_type(self, property_type_id: str) -> State:
        op = make_operation(Mutation, "delete_concept_link_property_type")
        op.delete_concept_link_property_type(id=property_type_id)
        res = self._gql_client.execute(op)
        res = op + res

        return res.delete_concept_link_property_type

    @prettify
    def add_concept_property_type(
        self, concept_type_id: str, name: str, value_type_id: str
    ) -> Union[ConceptPropertyType, object_types.PropertyType]:
        op = make_operation(Mutation, "add_concept_property_type")
        acpt = op.add_concept_property_type(
            form=ConceptPropertyTypeCreationInput(
                concept_type_id=concept_type_id,
                name=name,
                value_type_id=value_type_id,
            )
        )
        acpt.__fields__(*self.concept_property_type_fields)
        res = self._gql_client.execute(op)
        res = op + res

        return res.add_concept_property_type

    def delete_concept_property_type(self, property_type_id: str) -> State:
        op = make_operation(Mutation, "delete_concept_property_type")
        op.delete_concept_property_type(id=property_type_id)
        res = self._gql_client.execute(op)
        res = op + res

        return res.delete_concept_property_type

    def _add_link_composite_property_by_id(
        self,
        link_id: str,
        property_type_id: str,
        values: dict,
        components_type_mapping: Dict[str, CompositePropertyValueType],
        is_main: bool,
        perform_synchronously: Optional[bool] = None,
    ) -> ConceptProperty:
        op = make_operation(Mutation, "add_link_composite_property_by_id")
        aclp = op.add_concept_link_property(
            performance_control=PerformSynchronously(
                perform_synchronously=self.get_perform_synchronously_value(perform_synchronously)
            ),
            form=ConceptLinkPropertyInput(
                property_type_id=property_type_id,
                link_id=link_id,
                is_main=is_main,
                value_input=self._get_value_input(values, components_type_mapping),
            ),
        )
        self._configure_output_properties_fields(aclp)
        res = self._gql_client.execute(op)
        res = op + res

        return res.add_concept_link_property

    @prettify
    def add_link_composite_property_by_id(
        self,
        link_id: str,
        property_type_id: str,
        values: dict,
        components_type_mapping: Dict[str, CompositePropertyValueType],
        is_main: bool,
        perform_synchronously: Optional[bool] = None,
    ) -> Union[ConceptProperty, objects.Property]:
        return self._add_link_composite_property_by_id(
            link_id, property_type_id, values, components_type_mapping, is_main, perform_synchronously
        )

    def _add_composite_property_by_id(
        self,
        id: str,
        type_id: str,
        values: dict,
        is_main: bool,
        components_type_mapping: Dict[str, CompositePropertyValueType],
        perform_synchronously: Optional[bool] = None,
    ) -> ConceptProperty:
        op = make_operation(Mutation, "add_composite_property_by_id")
        acp = op.add_concept_property(
            performance_control=PerformSynchronously(
                perform_synchronously=self.get_perform_synchronously_value(perform_synchronously)
            ),
            form=ConceptPropertyCreateInput(
                concept_id=id,
                property_type_id=type_id,
                is_main=is_main,
                value_input=self._get_value_input(values, components_type_mapping),
            ),
        )
        self._configure_output_properties_fields(acp)
        res = self._gql_client.execute(op)
        res = op + res

        return res.add_concept_property

    @prettify
    def add_composite_property_by_id(
        self,
        id: str,
        type_id: str,
        values: dict,
        is_main: bool,
        components_type_mapping: Dict[str, CompositePropertyValueType],
        perform_synchronously: Optional[bool] = None,
    ) -> Union[ConceptProperty, objects.Property]:
        return self._add_composite_property_by_id(
            id, type_id, values, is_main, components_type_mapping, perform_synchronously
        )

    def _add_link_property_with_input_by_id(
        self,
        link_id: str,
        property_type_id: str,
        value_input: List[ComponentValueInput],
        is_main: bool,
        perform_synchronously: Optional[bool] = None,
    ) -> ConceptProperty:
        op = make_operation(Mutation, "_add_link_property_with_input_by_id")
        aclp = op.add_concept_link_property(
            performance_control=PerformSynchronously(
                perform_synchronously=self.get_perform_synchronously_value(perform_synchronously)
            ),
            form=ConceptLinkPropertyInput(
                property_type_id=property_type_id,
                link_id=link_id,
                is_main=is_main,
                value_input=value_input,
            ),
        )
        self._configure_output_properties_fields(aclp)
        res = self._gql_client.execute(op)
        res = op + res

        return res.add_concept_link_property

    def _add_link_property(
        self,
        link_id: str,
        link_type_code: str,
        property_type_code: str,
        value: Any,
        is_composite: Optional[bool] = False,
        is_main: bool = False,
        perform_synchronously: Optional[bool] = None,
    ) -> ConceptProperty:
        property_type = (
            self._get_link_composite_property_type(link_type_code, property_type_code)
            if is_composite
            else self._get_link_property_type(link_type_code, property_type_code)
        )
        if not property_type:
            raise Exception("Cannot add property: no property type id")

        if is_composite:
            component_values = self._type_mapping.get_concept_link_composite_property_component_values(
                link_type_code, property_type_code
            )
            components_type_mapping: Dict[str, CompositePropertyValueType] = self._get_components_mapping(
                component_values, property_type.value_type.component_value_types
            )

            link_property = self._add_link_composite_property_by_id(
                link_id,
                property_type.id,
                value,
                components_type_mapping,
                is_main,
                perform_synchronously,
            )
        else:
            link_property = self._add_link_property_by_id(
                link_id,
                property_type.id,
                value,
                is_main,
                property_type.value_type.value_type,
                perform_synchronously,
            )

        if self.tdm_builder is not None:
            self.tdm_builder.add_link_property_fact(
                link_property, self._get_concept_link(link_id), value, property_type
            )

        return link_property

    @prettify
    def add_link_property(
        self,
        link_id: str,
        link_type_code: str,
        property_type_code: str,
        value: Any,
        is_composite: Optional[bool] = False,
        is_main: bool = False,
        perform_synchronously: Optional[bool] = None,
    ) -> Union[ConceptProperty, objects.Property]:
        return self._add_link_property(
            link_id=link_id,
            link_type_code=link_type_code,
            property_type_code=property_type_code,
            value=value,
            is_composite=is_composite,
            is_main=is_main,
            perform_synchronously=perform_synchronously,
        )

    @prettify
    def get_all_concept_link_types(
        self,
        filter_settings: Optional[ConceptLinkTypeFilterSettings] = None,
        direction: SortDirection = "ascending",
        sort_field: ConceptLinkTypeSorting = "id",
    ) -> Union[Iterable[ConceptLinkType], Iterable[object_types.LinkType]]:
        current_step = 0
        while True:
            concept_link_types = self.get_concept_link_types(
                skip=current_step,
                take=self.limit,
                filter_settings=filter_settings,
                direction=direction,
                sort_field=sort_field,
            )
            if len(concept_link_types) < 1:
                break
            current_step += self.limit
            yield from concept_link_types

    @prettify
    def get_concept_link_types(
        self,
        skip: int = 0,
        take: Optional[int] = None,
        filter_settings: Optional[ConceptLinkTypeFilterSettings] = None,
        direction: SortDirection = "ascending",
        sort_field: ConceptLinkTypeSorting = "id",
    ) -> Union[Sequence[ConceptLinkType], Sequence[object_types.LinkType]]:
        op = make_operation(Query, "get_concept_link_types")
        take = self.get_take_value(take)
        if not filter_settings:
            filter_settings = ConceptLinkTypeFilterSettings()
        pclt: ConceptLinkTypePagination = op.pagination_concept_link_type(
            direction=direction, filter_settings=filter_settings, limit=take, offset=skip, sort_field=sort_field
        )
        lclt = pclt.list_concept_link_type()
        lclt.__fields__(*self.concept_link_type_fields)
        lclt.concept_from_type().__fields__(*self.concept_type_fields)
        lclt.concept_to_type().__fields__(*self.concept_type_fields)
        res = self._gql_client.execute(op)
        res = op + res
        return res.pagination_concept_link_type.list_concept_link_type

    def _get_concept_link_type_by_name(
        self, link_name: str, from_type_id: str, to_type_id: str, limit: int = 20
    ) -> Sequence[ConceptLinkType]:
        op = make_operation(Query, "get_concept_link_type_by_name")
        pclt: ConceptLinkTypePagination = op.pagination_concept_link_type(
            filter_settings=ConceptLinkTypeFilterSettings(
                name=link_name, concept_from_type_id=from_type_id, concept_to_type_id=to_type_id
            ),
            limit=limit,
        )
        lclt = pclt.list_concept_link_type()
        lclt.__fields__(*self.concept_link_type_fields)
        lclt.concept_from_type().__fields__(*self.concept_type_fields)
        lclt.concept_to_type().__fields__(*self.concept_type_fields)
        res = self._gql_client.execute(op)
        res = op + res
        return res.pagination_concept_link_type.list_concept_link_type

    @prettify
    def get_concept_link_type_by_name(
        self, link_name: str, from_type_id: str, to_type_id: str, limit: int = 20
    ) -> Union[Sequence[ConceptLinkType], Sequence[object_types.LinkType]]:
        return self._get_concept_link_type_by_name(link_name, from_type_id, to_type_id, limit)

    def _get_link_type(self, link_type_code: str) -> Optional[ConceptLinkType]:
        link_type = self._type_mapping.get_concept_link_type(link_type_code)
        if link_type:
            return link_type

        concept_from_type_code = self._type_mapping.get_source_concept_type_code(link_type_code)
        concept_to_type_code = self._type_mapping.get_target_concept_type_code(link_type_code)
        concept_from_type = self._get_concept_type(concept_from_type_code)
        concept_to_type = self._get_concept_type(concept_to_type_code)
        link_type_name = self._type_mapping.get_concept_link_type_name(link_type_code)
        link_types = self._get_concept_link_type_by_name(link_type_name, concept_from_type.id, concept_to_type.id)
        for link_type in link_types:
            if link_type.name == link_type_name:
                self._type_mapping.add_concept_link_type(link_type_code, link_type)
                return link_type
        return None

    @prettify
    def get_link_type(self, link_type_code: str) -> Union[ConceptLinkType, object_types.LinkType, None]:
        return self._get_link_type(link_type_code)

    def _add_relation_by_id(
        self, from_id: str, to_id: str, link_type_id: str, perform_synchronously: Optional[bool] = None
    ) -> ConceptLink:
        op = make_operation(Mutation, "add_relation_by_id")
        acl = op.add_concept_link(
            performance_control=PerformSynchronously(
                perform_synchronously=self.get_perform_synchronously_value(perform_synchronously)
            ),
            form=ConceptLinkCreationMutationInput(
                concept_from_id=from_id, concept_to_id=to_id, link_type_id=link_type_id
            ),
        )
        self._configure_output_link_fields(acl)

        res = self._gql_client.execute(op)
        res = op + res

        return res.add_concept_link

    @prettify
    def add_relation_by_id(
        self, from_id: str, to_id: str, link_type_id: str, perform_synchronously: Optional[bool] = None
    ) -> Union[ConceptLink, objects.Link]:
        return self._add_relation_by_id(from_id, to_id, link_type_id, perform_synchronously)

    @prettify
    def add_relation(
        self,
        concept_from_id: str,
        concept_to_id: str,
        type_code: str,
        perform_synchronously: Optional[bool] = None,
    ) -> Union[ConceptLink, objects.Link]:
        link_type = self._get_link_type(type_code)
        if not link_type:
            raise Exception("Cannot add relation: no link type")
        relation = self._add_relation_by_id(
            concept_from_id, concept_to_id, link_type.id, perform_synchronously=perform_synchronously
        )

        if self.tdm_builder is not None:
            self.tdm_builder.add_link_fact(relation)

        return relation

    def delete_documents(self, document_ids: List[str]) -> bool:
        op = make_operation(Mutation, "delete_documents")
        dd = op.delete_documents(ids=document_ids)
        dd.__fields__("is_success")
        res = self._gql_client.execute(op)
        res = op + res

        return res.delete_documents.is_success

    def delete_concept(self, concept_id: str) -> bool:
        return self.delete_concepts([concept_id])

    def delete_concepts(self, concept_ids: List[str]) -> bool:
        op = make_operation(Mutation, "delete_concept")
        dc = op.delete_concept(ids=concept_ids)
        dc.__fields__("is_success")
        res = self._gql_client.execute(op)
        res = op + res

        return res.delete_concept.is_success

    def delete_concept_link(self, link_id: str) -> bool:
        op = make_operation(Mutation, "delete_concept_link")
        dcl: ConceptLink = op.delete_concept_link(id=link_id)
        dcl.__fields__("is_success")
        res = self._gql_client.execute(op)
        res = op + res

        return res.delete_concept_link.is_success

    def delete_concept_link_property(self, link_property_id: str) -> bool:
        op = make_operation(Mutation, "delete_concept_link_property")
        clp: ConceptProperty = op.delete_concept_link_property(id=link_property_id)
        clp.__fields__("is_success")
        res = self._gql_client.execute(op)
        res = op + res

        return res.delete_concept_link_property.is_success

    @prettify
    def add_concept_markers(
        self, concept_id: str, markers: List[str], perform_synchronously: Optional[bool] = None
    ) -> Union[Concept, objects.Concept]:
        c = self._get_concept(concept_id)
        c.markers.extend(markers)
        new_markers = list(set(c.markers))
        return self.update_concept(c, markers=new_markers, perform_synchronously=perform_synchronously)

    @prettify
    def set_concept_markers(
        self, concept_id: str, markers: List[str], perform_synchronously: Optional[bool] = None
    ) -> Union[Concept, objects.Concept]:
        c = self._get_concept(concept_id)
        return self.update_concept(c, markers=markers, perform_synchronously=perform_synchronously)

    def get_concept_presentation(self, root_concept_id: str, concept_type_presentation_id: str) -> ConceptPresentation:
        op = make_operation(Query, "get_concept_presentation")
        cp: ConceptPresentation = op.concept_presentation(
            root_concept_id=root_concept_id, concept_type_presentation_id=concept_type_presentation_id
        )
        self._configure_output_concept_fields(
            cp.root_concept, with_aliases=False, with_link_properties=False, with_links=False, with_properties=False
        )
        lwt = cp.concept_type_presentation().list_widget_type()
        lwt.__fields__(*self.concept_presentation_widget_type)
        lwt.columns_info.__fields__(*self.concept_presentation_widget_type_columns_info)

        res = self._gql_client.execute(op)
        res = op + res
        return res.concept_presentation

    def get_single_widget(
        self,
        root_concept_id: str,
        concept_type_presentation_id: str,
        widget_type_id: str,
        limit: int = 20,
        offset: int = 0,
    ) -> ConceptPresentationWidgetRowPagination:
        op = make_operation(Query, "get_single_widget")
        cp: ConceptPresentation = op.concept_presentation(
            root_concept_id=root_concept_id, concept_type_presentation_id=concept_type_presentation_id
        )
        psw: ConceptPresentationWidgetRowPagination = cp.paginate_single_widget(
            widget_type_id=widget_type_id, limit=limit, offset=offset
        )
        psw.__fields__("total")
        self._configure_output_value_fields(psw.rows, with_composite_values=True, with_object_values=True)

        res = self._gql_client.execute(op)
        res = op + res
        return res.concept_presentation.paginate_single_widget

    def add_concept_fact(self, concept_id: str, document_id: str) -> State:
        op = make_operation(Mutation, "add_concept_fact")
        op.add_concept_fact(id=concept_id, fact=FactInput(document_id=document_id))
        res = self._gql_client.execute(op)
        res = op + res
        return res.add_concept_fact

    def delete_concept_fact(self, fact_id: str) -> State:
        op = make_operation(Mutation, "delete_concept_fact")
        op.delete_concept_fact(
            id=fact_id,
        )
        res = self._gql_client.execute(op)
        res = op + res
        return res.delete_concept_fact

    def add_concept_property_fact(self, property_id: str, document_id: str) -> State:
        op = make_operation(Mutation, "add_concept_property_fact")
        op.add_concept_property_fact(id=property_id, fact=FactInput(document_id=document_id))
        res = self._gql_client.execute(op)
        res = op + res
        return res.add_concept_property_fact

    def delete_concept_property_fact(self, fact_id: str) -> State:
        op = make_operation(Mutation, "delete_concept_property_fact")
        op.delete_concept_property_fact(
            id=fact_id,
        )
        res = self._gql_client.execute(op)
        res = op + res
        return res.delete_concept_property_fact

    def add_concept_link_fact(self, link_id: str, document_id: str) -> State:
        op = make_operation(Mutation, "add_concept_link_fact")
        op.add_concept_link_fact(id=link_id, fact=FactInput(document_id=document_id))
        res = self._gql_client.execute(op)
        res = op + res
        return res.add_concept_link_fact

    def delete_concept_link_fact(self, fact_id: str) -> State:
        op = make_operation(Mutation, "delete_concept_link_fact")
        op.delete_concept_link_fact(
            id=fact_id,
        )
        res = self._gql_client.execute(op)
        res = op + res
        return res.delete_concept_link_fact

    def add_concept_link_property_fact(self, link_property_id: str, document_id: str) -> State:
        op = make_operation(Mutation, "add_concept_link_property_fact")
        op.add_concept_link_property_fact(id=link_property_id, fact=FactInput(document_id=document_id))
        res = self._gql_client.execute(op)
        res = op + res
        return res.add_concept_link_property_fact

    def delete_concept_link_property_fact(self, fact_id: str) -> State:
        op = make_operation(Mutation, "delete_concept_link_property_fact")
        op.delete_concept_link_property_fact(
            id=fact_id,
        )
        res = self._gql_client.execute(op)
        res = op + res
        return res.delete_concept_link_property_fact

    def update_document_node(
        self, document_id: str, node_id: str, target: str, translation: str, source: Optional[str] = None
    ) -> Document:
        op = make_operation(Mutation, "update_document_node")
        udn: Document = op.update_document_node(
            form=DocumentNodeUpdateInput(
                id=document_id,
                node_id=node_id,
                language=LanguageUpdateInput(id=source),
                translation=TranslationInput(language=LanguageInput(id=target), text=translation),
            )
        )
        self._configure_output_document_fields(udn)
        res = self._gql_client.execute(op)
        res = op + res

        return res.update_document_node

    @prettify
    def merge_concepts(self, c_main_id: str, c_merged_id: str) -> Union[Concept, objects.Concept]:
        op = make_operation(Mutation, "merge_concepts")
        mc: Concept = op.merge_concepts(
            form=ConceptMergeInput(main_concept_id=c_main_id, merged_concept_id=c_merged_id)
        )
        self._configure_output_concept_fields(mc)
        res = self._gql_client.execute(op)
        res = op + res

        return res.merge_concepts

    @prettify
    def unmerge_concepts(self, c_main_id: str, c_merged_id: List[str]) -> Union[Concept, objects.Concept]:
        op = make_operation(Mutation, "unmerge_concepts")
        umc: Concept = op.unmerge_concepts(
            form=ConceptUnmergeInput(main_concept_id=c_main_id, merged_concept_id=c_merged_id)
        )
        self._configure_output_concept_fields(umc)
        res = self._gql_client.execute(op)
        res = op + res

        return res.unmerge_concepts

    def get_platforms(
        self,
        skip: int = 0,
        take: Optional[int] = None,
        filter_settings: Optional[PlatformFilterSettings] = None,
        direction: SortDirection = "descending",
        sort_field: PlatformSorting = "id",
        with_metric: bool = False,
    ) -> Sequence[Platform]:
        op = make_operation(Query, "get_platforms")
        take = self.get_take_value(take)
        pp: PlatformPagination = op.pagination_platform(
            offset=skip,
            limit=take,
            filter_settings=filter_settings if filter_settings else PlatformFilterSettings(),
            direction=direction,
            sort_field=sort_field,
        )
        self._configure_output_platform_fields(pp.list_platform(), with_metric)

        res = self._gql_client.execute(op)
        res = op + res
        return res.pagination_platform.list_platform

    def update_platform(
        self,
        platform_id: str,
        name: str,
        new_platform_id: str,
        platform_type: str,
        url: str,
        start_date: DateTimeInput,
        country: Optional[str] = None,
        language: Optional[str] = None,
        markers: List[str] = None,
    ) -> Platform:
        op = make_operation(Mutation, "update_platform")
        up: Platform = op.update_platform(
            form=PlatformUpdateInput(
                platform_id=platform_id,
                name=name,
                new_id=new_platform_id,
                platform_type=platform_type,
                url=url,
                start_date=start_date,
                country=country,
                language=language,
                markers=markers if markers else [],
            )
        )
        self._configure_output_platform_fields(up)
        res = self._gql_client.execute(op)
        res = op + res

        return res.update_platform

    def get_accounts(
        self,
        skip: int = 0,
        take: Optional[int] = None,
        filter_settings: Optional[AccountFilterSettings] = None,
        direction: SortDirection = "descending",
        sort_field: PlatformSorting = "id",
        with_metric: bool = False,
    ) -> Sequence[Account]:
        op = make_operation(Query, "get_accounts")
        take = self.get_take_value(take)
        ap: AccountPagination = op.pagination_account(
            offset=skip,
            limit=take,
            filter_settings=filter_settings if filter_settings else AccountFilterSettings(),
            direction=direction,
            sort_field=sort_field,
        )
        self._configure_output_account_fields(ap.list_account(), with_metric)

        res = self._gql_client.execute(op)
        res = op + res
        return res.pagination_account.list_account

    def update_account(
        self,
        account_id: str,
        platform_id: str,
        name: str,
        new_account_id: str,
        url: str,
        start_date: DateTimeInput,
        country: Optional[str] = None,
        markers: List[str] = None,
    ) -> Account:
        op = make_operation(Mutation, "update_account")
        ua: Account = op.update_account(
            form=AccountUpdateInput(
                account_id=account_id,
                platform_id=platform_id,
                name=name,
                new_id=new_account_id,
                url=url,
                start_date=start_date,
                country=country,
                markers=markers if markers else [],
            )
        )
        self._configure_output_account_fields(ua)
        res = self._gql_client.execute(op)
        res = op + res

        return res.update_account

    # region Crawlers methods

    def get_crawler_start_urls(self, take: Optional[int] = None) -> Sequence[Crawler]:
        op = make_operation(CrQuery, "get_crawler_start_urls")
        take = self.get_take_value(take)
        pc: CrawlerPagination = op.pagination_crawler(limit=take)
        lc = pc.list_crawler()
        lc.__fields__("start_urls")

        res = self._gql_client.execute(op)
        res = op + res
        return res.pagination_crawler.list_crawler

    # endregion

    # region Utils methods

    @prettify
    @check_utils_gql_client
    def create_or_get_concept_by_name(
        self,
        name: str,
        type_id: str,
        notes: Optional[str] = None,
        take_first_result: bool = False,
        with_properties: bool = False,
        with_links: bool = False,
        with_link_properties: bool = False,
        with_facts: bool = False,
        with_potential_facts: bool = False,
        with_metrics: bool = False,
    ) -> Union[Concept, objects.Concept]:
        """Finds concept by near name"""
        op = make_operation(uas.Mutation, "create_or_get_concept_by_name")
        if type_id:
            concept_filter_settings = uas.ConceptFilterSettings(exact_name=name, concept_type_ids=[type_id])
        else:
            concept_filter_settings = uas.ConceptFilterSettings(exact_name=name)
        goac = op.get_or_add_concept_internal(
            filter_settings=concept_filter_settings,
            form=uas.ConceptMutationInput(name=name, concept_type_id=type_id, notes=notes),
            take_first_result=take_first_result,
        )
        self._configure_output_concept_fields(
            goac,
            with_properties=with_properties,
            with_links=with_links,
            with_link_properties=with_link_properties,
            with_facts=with_facts,
            with_potential_facts=with_potential_facts,
            with_metrics=with_metrics,
        )

        res = self._utils_gql_client.execute(op)
        res = op + res  # type: uas.Mutation

        if self.tdm_builder is not None:
            self.tdm_builder.add_concept_fact(res.get_or_add_concept_internal)

        return res.get_or_add_concept_internal

    @check_utils_gql_client
    def get_tdm(self, doc_id: str) -> str:
        op = make_operation(uas.Query, "get_tdm")
        op.tdm_internal(id=doc_id)
        res = self._utils_gql_client.execute(op)
        res = op + res
        return res.tdm_internal

    @check_utils_gql_client
    def get_new_tdm(self, doc_id: str) -> str:
        op = make_operation(uas.Query, "get_new_tdm")
        op.tdm_new_internal(id=doc_id)
        res = self._utils_gql_client.execute(op)
        res = op + res
        return res.tdm_new_internal

    # endregion

    # region tcontroller methods

    def get_pipeline_configs(
        self,
        with_transforms: bool = True,
        filter_settings: Optional[tc.PipelineConfigFilter] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort_by: tc.PipelineConfigSort = "id",
        sort_direction: tc.SortDirection = "ascending",
    ) -> tc.PipelineConfigList:
        op = make_operation(tc.Query, "get_pipeline_configs")
        pcl: tc.PipelineConfigList = op.pipeline_configs(
            filter=filter_settings, limit=limit, offset=offset, sort_by=sort_by, sort_direction=sort_direction
        )
        pc = pcl.pipeline_configs()
        pc.__fields__(*self.pipeline_config_fields)
        if with_transforms:
            pc.transforms().__fields__("id")
            pc.transforms().__fields__("params")
        res = self._gql_client.execute(op)
        res = op + res
        return res.pipeline_configs

    def get_pipeline_topics(
        self,
        filter_settings: Optional[tc.KafkaTopicFilter] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort_by: tc.KafkaTopicSort = "topic",
        sort_direction: tc.SortDirection = "ascending",
    ) -> tc.KafkaTopicList:
        op = make_operation(tc.Query, "get_pipeline_topics")
        ktl: tc.KafkaTopicList = op.kafka_topics(
            filter=filter_settings, limit=limit, offset=offset, sort_by=sort_by, sort_direction=sort_direction
        )
        self._configure_pipeline_topic_fields(ktl.topics())
        res = self._gql_client.execute(op)
        res = op + res
        return res.kafka_topics

    def upsert_pipeline_topic(self, topic_id: str, config_id: str, stopped: bool) -> tc.KafkaTopic:
        op = make_operation(tc.Mutation, "upsert_pipeline_topic")
        kt: tc.KafkaTopic = op.put_kafka_topic(
            topic=topic_id, pipeline=tc.PipelineSetupInput(pipeline_config=config_id), stopped=stopped
        )
        self._configure_pipeline_topic_fields(kt)
        res = self._gql_client.execute(op)
        res = op + res
        return res.put_kafka_topic

    def get_failed_messages_from_topic(
        self,
        topic_id: str,
        filter_settings: Optional[tc.MessageFilter] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        sort_by: tc.MessageSort = "timestamp",
        sort_direction: tc.SortDirection = "descending",
    ) -> tc.FailedMessageList:
        op = make_operation(tc.Query, "get_failed_messages_from_topic")
        fm: tc.FailedMessageList = op.failed_messages(
            topic=topic_id,
            filter=filter_settings,
            offset=offset,
            limit=limit,
            sort_by=sort_by,
            sort_direction=sort_direction,
        )
        fm.messages().id()
        fm.messages().info().error().description()
        fm.messages().info().message()
        res = self._gql_client.execute(op)
        res = op + res
        return res.failed_messages

    def get_ok_messages_from_topic(
        self,
        topic_id: str,
        filter_settings: Optional[tc.MessageFilter] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        sort_by: tc.MessageSort = "timestamp",
        sort_direction: tc.SortDirection = "descending",
    ) -> tc.CompletedOkMessageList:
        op = make_operation(tc.Query, "get_ok_messages_from_topic")
        om: tc.CompletedOkMessageList = op.completed_ok_messages(
            topic=topic_id,
            filter=filter_settings,
            offset=offset,
            limit=limit,
            sort_by=sort_by,
            sort_direction=sort_direction,
        )
        om.messages().id()
        om.messages().info().message()
        res = self._gql_client.execute(op)
        res = op + res
        return res.completed_ok_messages

    def get_active_messages_from_topic(
        self,
        topic_id: str,
        filter_settings: Optional[tc.MessageFilter] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        sort_by: tc.MessageSort = "timestamp",
        sort_direction: tc.SortDirection = "descending",
    ) -> tc.CompletedOkMessageList:
        op = make_operation(tc.Query, "get_active_messages_from_topic")
        am: tc.CompletedOkMessageList = op.active_messages(
            topic=topic_id,
            filter=filter_settings,
            offset=offset,
            limit=limit,
            sort_by=sort_by,
            sort_direction=sort_direction,
        )
        am.messages().id()
        am.messages().info().message()
        res = self._gql_client.execute(op)
        res = op + res
        return res.active_messages

    def retry_failed_in_topic(self, topic_id: str) -> int:
        op = make_operation(tc.Mutation, "retry_failed_in_topic")
        op.retry_failed_in_topic(topic=topic_id)
        res = self._gql_client.execute(op)
        res = op + res
        return res.retry_failed_in_topic

    def reprocess_documents(
        self,
        topic_id: str,
        filter_settings: Optional[DocumentFilterSettings] = None,
        extra_settings: Optional[ExtraSettings] = None,
        priority: tc.MessagePriority = "Normal",
        use_kb=False,
    ) -> Iterable[Union[str, Exception]]:
        # TODO: Required to redesign method to work with
        # sequence of documents' ids as arguments instead of filter settings objects
        documents = self.get_all_documents(
            filter_settings=filter_settings,
            extra_settings=extra_settings,
        )
        if documents is None:
            return []
        else:
            uuids = (doc.main.uuid for doc in documents)

        yield from self.reprocess_messages(topic_id=topic_id, message_ids=uuids, priority=priority, use_kb=use_kb)

    def reprocess_messages(
        self,
        topic_id: str,
        message_ids: Iterable[str],
        priority: tc.MessagePriority = "Normal",
        use_kb: bool = False,
    ) -> Iterable[Union[str, Exception]]:
        import sgqlc.types

        mut = make_operation(
            tc.Mutation,
            "reprocess_messages",
            {
                "messageId": sgqlc.types.Arg(sgqlc.types.non_null(tc.ID)),
            },
        )
        mut.reprocess_message(
            message_id=sgqlc.types.Variable("messageId"), topic=topic_id, use_kb=use_kb, priority=priority
        )

        for msg_id in message_ids:
            try:
                res = self._gql_client.execute(mut, variables={"messageId": msg_id})
                res = mut + res
                yield res.reprocess_message
            except Exception as ex:
                yield ex

    def add_message_to_topic(
        self, topic_id: str, message: dict, priority: tc.MessagePriority = "Normal"
    ) -> tc.MessageStatus:
        op = make_operation(tc.Mutation, "add_message_to_topic")
        ms: tc.MessageStatus = op.add_message(topic=topic_id, message=json.dumps(message), priority=priority)
        ms.id()
        ms.info()
        res = self._gql_client.execute(op)
        res = op + res
        return res.add_message

    # endregion

    # region translator methods

    def translate_str(self, text: str, target: str, source: Optional[str] = None) -> str:
        op = make_operation(ts.Query, "translate_str")
        op.translate_str(text=text, target=target, source=source)
        res = self._gql_client.execute(op)
        res = op + res
        return res.translate_str

    # endregion
