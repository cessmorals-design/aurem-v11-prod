from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import pathlib
out=pathlib.Path("out/cvs"); out.mkdir(parents=True, exist_ok=True)
def make_cv(fn,title,profile,skills):
    path=out/fn
    doc=SimpleDocTemplate(str(path), pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles=getSampleStyleSheet()
    s_title=ParagraphStyle('t', parent=styles['Heading1'], fontSize=16)
    s_head=ParagraphStyle('h', parent=styles['Heading2'], fontSize=12, textColor=colors.HexColor('#1a73e8'))
    s_norm=styles['Normal']; s_norm.fontSize=10
    story=[Paragraph(title,s_title),Paragraph("Profile",s_head),Paragraph(profile,s_norm),Spacer(1,12),Paragraph("Skills",s_head),Paragraph("<br/>".join([f" {x}" for x in skills]),s_norm),Spacer(1,20),Paragraph("Nairobi 997: https://cpsb.nairobi.go.ke/vacancies | Channel: https://whatsapp.com/channel/0029VbD5CSQ6LwHlCzEAt01s | 0716706708", s_norm)]
    doc.build(story); print(f"OK {path}")
make_cv("Nurse_CV_Nairobi997.pdf","Registered Nurse CV Nairobi 997","Dedicated Nurse 3yrs county hospitals MCH emergency.",["Patient Care","MCH","Infection Prevention","Triage","HMIS"])
make_cv("Clinical_Officer_CV_Nairobi997.pdf","Clinical Officer CV Nairobi 997","Clinical Officer OPD MCH outreach.",["Diagnosis","OPD","MCH","Minor Surgery","DHIS2"])
make_cv("Support_Staff_CV_Nairobi997.pdf","Support Staff CV Nairobi 997","Hardworking support staff cleaning office assistance.",["Cleaning","Filing","Customer Service","Team Work","Computer"])
make_cv("NAIROBI_997_Application_Guide.pdf","NAIROBI 997 Guide + 3 CVs @150","How to apply: register cpsb.nairobi.go.ke, upload CV, submit.",["Register","Fill","Upload CV","Submit","Join Channel"])
