# suggestion_engine.py

def generate_suggestions(attention_items, risk_label: str):
    """
    attention_items: list of component names that have ⚠
    risk_label: e.g. 'Good', 'Moderate', 'Poor'
    """
    suggestions = []

    r = (risk_label or "").lower()

    # Risk-level based suggestion
    if "poor" in r or "critical" in r:
        suggestions.append(
            "Machine is in a critical state. Schedule immediate detailed inspection and corrective maintenance."
        )
    elif "moderate" in r or "attention" in r:
        suggestions.append(
            "Machine requires attention. Plan preventive maintenance in the next maintenance cycle."
        )
    elif "good" in r or "healthy" in r:
        suggestions.append(
            "Machine is in good condition. Continue regular preventive maintenance as per schedule."
        )
    else:
        suggestions.append(
            "Risk status unclear. Please manually review the latest maintenance report."
        )

    # Component-level suggestions
    for comp in attention_items:
        c = comp.lower()
        if "fan" in c:
            suggestions.append("CNC fan filter requires cleaning or service.")
        if "cooling pump" in c:
            suggestions.append("Cooling pump requires service. Check for flow or noise issues.")
        if "alignment" in c:
            suggestions.append("Tool changer alignment needs verification and possible calibration.")
        if "guard" in c:
            suggestions.append("Check guarding components for wear and proper enclosure.")
        if "lubrication" in c:
            suggestions.append("Verify lubrication levels and schedules for axes and moving parts.")

    if not attention_items:
        suggestions.append("No critical components detected in the latest checklist.")

    return suggestions
