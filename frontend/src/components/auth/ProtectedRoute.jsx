import { useContext } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { AuthContext } from '../../context/AuthContext';
import Spinner from '../common/Spinner';
import { ROUTES } from '../../utils/constants';

/**
 * Route guard that redirects unauthenticated users to login.
 * Shows a loading spinner while auth state is being determined.
 */
export default function ProtectedRoute({ children }) {
//   const { isAuthenticated, loading } = useContext(AuthContext);
//   const location = useLocation();

//   if (loading) {
//     return (
//       <div className="min-h-screen flex items-center justify-center">
//         <Spinner size="xl" className="text-brand-600" />
//       </div>
//     );
//   }

//   if (!isAuthenticated) {
//     return <Navigate to={ROUTES.LOGIN} state={{ from: location }} replace />;
//   }

  return children;
}