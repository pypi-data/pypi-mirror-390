from usdm4_excel.import_.excel_sheet_reader.base_sheet import BaseSheet
from simple_error_log.errors import Errors
from usdm4.builder.builder import Builder
from usdm4.api.study_role import StudyRole
from usdm4.api.assigned_person import AssignedPerson
from usdm4.api.organization import Organization
from usdm4.api.masking import Masking


class StudyRoleSheet(BaseSheet):
    SHEET_NAME = "roles"

    def __init__(self, file_path: str, builder: Builder, errors: Errors):
        try:
            self.items = []
            super().__init__(
                file_path=file_path,
                builder=builder,
                errors=errors,
                sheet_name=self.SHEET_NAME,
                optional=True,
            )
            if self._success:
                self._process_sheet()
        except Exception as e:
            self._sheet_exception(e)

    def _process_sheet(self):
        for index, row in self._sheet.iterrows():
            params = {
                "name": self._read_cell_by_name(index, "name"),
                "description": self._read_cell_by_name(
                    index, "description", default=""
                ),
                "label": self._read_cell_by_name(index, "label", default=""),
                "organizationIds": self._get_refs_for(
                    Organization, index, "organizations", ids=True
                ),
                "assignedPersons": self._get_refs_for(AssignedPerson, index, "people"),
                "masking": self._get_masking(index),
                "code": self._read_cdisc_klass_attribute_cell_by_name(
                    "StudyRole", "code", index, "role"
                ),
            }
            notes = self._read_cell_multiple_by_name(
                index, "notes", must_be_present=False
            )
            item: StudyRole = self._create(StudyRole, params)
            if item:
                self.items.append(item)
                self._add_notes(item, notes)

    def _get_masking(self, index):
        masking = None
        masking_text = self._read_cell_by_name(index, "masking", default="")
        if masking_text:
            masking = self._create(Masking, {"text": masking_text, "isMasked": True})
        return masking

    def _get_refs_for(self, klass, index: int, column_name: str, ids=False):
        collection = []
        refs = self._read_cell_multiple_by_name(
            index, column_name, must_be_present=False
        )
        for ref in refs:
            item = self._builder.cross_reference.get_by_name(klass, ref)
            if item:
                if ids:
                    collection.append(item.id)
                else:
                    collection.append(item)
            else:
                self._errors.warning(
                    f"Failed to find {klass.__name__.lower()} with name '{ref}'"
                )
        return collection
