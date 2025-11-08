from usdm4.api.study import Study
from usdm4_excel.export.base.collection_panel import CollectionPanel


class StudyPopulationPanel(CollectionPanel):
    def execute(self, study: Study) -> list[list[dict]]:
        collection = []
        self._add_default(collection)
        return super().execute(
            collection,
            [
                "level",
                "name",
                "description",
                "label",
                "plannedCompletionNumber",
                "plannedEnrollmentNumber",
                "plannedAge",
                "plannedSexOfParticipants",
                "includesHealthySubjects",
            ],
        )

    def _add_default(self, collection: list):
        data = {
            "level": "Main",
            "name": "POP1",
            "description": "Default Population",
            "label": "Default Population",
            "plannedCompletionNumber": "0",
            "plannedEnrollmentNumber": "0",
            "plannedAge": "18..100 years",
            "plannedSexOfParticipants": "BOTH",
            "includesHealthySubjects": "N",
        }
        collection.append(data)
