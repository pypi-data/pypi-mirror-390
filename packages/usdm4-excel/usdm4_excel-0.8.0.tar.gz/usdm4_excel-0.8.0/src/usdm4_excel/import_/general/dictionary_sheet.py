from usdm4_excel.import_.excel_sheet_reader.base_sheet import BaseSheet
from simple_error_log.errors import Errors
from usdm4.builder.builder import Builder
from usdm4.api.syntax_template_dictionary import SyntaxTemplateDictionary, ParameterMap


class DictionarySheet(BaseSheet):
    SHEET_NAME = "dictionaries"

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
                current_name = None
                current_dictionary = None
                current_map = []
                for index, row in self._sheet.iterrows():
                    name = self._read_cell_by_name(index, "name")
                    if name:
                        if name != current_name:
                            current_name = name
                            if current_dictionary:
                                current_dictionary.parameterMaps = current_map
                                current_map = []
                            item = self._create(
                                SyntaxTemplateDictionary,
                                {
                                    "name": name,
                                    "description": self._read_cell_by_name(
                                        index, "description"
                                    ),
                                    "label": self._read_cell_by_name(index, "label"),
                                    "parameterMaps": [],
                                },
                            )
                            if item:
                                self._items.append(item)
                            current_dictionary = item
                    key = self._read_cell_by_name(index, "key")
                    klass = self._read_cell_by_name(index, "class", default="")
                    xref_name = self._read_cell_by_name(index, "xref", default="")
                    attribute_path = self._read_cell_by_name(
                        index, ["attribute", "path"], default=""
                    )
                    value = self._read_cell_by_name(
                        index, "value", default="", must_be_present=False
                    )
                    if klass:
                        try:
                            instance, attribute = (
                                self._builder.cross_reference.get_by_path(
                                    klass, xref_name, attribute_path
                                )
                            )
                        except Exception as e:
                            instance = None
                            col = self._column_present(["attribute", "path"])
                            self._errors.error(str(e), self._location(index, col + 1))
                        if instance:
                            map_item = self._create(
                                ParameterMap,
                                {
                                    "tag": key,
                                    "reference": f'<usdm:ref klass="{instance.__class__.__name__}" id="{instance.id}" attribute="{attribute}"></usdm:ref>',
                                },
                            )
                            if map_item:
                                current_map.append(map_item)
                    else:
                        map_item = self._create(
                            ParameterMap, {"tag": key, "reference": f"{value}"}
                        )
                        if map_item:
                            current_map.append(map_item)
                # Clean up last dictionary if present
                if current_dictionary:
                    current_dictionary.parameterMaps = current_map

        except Exception as e:
            self._sheet_exception(e)

    @property
    def items(self):
        return self._items
