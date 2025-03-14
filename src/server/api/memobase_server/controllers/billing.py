from pydantic import ValidationError
from ..models.utils import Promise
from ..models.database import (
    GeneralBlob,
    UserProfile,
    ProjectBilling,
    Billing,
    next_month_first_day,
)
from ..models.response import CODE, IdData, IdsData, UserProfilesData, BillingData
from ..connectors import Session
from ..telemetry.capture_key import get_int_key
from ..env import LOG, CONFIG, TelemetryKeyName, USAGE_TOKEN_LIMIT_MAP
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
        billing_status = billing.billing_status
        usage_left_this_billing = billing.usage_left

        today = datetime.now()
        next_refill_date = billing.next_refill_at
        if today > next_refill_date:
            usage_left_this_billing = billing.refill_amount

            billing.next_refill_at = next_month_first_day()
            billing.usage_left = usage_left_this_billing
            session.commit()

    billing_data = BillingData(
        billing_status=billing_status,
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
            billing_status=status,
            token_left=this_month_left_tokens,
            next_refill_at=next_month,
            project_token_cost_month=this_month_token_costs,
        )
    )
