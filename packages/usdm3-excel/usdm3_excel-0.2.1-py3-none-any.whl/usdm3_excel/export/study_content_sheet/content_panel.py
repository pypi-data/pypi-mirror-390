from usdm4.api.study import Study
from usdm4.api.study_version import StudyVersion
from usdm4.api.study_definition_document_version import StudyDefinitionDocumentVersion
from usdm4.api.narrative_content import NarrativeContent, NarrativeContentItem
from usdm4_excel.export.base.collection_panel import CollectionPanel


class ContentPanel(CollectionPanel):
    def execute(self, study: Study) -> list[list[dict]]:
        last_section = "0"
        collection = []
        for version in study.versions:
            for doc_version_id in version.documentVersionIds:
                doc = self._find_document_version(study, doc_version_id)
                if doc:
                    for nc in doc.contents:
                        nc.sectionNumber = (
                            nc.sectionNumber if nc.sectionNumber else last_section
                        )
                        last_section = nc.sectionNumber
                        self._add_content(collection, nc, version)
        return super().execute(
            collection,
            [
                "name",
                "sectionNumber",
                "sectionTitle",
                "text",
            ],
        )

    def _add_content(
        self, collection: list, item: NarrativeContent, version: StudyVersion
    ):
        data = item.model_dump()
        nci = self._find_content_item(version, item.contentItemId)
        data["text"] = nci.text if nci else None
        collection.append(data)

    def _find_document_version(
        self, study: Study, id: str
    ) -> StudyDefinitionDocumentVersion:
        for doc in study.documentedBy:
            doc_version = next((x for x in doc.versions if x.id == id), None)
            if doc_version:
                return doc_version
        return None

    def _find_content_item(
        self, version: StudyVersion, id: str
    ) -> NarrativeContentItem:
        return next((x for x in version.narrativeContentItems if x.id == id), None)
