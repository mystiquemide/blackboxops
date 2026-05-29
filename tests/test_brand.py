from app.brand import BRAND_TOKENS, build_brand_css, risk_label


def test_brand_tokens_match_blackboxops_design_file():
    assert BRAND_TOKENS["background"] == "#070A0F"
    assert BRAND_TOKENS["splunkGreen"] == "#65A637"
    assert BRAND_TOKENS["evidenceBlue"] == "#38BDF8"
    assert BRAND_TOKENS["criticalRed"] == "#EF4444"
    assert BRAND_TOKENS["blackboxOrange"] == "#FF6B2C"


def test_brand_css_contains_command_center_classes():
    css = build_brand_css()

    assert ".bb-hero" in css
    assert ".bb-card" in css
    assert ".bb-risk-critical" in css
    assert "The flight recorder" not in css
    assert "#070A0F" in css


def test_risk_label_has_text_and_icon_not_color_only():
    label = risk_label(0.95)

    assert label["level"] == "critical"
    assert label["icon"]
    assert "Critical" in label["text"]
