import OrderRow from './OrderRow';

/**
 * OrdersTable - Table displaying all repair orders
 */
export default function OrdersTable({ orders, endingStatuses, holidays }) {
  // Sort orders by ID (newest first)
  const sortedOrders = [...orders].sort((a, b) => b.id - a.id);

  return (
    <table>
      <thead>
        <tr>
          <th>Start</th>
          <th>Finish</th>
          <th>Days</th>
          <th>Name</th>
          <th>Color</th>
          <th>Status</th>
          <th>Boards</th>
          <th>Machines</th>
          <th>Hashboard Counts</th>
          <th>Machine Counts</th>
        </tr>
      </thead>
      <tbody>
        {sortedOrders.map(order => (
          <OrderRow
            key={order.id}
            order={order}
            endingStatuses={endingStatuses}
            holidays={holidays}
          />
        ))}
      </tbody>
    </table>
  );
}
