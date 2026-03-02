import React, { useState } from 'react';
import InvoiceEditor from './components/InvoiceEditor';
import InvoicePreview from './components/InvoicePreview';
import DraftItems from './components/DraftItems';
import { sampleInvoice } from './sample-invoice';
import { sampleDraftItems } from './sample-draft-items';

/**
 * Main App component — provides a split-pane invoice editor.
 * Left side: JSON editor + draft items to add.
 * Right side: Live invoice preview with customizable brand color.
 */
function App() {
  // State: current invoice data, available draft items, and brand color
  const [invoice, setInvoice] = useState(sampleInvoice);
  const [draftItems, setDraftItems] = useState(sampleDraftItems);
  const [brandColor, setBrandColor] = useState('#000000');

  // Updates the entire invoice object when JSON is edited
  const handleInvoiceChange = (newInvoice) => {
    setInvoice(newInvoice);
  };

  // Moves a draft item into the invoice's line items and removes it from drafts
  const handleAddItem = (item) => {
    const newItem = {
      id: invoice.items.length + 1,
      description: item.description,
      quantity: 1,
      unit_price: item.unit_price,
      line_total: item.unit_price,
    };

    const newInvoice = {
      ...invoice,
      items: [...invoice.items, newItem],
      total_amount: invoice.total_amount + newItem.line_total,
    };

    setInvoice(newInvoice);
    setDraftItems(draftItems.filter((draftItem) => draftItem.id !== item.id));
  };

  return (
    <div className="App">
        <div className="p-4">
            <label htmlFor="brandColor" className="block mb-2">
            Brand Color:
            </label>
            <input
            type="color"
            id="brandColor"
            value={brandColor}
            onChange={(e) => setBrandColor(e.target.value)}
            className="w-20 h-10"
            />
        </div>
        <div className="flex">
            <div className="w-1/2">
                <InvoiceEditor
                    invoice={invoice}
                    onInvoiceChange={handleInvoiceChange}
                />
                <DraftItems draftItems={draftItems} onAddItem={handleAddItem} />
            </div>
            <div className="w-1/2">
                <InvoicePreview invoice={invoice} brandColor={brandColor} />
            </div>
        </div>
    </div>
  );
}

export default App;
