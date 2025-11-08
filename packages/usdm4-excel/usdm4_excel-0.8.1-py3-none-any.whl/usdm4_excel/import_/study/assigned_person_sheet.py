from usdm4_excel.import_.excel_sheet_reader.base_sheet import BaseSheet
from simple_error_log.errors import Errors
from usdm4.builder.builder import Builder
from usdm4.api.assigned_person import AssignedPerson
from usdm4.api.person_name import PersonName
from usdm4.api.organization import Organization


class AssignedPersonSheet(BaseSheet):
    SHEET_NAME = "people"

    def __init__(self, file_path: str, builder: Builder, errors: Errors):
        try:
            print("ASSIGNED PERSON")
            self.items = []
            super().__init__(
                file_path=file_path,
                builder=builder,
                errors=errors,
                sheet_name=self.SHEET_NAME,
                optional=True,
            )
            if self._success:
                for index, row in self._sheet.iterrows():
                    person_name = self._create_person_name(index)
                    item: AssignedPerson = self._create(
                        AssignedPerson,
                        {
                            "name": self._read_cell_by_name(index, "name"),
                            "description": self._read_cell_by_name(
                                index, "description", must_be_present=False
                            ),
                            "label": self._read_cell_by_name(
                                index, "label", must_be_present=False
                            ),
                            "personName": person_name,
                            "jobTitle": self._read_cell_by_name(index, "jobTitle"),
                            "organizationId": self._get_org_id(index),
                        },
                    )
                    if item:
                        self.items.append(item)
        except Exception as e:
            self._sheet_exception(e)

    def _create_person_name(self, index: int) -> PersonName:
        """Create a PersonName object from the personName cell"""
        person_name_text = self._read_cell_by_name(
            index, "personName", must_be_present=False
        )
        if not person_name_text:
            return None

        # Parse the person name - assuming format like "First Last" or "First Middle Last"
        # This is a simplified parser - could be enhanced based on actual data format
        name_parts = person_name_text.strip().split()

        if len(name_parts) == 0:
            return None
        elif len(name_parts) == 1:
            # Only one name part - treat as given name
            given_names = [name_parts[0]]
            family_name = None
        elif len(name_parts) == 2:
            # Two parts - first is given name, second is family name
            given_names = [name_parts[0]]
            family_name = name_parts[1]
        else:
            # Multiple parts - last is family name, rest are given names
            given_names = name_parts[:-1]
            family_name = name_parts[-1]

        params = {
            "text": person_name_text,
            "familyName": family_name,
            "givenNames": given_names,
            "prefixes": [],
            "suffixes": [],
        }

        return self._create(PersonName, params)

    def _get_org_id(self, index: int) -> str:
        """Get organization ID from organization reference"""
        org_ref = self._read_cell_by_name(index, "organization", must_be_present=False)
        if not org_ref:
            return None

        # Try to find the organization by name in the builder's cross references
        try:
            org = self._builder.cross_reference.get_by_name(Organization, org_ref)
            return org.id if org else None
        except Exception:
            # If cross reference lookup fails, return None
            return None
