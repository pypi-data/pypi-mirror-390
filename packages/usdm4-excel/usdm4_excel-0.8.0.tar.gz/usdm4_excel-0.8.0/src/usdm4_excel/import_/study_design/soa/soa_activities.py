from usdm4_excel.import_.excel_sheet_reader.base_sheet import BaseSheet
from usdm4_excel.import_.study_design.soa.soa_column_rows import SoAColumnRows
from usdm4_excel.import_.study_design.soa.soa_activity import SoAActivity


class SoAActivities:
    def __init__(
        self,
        parent: BaseSheet,
    ):
        self._parent = parent
        self.items = []
        self._map = {}
        self._parent_activity = None
        for row_index, col_def in self._parent._sheet.iterrows():
            if row_index >= SoAColumnRows.FIRST_ACTIVITY_ROW:
                activity = SoAActivity(self._parent, row_index, self._map)
                the_activity = activity.activity
                if the_activity:
                    self.items.append(activity)

    def group_and_link(self):
        activities = []
        biomedical_concepts = []
        biomedical_concept_surrogates = []
        item: SoAActivity
        for item in self.items:
            the_activity = item.activity
            activities.append(the_activity)
            biomedical_concept_surrogates += item.biomedical_concept_surrogates
            biomedical_concepts += item.biomedical_concepts
        self._parent._double_link(activities, "previousId", "nextId")
        return activities, biomedical_concepts, biomedical_concept_surrogates

    def set_parents(self):
        parents = any([x.is_parent for x in self.items])
        if parents:
            parent_activity = None
            for item in self.items:
                the_activity = item.activity
                if item.is_parent:
                    parent_activity = the_activity
                elif parent_activity:
                    parent_activity.childIds.append(the_activity.id)
                else:
                    self._parent.errors.error(
                        f"Child activity with name '{the_activity.name}' does not have a parent specified"
                    )
