import { Outlet, useLocation } from 'react-router-dom';
import { useContext } from 'react';
import Navbar from './Navbar';
import Sidebar from './Sidebar';
import { AuthContext } from '../../context/AuthContext';
import { ROUTES } from '../../utils/constants';

/**
 * Layout wrapper for authenticated application pages.
 * Uses the dim background color consistently.
 * Chat page gets fixed height layout, other pages are scrollable.
 */
export default function AppLayout() {
  const { user, logout } = useContext(AuthContext);
  const location = useLocation();
  
  // Check if current page is the chat page
  const isChatPage = location.pathname === ROUTES.CHAT;

  return (
    <div className={`flex flex-col bg-[#F6F7F9] ${isChatPage ? 'h-screen overflow-hidden' : 'min-h-screen'}`}>
      <Navbar isAuthenticated={true} user={user} onLogout={logout} />
      <div className={`flex flex-1 ${isChatPage ? 'overflow-hidden' : ''}`}>
        <Sidebar />
        <main className={`flex-1 p-6 lg:p-8 max-w-7xl w-full mx-auto ${isChatPage ? 'overflow-hidden' : 'overflow-y-auto'}`}>
          <div className="h-full">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}