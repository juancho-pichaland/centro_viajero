from types import SimpleNamespace

from app.api import usuarios


def test_build_user_dashboard_returns_operational_summary():
    user = SimpleNamespace(id=1, nombre='Juan García', email='juan@centro.viajero')
    trip = SimpleNamespace(
        titulo='Ruta por Cartagena',
        destino='Cartagena',
        estado='En preparación',
        presupuesto_total=1800000,
        presupuesto_detallado={'hospedaje': 700000, 'transporte': 350000},
        plan=[{'day': 1, 'title': 'Llegada', 'activities': ['Confirmar check-in']}],
    )
    tasks = [
        SimpleNamespace(titulo='Confirmar alojamiento', completada=False),
        SimpleNamespace(titulo='Reservar tour', completada=True),
    ]

    db = SimpleNamespace(
        scalar=lambda *args, **kwargs: trip,
        scalars=lambda *args, **kwargs: SimpleNamespace(all=lambda: tasks),
    )

    summary = usuarios.build_user_dashboard(user, db)

    assert summary['nombre'] == 'Juan García'
    assert summary['travel_readiness_score'] >= 0
    assert summary['next_focus']
    assert summary['budget_status'] in {'within_budget', 'watching_budget', 'over_budget'}
    assert summary['trip_destino'] == 'Cartagena'


def test_build_operations_summary_returns_business_health():
    users = [
        SimpleNamespace(id=1, nombre='Ana'),
        SimpleNamespace(id=2, nombre='Luis'),
    ]
    trips = [
        SimpleNamespace(id=1, usuario_id=1, estado='En preparación', presupuesto_total=1000000, presupuesto_detallado={'hospedaje': 500000, 'transporte': 300000}, plan=[{'title': 'Llegada'}]),
        SimpleNamespace(id=2, usuario_id=2, estado='Confirmado', presupuesto_total=2000000, presupuesto_detallado={'hospedaje': 1200000, 'transporte': 500000}, plan=[{'title': 'Salida'}]),
    ]
    tasks = [
        SimpleNamespace(viaje_id=1, completada=False),
        SimpleNamespace(viaje_id=1, completada=True),
        SimpleNamespace(viaje_id=2, completada=True),
    ]

    class FakeResult:
        def __init__(self, rows):
            self._rows = rows

        def all(self):
            return self._rows

    class FakeDB:
        def scalars(self, query):
            query_text = str(query).lower()
            if 'usuarios' in query_text:
                return FakeResult(users)
            if 'viajes' in query_text:
                return FakeResult(trips)
            if 'tareas' in query_text:
                return FakeResult(tasks)
            return FakeResult([])

    summary = usuarios.build_operations_summary(FakeDB())

    assert summary['total_usuarios'] == 2
    assert summary['total_viajes'] == 2
    assert summary['viajes_activos'] >= 1
    assert summary['promedio_preparacion'] >= 0
    assert summary['presupuesto_total'] > 0
    assert summary['alertas_presupuesto'] >= 0
    assert 'foco_principal' in summary


def test_build_admin_overview_returns_role_based_business_controls():
    users = [
        SimpleNamespace(id=1, nombre='Ana', rol='admin'),
        SimpleNamespace(id=2, nombre='Luis', rol='traveler'),
        SimpleNamespace(id=3, nombre='Marta', rol='traveler'),
    ]
    trips = [
        SimpleNamespace(id=1, usuario_id=2, estado='En preparación', presupuesto_total=1200000, presupuesto_detallado={'hospedaje': 450000, 'transporte': 250000}, plan=[{'title': 'Llegada'}]),
        SimpleNamespace(id=2, usuario_id=3, estado='Confirmado', presupuesto_total=1800000, presupuesto_detallado={'hospedaje': 950000, 'transporte': 400000}, plan=[{'title': 'Salida'}]),
    ]
    tasks = [
        SimpleNamespace(viaje_id=1, completada=False),
        SimpleNamespace(viaje_id=2, completada=True),
    ]

    class FakeResult:
        def __init__(self, rows):
            self._rows = rows

        def all(self):
            return self._rows

    class FakeDB:
        def scalars(self, query):
            query_text = str(query).lower()
            if 'usuarios' in query_text:
                return FakeResult(users)
            if 'viajes' in query_text:
                return FakeResult(trips)
            if 'tareas' in query_text:
                return FakeResult(tasks)
            return FakeResult([])

    overview = usuarios.build_admin_overview(FakeDB())

    assert overview['admin_count'] == 1
    assert overview['traveler_count'] == 2
    assert overview['travelers_with_trip'] >= 1
    assert overview['report_status'] in {'healthy', 'monitoring', 'attention'}
    assert 'permissions' in overview


def test_build_business_report_returns_exportable_summary():
    users = [
        SimpleNamespace(id=1, nombre='Ana', rol='admin', email='ana@centro.viajero'),
        SimpleNamespace(id=2, nombre='Luis', rol='traveler', email='luis@centro.viajero'),
    ]
    trips = [
        SimpleNamespace(id=1, usuario_id=2, destino='Cartagena', estado='En preparación', presupuesto_total=1200000, presupuesto_detallado={'hospedaje': 500000, 'transporte': 300000}, plan=[{'title': 'Llegada'}]),
        SimpleNamespace(id=2, usuario_id=2, destino='Bogotá', estado='Confirmado', presupuesto_total=1800000, presupuesto_detallado={'hospedaje': 900000, 'transporte': 250000}, plan=[{'title': 'Salida'}]),
    ]
    tasks = [
        SimpleNamespace(viaje_id=1, completada=False),
        SimpleNamespace(viaje_id=2, completada=True),
    ]

    class FakeResult:
        def __init__(self, rows):
            self._rows = rows

        def all(self):
            return self._rows

    class FakeDB:
        def scalars(self, query):
            query_text = str(query).lower()
            if 'usuarios' in query_text:
                return FakeResult(users)
            if 'viajes' in query_text:
                return FakeResult(trips)
            if 'tareas' in query_text:
                return FakeResult(tasks)
            return FakeResult([])

    report = usuarios.build_business_report(FakeDB())

    assert report['summary']['total_viajes'] == 2
    assert report['summary']['budget_alerts'] >= 0
    assert len(report['csv_rows']) == 2
    assert report['csv_rows'][0]['destino'] in {'Cartagena', 'Bogotá'}


def test_build_operations_summary_includes_chart_ready_payload():
    class FakeResult:
        def __init__(self, rows):
            self._rows = rows

        def all(self):
            return self._rows

    users = [SimpleNamespace(id=1, nombre='Ana', rol='admin', email='ana@centro.viajero')]
    trips = [SimpleNamespace(id=1, usuario_id=1, estado='En preparación', presupuesto_total=1500000, presupuesto_detallado={'hospedaje': 600000, 'transporte': 300000}, plan=[{'title': 'Llegada'}])]
    tasks = [SimpleNamespace(viaje_id=1, completada=True)]

    class FakeDB:
        def scalars(self, query):
            query_text = str(query).lower()
            if 'usuarios' in query_text:
                return FakeResult(users)
            if 'viajes' in query_text:
                return FakeResult(trips)
            if 'tareas' in query_text:
                return FakeResult(tasks)
            return FakeResult([])

    summary = usuarios.build_operations_summary(FakeDB())

    assert isinstance(summary['chart_data'], list)
    assert summary['chart_data'][0]['label']
    assert summary['chart_data'][0]['value'] >= 0
