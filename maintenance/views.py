# maintenance/views.py

import os
from django.shortcuts import render
from django.conf import settings
from pipeline import run_pipeline


def upload_view(request):
    context = {}

    if request.method == "POST":
        pdf_file = request.FILES.get("pdf_file")

        if pdf_file:
            upload_dir = os.path.join(settings.MEDIA_ROOT, "uploads")
            os.makedirs(upload_dir, exist_ok=True)

            upload_path = os.path.join(upload_dir, pdf_file.name)
            with open(upload_path, "wb+") as destination:
                for chunk in pdf_file.chunks():
                    destination.write(chunk)

            # Run full AI pipeline
            results = run_pipeline(upload_path)

            # Build report download URL
            report_path = results.get("report_path")  # e.g. "outputs/maintenance_report.pdf"
            report_url = None

            if report_path:
                # if it’s an absolute path, convert to relative from MEDIA_ROOT
                if os.path.isabs(report_path):
                    rel_path = os.path.relpath(report_path, settings.MEDIA_ROOT)
                else:
                    rel_path = report_path

                rel_path = rel_path.replace("\\", "/")
                report_url = settings.MEDIA_URL + rel_path

            context["result"] = {
                "risk": results.get("risk_label", "Unknown"),
                "completeness": results.get("completeness_score", 0.0),
                "health": results.get("health_score", 0.0),
                "report_url": report_url,
            }

    return render(request, "maintenance/upload.html", context)
