/**
 * Date utility functions
 */

/**
 * Convert UTC ISO string to local time string
 * @param {string} utcString - UTC ISO datetime string
 * @returns {string} - Local datetime string
 */
export function utcToLocal(utcString) {
  if (!utcString) return '-';
  const date = new Date(utcString);
  return date.toLocaleString();
}

/**
 * Convert UTC ISO string to local date string (date only)
 * @param {string} utcString - UTC ISO datetime string
 * @returns {string} - Local date string
 */
export function utcToLocalDate(utcString) {
  if (!utcString) return '-';
  const date = new Date(utcString);
  return date.toLocaleDateString();
}

/**
 * Calculate business days between two dates (excluding weekends and holidays)
 * @param {Date|string} startDate - Start date
 * @param {Date|string} endDate - End date
 * @param {Set<string>} holidaySet - Set of holiday dates in YYYY-MM-DD format
 * @returns {number} - Number of business days
 */
export function calculateBusinessDays(startDate, endDate, holidaySet = new Set()) {
  let businessDays = 0;
  const current = new Date(startDate);
  const end = new Date(endDate);

  // Normalize to UTC dates only
  current.setUTCHours(0, 0, 0, 0);
  end.setUTCHours(0, 0, 0, 0);

  while (current <= end) {
    const dayOfWeek = current.getUTCDay();
    const isoDate = current.toISOString().split('T')[0]; // YYYY-MM-DD

    // Skip weekends (Saturday=6, Sunday=0) and holidays
    if (dayOfWeek !== 0 && dayOfWeek !== 6 && !holidaySet.has(isoDate)) {
      businessDays++;
    }

    current.setUTCDate(current.getUTCDate() + 1);
  }

  return businessDays;
}

/**
 * Format date for input elements
 * @param {Date|string} date - Date to format
 * @returns {string} - Date in YYYY-MM-DD format
 */
export function formatDateForInput(date) {
  if (!date) return '';
  const d = new Date(date);
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}
