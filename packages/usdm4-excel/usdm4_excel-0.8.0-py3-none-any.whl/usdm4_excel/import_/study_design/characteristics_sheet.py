from usdm4_excel.import_.excel_sheet_reader.base_sheet import BaseSheet
from simple_error_log.errors import Errors
from usdm4.builder.builder import Builder
from usdm4.api.characteristic import Characteristic


class CharacteristicsSheet(BaseSheet):
    SHEET_NAME = "studyDesignCharacteristics"

    def __init__(self, file_path: str, builder: Builder, errors: Errors):
        try:
            print("CHARACTERISTICS")
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
                    name = self._read_cell_by_name(index, "name")
                    description = self._read_cell_by_name(index, "description")
                    label = self._read_cell_by_name(index, "label")
                    text = self._read_cell_by_name(index, "text")
                    dictionary_name = self._read_cell_by_name(index, "dictionary")
                    dictionary_id = self._get_dictionary_id(dictionary_name)
                    note_refs = self._read_cell_multiple_by_name(
                        index, "notes", must_be_present=False
                    )

                    item: Characteristic = self._create(
                        Characteristic,
                        {
                            "name": name,
                            "description": description,
                            "label": label,
                            "text": text,
                            "dictionaryId": dictionary_id,
                        },
                    )
                    if item:
                        self._add_notes(item, note_refs)
                        self.items.append(item)
        except Exception as e:
            self._sheet_exception(e)
