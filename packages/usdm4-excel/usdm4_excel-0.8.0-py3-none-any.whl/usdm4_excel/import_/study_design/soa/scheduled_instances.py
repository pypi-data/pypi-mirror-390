from usdm4_excel.import_.excel_sheet_reader.base_sheet import BaseSheet
from usdm4_excel.import_.study_design.soa.soa_column_rows import SoAColumnRows
from usdm4_excel.import_.study_design.soa.scheduled_instance import ScheduledInstance

from usdm4.api.schedule_timeline_exit import ScheduleTimelineExit
from usdm4.api.scheduled_instance import ConditionAssignment
from usdm4.api.scheduled_instance import (
    ScheduledInstance as USDMScheduledInstance,
    ScheduledDecisionInstance,
)


class ScheduledInstances:
    def __init__(self, parent: BaseSheet):
        self._parent = parent
        self._items = []
        self._map = {}
        self._exits = []
        self._instances = []
        self._build_instances()
        self._set_default_references()
        self._set_condition_references()

    @property
    def items(self):
        return self._items

    @property
    def instances(self):
        return self._instances

    @property
    def exits(self):
        return self._exits

    def match(self, name):
        return self._map[name] if name in self._map else None

    def _build_instances(self):
        for col_index in range(self._parent._sheet.shape[1]):
            if col_index >= SoAColumnRows.FIRST_VISIT_COL:
                record = ScheduledInstance(self._parent, col_index)
                self._items.append(record)
                self._map[record.name] = record

    def _set_default_references(self):
        instance: ScheduledInstance
        for instance in self._items:
            item: USDMScheduledInstance = instance.item
            self._instances.append(item)
            if instance.default_name in self._map.keys():
                instance.item.defaultConditionId = self._map[
                    instance.default_name
                ].item.id
            elif instance.default_name.upper() == "(EXIT)":
                exit = self._add_exit()
                item.timelineExitId = exit.id
                self._exits.append(exit)
            else:
                self._parent._errors.error(
                    f"Default reference from {instance.name} to {instance.default_name} cannot be made, not found on the same timeline"
                )

    def _add_exit(self):
        return self._parent._create(ScheduleTimelineExit, {})

    def _set_condition_references(self):
        instance: ScheduledInstance
        for instance in self._items:
            item: ScheduledDecisionInstance = instance.item
            if item.instanceType == "ScheduledDecisionInstance":
                for condition in instance.conditions.items:
                    # print(f"COND: {condition} ")
                    if condition["name"] in self._map.keys():
                        ca = self._parent._create(
                            ConditionAssignment,
                            {
                                "condition": condition["condition"],
                                "conditionTargetId": self._map[
                                    condition["name"]
                                ].item.id,
                            },
                        )
                        if ca:
                            item.conditionAssignments.append(ca)
                    else:
                        self._parent._errors.error(
                            f"Conditonal reference from {instance.name} to {condition['name']} cannot be made, not found on the same timeline"
                        )
