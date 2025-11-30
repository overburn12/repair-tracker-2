import { useOrdersData } from '@hooks/useOrdersData';
import { useHolidays } from '@hooks/useHolidays';
import ElementBlock from '@components/ui/ElementBlock';
import SearchBox from '@components/ui/SearchBox';
import LoadingSpinner from '@components/ui/LoadingSpinner';
import ErrorMessage from '@components/ui/ErrorMessage';
import OrdersTable from '@components/tables/OrdersTable';

/**
 * OrdersListPage - Main orders listing page
 */
export default function OrdersListPage() {
  const { orders, statuses, loading, error, addOrder } = useOrdersData();
  const holidays = useHolidays();

  // Filter for ending statuses only
  const endingStatuses = statuses.filter(s => s.is_ending_status === 1);

  const handleAddOrder = (name) => {
    addOrder(name);
  };

  return (
    <ElementBlock>
      <SearchBox
        placeholder="Enter new order name"
        onAdd={handleAddOrder}
        buttonText="Add"
      />

      {loading && <LoadingSpinner>Loading repair orders...</LoadingSpinner>}

      {error && <ErrorMessage>Error loading repair orders: {error}</ErrorMessage>}

      {!loading && !error && orders.length > 0 && (
        <OrdersTable
          orders={orders}
          endingStatuses={endingStatuses}
          holidays={holidays}
        />
      )}

      {!loading && !error && orders.length === 0 && (
        <div style={{ color: 'var(--text-secondary)', textAlign: 'center', padding: '20px' }}>
          No orders yet. Add one above to get started.
        </div>
      )}
    </ElementBlock>
  );
}
