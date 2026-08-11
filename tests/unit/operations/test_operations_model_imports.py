from app.modules.operations.infrastructure.manufacturing_maintenance.models import (
    AssetRecord,
    SiteRecord,
    SparePartRecord,
    WorkOrderRecord,
)


def test_manufacturing_maintenance_model_package_exports() -> None:
    assert AssetRecord.__name__ == "AssetRecord"
    assert SiteRecord.__name__ == "SiteRecord"
    assert SparePartRecord.__name__ == "SparePartRecord"
    assert WorkOrderRecord.__name__ == "WorkOrderRecord"
