from usdm4_excel.import_.excel_sheet_reader.base_sheet import BaseSheet
from usdm4_excel.import_.study_design.soa.soa_column_rows import SoAColumnRows
from usdm4_excel.import_.types.condition_type import ConditionType
from usdm4.api.scheduled_instance import (
    ScheduledInstance as USDMScheduledInstance,
    ScheduledActivityInstance,
    ScheduledDecisionInstance,
)
from usdm4.api.encounter import Encounter
from usdm4.api.study_epoch import StudyEpoch
from usdm4.api.activity import Activity


class ScheduledInstance:
    def __init__(self, parent: BaseSheet, col_index):
        self._parent = parent
        self._item: USDMScheduledInstance = None
        self._col_index = col_index
        epoch_id = None
        encounter_id = None
        name = self._parent._read_cell(SoAColumnRows.NAME_ROW, col_index)
        self.name = name
        description = self._parent._read_cell(SoAColumnRows.DESCRIPTION_ROW, col_index)
        label = self._parent._read_cell(SoAColumnRows.LABEL_ROW, col_index)
        epoch_name = self._parent._read_cell(SoAColumnRows.EPOCH_ROW, col_index)
        encounter_name = self._parent._read_cell(SoAColumnRows.ENCOUNTER_ROW, col_index)
        type = self._parent._read_cell(SoAColumnRows.TYPE_ROW, col_index)
        self.default_name = self._parent._read_cell(
            SoAColumnRows.DEFAULT_ROW, col_index
        )
        self.conditions = ConditionType(
            self._parent._read_cell(SoAColumnRows.CONDITIONS_ROW, col_index),
            self._parent._errors,
        )
        if encounter_name:
            encounter = self._parent._builder.cross_reference.get_by_name(
                Encounter, encounter_name
            )
            if encounter:
                encounter_id = encounter.id
            else:
                self._parent._errors.warning(
                    f"Failed to find encounter with name '{encounter_name}'"
                )
        if epoch_name:
            epoch = self._parent._builder.cross_reference.get_by_name(
                StudyEpoch, epoch_name
            )
            if epoch:
                epoch_id = epoch.id
            else:
                self._parent._errors.warning(
                    f"Failed to find epoch with name '{epoch_name}'"
                )
        try:
            if type.upper() == "ACTIVITY":
                self._item = self._parent._create(
                    ScheduledActivityInstance,
                    {
                        "name": name,
                        "description": description,
                        "label": label,
                        "timelineExitId": None,
                        "encounterId": encounter_id,
                        "scheduledInstanceTimelineId": None,
                        "defaultConditionId": None,
                        "epochId": epoch_id,
                        "activityIds": self._add_activities(),
                    },
                )
            elif type.upper() == "DECISION":
                self._item = self._parent._create(
                    ScheduledDecisionInstance,
                    {
                        "name": name,
                        "description": description,
                        "label": label,
                        "timelineExitId": None,
                        "scheduledInstanceTimelineId": None,
                        "defaultConditionId": None,
                        "conditionAssignments": [],
                    },
                )
            else:
                self._parent._errors.warning(
                    f"Unrecognized ScheduledInstance type: '{type}'"
                )
        except Exception as e:
            self._parent._errors.exception("Error raised reading sheet", e)

    @property
    def item(self) -> USDMScheduledInstance:
        return self._item

    def _add_activities(self):
        activities = []
        row = 0
        column = self._parent._sheet.iloc[:, self._col_index]
        for cell in column:
            if row >= SoAColumnRows.FIRST_ACTIVITY_ROW:
                activity_name = self._parent._read_cell(
                    row, SoAColumnRows.CHILD_ACTIVITY_COL
                )
                if str(cell).upper() == "X":
                    activity = self._parent._builder.cross_reference.get_by_name(
                        Activity, activity_name
                    )
                    if activity:
                        activities.append(activity.id)
                    else:
                        self._parent._errors.warning(
                            f"Unable to find activity '{activity_name}' when adding to schedule instance"
                        )
            row += 1
        return activities
