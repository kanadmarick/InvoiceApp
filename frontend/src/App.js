import React, { useState } from 'react';
import InvoiceEditor from './components/InvoiceEditor';
import InvoicePreview from './components/InvoicePreview';
import DraftItems from './components/DraftItems';
import { sampleInvoice } from './sample-invoice';
import { sampleDraftItems } from './sample-draft-items';

function App() {
  const [invoice, setInvoice] = useState(sampleInvoice);
  const [draftItems, setDraftItems] = useState(sampleDraftItems);
  const [brandColor, setBrandColor] = useState('#000000');

  const handleInvoiceChange = (newInvoice) => {
    setInvoice(newInvoice);
  };

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
