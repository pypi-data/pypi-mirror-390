from usdm4_excel.import_.excel_sheet_reader.base_sheet import BaseSheet
from simple_error_log.errors import Errors
from usdm4.builder.builder import Builder
from usdm4.api.study_title import StudyTitle


class StudySheet(BaseSheet):
    SHEET_NAME = "study"

    NAME_KEY = "name"
    DESCRIPTION_KEY = "description"
    LABEL_KEY = "label"
    VERSION_KEY = "studyVersion"
    ACRONYM_KEY = "studyAcronym"
    RATIONALE_KEY = "studyRationale"
    TA_KEY = "businessTherapeuticAreas"
    BRIEF_KEY = "briefTitle"
    OFFICAL_KEY = "officialTitle"
    PUBLIC_KEY = "publicTitle"
    SCIENTIFIC_KEY = "scientificTitle"
    STUDY_DESIGN_KEY = "studyDesigns"
    NOTES_KEY = "notes"

    PARAMS_NAME_COL = 0
    PARAMS_DATA_COL = 1

    STUDY_VERSION_DATE = "study_version"
    PROTOCOL_VERSION_DATE = "protocol_document"
    AMENDMENT_DATE = "amendment"

    def __init__(self, file_path: str, builder: Builder, errors: Errors):
        try:
            self.items = []  # Add items attribute for consistency with other sheets
            super().__init__(
                file_path=file_path,
                builder=builder,
                errors=errors,
                sheet_name=self.SHEET_NAME,
                header=None,
                optional=True,
            )
            self._date_categories = [
                self.STUDY_VERSION_DATE,
                self.PROTOCOL_VERSION_DATE,
                self.AMENDMENT_DATE,
            ]
            self._version: str = None
            self._type: str = None
            self._name: str = None
            self._description: str = None
            self._label: str = None
            self._titles: list[StudyTitle] = []
            self._rationale: str = None
            self._therapeutic_areas: list[str] = []
            self._dates = {}
            self._notes = []
            self._study_design_files: list[str] = []
            for category in self._date_categories:
                self._dates[category] = []
            if self._success:
                self._process_sheet()
        except Exception as e:
            self._sheet_exception(e)

    @property
    def study_version(self):
        return {
            "versionIdentifier": self._version,
            "businessTherapeuticAreas": self._therapeutic_areas,
            "rationale": self._rationale,
            "titles": self._titles,
            "notes": self._notes,
        }

    @property
    def study(self):
        return {
            "name": self._name,
            "label": self._label,
            "description": self._description,
        }

    def _process_sheet(self):
        for rindex, row in self._sheet.iterrows():
            field_name = self._read_cell(rindex, self.PARAMS_NAME_COL)
            if field_name == self.NAME_KEY:
                self._name = self._read_cell(rindex, self.PARAMS_DATA_COL)
            elif field_name == self.DESCRIPTION_KEY:
                self._description = self._read_cell(rindex, self.PARAMS_DATA_COL)
            elif field_name == self.LABEL_KEY:
                self._label = self._read_cell(rindex, self.PARAMS_DATA_COL)
            elif field_name == self.STUDY_DESIGN_KEY:
                self._study_design_files = self._read_cell_multiple(
                    rindex, self.PARAMS_DATA_COL
                )
            elif field_name == self.VERSION_KEY:
                self._version = self._read_cell(rindex, self.PARAMS_DATA_COL)
            elif field_name == self.ACRONYM_KEY:
                self._acronym = self._set_title(
                    rindex, self.PARAMS_DATA_COL, "Study Acronym"
                )
            elif field_name == self.RATIONALE_KEY:
                self._rationale = self._read_cell(rindex, self.PARAMS_DATA_COL)
            elif field_name == self.TA_KEY:
                self._therapeutic_areas = self._read_other_code_cell_multiple(
                    rindex, self.PARAMS_DATA_COL
                )
            elif field_name == self.BRIEF_KEY:
                self._set_title(rindex, self.PARAMS_DATA_COL, "Brief Study Title")
            elif field_name == self.OFFICAL_KEY:
                self._set_title(rindex, self.PARAMS_DATA_COL, "Official Study Title")
            elif field_name == self.PUBLIC_KEY:
                self._set_title(rindex, self.PARAMS_DATA_COL, "Public Study Title")
            elif field_name == self.SCIENTIFIC_KEY:
                self._set_title(rindex, self.PARAMS_DATA_COL, "Scientific Study Title")
            elif field_name == self.NOTES_KEY:
                self._notes = self._read_cell_multiple(rindex, self.PARAMS_DATA_COL)
            else:
                self._errors.warning(
                    f"Unrecognized key '{field_name}', ignored",
                    self._location(rindex, self.PARAMS_DATA_COL),
                )

    def _set_title(self, rindex: int, cindex: int, title_type: str) -> None:
        try:
            text = self._read_cell(rindex, cindex)
            if text:
                code = self._builder.klass_and_attribute_value(
                    "StudyTitle", "type", title_type
                )
                title = self._create(
                    StudyTitle,
                    {
                        "text": text,
                        "type": code,
                    },
                )
                if title:
                    self._titles.append(title)
                return title
            else:
                self._errors.error(
                    "Failed to create StudyTitle object",
                    self._location(rindex, cindex),
                )
        except Exception as e:
            self._errors.exception(
                "Exception raised creating StudyTitle object",
                e,
                self._location(rindex, cindex),
            )
