from usdm4_excel.import_.excel_sheet_reader.base_sheet import BaseSheet
from simple_error_log.errors import Errors
from usdm4.builder.builder import Builder
from usdm4.api.narrative_content import NarrativeContent, NarrativeContentItem


class DocumentTemplateSheet(BaseSheet):
    def __init__(
        self,
        file_path: str,
        builder: Builder,
        errors: Errors,
        template_name: str,
        sheet_name: str,
    ):
        try:
            self._items = []
            self._template_name = template_name
            super().__init__(
                file_path=file_path,
                builder=builder,
                errors=errors,
                sheet_name=sheet_name,
                optional=True,
                converters={"sectionName": str},
            )
            if self._success:
                current_level = 0
                new_level = 0
                self._parent_stack = []
                previous_item = None
                for index, row in self._sheet.iterrows():
                    name = self._read_cell_by_name(index, "name")
                    section_number = self._read_cell_by_name(index, "sectionNumber")
                    name = f"SECTION {section_number}" if not name else name
                    new_level = self._get_level(section_number)
                    section_title = self._read_cell_by_name(index, "sectionTitle")
                    display_section_number = self._read_boolean_cell_by_name(
                        index, "displaySectionNumber"
                    )
                    display_section_title = self._read_boolean_cell_by_name(
                        index, "displaySectionTitle"
                    )
                    content_name = self._read_cell_by_name(index, "content")
                    content = None
                    if content_name:
                        content = self._builder.cross_reference.get_by_name(
                            NarrativeContentItem, content_name
                        )
                        if not content:
                            self._errors.warning(
                                f"Unable to find narrative content item with name '{content_name}'",
                                self._location(index, None),
                            )
                    else:
                        self._errors.warning(
                            f"No content item specified for section '{section_number}', '{section_title}'",
                            self._location(index, None),
                        )
                        content = None

                    params = {
                        "name": name,
                        "sectionNumber": section_number,
                        "displaySectionNumber": display_section_number,
                        "sectionTitle": section_title,
                        "displaySectionTitle": display_section_title,
                        "contentItemId": content.id if content else None,
                    }
                    item: NarrativeContent = self._create(NarrativeContent, params)
                    if item:
                        self._items.append(item)
                        if new_level == current_level:
                            # Same level
                            self._add_child_to_parent(item)
                        elif new_level > current_level:
                            # Down
                            if (new_level - current_level) > 1:
                                try:
                                    column = self._column_present("sectionNumber")
                                    self._errors.error(
                                        f"Error with section number increasing by more than one level, section '{section_number}'.",
                                        self._location(index, column),
                                    )
                                except Exception:
                                    self._errors.error(
                                        f"Error with section number increasing by more than one level, section '{section_number}'.",
                                        self._location(index, None),
                                    )
                                raise BaseSheet.FormatError
                            if previous_item:
                                self._push_parent(previous_item)
                            self._add_child_to_parent(item)
                            current_level = new_level
                        else:
                            # Up
                            self._pop_parent(current_level, new_level)
                            self._add_child_to_parent(item)
                            current_level = new_level
                        previous_item = item
                    self._double_link(self._items, "previousId", "nextId")
        except Exception as e:
            self._sheet_exception(e)

    @property
    def items(self):
        return self._items

    @property
    def template_name(self):
        return self._template_name

    def _get_level(self, section_number):
        sn = section_number[:-1] if section_number.endswith(".") else section_number
        parts = sn.split(".")
        return len(parts)

    def _push_parent(self, parent):
        self._parent_stack.append(parent)

    def _pop_parent(self, current_level, new_level):
        for _ in range(new_level, current_level):
            _ = self._parent_stack.pop()

    def _add_child_to_parent(self, child):
        if self._parent_stack:
            parent = self._parent_stack[-1]
            parent.childIds.append(child.id)
