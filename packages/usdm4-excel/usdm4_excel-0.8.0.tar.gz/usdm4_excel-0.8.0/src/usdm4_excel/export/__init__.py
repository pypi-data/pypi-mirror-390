import json
from usdm4_excel.export.study_sheet.study_sheet import StudySheet
from usdm4_excel.export.study_organizations_sheet.study_organizations_sheet import (
    StudyOrganizationsSheet,
)
from usdm4_excel.export.study_identifiers_sheet.study_identifiers_sheet import (
    StudyIdentifiersSheet,
)
from usdm4_excel.export.study_document_content_sheet.study_document_content_sheet import (
    StudyDocumentContentSheet,
)
from usdm4_excel.export.study_document_sheet.study_document_sheet import (
    StudyDocumentSheet,
)
from usdm4_excel.export.study_activities_sheet.study_activities_sheet import (
    StudyActivitiesSheet,
)
from usdm4_excel.export.study_encounters_sheet.study_encounters_sheet import (
    StudyEncountersSheet,
)
from usdm4_excel.export.study_epochs_sheet.study_epochs_sheet import (
    StudyEpochsSheet,
)
from usdm4_excel.export.study_arms_sheet.study_arms_sheet import (
    StudyArmsSheet,
)
from usdm4_excel.export.study_design_sheet.study_design_sheet import (
    StudyDesignSheet,
)
from usdm4_excel.export.study_timeline_sheet.study_timeline_sheet import (
    StudyTimelineSheet,
)
from usdm4_excel.export.study_procedures_sheet.study_procedures_sheet import (
    StudyProceduresSheet,
)
from usdm4_excel.export.configuration_sheet.configuration_sheet import (
    ConfigurationSheet,
)
from usdm4_excel.export.study_timing_sheet.study_timing_sheet import StudyTimingSheet
from usdm4_excel.export.base.ct_version import CTVersion
from usdm4_excel.export.excel_table_writer.excel_table_writer import ExcelTableWriter
from usdm4 import USDM4
from usdm4.api.wrapper import Wrapper


class USDM4ExcelExport:
    def to_excel(self, usdm_filepath: str, excel_filepath: str):
        ct_version = CTVersion()
        etw = ExcelTableWriter(excel_filepath, default_sheet_name="study")
        with open(usdm_filepath) as f:
            data = json.load(f)
        usdm = USDM4()
        wrapper: Wrapper = usdm.from_json(data)
        study = wrapper.study
        for klass in [
            StudySheet,
            StudyOrganizationsSheet,
            StudyIdentifiersSheet,
            StudyDocumentContentSheet,
            StudyDocumentSheet,
            StudyActivitiesSheet,
            StudyTimingSheet,
            StudyEncountersSheet,
            StudyEpochsSheet,
            StudyArmsSheet,
            StudyDesignSheet,
            StudyTimelineSheet,
            StudyProceduresSheet,
            ConfigurationSheet,
        ]:
            klass(ct_version, etw).save(study)
        etw.save()
