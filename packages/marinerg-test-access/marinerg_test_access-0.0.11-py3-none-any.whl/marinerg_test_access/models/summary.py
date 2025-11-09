import zipfile
import os
from pathlib import Path

from django.conf import settings

from weasyprint import HTML


def generate_summary(
    instance,
    output_field: str = "summary",
    include_fields=("funding_statement", "safety_statement"),
):

    html = f"<html><body><p>Device Details:{instance.device_details}</p></body></html>"
    pdf_bytes = HTML(string=html).write_pdf()

    field_path = f"{instance._meta.model_name}_{output_field}"
    work_dir = Path(settings.MEDIA_ROOT) / field_path
    os.makedirs(work_dir, exist_ok=True)

    filename = f"{field_path}_{instance.id}.zip"
    with zipfile.ZipFile(
        work_dir / filename, "w", zipfile.ZIP_DEFLATED, False
    ) as zip_file:
        for field in include_fields:
            if instance.getattr(field):
                zip_file.write(
                    Path(settings.MEDIA_ROOT) / instance.getattr(field).name,
                    arcname=f"{field}.pdf",
                )
        zip_file.writestr("summary.pdf", pdf_bytes)

    instance.summary.name = os.path.join(field_path, filename)
    instance.save()
