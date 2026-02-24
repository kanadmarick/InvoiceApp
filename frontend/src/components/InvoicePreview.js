import React from 'react';

const InvoicePreview = ({ invoice, brandColor }) => {
  const brandStyle = {
    '--brand-color': brandColor,
  };

  return (
    <div className="p-8 bg-white shadow-lg" style={brandStyle}>
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-2xl font-bold" style={{ color: 'var(--brand-color)' }}>
            Invoice
          </h1>
          <p className="text-gray-500">{invoice.invoice_number}</p>
        </div>
        <div className="text-right">
          <p className="text-gray-500">
            <strong>Client:</strong> {invoice.client.name}
          </p>
          <p className="text-gray-500">{invoice.client.email}</p>
        </div>
      </div>

      <div className="mb-8">
        <h2 className="text-xl font-bold mb-4" style={{ borderColor: 'var(--brand-color)' }}>
          Milestones
        </h2>
        <table className="w-full">
          <thead>
            <tr className="border-b" style={{ borderColor: 'var(--brand-color)' }}>
              <th className="text-left py-2">Description</th>
              <th className="text-right py-2">Due Date</th>
              <th className="text-right py-2">Status</th>
            </tr>
          </thead>
          <tbody>
            {invoice.milestones.map((milestone) => (
              <tr key={milestone.id} className="border-b">
                <td className="py-2">{milestone.description}</td>
                <td className="text-right py-2">{milestone.due_date}</td>
                <td className="text-right py-2">{milestone.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div>
        <h2 className="text-xl font-bold mb-4" style={{ borderColor: 'var(--brand-color)' }}>
          Invoice Items
        </h2>
        <table className="w-full">
          <thead>
            <tr className="border-b" style={{ borderColor: 'var(--brand-color)' }}>
              <th className="text-left py-2">Description</th>
              <th className="text-right py-2">Quantity</th>
              <th className="text-right py-2">Unit Price</th>
              <th className="text-right py-2">Total</th>
            </tr>
          </thead>
          <tbody>
            {invoice.items.map((item) => (
              <tr key={item.id} className="border-b">
                <td className="py-2">{item.description}</td>
                <td className="text-right py-2">{item.quantity}</td>
                <td className="text-right py-2">${item.unit_price}</td>
                <td className="text-right py-2">${item.line_total}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="flex justify-end mt-8">
        <div className="text-right">
          <p className="font-bold text-xl">
            Total: ${invoice.total_amount}
          </p>
        </div>
      </div>
    </div>
  );
};

export default InvoicePreview;
