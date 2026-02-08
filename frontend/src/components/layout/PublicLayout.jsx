import { Outlet } from 'react-router-dom';
import Navbar from './Navbar';
import Footer from './Footer';

/**
 * Layout wrapper for public (unauthenticated) pages.
 * Includes public navbar and footer.
 */
export default function PublicLayout() {
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar isAuthenticated={false} />
      <main className="flex-1">
        <Outlet />
      </main>
      <Footer />
    </div>
  );
}