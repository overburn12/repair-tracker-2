/**
 * ErrorMessage - Error display component
 */
export default function ErrorMessage({ children }) {
  if (!children) return null;

  return (
    <div className="error-message">
      {children}
    </div>
  );
}
