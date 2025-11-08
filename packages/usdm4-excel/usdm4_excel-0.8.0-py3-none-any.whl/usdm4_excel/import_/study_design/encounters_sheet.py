from usdm4_excel.import_.excel_sheet_reader.base_sheet import BaseSheet
from simple_error_log.errors import Errors
from usdm4.builder.builder import Builder
from usdm4.api.encounter import Encounter
from usdm4.api.timing import Timing
from usdm4.api.transition_rule import TransitionRule


class EncountersSheet(BaseSheet):
    SHEET_NAME = "studyDesignEncounters"

    def __init__(self, file_path: str, builder: Builder, errors: Errors):
        try:
            print("ENCOUNTERS")
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
                    start_rule = None
                    end_rule = None

                    # Read basic encounter information
                    name = self._read_cell_by_name(index, ["encounterName", "name"])
                    description = self._read_cell_by_name(
                        index, ["encounterDescription", "description"]
                    )
                    label = self._read_cell_by_name(
                        index, "label", default="", must_be_present=False
                    )

                    # Read encounter type using CDISC codes
                    encounter_type = self._read_cdisc_klass_attribute_cell_by_name(
                        Encounter,
                        "type",
                        index,
                        ["type"],
                        allow_empty=True,
                    )

                    # Read environmental settings and contact modes
                    settings = self._read_cdisc_klass_attribute_cell_multiple_by_name(
                        Encounter,
                        "environmentalSettings",
                        index,
                        ["environmentalSettings"],
                    )

                    modes = self._read_cdisc_klass_attribute_cell_multiple_by_name(
                        Encounter,
                        "contactModes",
                        index,
                        ["encounterContactModes", "contactModes"],
                    )

                    # Read transition rules
                    start_rule_text = self._read_cell_by_name(
                        index, "transitionStartRule", must_be_present=False
                    )
                    end_rule_text = self._read_cell_by_name(
                        index, "transitionEndRule", must_be_present=False
                    )

                    # Create transition rules if text is provided
                    start_rule = None
                    end_rule = None

                    if start_rule_text:
                        start_rule = self._create(
                            TransitionRule,
                            {
                                "name": f"ENCOUNTER_START_RULE_{index + 1}",
                                "text": start_rule_text,
                            },
                        )

                    if end_rule_text:
                        end_rule = self._create(
                            TransitionRule,
                            {
                                "name": f"ENCOUNTER_END_RULE_{index + 1}",
                                "text": end_rule_text,
                            },
                        )

                    # Read timing reference
                    timing_xref = self._read_cell_by_name(
                        index, "window", must_be_present=False
                    )
                    timing = self._builder.cross_reference.get_by_name(
                        Timing, timing_xref
                    )
                    timing_id = timing.id if timing else None

                    # Create the encounter object
                    item: Encounter = self._create(
                        Encounter,
                        {
                            "name": name,
                            "description": description,
                            "label": label,
                            "type": encounter_type,
                            "environmentalSettings": settings,
                            "contactModes": modes,
                            "transitionStartRule": start_rule,
                            "transitionEndRule": end_rule,
                            "scheduledAtId": timing_id,
                        },
                    )

                    if item:
                        self.items.append(item)

        except Exception as e:
            self._sheet_exception(e)
