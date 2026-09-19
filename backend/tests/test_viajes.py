from app.api import viajes


def test_default_plan_creates_destination_specific_stages():
    plan = viajes.build_default_plan('Medellín')

    assert isinstance(plan, list)
    assert len(plan) >= 3
    assert plan[0]['title']
    assert plan[0]['day'] == 1
    assert isinstance(plan[0]['activities'], list)
    assert any('Medellín' in step.get('title', '') or 'Medellín' in step.get('summary', '') for step in plan)


def test_plan_normalizer_keeps_stage_metadata_and_budget_values():
    normalized_plan = viajes.normalize_plan([
        {'title': 'Día 1', 'summary': 'Llegada', 'activities': ['Check-in']}
    ], 'Cartagena')
    normalized_budget = viajes.normalize_budget_breakdown({'hospedaje': '700000', 'transporte': 350000})

    assert normalized_plan[0]['day'] == 1
    assert normalized_plan[0]['activities'] == ['Check-in']
    assert normalized_budget['hospedaje'] == 700000
    assert normalized_budget['transporte'] == 350000


def test_budget_breakdown_is_saved_as_numeric_values():
    trip = {
        'destino': 'Cartagena',
        'presupuesto_total': 1800000,
        'presupuesto_detallado': {
            'hospedaje': 700000,
            'transporte': 350000,
            'alimentacion': 250000,
            'actividades': 300000,
        }
    }

    totals = viajes.calculate_budget_summary(trip)

    assert totals['total'] == 1800000
    assert totals['categories']['hospedaje'] == 700000
    assert totals['used'] == 1600000
    assert totals['remaining'] == 200000
