import React from 'react';

const DraftItems = ({ draftItems, onAddItem }) => {
  return (
    <div className="p-4">
      <h2 className="text-xl font-bold mb-4">Draft Items</h2>
      <ul>
        {draftItems.map((item) => (
          <li key={item.id} className="flex justify-between items-center mb-2">
            <span>{item.description} - ${item.unit_price}</span>
            <button
              onClick={() => onAddItem(item)}
              className="bg-green-500 text-white px-2 py-1 rounded"
            >
              Add to Invoice
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default DraftItems;
