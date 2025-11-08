from types import SimpleNamespace

import pytest

from surf_report.main import handle_search, main as cli_main
from surf_report.providers.surfline.models import SurflineSearchResult


def test_handle_search_returns_none_when_no_results(monkeypatch, capsys):
    fake_api = SimpleNamespace(search_surfline=lambda query: [])
    monkeypatch.setattr("surf_report.main.surfline", fake_api)

    result = handle_search("nowhere")

    assert result is None
    assert "No spots found" in capsys.readouterr().out


def test_handle_search_returns_id_for_single_result(monkeypatch, capsys):
    search_result = SurflineSearchResult(
        id="spot-1", name="Ocean Beach", breadcrumbs=["SF", "Ocean Beach"], type="spot"
    )
    fake_api = SimpleNamespace(search_surfline=lambda query: [search_result])
    monkeypatch.setattr("surf_report.main.surfline", fake_api)

    result = handle_search("ocean beach", verbose=True)

    assert result == "spot-1"
    output = capsys.readouterr().out
    assert "Ocean Beach" in output
    assert "[ID: spot-1]" in output


def test_handle_search_prompts_for_selection(monkeypatch, capsys):
    results = [
        SurflineSearchResult(
            id="spot-1", name="Spot One", breadcrumbs=["Region", "Spot One"], type="spot"
        ),
        SurflineSearchResult(
            id="spot-2", name="Spot Two", breadcrumbs=["Region", "Spot Two"], type="spot"
        ),
    ]
    fake_api = SimpleNamespace(search_surfline=lambda query: results)
    monkeypatch.setattr("surf_report.main.surfline", fake_api)
    monkeypatch.setattr("surf_report.main.get_user_choice", lambda _options: 2)

    result = handle_search("spot")

    assert result == "spot-2"
    output = capsys.readouterr().out
    assert "Select a spot" in output


def test_main_fetches_spot_data_when_search_succeeds(monkeypatch, make_args):
    args = make_args(search=True, search_string="mav", days=2)
    monkeypatch.setattr("surf_report.main.parse_arguments", lambda: args)
    monkeypatch.setattr("surf_report.main.handle_search", lambda search: "spot-9")

    forecast = SimpleNamespace(forecast_data={"data": {}})
    report = SimpleNamespace(report_data={})

    fake_api = SimpleNamespace(
        get_spot_forecast=lambda spot_id, days: forecast,
        get_spot_report=lambda spot_id, days: report,
    )
    monkeypatch.setattr("surf_report.main.surfline", fake_api)

    called = {}

    def fake_display(forecast_arg, report_arg):
        called["display"] = (forecast_arg, report_arg)

    monkeypatch.setattr(
        "surf_report.main.display_combined_spot_report",
        fake_display,
    )

    cli_main()

    assert called["display"] == (forecast, report)


def test_main_skips_fetch_when_handle_search_returns_none(monkeypatch, make_args):
    args = make_args(search=True, search_string="mav", days=2)
    monkeypatch.setattr("surf_report.main.parse_arguments", lambda: args)
    monkeypatch.setattr("surf_report.main.handle_search", lambda search: None)

    def unexpected_call(*args, **kwargs):
        raise AssertionError("Surfline API should not be invoked")

    fake_api = SimpleNamespace(
        get_spot_forecast=unexpected_call,
        get_spot_report=unexpected_call,
    )
    monkeypatch.setattr("surf_report.main.surfline", fake_api)

    cli_main()
