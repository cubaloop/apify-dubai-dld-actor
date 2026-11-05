import asyncio
import json
import re
import urllib.request
from datetime import datetime, timezone

AREA_BENCHMARKS = {
    "business bay": {"gross_yield": 0.074, "cagr_5y": 0.089, "service_charge_sqft": 18.5, "avg_psf": 2150},
    "dubai marina": {"gross_yield": 0.078, "cagr_5y": 0.082, "service_charge_sqft": 19.2, "avg_psf": 2050},
    "downtown dubai": {"gross_yield": 0.068, "cagr_5y": 0.095, "service_charge_sqft": 24.0, "avg_psf": 2950},
    "jvc": {"gross_yield": 0.086, "cagr_5y": 0.079, "service_charge_sqft": 13.5, "avg_psf": 1350},
    "palm jumeirah": {"gross_yield": 0.064, "cagr_5y": 0.112, "service_charge_sqft": 26.5, "avg_psf": 3850},
}

def simulate_dld_roi(community: str, price_aed: float) -> dict:
    key = (community or "business bay").strip().lower()
    bench = AREA_BENCHMARKS.get(key, AREA_BENCHMARKS["business bay"])
    est_sqft = round(price_aed / bench["avg_psf"], 1)
    gross_rent_aed = round(price_aed * bench["gross_yield"], 2)
    service_charges_aed = round(est_sqft * bench["service_charge_sqft"], 2)
    net_rent_aed = round(gross_rent_aed - service_charges_aed, 2)
    net_yield_pct = round((net_rent_aed / price_aed) * 100, 2)
    dld_fee_aed = round(price_aed * 0.04 + 4200, 2)
    projected_5y_value_aed = round(price_aed * ((1 + bench["cagr_5y"]) ** 5), 2)
    return {
        "community": community,
        "purchase_price_aed": price_aed,
        "estimated_size_sqft": est_sqft,
        "annual_gross_rent_aed": gross_rent_aed,
        "annual_service_charges_aed": service_charges_aed,
        "annual_net_income_aed": net_rent_aed,
        "net_roi_percent": net_yield_pct,
        "dld_registration_fee_aed": dld_fee_aed,
        "projected_5y_capital_value_aed": projected_5y_value_aed,
        "projected_5y_total_return_aed": round((projected_5y_value_aed - price_aed) + (net_rent_aed * 5), 2),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

def passive_compliance_audit(url: str) -> dict:
    result = {
        "url": url,
        "status": "checked",
        "wcag_missing_alt_count": 0,
        "has_lang_attribute": False,
        "has_viewport_meta": False,
        "has_trakheesi_or_rera_mention": False,
        "public_phones_found": [],
        "compliance_score": 100,
        "recommended_remediation_usd": 199
    }
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Compatible; B2BComplianceAuditor/1.0)"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
        imgs = re.findall(r"<img\b[^>]*>", html, flags=re.IGNORECASE)
        missing_alt = sum(1 for tag in imgs if "alt=" not in tag.lower())
        result["wcag_missing_alt_count"] = missing_alt
        result["has_lang_attribute"] = bool(re.search(r"<html[^>]+lang=", html, re.IGNORECASE))
        result["has_viewport_meta"] = bool(re.search(r'name=["\']viewport["\']', html, re.IGNORECASE))
        result["has_trakheesi_or_rera_mention"] = bool(re.search(r"(trakheesi|rera|dld permit|madmoun)", html, re.IGNORECASE))
        phones = set(re.findall(r"\+971[\s\-]?[0-9]{1,2}[\s\-]?[0-9]{3}[\s\-]?[0-9]{4}", html))
        result["public_phones_found"] = sorted(list(phones))[:5]
        penalties = (min(missing_alt, 10) * 4) + (0 if result["has_lang_attribute"] else 15) + (0 if result["has_trakheesi_or_rera_mention"] else 20)
        result["compliance_score"] = max(25, 100 - penalties)
    except Exception as e:
        result["status"] = f"unreachable ({str(e)[:80]})"
    return result

async def main():
    inp = {
        "mode": "combined",
        "community": "Business Bay",
        "propertyPriceAed": 2500000,
        "targetUrls": ["https://famproperties.com", "https://metropolitan.realestate"]
    }
    output_records = []
    if inp["mode"] in ("dld_roi_simulation", "combined"):
        output_records.append({
            "event_type": "dld_roi_result",
            "ppe_charge_usd": 0.05,
            "data": simulate_dld_roi(inp["community"], inp["propertyPriceAed"])
        })
    if inp["mode"] in ("b2b_compliance_audit", "combined"):
        for u in inp.get("targetUrls", []):
            output_records.append({
                "event_type": "b2b_compliance_audit",
                "ppe_charge_usd": 0.03,
                "data": passive_compliance_audit(u)
            })
    print(json.dumps(output_records, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
