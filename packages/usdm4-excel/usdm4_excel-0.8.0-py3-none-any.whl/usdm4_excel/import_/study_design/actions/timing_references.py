from simple_error_log.errors import Errors
from usdm4_excel.import_.study_design.soa_sheet import SoASheet
from usdm4_excel.import_.study_design.timing_sheet import TimingSheet


@staticmethod
def check_timing_references(soas: list[SoASheet], timing: TimingSheet, errors: Errors):
    timing_check = {}
    for item in timing.items:
        timing_check[item.name] = None
    for soa in soas:
        soa.timeline.timings = soa.check_timing_references(timing.items, timing_check)
    for item in timing.items:
        if not timing_check[item.name]:
            errors.warning(f"Timing with name '{item.name}' not referenced")


@staticmethod
def set_timing_references(soas: list[SoASheet], timing: TimingSheet, errors: Errors):
    for timing in timing.items:
        found = {"from": False, "to": False}
        for soa in soas:
            if not found["from"]:
                instance = soa.timing_match(timing.relativeFromScheduledInstanceId)
                if instance:
                    item = instance.item
                    timing.relativeFromScheduledInstanceId = item.id
                    found["from"] = True
            if not found["to"]:
                instance = soa.timing_match(timing.relativeToScheduledInstanceId)
                if instance:
                    item = instance.item
                    timing.relativeToScheduledInstanceId = item.id
                    found["to"] = True
        if not found["from"]:
            errors.error(
                f"Unable to find timing 'from' reference with name {timing.relativeFromScheduledInstanceId}"
            )
        if not found["to"]:
            errors.error(
                f"Unable to find timing 'to' reference with name {timing.relativeToScheduledInstanceId}"
            )
