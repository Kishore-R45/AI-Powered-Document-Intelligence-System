import { useNavigate } from 'react-router-dom';
import { Home, ArrowLeft, FileQuestion } from 'lucide-react';
import Button from '../components/common/Button';
import { ROUTES } from '../utils/constants';

/**
 * 404 Not Found page with dimmed background.
 */
export default function NotFoundPage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-[#F6F7F9] flex items-center justify-center px-4">
      <div className="max-w-md w-full text-center animate-fade-in">
        <div className="w-20 h-20 bg-neutral-100 rounded-2xl flex items-center justify-center mx-auto mb-8">
          <FileQuestion size={40} className="text-neutral-400" />
        </div>

        <h1 className="text-6xl font-bold text-neutral-300 mb-4">404</h1>

        <h2 className="text-xl font-bold text-neutral-900 mb-2">
          Page not found
        </h2>
        <p className="text-sm text-neutral-500 mb-8 max-w-sm mx-auto">
          The page you're looking for doesn't exist or has been moved.
          Please check the URL or navigate back to a known page.
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
          <Button
            variant="primary"
            leftIcon={<Home size={16} />}
            onClick={() => navigate(ROUTES.HOME)}
          >
            Go Home
          </Button>
          <Button
            variant="outline"
            leftIcon={<ArrowLeft size={16} />}
            onClick={() => navigate(-1)}
          >
            Go Back
          </Button>
        </div>
      </div>
    </div>
  );
}