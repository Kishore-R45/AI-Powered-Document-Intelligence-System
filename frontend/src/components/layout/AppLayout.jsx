import { Outlet } from 'react-router-dom';
import { useContext } from 'react';
import Navbar from './Navbar';
import Sidebar from './Sidebar';
import { AuthContext } from '../../context/AuthContext';

/**
 * Layout wrapper for authenticated application pages.
 * Uses the dim background color consistently.
 */
export default function AppLayout() {
  const { user, logout } = useContext(AuthContext);

  return (
    <div className="min-h-screen flex flex-col bg-[#F6F7F9]">
      <Navbar isAuthenticated={true} user={user} onLogout={logout} />
      <div className="flex flex-1">
        <Sidebar />
        <main className="flex-1 p-6 lg:p-8 max-w-7xl w-full mx-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
}