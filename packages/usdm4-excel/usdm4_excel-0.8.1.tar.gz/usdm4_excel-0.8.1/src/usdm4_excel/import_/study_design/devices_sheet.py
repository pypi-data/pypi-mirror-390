from usdm4_excel.import_.excel_sheet_reader.base_sheet import BaseSheet
from simple_error_log.errors import Errors
from usdm4.builder.builder import Builder
from usdm4.api.medical_device import MedicalDevice
from usdm4.api.administrable_product import AdministrableProduct


class DevicesSheet(BaseSheet):
    SHEET_NAME = "studyDevices"

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
                "description": self._read_cell_by_name(index, "description"),
                "label": self._read_cell_by_name(index, "label"),
                "hardwareVersion": self._read_cell_by_name(index, "hardwareVersion"),
                "softwareVersion": self._read_cell_by_name(index, "softwareVersion"),
                "sourcing": self._read_cdisc_klass_attribute_cell_by_name(
                    "MedicalDevice", "sourcing", index, "sourcing"
                ),
            }
            product_name = self._read_cell_by_name(index, "product")
            product = self._builder.cross_reference.get_by_name(
                AdministrableProduct, product_name
            )
            if product:
                params["embeddedProductId"] = product.id
            else:
                self._errors.warning(
                    f"Failed to find administrable product with name '{product_name}'"
                )
            notes = self._read_cell_multiple_by_name(
                index, "notes", must_be_present=False
            )
            item: MedicalDevice = self._create(MedicalDevice, params)
            if item:
                self.items.append(item)
                self._add_notes(item, notes)
