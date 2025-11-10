from pbi_core import LocalReport
from pbi_core.ssas.model_tables.role_membership.enums import MemberType
from pbi_core.ssas.model_tables.role_membership.local import LocalRoleMembership


def test_role_membership_create():
    ssas_report = LocalReport.load_pbix("test_ssas.pbix")

    LocalRoleMembership(
        identity_provider="AzureAD",
        member_id="user@example.com",
        member_name="User Example",
        member_type=MemberType.USER,
        role_id=ssas_report.ssas.roles[0].id,
    ).load(ssas_report.ssas)
