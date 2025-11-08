from usdm4_excel.import_.excel_sheet_reader.base_sheet import BaseSheet
from usdm4_excel.import_.study_design.soa.soa_column_rows import SoAColumnRows
from usdm4.api.activity import Activity
from usdm4.api.biomedical_concept_surrogate import BiomedicalConceptSurrogate
from usdm4.api.procedure import Procedure
from usdm4.api.schedule_timeline import ScheduleTimeline


class SoAActivity:
    def __init__(self, parent: BaseSheet, row_index: int, map: dict):
        self._parent = parent
        self._row_index = row_index
        self._map = map
        self._biomedical_concept_surrogates = []
        self._biomedical_concepts = []
        self._parent_name = self._parent._read_cell(
            row_index, SoAColumnRows.ACTIVITY_COL
        )
        self._child_name = self._parent._read_cell(
            row_index, SoAColumnRows.CHILD_ACTIVITY_COL
        )
        self._bcs, self._prs, self._tls = self._get_observation_cell(
            row_index, SoAColumnRows.BC_COL
        )
        self.is_parent = False
        self.activity = (
            self._process_parent() if self._parent_name else self._process_child()
        )

    @property
    def biomedical_concepts(self):
        return self._biomedical_concepts

    @property
    def biomedical_concept_surrogates(self):
        return self._biomedical_concept_surrogates

    def _process_parent(self) -> Activity:
        self.is_parent = True
        if self._child_name:
            self._parent._errors.warning(
                f"Both parent '{self._parent_name}' and child activity '{self._child_name}' found, child has been ignored",
                self._parent._location(
                    self._row_index, SoAColumnRows.CHILD_ACTIVITY_COL
                ),
            )
        if self._parent_name in self._map:
            self._parent._errors.error(
                f"Parent activity '{self._parent_name}' has already been referenced in the SoA, parent has been ignored",
                self._parent._location(self._row_index, SoAColumnRows.ACTIVITY_COL),
            )
            return None
        else:
            return self._set_activity(self._parent_name, [], [], [], None)

    def _process_child(self) -> Activity:
        if self._child_name in self._map:
            self._parent._errors.error(
                f"Child activity '{self._child_name}' has already been referenced in the SoA, child has been ignored",
                self._parent._location(
                    self._row_index, SoAColumnRows.CHILD_ACTIVITY_COL
                ),
            )
            return None
        else:
            full_bc_items, surrogate_bc_items = self._set_biomedical_concepts()
            timeline = self._set_timeline()
            procedures = self._set_procedures()
            return self._set_activity(
                self._child_name,
                full_bc_items,
                surrogate_bc_items,
                procedures,
                timeline,
            )

    def _set_activity(
        self, name, full_bc_items, surrogate_bc_items, procedures, timeline
    ) -> Activity:
        activity: Activity = self._parent._builder.cross_reference.get_by_name(
            Activity, name
        )
        if activity is None:
            params = {
                "name": name,
                "description": name,
                "label": name,
                "definedProcedures": procedures,
                "biomedicalConceptIds": full_bc_items,
                "bcCategoryIds": [],
                "bcSurrogateIds": surrogate_bc_items,
                "timelineId": timeline.id if timeline else None,
            }
            activity = self._parent._create(Activity, params)
            if activity:
                self._parent._errors.warning(
                    f"No activity '{name}' found, so one has been created",
                    self._parent._location(self._row_index, SoAColumnRows.BC_COL),
                )
        else:
            activity.definedProcedures = procedures
            activity.biomedicalConceptIds = full_bc_items
            activity.bcSurrogateIds = surrogate_bc_items
            activity.timelineId = timeline.id if timeline else None
        self._map[activity.name] = activity
        return activity

    def _set_biomedical_concepts(self) -> tuple[list, list]:
        full_bc_items = []
        surrogate_bc_items = []
        for bc_name in self._bcs:
            full_bc = self._parent._builder.bc(bc_name)
            if full_bc:
                full_bc_items.append(full_bc.id)
                self._biomedical_concepts.append(full_bc)
            else:
                params = {
                    "name": bc_name,
                    "description": bc_name,
                    "label": bc_name,
                    "reference": "None set",
                }
                item = self._parent._create(
                    BiomedicalConceptSurrogate, params, False
                )  # No cross reference for BCs
                if item:
                    surrogate_bc_items.append(item.id)
                    self._biomedical_concept_surrogates.append(item)
        return full_bc_items, surrogate_bc_items

    def _set_procedures(self) -> list:
        results = []
        for procedure in self._prs:
            ref = self._parent._builder.cross_reference.get_by_name(
                Procedure, procedure
            )
            if ref:
                results.append(ref)
            else:
                self._parent._errors.warning(
                    f"No procedure '{procedure}' found, missing cross reference",
                    self._parent._location(self._row_index, SoAColumnRows.BC_COL),
                )
        return results

    def _set_timeline(self) -> ScheduleTimeline | None:
        result = None
        if self._tls:
            result = self._parent._builder.cross_reference.get_by_name(
                ScheduleTimeline, self._tls[0]
            )
            if not result:
                self._parent._errors.warning(
                    f"No timeline '{self._tls[0]}' found, missing cross reference",
                    self._parent._location(self._row_index, SoAColumnRows.BC_COL),
                )
        return result

    def _get_observation_cell(
        self, row_index: int, col_index: int
    ) -> tuple[list, list, list]:
        bcs = []
        prs = []
        tls = []
        if not self._parent._empty(row_index, col_index):
            value = self._parent._read_cell(row_index, col_index)
            outer_parts = value.split(",")
            for outer_part in outer_parts:
                parts = outer_part.split(":")
                if parts[0].strip().upper() == "BC":
                    bcs.append(parts[1].strip())
                elif parts[0].strip().upper() == "PR":
                    prs.append(parts[1].strip())
                elif parts[0].strip().upper() == "TL":
                    tls.append(parts[1].strip())
                else:
                    pass
        return bcs, prs, tls
