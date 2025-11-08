from usdm4.api.study import Study
from usdm4.api.identifier import StudyIdentifier
from usdm4.api.address import Address
from usdm4.api.organization import Organization
from usdm4.api.study_version import StudyVersion
from usdm4_excel.export.base.collection_panel import CollectionPanel


class IdentifiersPanel(CollectionPanel):
    def execute(self, study: Study) -> list[list[dict]]:
        collection = []
        for version in study.versions:
            for item in version.studyIdentifiers:
                self._add_identifier(collection, item, version)
        return super().execute(
            collection,
            [
                "organizationIdentifierScheme",
                "organizationIdentifier",
                "organizationName",
                "organizationType",
                "studyIdentifier",
                "organizationAddress",
            ],
        )

    def _add_identifier(
        self, collection: list, item: StudyIdentifier, version: StudyVersion
    ):
        org: Organization = version.organization(item.scopeId)
        data = org.model_dump()
        data["organizationIdentifierScheme"] = data["identifierScheme"]
        data["organizationIdentifier"] = data["identifier"]
        data["organizationName"] = data["name"]
        data["organizationType"] = self._map_org_type(self._pt_from_code(org.type))
        data["organizationAddress"] = self._from_address(org.legalAddress)
        data["studyIdentifier"] = item.text
        collection.append(data)

    def _from_address(self, address: Address):
        if address is None:
            return "|||||"
        lines_to_line = (", ").join(address.lines)
        items = [lines_to_line if lines_to_line else ""]
        self._append_address_item(items, address.district)
        self._append_address_item(items, address.city)
        self._append_address_item(items, address.state)
        self._append_address_item(items, address.postalCode)
        code = address.country.code if address.country else ""
        self._append_address_item(items, code)
        return ("|").join(items)

    def _append_address_item(self, items: list[str], value: str) -> None:
        items.append(value if value else "")

    def _map_org_type(self, code: str) -> str:
        code_map = {"Pharmaceutical Company": "Clinical Study Sponsor"}
        return code_map[code] if code in code_map else code
