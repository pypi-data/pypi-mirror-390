from usdm4.api.study import Study
from usdm4.api.study_design import StudyDesign
from usdm4_excel.export.base.base_panel import BasePanel


class MainPanel(BasePanel):
    def execute(self, study: Study) -> list[list[dict]]:
        version = study.versions[0]
        design = version.studyDesigns[0]
        result = []
        result.append(["studyDesignName", design.name])
        result.append(["studyDesignDescription", design.description])
        result.append(["therapeuticAreas", self._tas(design)])
        result.append(["studyDesignRationale", design.rationale])
        result.append(
            [
                "studyDesignBlindingScheme",
                self._pt_from_alias_code(design.blindingSchema),
            ]
        )
        result.append(
            [
                "trialIntentTypes",
                (", ").join([self._pt_from_code(x) for x in design.intentTypes]),
            ]
        )
        result.append(
            [
                "trialSubTypes",
                (", ").join([self._pt_from_code(x) for x in design.subTypes]),
            ]
        )
        result.append(["interventionModel", self._pt_from_code(design.model)])
        result.append(["masking", ""])
        result.append(
            [
                "characteristics",
                (", ").join([self._pt_from_code(x) for x in design.characteristics]),
            ]
        )
        result.append(["mainTimeline", "mainTimeline"])
        result.append(["otherTimelines", ""])
        # result.append(["studyType", self._pt_from_code(design.studyType)])
        # result.append(["studyPhase", self._pt_from_alias_code(design.studyPhase)])
        # result.append(["spare", ""])
        return result

    def _tas(self, design: StudyDesign) -> str:
        items = []
        for area in design.therapeuticAreas:
            self.ct_version.add(area.codeSystem, area.codeSystemVersion)
            items.append(f"{area.codeSystem}: {area.code} = {area.decode}")
        return ", ".join(items)
