import os
import re
from flask import Flask, render_template, request, send_file
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

app = Flask(__name__)

OUTPUT_DIR = "generated_portfolios"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def slugify(text: str) -> str:
    text = text.strip().replace(" ", "_")
    text = re.sub(r"(?u)[^-\w.]", "", text)
    return text or "portfolio"


def make_list(text: str, prefer_newline=False):
    """
    Convert a text string into a clean list of items.
    Handles both comma-separated and newline-separated input.
    Prevents breaking words like 'Data Analytics' or 'Web Development'.
    """
    if not text:
        return []
    text = text.replace("\r", "").strip()

    # If user pressed Enter, split by lines, else split by commas/newlines
    if prefer_newline and "\n" in text:
        parts = [line.strip() for line in text.split("\n")]
    else:
        parts = [p.strip() for p in re.split(r"[,\n]+", text)]

    # Remove empty or broken entries
    clean_parts = [p for p in parts if p and len(p) > 1]

    return clean_parts


@app.route("/")
def home():
    return render_template("form.html")


@app.route("/generate", methods=["POST"])
def generate():
    data = {
        "name": request.form.get("name", "").strip(),
        "email": request.form.get("email", "").strip(),
        "phone": request.form.get("phone", "").strip(),
        "linkedin": request.form.get("linkedin", "").strip(),
        "github": request.form.get("github", "").strip(),
        "website": request.form.get("website", "").strip(),
        "about": request.form.get("about", "").strip(),
        "skills": make_list(request.form.get("skills", ""), prefer_newline=True),
        "education": request.form.get("education", "").strip(),
        "projects": make_list(request.form.get("projects", ""), prefer_newline=True),
        "certifications": make_list(request.form.get("certifications", ""), prefer_newline=True),
        "achievements": make_list(request.form.get("achievements", ""), prefer_newline=True),
        "interests": make_list(request.form.get("interests", ""), prefer_newline=True),
    }

    filename = f"{slugify(data['name'] or 'portfolio')}.pdf"
    pdf_path = os.path.join(OUTPUT_DIR, filename)

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "title",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#1f5a8a"),
        spaceAfter=10,
    )

    heading_style = ParagraphStyle(
        "heading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#2b6fb3"),
        spaceBefore=10,
        spaceAfter=4,
    )

    normal = ParagraphStyle(
        "normal",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=11,
        leading=14,
    )

    elements = []

    # --- Header ---
    elements.append(Paragraph(data["name"] or "Your Name", title_style))

    contact_parts = []
    if data["email"]:
        contact_parts.append(f"Email: {data['email']}")
    if data["phone"]:
        contact_parts.append(f"Phone: {data['phone']}")
    if data["linkedin"]:
        contact_parts.append(f"LinkedIn: {data['linkedin']}")
    if data["github"]:
        contact_parts.append(f"GitHub: {data['github']}")
    if data["website"]:
        contact_parts.append(f"Website: {data['website']}")

    if contact_parts:
        contact_line = " | ".join(contact_parts)
        elements.append(Paragraph(contact_line, normal))

    # Divider line
    divider = Table(
        [[""]],
        colWidths=[doc.width],
        style=[("LINEBELOW", (0, 0), (-1, -1), 1, colors.HexColor("#cccccc"))],
    )
    elements.append(divider)
    elements.append(Spacer(1, 8))

    # --- About Me ---
    elements.append(Paragraph("About Me", heading_style))
    elements.append(Paragraph(data["about"] or "-", normal))

    # --- Skills ---
    elements.append(Paragraph("Skills", heading_style))
    if data["skills"]:
        for skill in data["skills"]:
            elements.append(Paragraph(f"• {skill}", normal))
    else:
        elements.append(Paragraph("-", normal))

    # --- Education ---
    elements.append(Paragraph("Education", heading_style))
    elements.append(Paragraph(data["education"] or "-", normal))

    # --- Projects ---
    elements.append(Paragraph("Projects", heading_style))
    if data["projects"]:
        for p in data["projects"]:
            elements.append(Paragraph(f"• {p}", normal))
    else:
        elements.append(Paragraph("-", normal))

    # --- Certifications ---
    elements.append(Paragraph("Certifications", heading_style))
    if data["certifications"]:
        for c in data["certifications"]:
            elements.append(Paragraph(f"• {c}", normal))
    else:
        elements.append(Paragraph("-", normal))

    # --- Achievements ---
    elements.append(Paragraph("Achievements", heading_style))
    if data["achievements"]:
        for a in data["achievements"]:
            elements.append(Paragraph(f"• {a}", normal))
    else:
        elements.append(Paragraph("-", normal))

    # --- Interests ---
    elements.append(Paragraph("Interests", heading_style))
    if data["interests"]:
        for interest in data["interests"]:
            elements.append(Paragraph(f"• {interest}", normal))
    else:
        elements.append(Paragraph("-", normal))

    # Build PDF
    doc.build(elements)

    return render_template("portfolio.html", data=data, download_link=filename)


@app.route("/download/<filename>")
def download(filename):
    filepath = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(filepath):
        return "File not found.", 404
    return send_file(filepath, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
