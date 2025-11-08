from usdm4_excel.import_.excel_sheet_reader.base_sheet import BaseSheet
from simple_error_log.errors import Errors
from usdm4.builder.builder import Builder
from usdm4.api.administrable_product import AdministrableProduct
from usdm4.api.ingredient import Ingredient
from usdm4.api.substance import Substance
from usdm4.api.strength import Strength


class ProductSheet(BaseSheet):
    SHEET_NAME = "studyProducts"

    def __init__(self, file_path: str, builder: Builder, errors: Errors):
        try:
            self.items = []
            self._current_product = None
            self._current_substance = None
            self._current_reference_substance = None
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
            self._create_administrable_product(index)
            self._create_ingredient_and_substance(index)
            self._create_strength(index)
            self._create_reference_substance(index)
            self._create_reference_strength(index)

    def _create_administrable_product(self, index):
        name = self._read_cell_by_name(index, "name")
        if name:
            params = {
                "name": name,
                "description": self._read_cell_by_name(
                    index, "description", must_be_present=False
                ),
                "label": self._read_cell_by_name(index, "label", must_be_present=False),
                "administrableDoseForm": self._builder.alias_code(
                    self._read_cdisc_klass_attribute_cell_by_name(
                        "AdministrableProduct",
                        "administrableDoseForm",
                        index,
                        "administrableDoseForm",
                    )
                ),
                "pharmacologicClass": self._read_other_code_cell_by_name(
                    index, "pharmacologicClass"
                ),
                "productDesignation": self._read_cdisc_klass_attribute_cell_by_name(
                    "AdministrableProduct",
                    "productDesignation",
                    index,
                    "productDesignation",
                ),
                "sourcing": self._read_cdisc_klass_attribute_cell_by_name(
                    "AdministrableProduct", "sourcing", index, "productSourcing"
                ),
            }
            item: AdministrableProduct = self._create(AdministrableProduct, params)
            if item:
                self.items.append(item)
                self._current_product = item

    def _create_ingredient_and_substance(self, index):
        name = self._read_cell_by_name(index, "substanceName")
        if name:
            params = {
                "name": name,
                "description": self._read_cell_by_name(
                    index, "substanceDescription", must_be_present=False
                ),
                "label": self._read_cell_by_name(
                    index, "substanceLabel", must_be_present=False
                ),
            }
            substance: Substance = self._create(Substance, params)
            if substance:
                # Add substance code if provided
                substance_code = self._read_other_code_cell_by_name(
                    index, "substanceCode"
                )
                if substance_code:
                    substance.codes.append(substance_code)

                params = {
                    "role": self._read_other_code_cell_by_name(index, "ingredientRole"),
                    "substance": substance,
                }
                ingredient: Ingredient = self._create(Ingredient, params)
                if ingredient:
                    self._current_product.ingredients.append(ingredient)
                    self._current_substance = substance

    def _create_reference_substance(self, index):
        name = self._read_cell_by_name(index, "referenceSubstanceName")
        if name:
            params = {
                "name": name,
                "description": self._read_cell_by_name(
                    index, "referenceSubstanceDescription", must_be_present=False
                ),
                "label": self._read_cell_by_name(
                    index, "referenceSubstanceLabel", must_be_present=False
                ),
            }
            substance: Substance = self._create(Substance, params)
            if substance:
                # Add reference substance code if provided
                reference_code = self._read_other_code_cell_by_name(
                    index, "referenceSubstanceCode"
                )
                if reference_code:
                    substance.codes.append(reference_code)

                self._current_substance.referenceSubstance = substance
                self._current_reference_substance = substance
                return
        self._current_reference_substance = None
        return

    def _create_strength(self, index):
        strength_name = self._read_cell_by_name(index, "strengthName")
        if strength_name:
            numerator = self._read_numerator(index, "strengthNumerator")
            params = {
                "name": strength_name,
                "description": self._read_cell_by_name(
                    index, "strengthdescription", must_be_present=False
                ),
                "label": self._read_cell_by_name(
                    index, "strengthLabel", must_be_present=False
                ),
                "numerator": numerator,
                "denominator": self._read_quantity_cell_by_name(
                    index, "strengthDenominator"
                ),
            }
            strength: Strength = self._create(Strength, params)
            if strength:
                self._current_substance.strengths.append(strength)

    def _create_reference_strength(self, index):
        name = self._read_cell_by_name(index, "referenceSubstanceStrengthName")
        if name:
            numerator = self._read_numerator(
                index, "referenceSubstanceStrengthNumerator"
            )
            params = {
                "name": name,
                "description": self._read_cell_by_name(
                    index,
                    "referenceSubstanceStrengthdescription",
                    must_be_present=False,
                ),
                "label": self._read_cell_by_name(
                    index, "referenceSubstanceStrengthLabel", must_be_present=False
                ),
                "numerator": numerator,
                "denominator": self._read_quantity_cell_by_name(
                    index, "referenceSubstanceStrengthDenominator"
                ),
            }
            strength: Strength = self._create(Strength, params)
            if strength:
                self._current_reference_substance.strengths.append(strength)

    def _read_numerator(self, index, field_name):
        text = self._read_cell_by_name(index, field_name)
        if not text:
            return None

        value = (
            self._read_range_cell_by_name(
                index, field_name, require_units=False, allow_empty=False
            )
            if ".." in text
            else self._read_quantity_cell_by_name(
                index, field_name, allow_missing_units=False, allow_empty=False
            )
        )
        if value is None:
            self._errors.warning(f"Failed to create numerator from '{text}'")
        return value
