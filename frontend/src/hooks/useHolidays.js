import { useState, useEffect } from 'react';

/**
 * Custom hook to fetch holidays
 * @returns {Set<string>} - Set of holiday dates in YYYY-MM-DD format
 */
export function useHolidays() {
  const [holidays, setHolidays] = useState(new Set());

  useEffect(() => {
    fetch('/api/get_holidays')
      .then(res => res.json())
      .then(data => {
        if (data.holidays && Array.isArray(data.holidays)) {
          setHolidays(new Set(data.holidays));
        }
      })
      .catch(error => {
        console.warn('Failed to fetch holidays:', error);
        setHolidays(new Set());
      });
  }, []);

  return holidays;
}
