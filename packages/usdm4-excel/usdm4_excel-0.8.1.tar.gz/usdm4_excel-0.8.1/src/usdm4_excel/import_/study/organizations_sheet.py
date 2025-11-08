from usdm4_excel.import_.excel_sheet_reader.base_sheet import BaseSheet
from simple_error_log.errors import Errors
from usdm4.builder.builder import Builder
from usdm4.api.organization import Organization


class OrganizationsSheet(BaseSheet):
    SHEET_NAME = "studyOrganizations"

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
                for index, row in self._sheet.iterrows():
                    org_type = self._read_cdisc_klass_attribute_cell_by_name(
                        "Organization",
                        "type",
                        index,
                        ["organisationType", "organizationType", "type"],
                    )
                    org_id_scheme = self._read_cell_by_name(
                        index,
                        [
                            "organisationIdentifierScheme",
                            "organizationIdentifierScheme",
                            "identifierScheme",
                        ],
                    )
                    org_identifier = self._read_cell_by_name(
                        index,
                        [
                            "organisationIdentifier",
                            "organizationIdentifier",
                            "identifier",
                        ],
                    )
                    org_name = self._read_cell_by_name(
                        index, ["organisationName", "organizationName", "name"]
                    )
                    org_label = self._read_cell_by_name(
                        index, "label", default="", must_be_present=False
                    )
                    org_address = self._read_address_cell_by_name(
                        index,
                        ["organisationAddress", "organizationAddress", "address"],
                        allow_empty=True,
                    )
                    organization: Organization = self._create(
                        Organization,
                        {
                            "identifierScheme": org_id_scheme,
                            "identifier": org_identifier,
                            "name": org_name,
                            "label": org_label,
                            "type": org_type,
                            "legalAddress": org_address,
                        },
                    )
                    if organization:
                        self.items.append(organization)
        except Exception as e:
            self._sheet_exception(e)
