export default function CustomerSelector({
  customerId,
  setCustomerId,
}) {
  const customers = [
    { id: "C-100", name: "Ananya Rao" },
    { id: "C-101", name: "Marcus Bell" },
    { id: "C-102", name: "Priya Nair" },
    { id: "C-103", name: "Diego Ramos" },
  ];

  return (
    <div className="shrink-0">
      <label className="mb-2 block text-sm font-medium text-[#111827]">
        Select Customer
      </label>

      <select
        value={customerId}
        onChange={(e) => setCustomerId(e.target.value)}
        className="w-full cursor-pointer rounded-xl border border-[#E5E7EB] bg-white px-4 py-2.5 text-sm text-[#111827] transition-all duration-200 hover:bg-[#F9F9F9] focus:border-blue-400 focus:outline-none focus:ring-4 focus:ring-blue-100"
      >
        {customers.map((customer) => (
          <option key={customer.id} value={customer.id}>
            {customer.id} — {customer.name}
          </option>
        ))}
      </select>
    </div>
  );
}
