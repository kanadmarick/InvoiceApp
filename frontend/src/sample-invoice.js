// Sample invoice data used for the React frontend preview.
// This is mock data — in production, this would come from the Django API.
export const sampleInvoice = {
  invoice_number: 'INV-001',
  client: {
    name: 'Acme Corp',
    email: 'contact@acme.com',
  },
  milestones: [
    {
      id: 1,
      description: 'Project Deposit',
      due_date: '2026-03-01',
      status: 'PAID',
    },
    {
      id: 2,
      description: 'First Draft',
      due_date: '2026-03-15',
      status: 'PENDING',
    },
    {
        id: 3,
        description: 'Final Delivery',
        due_date: '2026-03-30',
        status: 'PENDING',
      },
  ],
  items: [
    {
      id: 1,
      description: 'Website Design',
      quantity: 1,
      unit_price: 5000,
      line_total: 5000,
    },
    {
      id: 2,
      description: 'Logo Design',
      quantity: 1,
      unit_price: 1500,
      line_total: 1500,
    },
  ],
  total_amount: 6500,
};
