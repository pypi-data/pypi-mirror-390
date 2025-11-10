from pbi_core import LocalReport
from pbi_core.ssas.model_tables.expression.local import LocalExpression


def test_expression_children(ssas_pbix):
    expr = ssas_pbix.ssas.expressions.find(616)
    children = expr.children()
    assert len(children) == 2
    assert {c.pbi_core_name() for c in children} == {"PBI_ResultType", "PBI_NavigationStepName"}
    assert {c.__class__.__name__ for c in children} == {"Annotation"}


def test_expression_parents(ssas_pbix):
    expr = ssas_pbix.ssas.expressions.find(616)
    parents = expr.parents()
    assert len(parents) == 1
    assert {p.pbi_core_name() for p in parents} == {"Model"}
    assert {p.__class__.__name__ for p in parents} == {"Model"}


def test_expression_alter(ssas_pbix):
    expr = ssas_pbix.ssas.expressions.find(616)
    expr.name = "new_country"
    expr.alter()


def test_expression_delete():
    ssas_pbix = LocalReport.load_pbix("test_ssas.pbix")
    expr = ssas_pbix.ssas.expressions.find(616)
    expr.delete()


def test_expression_create():
    ssas_report = LocalReport.load_pbix("test_ssas.pbix")
    m = LocalExpression(
        name="Test Expression",
        expression="1",
        model_id=ssas_report.ssas.model.id,
    ).load(ssas_report.ssas)
