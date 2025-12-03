import { updateDocument } from "../servers/google-drive/index";

async function main() {
  try {
    const result = await updateDocument(
      "doc_12345",
      undefined, // Keep the title unchanged
      `Latest Budget Figures - Q4 2025

Revenue Projections:
- Product Sales: $2,500,000
- Services Revenue: $1,200,000
- Licensing Fees: $800,000
- Total Expected Revenue: $4,500,000

Operating Expenses:
- Personnel Costs: $1,800,000
- Infrastructure & Cloud: $450,000
- Marketing & Sales: $600,000
- R&D: $500,000
- Administrative Overhead: $300,000
- Total Operating Expenses: $3,650,000

Gross Profit Margin: $850,000 (18.9%)

Capital Allocation:
- Equipment & Technology: $250,000
- Team Expansion: $400,000
- Marketing Initiatives: $150,000
- Contingency Reserve: $50,000

Cash Position:
- Current Cash on Hand: $2,100,000
- Projected End-of-Quarter Cash: $2,850,000

Key Metrics:
- Burn Rate: $120,000/month
- Runway: 23.75 months
- Break-even Projection: Q2 2026`
    );
    
    console.log("Document updated successfully:");
    console.log(JSON.stringify(result, null, 2));
  } catch (error) {
    console.error("Error updating document:", error);
  }
}

main();
