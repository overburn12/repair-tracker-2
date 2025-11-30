import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import OrdersListPage from './pages/OrdersListPage';

/**
 * App - Root component with routing
 */
function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<OrdersListPage />} />
        {/* Additional routes will be added here */}
      </Routes>
    </Router>
  );
}

export default App;
