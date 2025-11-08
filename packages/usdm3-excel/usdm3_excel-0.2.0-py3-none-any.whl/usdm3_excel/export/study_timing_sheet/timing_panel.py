import re
from usdm4.api.study import Study
from usdm4.api.timing import Timing
from usdm4.api.code import Code
from usdm4.api.schedule_timeline import ScheduleTimeline
from usdm4_excel.export.base.collection_panel import CollectionPanel


class TimingPanel(CollectionPanel):
    def execute(self, study: Study) -> list[list[dict]]:
        collection = []
        for version in study.versions:
            for design in version.studyDesigns:
                for timeline in design.scheduleTimelines:
                    for item in timeline.timings:
                        self._add_timing(collection, item, timeline)
        return super().execute(
            collection,
            [
                "name",
                "description",
                "label",
                "type",
                "from",
                "to",
                "timingValue",
                "toFrom",
                "window",
            ],
        )

    def _add_timing(self, collection: list, item: Timing, timeline: ScheduleTimeline):
        data = item.model_dump()
        data["type"] = self._encode_type(item.type)
        from_tp = timeline.find_timepoint(item.relativeFromScheduledInstanceId)
        data["from"] = from_tp.name if from_tp else ""
        to_tp = timeline.find_timepoint(item.relativeToScheduledInstanceId)
        data["to"] = to_tp.name if to_tp else ""
        data["timingValue"] = self._decode_iso8601_duration(item.value)
        data["window"] = item.windowLabel
        data["toFrom"] = self._encode_to_from(item.relativeToFrom)
        collection.append(data)

    def _encode_type(self, code: Code):
        mapping = {"C201358": "FIXED", "C201356": "AFTER", "C201357": "BEFORE"}
        return mapping[code.code]

    def _encode_to_from(self, code: Code):
        mapping = {
            "C201355": "S2S",
            "C201354": "S2E",
            "C201353": "E2S",
            "C201352": "E2E",
        }
        return mapping[code.code]

    def _decode_iso8601_duration(self, value: str) -> str:
        units_map = {
            "Y": "Years",
            "M": "Months",
            "W": "Weeks",
            "D": "Days",
            "H": "Hours",
            "M": "Minutes",
            "S": "Seconds",
        }
        units_char = value[-1]
        if units_char in units_map:
            units_str = units_map[units_char]
            match = re.search(r'\d+', value)
            if match:
                return f"{match.group()} {units_str}"
        return "1 Day"
