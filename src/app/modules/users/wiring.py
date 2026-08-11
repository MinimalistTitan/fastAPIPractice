from dataclasses import dataclass

from app.core.config import Environment, Settings
from app.core.database import SessionFactory
from app.modules.users.api.user_auditor_tools import (
    build_users_consistency_auditor_tool,
)
from app.modules.users.application.ports import UserUnitOfWorkFactory
from app.modules.users.application.use_cases import GetUser, RegisterUser
from app.modules.users.infrastructure.unit_of_work import UserUnitOfWork
from app.shared.kernel.tools import LocalTool


@dataclass(frozen=True, slots=True)
class UsersModule:
    unit_of_work_factory: UserUnitOfWorkFactory
    register_user: RegisterUser
    get_user: GetUser
    consistency_auditor_tool: LocalTool
    audit_endpoint_enabled: bool

    @property
    def tools(self) -> tuple[LocalTool, ...]:
        return (self.consistency_auditor_tool,)


def build_users_module(
    settings: Settings,
    session_factory: SessionFactory,
) -> UsersModule:
    def unit_of_work_factory() -> UserUnitOfWork:
        return UserUnitOfWork(session_factory)

    consistency_auditor_tool = build_users_consistency_auditor_tool(
        unit_of_work_factory=unit_of_work_factory
    )

    return UsersModule(
        unit_of_work_factory=unit_of_work_factory,
        register_user=RegisterUser(
            unit_of_work_factory=unit_of_work_factory,
        ),
        get_user=GetUser(
            unit_of_work_factory=unit_of_work_factory,
        ),
        consistency_auditor_tool=consistency_auditor_tool,
        audit_endpoint_enabled=settings.environment
        in {
            Environment.LOCAL,
            Environment.TEST,
        },
    )