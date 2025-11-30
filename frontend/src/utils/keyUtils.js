/**
 * JIRA-style key utilities
 */

/**
 * Parse a JIRA-style key (e.g., "RO-123", "RU-456")
 * @param {string} key - JIRA-style key
 * @returns {Object|null} - Parsed key with type and id, or null if invalid
 */
export function parseJiraKey(key) {
  if (!key || typeof key !== 'string') return null;

  const parts = key.split('-');
  if (parts.length !== 2) return null;

  const [prefix, idStr] = parts;
  const id = parseInt(idStr, 10);

  if (isNaN(id)) return null;

  const typeMap = {
    'AS': 'assignee',
    'ST': 'status',
    'UM': 'unit_model',
    'RO': 'repair_order',
    'RU': 'repair_unit'
  };

  const type = typeMap[prefix];
  if (!type) return null;

  return { type, id, prefix };
}

/**
 * Create a JIRA-style key from type and id
 * @param {string} type - Entity type (assignee, status, unit_model, repair_order, repair_unit)
 * @param {number} id - Entity ID
 * @returns {string} - JIRA-style key
 */
export function createJiraKey(type, id) {
  const prefixMap = {
    'assignee': 'AS',
    'status': 'ST',
    'unit_model': 'UM',
    'repair_order': 'RO',
    'repair_unit': 'RU'
  };

  const prefix = prefixMap[type];
  if (!prefix) return null;

  return `${prefix}-${id}`;
}

/**
 * Extract numeric ID from JIRA-style key
 * @param {string} key - JIRA-style key
 * @returns {number|null} - Numeric ID or null if invalid
 */
export function getIdFromKey(key) {
  const parsed = parseJiraKey(key);
  return parsed ? parsed.id : null;
}
