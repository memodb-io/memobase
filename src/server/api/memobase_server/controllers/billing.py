from pydantic import ValidationError
from ..models.utils import Promise
from ..models.database import (
    ProjectBilling,
    Billing,
    next_month_first_day,
)
from ..models.response import CODE, IdData, IdsData, UserProfilesData, BillingData
from ..connectors import Session
from ..telemetry.capture_key import get_int_key, capture_int_key
from ..env import (
    LOG,
    CONFIG,
    TelemetryKeyName,
    USAGE_TOKEN_LIMIT_MAP,
    BILLING_REFILL_AMOUNT_MAP,
    BillingStatus,
)
from datetime import datetime, date


async def get_project_billing(project_id: str) -> Promise[BillingData]:
    with Session() as session:
        billing = (
            session.query(ProjectBilling)
            .filter(ProjectBilling.project_id == project_id)
            .first()
        )
        if billing is None:
            return await fallback_billing_data(project_id)
            # return Promise.reject(CODE.NOT_FOUND, "Billing not found").to_response(
            #     BillingData
            # )
        billing = billing.billing

        this_month_token_costs_in = await get_int_key(
            TelemetryKeyName.llm_input_tokens, project_id, in_month=True
        )
        this_month_token_costs_out = await get_int_key(
            TelemetryKeyName.llm_output_tokens, project_id, in_month=True
        )
        usage_left_this_billing = billing.usage_left

        next_refill_date = billing.next_refill_at
        today = datetime.now(next_refill_date.tzinfo)
        if (
            today > next_refill_date
            and usage_left_this_billing is not None
            and BILLING_REFILL_AMOUNT_MAP[BillingStatus.free] is not None
            and usage_left_this_billing < BILLING_REFILL_AMOUNT_MAP[BillingStatus.free]
        ):
            usage_left_this_billing = BILLING_REFILL_AMOUNT_MAP[BillingStatus.free]

            billing.next_refill_at = next_month_first_day()
            billing.usage_left = usage_left_this_billing
            session.commit()
    billing_data = BillingData(
        token_left=usage_left_this_billing,
        next_refill_at=next_refill_date,
        project_token_cost_month=this_month_token_costs_in + this_month_token_costs_out,
    )
    return Promise.resolve(billing_data)


async def fallback_billing_data(project_id: str) -> Promise[BillingData]:
    from .project import get_project_status

    this_month_token_costs_in = await get_int_key(
        TelemetryKeyName.llm_input_tokens, project_id, in_month=True
    )
    this_month_token_costs_out = await get_int_key(
        TelemetryKeyName.llm_output_tokens, project_id, in_month=True
    )

    this_month_token_costs = this_month_token_costs_in + this_month_token_costs_out
    p = await get_project_status(project_id)
    if not p.ok():
        return p
    status = p.data()
    if status not in USAGE_TOKEN_LIMIT_MAP:
        return Promise.reject(
            CODE.INTERNAL_SERVER_ERROR, f"Invalid project status: {status}"
        )
    usage_token_limit = USAGE_TOKEN_LIMIT_MAP[status]
    if usage_token_limit < 0:
        this_month_left_tokens = None
    else:
        this_month_left_tokens = usage_token_limit - this_month_token_costs

    # Calculate first day of next month
    today = date.today()
    if today.month == 12:
        next_month = date(today.year + 1, 1, 1)
    else:
        next_month = date(today.year, today.month + 1, 1)

    return Promise.resolve(
        BillingData(
            token_left=this_month_left_tokens,
            next_refill_at=next_month,
            project_token_cost_month=this_month_token_costs,
        )
    )


async def project_cost_token_billing(
    project_id: str, input_tokens: int, output_tokens: int
) -> Promise[None]:
    await capture_int_key(
        TelemetryKeyName.llm_input_tokens, input_tokens, project_id=project_id
    )
    await capture_int_key(
        TelemetryKeyName.llm_output_tokens, output_tokens, project_id=project_id
    )
    with Session() as session:
        _billing = (
            session.query(ProjectBilling)
            .filter(ProjectBilling.project_id == project_id)
            .one_or_none()
        )
        if _billing is None:
            return Promise.reject(CODE.NOT_FOUND, "Billing not found")
        billing = _billing.billing

        if billing.usage_left is not None:
            billing.usage_left -= input_tokens + output_tokens
            session.commit()
    return Promise.resolve(None)
