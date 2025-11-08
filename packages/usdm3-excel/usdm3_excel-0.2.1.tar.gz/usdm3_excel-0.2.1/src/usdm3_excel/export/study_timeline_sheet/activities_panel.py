from usdm4.api.study import Study
from usdm4.api.study_version import StudyVersion
from usdm4.api.study_design import StudyDesign
from usdm4.api.schedule_timeline import ScheduleTimeline
from usdm4_excel.export.base.collection_panel import CollectionPanel


class ActivitiesPanel(CollectionPanel):
    def execute(self, study: Study) -> list[list[dict]]:
        collection = []
        version: StudyVersion = study.versions[0]
        design: StudyDesign = version.studyDesigns[0]
        timeline: ScheduleTimeline = design.main_timeline()
        activity_order = design.activity_list()
        timepoints = timeline.timepoint_list() if timeline else []

        # Blank timepoints
        row = {}
        for timepoint in timepoints:
            row[timepoint.id] = ""

        # Activities
        activities = {}
        for activity in activity_order:
            for timepoint in timepoints:
                if activity.id in timepoint.activityIds:
                    if activity.name not in activities:
                        activities[activity.name] = row.copy()
                    activities[activity.name][timepoint.id] = "X"

        # Output
        collection.append(
            ["Parent Activity", "Child Activity", "BC/Procedure/Timeline"]
            + list(row.values())
        )
        for activity in activity_order:
            if activity.name in activities:
                data = activities[activity.name]
                label = activity.label if activity.label else activity.name
                collection.append(["", label, ""] + list(data.values()))
        return collection
