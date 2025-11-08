from usdm4.api.study import Study
from usdm4_excel.export.base.collection_panel import CollectionPanel


class HighLevelDesignPanel(CollectionPanel):
    def execute(self, study: Study) -> list[list[dict]]:
        collection = []
        version = study.versions[0]
        design = version.studyDesigns[0]
        row_n = [""]
        row = ["Epoch/Arms"]
        for epoch in design.epochs:
            row.append(epoch.name)
            row_n.append("")
        collection.append(row)
        if design.arms:
            for arm in design.arms:
                row = row_n.copy()
                row[0] = arm.name
                collection.append(row)
        else:
            row = row_n.copy()
            row[0] = "DEFAULT_ARM"
            collection.append(row)
        return collection
