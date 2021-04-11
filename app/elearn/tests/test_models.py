from django.contrib.auth.models import User, Group
from django.test import TestCase

from elearn.models import College, Plan, Invoice


class TestCollegeAndInvoice(TestCase):
    def setUp(self) -> None:
        # register the User
        self.new_user = User.objects.create_user(
            first_name="Test",
            last_name="Case",
            email="test@example.com",
            username="test@example.com",
        )
        self.new_user.set_password("test@example.com")
        self.new_user.save()

        # Add this user to collegeadmin group
        self.collegeadmin_group = Group.objects.get(name='collegeadmin')
        self.collegeadmin_group.user_set.add(self.new_user)

        # create the plan_subscribed object
        self.plan = Plan.objects.create(
            name="Basic",
            allotted_storage_space=100.00,
            price_per_month=130.00,
            price_per_year=1560.00,
        )
        # create the new_plan for test_upgrade_plan
        self.new_plan = Plan.objects.create(
            name="Standard",
            allotted_storage_space=400.00,
            price_per_month=300.00,
            price_per_year=3600.00,
        )

        # register the User as College
        self.college = College.objects.create(
            user=self.new_user,
            plan_subscribed=self.plan,
            first_name="Test",
            last_name="College",
            college_name="Test College",
            email="testcollege@example.com",
            phone_no="+911111111111",
            card_info="1234567890123456",
        )
        self.college.set_initial_subscription_dates()
        self.college.save()

        self.invoice = Invoice.objects.create(
            college=self.college,
            plan_subscribed=self.plan,
        )
        self.invoice.pay()
        self.invoice.save()

    def test_upgrade_plan(self):
        self.college.plan_upgrade(self.new_plan)
        self.assertEquals(self.college.plan_subscribed, self.new_plan)

    def test_cancel_plan(self):
        self.college.cancel_plan()
        self.assertEquals(self.college.subscription_active, False)

    def test_college_invoice(self):
        self.invoice.pay()
        self.assertEquals(self.invoice.total_amount, self.college.plan_subscribed.price_per_year)
