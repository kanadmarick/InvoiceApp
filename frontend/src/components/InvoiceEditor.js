import React from 'react';

const InvoiceEditor = ({ invoice, onInvoiceChange }) => {
  const handleChange = (e) => {
    try {
      const newInvoice = JSON.parse(e.target.value);
      onInvoiceChange(newInvoice);
    } catch (error) {
      // Ignore invalid JSON
    }
  };

  return (
    <div className="p-4">
      <h2 className="text-xl font-bold mb-4">Invoice JSON</h2>
      <textarea
        className="w-full h-96 border p-2"
        defaultValue={JSON.stringify(invoice, null, 2)}
        onChange={handleChange}
      />
    </div>
  );
};

export default InvoiceEditor;
