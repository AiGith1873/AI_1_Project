"""
Core class for generating historical financial documents for the RAG system's knowledge base.
These documents represent historical policies, contracts, and agreements that the system
will search through when answering queries.
"""

from fpdf import FPDF
from datetime import datetime, timedelta
import os
import random
import uuid

class HistoricalDocumentGenerator:
    """
    Generates historical financial documents for the RAG system's knowledge base.
    Creates realistic-looking PDFs with various financial terms and conditions
    that represent the historical policies and agreements in the system.
    """
    
    def __init__(self, output_dir: str = "data/rag_documents"):
        """
        Initialize the document generator.
        
        Args:
            output_dir (str): Directory where historical documents will be saved
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Our company (consistent lessor)
        self.lessor = "Financial Services Corp."
        
        # Sample customer companies (lessees) for variety
        self.lessees = [
            "Tech Solutions AB",
            "Nordic Manufacturing Ltd",
            "Green Energy Systems",
            "Healthcare Innovations",
            "Construction Partners",
            "Retail Solutions Group",
            "Logistics Experts",
            "Food Processing Co",
            "Educational Services",
            "Research & Development Corp"
        ]
        
        # Sample equipment types
        self.equipment_types = [
            "Office Equipment",
            "Manufacturing Machinery",
            "IT Infrastructure",
            "Medical Equipment",
            "Construction Equipment",
            "Energy Systems",
            "Logistics Equipment",
            "Food Processing Machinery",
            "Educational Technology",
            "Research Equipment"
        ]
        
        # Keep track of used dates to ensure uniqueness
        self.used_dates = set()
        
    def _get_unique_date(self, base_date, max_days=730):
        """Generate a unique date that hasn't been used before."""
        while True:
            days_ago = random.randint(0, max_days)
            date = base_date + timedelta(days=days_ago)
            date_str = date.strftime('%Y%m%d')
            if date_str not in self.used_dates:
                self.used_dates.add(date_str)
                return date
        
    def create_leasing_agreement(self, agreement_date: datetime = None, lessee: str = None, 
                               equipment: str = None, monthly_payment: float = None):
        """
        Create a historical equipment leasing agreement.
        
        Args:
            agreement_date (datetime): Date of the agreement
            lessee (str): Customer company name
            equipment (str): Type of equipment
            monthly_payment (float): Monthly payment amount
        """
        if agreement_date is None:
            agreement_date = datetime.now() - timedelta(days=730)
            agreement_date = self._get_unique_date(agreement_date)
            
        if lessee is None:
            lessee = random.choice(self.lessees)
            
        if equipment is None:
            equipment = random.choice(self.equipment_types)
            
        if monthly_payment is None:
            monthly_payment = random.randint(1000, 5000)
            
        unique_id = uuid.uuid4().hex[:6]
        filename = f"historical_leasing_agreement_{agreement_date.strftime('%Y%m%d')}_{unique_id}.pdf"
        pdf = FPDF()
        pdf.add_page()
        
        # Title
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'HISTORICAL EQUIPMENT LEASING AGREEMENT', 0, 1, 'C')
        pdf.ln(10)
        
        # Agreement Details
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, f'Agreement Date: {agreement_date.strftime("%Y-%m-%d")}', 0, 1)
        pdf.cell(0, 10, f'Agreement Number: LEA-{agreement_date.strftime("%Y%m")}-{random.randint(1, 999):03d}', 0, 1)
        pdf.ln(5)
        
        # Parties
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'PARTIES', 0, 1)
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, f'Lessor: {self.lessor}', 0, 1)
        pdf.cell(0, 10, f'Lessee: {lessee}', 0, 1)
        pdf.ln(5)
        
        # Terms and Conditions
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'TERMS AND CONDITIONS', 0, 1)
        pdf.set_font('Arial', '', 12)
        
        terms = [
            f"1. LEASE TERM: {random.choice([24, 36, 48])} months from the commencement date.",
            f"2. MONTHLY PAYMENT: EUR {monthly_payment:,.2f}, due on the first day of each month.",
            f"3. EQUIPMENT: {equipment} as specified in Schedule A.",
            "4. INSURANCE: Lessee shall maintain comprehensive insurance coverage.",
            "5. MAINTENANCE: Lessee responsible for routine maintenance.",
            "6. EARLY TERMINATION: 3 months' notice required with early termination fee.",
            "7. RENEWAL: Option to renew for additional 12 months at market rate.",
            "8. DEFAULT: Late payment fee of 5% after 5 business days.",
            "9. WARRANTIES: Equipment provided 'as is' with standard manufacturer warranty.",
            "10. CONFIDENTIALITY: Both parties agree to maintain confidentiality."
        ]
        
        for term in terms:
            pdf.multi_cell(0, 10, term)
            pdf.ln(2)
        
        # Save the PDF
        pdf.output(os.path.join(self.output_dir, filename))
        return filename
        
    def create_credit_policy(self, effective_date: datetime = None):
        """
        Create a historical credit policy document.
        
        Args:
            effective_date (datetime): Effective date of the policy
        """
        if effective_date is None:
            effective_date = datetime.now() - timedelta(days=730)
            effective_date = self._get_unique_date(effective_date)
            
        unique_id = uuid.uuid4().hex[:6]
        filename = f"historical_credit_policy_{effective_date.strftime('%Y%m%d')}_{unique_id}.pdf"
        pdf = FPDF()
        pdf.add_page()
        
        # Title
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'HISTORICAL CREDIT POLICY AND PROCEDURES', 0, 1, 'C')
        pdf.ln(10)
        
        # Policy Details
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, f'Effective Date: {effective_date.strftime("%Y-%m-%d")}', 0, 1)
        pdf.cell(0, 10, f'Policy Number: CP-{effective_date.strftime("%Y%m")}-{random.randint(1, 999):03d}', 0, 1)
        pdf.cell(0, 10, f'Issuing Company: {self.lessor}', 0, 1)
        pdf.ln(5)
        
        # Policy Sections
        sections = [
            ("CREDIT ASSESSMENT", [
                "1. All new customers must complete a credit application form.",
                "2. Credit checks will be performed through approved agencies.",
                f"3. Minimum credit score requirement: {random.randint(600, 700)}.",
                f"4. Trade references required for amounts over EUR {random.randint(30000, 70000):,}."
            ]),
            ("CREDIT LIMITS", [
                f"1. Standard credit limit: EUR {random.randint(20000, 30000):,} for new customers.",
                "2. Increased limits require senior management approval.",
                f"3. Maximum credit limit: EUR {random.randint(400000, 600000):,}.",
                "4. Regular review of credit limits every 6 months."
            ]),
            ("PAYMENT TERMS", [
                f"1. Standard payment terms: Net {random.choice([15, 30, 45])} days.",
                f"2. Early payment discount: {random.randint(1, 3)}% if paid within 10 days.",
                f"3. Late payment fee: {random.uniform(1.0, 2.0):.1f}% per month.",
                "4. Payment methods: Bank transfer, credit card, check."
            ]),
            ("COLLECTION PROCEDURES", [
                f"1. First reminder: {random.randint(3, 7)} days after due date.",
                f"2. Second reminder: {random.randint(10, 20)} days after due date.",
                f"3. Final notice: {random.randint(25, 35)} days after due date.",
                f"4. Legal action: After {random.randint(45, 75)} days of non-payment."
            ])
        ]
        
        for section_title, items in sections:
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, section_title, 0, 1)
            pdf.set_font('Arial', '', 12)
            for item in items:
                pdf.multi_cell(0, 10, item)
                pdf.ln(2)
            pdf.ln(5)
        
        # Save the PDF
        pdf.output(os.path.join(self.output_dir, filename))
        return filename 