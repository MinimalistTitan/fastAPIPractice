from typing import Any

from app.modules.users.application.ports import UserUnitOfWorkFactory
from app.modules.users.application.use_cases import (
    RunUserConsistencyAudit,
    UserConsistencyAuditCommand,
)
from app.modules.users.contracts.consistency_auditor import (
    TOOL_USERS_CONSISTENCY_AUDITOR_V1,
    ConsistencySeverity,
    ConsistencyToolResultCode,
    UserConsistencyAuditorInputV1,
    UserConsistencyAuditorOutputV1,
    UserConsistencyFindingV1,
    UserConsistencySeverityTotalsV1,
)
from app.shared.kernel.tools import LocalTool


def build_users_consistency_auditor_tool(
    unit_of_work_factory: UserUnitOfWorkFactory,
) -> LocalTool:
    use_case = RunUserConsistencyAudit(unit_of_work_factory=unit_of_work_factory)

    async def invoke(payload: dict[str, Any]) -> dict[str, Any]:
        data = UserConsistencyAuditorInputV1.model_validate(payload)

        command = UserConsistencyAuditCommand(
            checks=tuple(check.value for check in data.checks) if data.checks else None,
            limit_per_check=data.limit_per_check,
            run_id=data.run_id,
            now_utc=data.now_utc,
        )
        report = await use_case.execute(command)

        totals = UserConsistencySeverityTotalsV1()
        findings: list[UserConsistencyFindingV1] = []
        for item in report.findings:
            if item.severity == ConsistencySeverity.CRITICAL:
                totals.critical += 1
            elif item.severity == ConsistencySeverity.HIGH:
                totals.high += 1
            elif item.severity == ConsistencySeverity.MEDIUM:
                totals.medium += 1
            elif item.severity == ConsistencySeverity.LOW:
                totals.low += 1

            findings.append(
                UserConsistencyFindingV1(
                    check_id=item.check_id,
                    severity=item.severity,
                    user_id=item.user_id,
                    message=item.message,
                    evidence=item.evidence,
                )
            )

        output = UserConsistencyAuditorOutputV1(
            run_id=report.run_id,
            result_code=(
                ConsistencyToolResultCode.ISSUES_FOUND
                if report.issues_total > 0
                else ConsistencyToolResultCode.OK
            ),
            generated_at_utc=report.generated_at_utc,
            total_users=report.total_users,
            checks_executed=report.checks_executed,
            issues_total=report.issues_total,
            issues_by_severity=totals,
            findings=findings,
        )
        return output.model_dump(mode="json")

    return LocalTool(
        name=TOOL_USERS_CONSISTENCY_AUDITOR_V1,
        description="Deterministic consistency audit for users table",
        input_model=UserConsistencyAuditorInputV1,
        output_model=UserConsistencyAuditorOutputV1,
        invoke=invoke,
    )