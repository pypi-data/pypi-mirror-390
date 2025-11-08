from usdm4.api.study import Study
from usdm4.api.study_version import StudyVersion
from usdm4_excel.export.base.base_panel import BasePanel


class MainPanel(BasePanel):
    def execute(self, study: Study) -> list[list[dict]]:
        version = study.versions[0]
        result = []
        result.append(["name", study.name])
        result.append(["studyTitle", ""])
        result.append(["studyVersion", version.versionIdentifier])
        result.append(["studyType", ""])
        result.append(["studyPhase", version.studyDesigns[0].phase().decode])
        result.append(["studyAcronym", version.acronym_text()])
        result.append(["studyRationale", version.rationale])
        result.append(["businessTherapeuticAreas", self._business_tas(version)])
        result.append(["briefTitle", version.short_title_text()])
        result.append(["officialTitle", version.official_title_text()])
        result.append(["publicTitle", ""])
        result.append(["scientificTitle", ""])
        result.append(["protocolVersion", study.documentedBy[0].versions[0].version])
        result.append(
            ["protocolStatus", study.documentedBy[0].versions[0].status.decode]
        )
        return result

    def _business_tas(self, version: StudyVersion) -> str:
        items = []
        for area in version.businessTherapeuticAreas:
            self.ct_version.add(area.codeSystem, area.codeSystemVersion)
            items.append(f"{area.codeSystem}: {area.code} = {area.decode}")
        return ", ".join(items)
