from usdm4_excel.import_.excel_sheet_reader.base_sheet import BaseSheet
from simple_error_log.errors import Errors
from usdm4.builder.builder import Builder
from usdm4.api.study_amendment import StudyAmendment
from usdm4.api.governance_date import GovernanceDate
from usdm4.api.study_amendment_reason import StudyAmendmentReason
from usdm4.api.subject_enrollment import SubjectEnrollment


class AmendmentsSheet(BaseSheet):
    SHEET_NAME = "studyAmendments"

    def __init__(self, file_path: str, builder: Builder, errors: Errors):
        try:
            self._items = []
            super().__init__(
                file_path=file_path,
                builder=builder,
                errors=errors,
                sheet_name=self.SHEET_NAME,
                optional=True,
            )
            if self._success:
                for index, row in self._sheet.iterrows():
                    secondaries = []
                    name = self._read_cell_by_name(index, ["name"])
                    description = self._read_cell_by_name(
                        index, ["description"], default="", must_be_present=False
                    )
                    label = self._read_cell_by_name(
                        index, "label", default="", must_be_present=False
                    )
                    number = self._read_cell_by_name(index, "number")
                    date_name = self._read_cell_by_name(
                        index, "date", must_be_present=False
                    )
                    date = self._builder.cross_reference.get_by_name(
                        GovernanceDate, date_name
                    )
                    summary = self._read_cell_by_name(index, "summary")
                    notes = self._read_cell_multiple_by_name(
                        index, "notes", must_be_present=False
                    )
                    primary_reason = self._read_primary_reason_cell(index)
                    primary = self._amendment_reason(primary_reason)
                    secondary_reasons = self._read_secondary_reason_cell(index)
                    for reason in secondary_reasons:
                        amendment_reason = self._amendment_reason(reason)
                        if amendment_reason:
                            secondaries.append(amendment_reason)
                    enrollments = self._read_enrollment_cell(index, name)
                    scopes = self._read_geographic_scopes_cell_by_name(
                        index, "geographicScope"
                    )

                    item: StudyAmendment = self._create(
                        StudyAmendment,
                        {
                            "name": name,
                            "description": description,
                            "label": label,
                            "number": number,
                            "summary": summary,
                            "primaryReason": primary,
                            "secondaryReasons": secondaries,
                            "enrollments": enrollments,
                            "geographicScopes": scopes,
                            "dateValues": [date] if date else [],
                        },
                    )
                    if item:
                        self._items.append(item)
                        self._add_notes(item, notes)

                self._items.sort(key=lambda d: int(d.number), reverse=True)
                self._single_link(self._items, "previousId")

        except Exception as e:
            self._sheet_exception(e)

    @property
    def items(self):
        print(f"AMENDMENT ITEMS: {self._items}")
        return self._items

    def _amendment_reason(self, reason):
        if not reason:
            return None
        item = self._create(
            StudyAmendmentReason,
            {"code": reason["code"], "otherReason": reason["other"]},
        )
        return item

    def _read_enrollment_cell(
        self, row_index: int, name: str
    ) -> list[SubjectEnrollment]:
        result = []
        try:
            col_index = self._column_present("enrollment")
            value = self._read_cell(row_index, col_index)
            if value.strip() == "":
                self._errors.error(
                    "Empty cell detected where enrollment values expected",
                )
            else:
                for item in self._state_split(value):
                    name = f"{name}-{row_index + 1}"
                    key_value = self._key_value(item, row_index, col_index)
                    if key_value[0] == "COHORT":
                        pass  # TODO: Implement cohort enrollment
                    elif key_value[0] == "SITE":
                        pass  # TODO: Implement site enrollment
                    elif key_value[0] == "GLOBAL":
                        quantity = self._get_quantity(key_value[1])
                        scope = self._scope("Global", None)
                        result.append(
                            self._enrollment(quantity, scope=scope, name=name)
                        )
                    elif key_value[0] == "REGION":
                        code, quantity = self._country_region_quantity(
                            key_value[1], "Region", row_index, col_index
                        )
                        if code:
                            scope = self._scope("Region", code)
                            result.append(
                                self._enrollment(quantity, scope=scope, name=name)
                            )
                    elif key_value[0] == "COUNTRY":
                        code, quantity = self._country_region_quantity(
                            key_value[1], "Country", row_index, col_index
                        )
                        if code:
                            scope = self._scope("Country", code)
                            result.append(
                                self._enrollment(quantity, scope=scope, name=name)
                            )
        except Exception as e:
            self._errors.exception(
                "Exception raised reading enrollment cell",
                e,
                self._location(row_index, col_index),
            )
        return result

    def _enrollment(self, quantity, **kwargs) -> SubjectEnrollment:
        for_geographic_scope = None
        for_study_cohort_id = None
        for_study_site_id = None
        if "scope" in kwargs:
            for_geographic_scope = kwargs["scope"]
        if "cohort" in kwargs:
            for_study_cohort_id = kwargs["cohort"]
        if "site" in kwargs:
            for_study_site_id = kwargs["site"]
        return self._create(
            SubjectEnrollment,
            {
                "name": kwargs["name"],
                "quantity": quantity,
                "forGeographicScope": for_geographic_scope,
                "forStudyCohortId": for_study_cohort_id,
                "forStudySiteId": for_study_site_id,
            },
        )

    def _read_secondary_reason_cell(self, row_index):
        results = []
        try:
            col_index = self._column_present("secondaryReasons")
            value = self._read_cell(row_index, col_index)
            if not value.strip():
                return results
            parts = value.strip().split(",")
            for part in parts:
                result = self._extract_reason(part, row_index, col_index)
                if result:
                    results.append(result)
        except Exception as e:
            self._errors.exception(
                "Exception raised reading secondary reason cell",
                e,
                self._location(row_index, col_index),
            )
        return results

    def _read_primary_reason_cell(self, row_index):
        try:
            col_index = self._column_present("primaryReason")
            value = self._read_cell(row_index, col_index)
            return self._extract_reason(value, row_index, col_index)
        except Exception as e:
            self._errors.exception(
                "Exception raised reading primary reason cell",
                e,
                self._location(row_index, col_index),
            )
            return None

    def _extract_reason(self, value, row_index, col_index):
        if value.strip() == "":
            self._errors.error(
                "Empty cell detected where CDISC CT value expected.",
            )
            return None
        elif value.strip().upper().startswith("OTHER"):
            text = value.strip()
            parts = text.split("=")
            if len(parts) == 2:
                code = self._builder.klass_and_attribute_value(
                    "StudyAmendmentReason", "code", "Other"
                )
                return {
                    "code": code,
                    "other": parts[1].strip(),
                }
            else:
                self._errors.error(
                    f"Failed to decode reason data {text}, no '=' detected",
                )
        else:
            code = self._builder.klass_and_attribute_value(
                "StudyAmendmentReason", "code", value
            )
            if code is None:
                self._errors.error(f"CDISC CT not found for value '{value}'.")
            return {"code": code, "other": None}
