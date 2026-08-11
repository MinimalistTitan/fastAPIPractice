from __future__ import annotations

from dataclasses import dataclass

from app.core.config import Settings
from app.core.database import SessionFactory
from app.modules.operations.application.operation_services import OperationsService
from app.modules.operations.infrastructure.repositories.operations import OperationsRepository
from app.modules.operations.infrastructure.tools import (
    build_get_asset_status_tool,
    build_get_maintenance_tickets_tool,
    build_get_production_schedule_tool,
    build_get_spare_parts_availability_tool,
    build_get_work_orders_tool,
)
from app.shared.kernel.tools import LocalTool


@dataclass(frozen=True, slots=True)
class OperationsModule:
    service: OperationsService
    get_work_orders_tool: LocalTool
    get_asset_status_tool: LocalTool
    get_maintenance_tickets_tool: LocalTool
    get_spare_parts_availability_tool: LocalTool
    get_production_schedule_tool: LocalTool

    @property
    def tools(self) -> tuple[LocalTool, ...]:
        return (
            self.get_work_orders_tool,
            self.get_asset_status_tool,
            self.get_maintenance_tickets_tool,
            self.get_spare_parts_availability_tool,
            self.get_production_schedule_tool,
        )


def build_operations_module(
    settings: Settings,
    session_factory: SessionFactory,
) -> OperationsModule:
    def repository_factory() -> OperationsRepository:
        return OperationsRepository(session_factory())

    service = OperationsService(repository_factory=repository_factory)

    return OperationsModule(
        service=service,
        get_work_orders_tool=build_get_work_orders_tool(repository_factory),
        get_asset_status_tool=build_get_asset_status_tool(repository_factory),
        get_maintenance_tickets_tool=build_get_maintenance_tickets_tool(repository_factory),
        get_spare_parts_availability_tool=build_get_spare_parts_availability_tool(repository_factory),
        get_production_schedule_tool=build_get_production_schedule_tool(repository_factory),
    )