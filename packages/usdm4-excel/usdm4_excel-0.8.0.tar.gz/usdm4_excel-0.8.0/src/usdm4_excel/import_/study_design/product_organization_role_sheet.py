from usdm4_excel.import_.excel_sheet_reader.base_sheet import BaseSheet
from simple_error_log.errors import Errors
from usdm4.builder.builder import Builder
from usdm4.api.product_organization_role import ProductOrganizationRole
from usdm4.api.organization import Organization
from usdm4.api.administrable_product import AdministrableProduct
from usdm4.api.medical_device import MedicalDevice


class ProductOrganizationRoleSheet(BaseSheet):
    SHEET_NAME = "studyProductOrganizationRoles"

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
                "organizationId": self._get_organization_id(index),
                "code": self._read_cdisc_klass_attribute_cell_by_name(
                    "ProductOrganizationRole", "code", index, "role"
                ),
                "appliesToIds": self._process_applies_to_references(index),
            }
            item: ProductOrganizationRole = self._create(
                ProductOrganizationRole, params
            )
            if item:
                self.items.append(item)

    def _get_organization_id(self, index):
        organization_name = self._read_cell_by_name(index, "organization")
        organization = self._builder.cross_reference.get_by_name(
            Organization, organization_name
        )
        if organization:
            return organization.id
        else:
            self._errors.error(
                f"Failed to find organization with name '{organization_name}'"
            )
            return None

    def _process_applies_to_references(self, index):
        results = []
        klasses = [AdministrableProduct, MedicalDevice]
        references = self._read_cell_multiple_by_name(
            index, "appliesTo", must_be_present=False
        )
        for reference in references:
            if reference:
                found = False
                for klass in klasses:
                    item = self._builder.cross_reference.get_by_name(klass, reference)
                    if item:
                        results.append(item.id)
                        found = True
                        break
                if not found:
                    self._errors.error(
                        f"Could not resolve appliesTo reference '{reference}'"
                    )
        return results
