from simple_error_log.errors import Errors
from simple_error_log.error_location import KlassMethodLocation
from usdm4.builder.builder import Builder

from usdm4.api.study import Study
from usdm4.api.study_version import StudyVersion
from usdm4.api.study_design import StudyDesign
from usdm4.api.study_definition_document import StudyDefinitionDocument
from usdm4.api.study_definition_document_version import StudyDefinitionDocumentVersion

from usdm4_excel.import_.study_design.actions.study_design import StudyDesignAction

from usdm4_excel.import_.general.notes_sheet import NotesSheet
from usdm4_excel.import_.general.dates_sheet import DatesSheet
from usdm4_excel.import_.study.study_sheet import StudySheet
from usdm4_excel.import_.general.configuration_sheet import ConfigurationSheet
from usdm4_excel.import_.study.abbreviation_sheet import AbbreviationSheet
from usdm4_excel.import_.study.identifiers_sheet import IdentifiersSheet
from usdm4_excel.import_.study.organizations_sheet import OrganizationsSheet
from usdm4_excel.import_.study.document_content_sheet import DocumentContentSheet
from usdm4_excel.import_.study.documents_sheet import DocumentsSheet
from usdm4_excel.import_.study.document_versions_sheet import DocumentVersionsSheet
from usdm4_excel.import_.study.document_template_sheet import DocumentTemplateSheet
from usdm4_excel.import_.study.amendments_sheet import AmendmentsSheet
from usdm4_excel.import_.study.amendment_changes_sheet import AmendmentChangesSheet
from usdm4_excel.import_.study.amendment_impact_sheet import AmendmentImpactSheet


class StudyAction:
    MODULE = "usdm4_excel-import_.study.actions.study.StudyAction"

    def __init__(self, builder: Builder, errors: Errors):
        self._builder = builder
        self._errors = errors
        self._study_sheet = None
        self._configuration_sheet = None
        self._dictionary_sheet = None
        self._dates_sheet = None
        self._notes_sheet = None
        self._abbreviations_sheet = None
        self._amendments_sheet = None
        self._amendment_changes_sheet = None
        self._amendments_impact_sheet = None
        self._assigned_person_sheet = None
        self._documents_sheet = None
        self._document_content_sheet = None
        self._document_template_sheets = []
        self._eligibility_criteria_items_sheet = None
        self._identifiers_sheet = None
        self._organizations_sheet = None
        self._sites_sheet = None

    def process(
        self,
        file_path: str,
    ) -> Study | None:
        try:
            self._read_sheets(file_path)
            study_design_action = StudyDesignAction(self._builder, self._errors)
            study_design: StudyDesign = study_design_action.process(file_path)
            study_version: StudyVersion
            if study_version := self._create_version():
                study_version.studyDesigns = [study_design] if study_design else []
                study_version.biomedicalConcepts = (
                    study_design_action.biomedical_concepts
                )
                study_version.bcSurrogates = (
                    study_design_action.biomedical_concept_surrogates
                )
                return self._create_study(study_version)
            return None
        except Exception as e:
            location = KlassMethodLocation(self.MODULE, "process")
            self._errors.exception("Failure in study action", e, location)
            return None

    def _create_study(self, study_version: StudyVersion) -> Study:
        params = self._study_sheet.study
        params["id"] = None
        params["versions"] = [study_version]
        params["documentedBy"] = self._documents_sheet.items
        return self._builder.create(Study, params)

    def _create_version(self) -> StudyVersion:
        params = self._study_sheet.study_version
        params["studyIdentifiers"] = self._identifiers_sheet.items
        params["abbreviations"] = self._abbreviations_sheet.items
        params["narrativeContentItems"] = self._document_content_sheet.items
        params["amendments"] = self._amendments_sheet.items
        params["dateValues"] = self._dates_sheet.items
        return self._builder.create(StudyVersion, params)

    def _read_sheets(self, file_path: str) -> None:
        self._configuration_sheet = ConfigurationSheet(
            file_path, self._builder, self._errors
        )
        self._notes_sheet = NotesSheet(file_path, self._builder, self._errors)
        self._dates_sheet = DatesSheet(file_path, self._builder, self._errors)
        self._abbreviations_sheet = AbbreviationSheet(
            file_path, self._builder, self._errors
        )
        self._organizations_sheet = OrganizationsSheet(
            file_path, self._builder, self._errors
        )
        self._identifiers_sheet = IdentifiersSheet(
            file_path, self._builder, self._errors
        )
        self._amendments_sheet = AmendmentsSheet(file_path, self._builder, self._errors)
        self._amendment_changes_sheet = AmendmentChangesSheet(
            file_path, self._builder, self._errors
        )
        self._amendment_impact_sheet = AmendmentImpactSheet(
            file_path, self._builder, self._errors
        )
        self._document_content_sheet = DocumentContentSheet(
            file_path, self._builder, self._errors
        )
        self._document_versions_sheet = DocumentVersionsSheet(
            file_path, self._builder, self._errors
        )
        self._documents_sheet = DocumentsSheet(file_path, self._builder, self._errors)
        document: StudyDefinitionDocument
        for document in self._documents_sheet.items:
            version: StudyDefinitionDocumentVersion
            for version in document.versions:
                sheet_name: str = self._document_versions_sheet.sheet_name(version.id)
                template_sheet: DocumentTemplateSheet = DocumentTemplateSheet(
                    file_path,
                    self._builder,
                    self._errors,
                    document.templateName,
                    sheet_name,
                )
                version.contents = template_sheet.items
        self._study_sheet = StudySheet(file_path, self._builder, self._errors)
