from usdm4.api.study import Study
from usdm4.api.governance_date import GovernanceDate
from usdm4_excel.export.base.collection_panel import CollectionPanel


class DatesPanel(CollectionPanel):
    def execute(self, study: Study) -> list[list[dict]]:
        collection = []
        for version in study.versions:
            for date in version.dateValues:
                self._add_date(collection, date, "study_version")
            for amendment in version.amendments:
                for date in amendment.dateValues:
                    self._add_date(collection, date, "amendment")
        for document in study.documentedBy:
            for version in document.versions:
                for date in version.dateValues:
                    self._add_date(collection, date, "protocol_document")
        return super().execute(
            collection,
            ["category", "name", "description", "label", "type", "date", "scopes"],
        )

    def _add_date(self, collection: list, date: GovernanceDate, category: str):
        data = date.model_dump()
        data["type"] = self._pt_from_code(date.type)
        data["date"] = self._date_from_date(date.dateValue)
        data["scopes"] = self._scopes(date.geographicScopes)
        data["category"] = category
        collection.append(data)
