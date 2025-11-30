/**
 * LoadingSpinner - Loading state indicator
 */
export default function LoadingSpinner({ children = 'Loading...' }) {
  return <div className="loading">{children}</div>;
}
