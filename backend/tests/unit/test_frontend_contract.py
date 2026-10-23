"""ET-293 a ET-296 : squelette Next.js et StatusStrip avec statuts separes."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.mark.spec("ET-293")
@pytest.mark.spec("ET-294")
def test_nextjs_skeleton_exists_and_has_strict_typescript() -> None:
    assert Path("frontend/package.json").is_file()
    assert Path("frontend/app/layout.tsx").is_file()
    assert Path("frontend/app/page.tsx").is_file()
    tsconfig = Path("frontend/tsconfig.json").read_text(encoding="utf-8")
    assert '"strict": true' in tsconfig


@pytest.mark.spec("ET-295")
def test_status_strip_presents_five_axes_separately() -> None:
    component = Path("frontend/components/StatusStrip.tsx").read_text(encoding="utf-8")
    for axis in ("R", "C", "A", "D", "V"):
        assert f"{axis}:" in component
    assert "global" not in component.lower()


@pytest.mark.spec("ET-296")
def test_provisional_badge_is_visible() -> None:
    component = Path("frontend/components/StatusStrip.tsx").read_text(encoding="utf-8")
    page = Path("frontend/app/page.tsx").read_text(encoding="utf-8")
    assert "provisoire" in component.lower() or "provisoire" in page.lower()


@pytest.mark.spec("ET-293")
def test_forge_header_is_present_in_layout() -> None:
    layout = Path("frontend/app/layout.tsx").read_text(encoding="utf-8")
    assert "FORGE" in layout


@pytest.mark.spec("ET-294")
def test_no_business_rule_in_frontend() -> None:
    page = Path("frontend/app/page.tsx").read_text(encoding="utf-8")
    assert "if (" not in page
    assert "state =" not in page
