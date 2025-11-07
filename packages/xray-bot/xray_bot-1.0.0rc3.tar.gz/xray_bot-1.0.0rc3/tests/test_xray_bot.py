import pytest
from xraybot import XrayBot, TestEntity, TestResultEntity, XrayResultType

local_tests = [
    TestEntity(
        key="XT-6353",
        summary="foo1",
        description="desc",
        repo_path=["foo", "2nd folder", "inner"],
        unique_identifier="tests.function.foo1",
    ),
    TestEntity(
        key="XT-6354",
        summary="foo2",
        description="desc",
        repo_path=["foo", "2nd folder"],
        unique_identifier="tests.function.foo2",
        labels=["foo", "bar"],
        req_keys=["XT-5380", "XT-5457"],
        defect_keys=["XT-6339", "XT-6338"]
    ),
    TestEntity(
        key="XT-6355",
        summary="foo3",
        description="desc",
        repo_path=["bar"],
        unique_identifier="tests.function.foo3",
        labels=["foo"],
        req_keys=["XT-5380"],
        defect_keys=["XT-6339"]
    ),
    TestEntity(
        key="XT-5791",
        summary="foo4",
        description="desc",
        repo_path=["bar"],
        unique_identifier="tests.function.foo4",
        labels=["bar"],
        req_keys=["XT-5380"]
    ),
    TestEntity(
        key="XT-6205",
        summary="foo5",
        description="desc",
        unique_identifier="tests.function.foo5",
        labels=["bar"],
        req_keys=["XT-5380"]
    )
]
test_results = [
    TestResultEntity(
        key="XT-6353",
        result=XrayResultType.FAILED
    ),
    TestResultEntity(
        key="XT-6205",
        result=XrayResultType.PASSED
    )
]
class TestXrayBot:
    @pytest.fixture(scope="class")
    def bot(self) -> XrayBot:
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0ZW5hbnQiOiIzNDJhZDk1Mi01OWVjLTMxMWQtYjVmYi00MTFmNDljNjg3M2UiLCJhY2NvdW50SWQiOiI1ZGQyYjAzYWI2YjMyMzBlZWZiNzY3ZGYiLCJpc1hlYSI6ZmFsc2UsImlhdCI6MTc2MjQ4NDA4OSwiZXhwIjoxNzYyNTcwNDg5LCJhdWQiOiJENTJEMTBCMDY4QzE0RjZBOEFDQkIyNEJDQzE1Q0RBNCIsImlzcyI6ImNvbS54YmxlbmQucGx1Z2lucy54cmF5LWVudGVycHJpc2UiLCJzdWIiOiJENTJEMTBCMDY4QzE0RjZBOEFDQkIyNEJDQzE1Q0RBNCJ9.k0k5XyczKv3Ds7OPNuv-tdNM6N79vBp-uHCSbaHaO1s"
        bot = XrayBot(
            jira_url="https://telenav.atlassian.net",
            jira_username="svcqauser01@telenav.com",
            jira_pwd="ATATT3xFfGF0MPS8zKtC-3wiT3irrjuLdLE7N6MHSpwdDTCS36ow8ikOcBLBMLUectQwPOi0iuf51iz_dN5sPNvD0LwtTLDQGvJ2RV8YbuEAMoCgdp0U1LTgf8VVn88mmg47D6AzxX-EZ1gD04TwtZdX3Ic5mEQexIqQzgqIP5NSuaACLkP34c8=D58011A6",
            jira_account_id="5dd2b03ab6b3230eefb767df",
            project_key="XT",
            xray_api_token=token,
        )
        bot.config.configure_automation_folder_name("My Automation Test Folder")
        return bot

    def test_create_tests_draft(self, bot: XrayBot):
        bot.create_tests_draft(local_tests)

    def test_sync_tests(self, bot: XrayBot):
        bot.sync_tests(local_tests)

    def test_get_xray_tests(self, bot: XrayBot):
        results = bot.get_xray_tests()
        assert results

    def test_sync_check(self, bot: XrayBot):
        bot.sync_check(local_tests)

    def test_upload_test_results(self, bot: XrayBot):
        bot.upload_test_results(
            "my test plan 1019",
            "my test execution 1019",
            test_results,
            ignore_missing=True,
            clean_obsolete=True
        )

    def test_upload_test_results_by_key(self, bot: XrayBot):
        bot.upload_test_results_by_key(
            "XT-6358",
            test_results,
            "XT-6356",
            full_test_set=True,
            clean_obsolete=True,
        )