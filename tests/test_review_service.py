from types import SimpleNamespace

import pytest

from app.models.academic import STATUS_APPROVED, STATUS_DRAFT, STATUS_SUBMITTED
from app.services.plan_service import PlanError
from app.services.review_service import ReviewService


class FakePlanRepository:
    def __init__(self, status, comment=None):
        self.plan = SimpleNamespace(id=1, student_id=7, status=status, comment=comment)

    def get_by_id(self, plan_id):
        return self.plan if plan_id == self.plan.id else None

    def save(self, plan):
        return plan


def test_approving_clears_an_earlier_denial_comment():
    service = ReviewService(FakePlanRepository(STATUS_SUBMITTED, comment="old reason"), None)

    plan = service.approve(1)

    assert (plan.status, plan.comment) == (STATUS_APPROVED, None)


def test_denying_returns_the_plan_to_draft_with_the_comment():
    service = ReviewService(FakePlanRepository(STATUS_SUBMITTED, comment="old reason"), None)

    with pytest.raises(PlanError):
        service.deny(1, "   ")  # a comment is mandatory
    assert service.plan_repo.plan.status == STATUS_SUBMITTED

    plan = service.deny(1, "  new reason ")

    assert (plan.status, plan.comment) == (STATUS_DRAFT, "new reason")


@pytest.mark.parametrize("status", [STATUS_DRAFT, STATUS_APPROVED])
def test_only_a_submitted_plan_can_be_decided(status):
    service = ReviewService(FakePlanRepository(status), None)

    for decide in [lambda: service.approve(1), lambda: service.deny(1, "reason"), lambda: service.approve(99)]:
        with pytest.raises(PlanError):
            decide()
