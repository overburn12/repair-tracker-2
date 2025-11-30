import { utcToLocalDate, calculateBusinessDays } from '@utils/dateUtils';
import { Link } from 'react-router-dom';

/**
 * OrderRow - Individual order row with progress bars
 */
export default function OrderRow({ order, endingStatuses, holidays }) {
  const hashboardStatuses = endingStatuses.filter(s => s.can_use_for_hashboard === 1).sort((a, b) => a.status.localeCompare(b.status));
  const machineStatuses = endingStatuses.filter(s => s.can_use_for_machine === 1).sort((a, b) => a.status.localeCompare(b.status));

  // Calculate business days
  const businessDays = order.started
    ? calculateBusinessDays(
        order.started,
        order.finished || new Date(),
        holidays
      )
    : '-';

  return (
    <tr>
      {/* Start */}
      <td style={{ fontSize: '10px' }}>{utcToLocalDate(order.started)}</td>

      {/* Finish */}
      <td style={{ fontSize: '10px' }}>{utcToLocalDate(order.finished)}</td>

      {/* Days */}
      <td>{businessDays}</td>

      {/* Name */}
      <td>
        <Link to={`/order?key=${order.id}`}>{order.name}</Link>
      </td>

      {/* Color */}
      <td>
        <div
          style={{
            width: '20px',
            height: '20px',
            borderRadius: '50%',
            backgroundColor: order.color || '#FFFFFF',
            border: '1px solid var(--navbar-bg)',
            margin: 'auto'
          }}
        />
      </td>

      {/* Status */}
      <td>{order.status || '-'}</td>

      {/* Boards */}
      <td>{order.hashboard_count || 0}</td>

      {/* Machines */}
      <td>{order.machine_count || 0}</td>

      {/* Hashboard Counts */}
      <td>
        <StatusProgressBars
          order={order}
          statuses={hashboardStatuses}
          unitType="hashboard"
        />
      </td>

      {/* Machine Counts */}
      <td>
        <StatusProgressBars
          order={order}
          statuses={machineStatuses}
          unitType="machine"
        />
      </td>
    </tr>
  );
}

/**
 * StatusProgressBars - Progress bars for status counts
 */
function StatusProgressBars({ order, statuses, unitType }) {
  const total = unitType === 'hashboard' ? (order.hashboard_count || 0) : (order.machine_count || 0);
  const totalForCalc = total > 0 ? total : 1;

  const endingStatusCounts = unitType === 'hashboard'
    ? order.hashboard_ending_status_counts
    : order.machine_ending_status_counts;

  // Calculate sum of all ending statuses
  let sumOfEndingStatuses = 0;
  statuses.forEach(statusObj => {
    sumOfEndingStatuses += (endingStatusCounts?.[statusObj.status] || 0);
  });

  return (
    <div style={{ display: 'flex', flexDirection: 'row', gap: '4px', minWidth: `${statuses.length * 120 + (statuses.length - 1) * 4}px` }}>
      {statuses.map(statusObj => {
        const count = endingStatusCounts?.[statusObj.status] || 0;
        const color = statusObj.color || 'var(--accent-color)';
        const percentage = (count / totalForCalc) * 100;

        return (
          <div
            key={statusObj.id}
            style={{
              width: '120px',
              height: '16px',
              border: '1px solid var(--progress-bar-border)',
              borderRadius: '3px',
              overflow: 'hidden',
              position: 'relative',
              backgroundColor: color + '20'
            }}
          >
            {/* Progress fill */}
            <div
              style={{
                width: `${Math.min(percentage, 100)}%`,
                height: '100%',
                backgroundColor: color,
                transition: 'width 0.3s ease'
              }}
            />

            {/* Overlay text */}
            <div
              style={{
                position: 'absolute',
                top: '50%',
                left: '4px',
                transform: 'translateY(-50%)',
                fontSize: '11px',
                fontWeight: 'bold',
                color: 'var(--navbar-text)',
                textShadow: '1px 1px 1px rgba(0,0,0,0.5)',
                pointerEvents: 'none'
              }}
            >
              {percentage.toFixed(1)}% ({count})
            </div>
          </div>
        );
      })}

      {/* Alert if mismatch */}
      {total > 0 && sumOfEndingStatuses !== total && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '11px', color: 'var(--warning-color)', fontWeight: 'bold' }}>
          <span>⚠️</span>
          <span>{total - sumOfEndingStatuses}</span>
        </div>
      )}
    </div>
  );
}
