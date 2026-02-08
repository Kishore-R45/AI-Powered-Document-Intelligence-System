import { useNavigate } from 'react-router-dom';
import {
  Shield,
  FileSearch,
  Bell,
  Lock,
  Upload,
  MessageSquare,
  CheckCircle,
  ArrowRight,
  Database,
  Eye,
  Fingerprint,
  Server,
} from 'lucide-react';
import Button from '../components/common/Button';
import Card from '../components/common/Card';
import { APP_NAME, ROUTES } from '../utils/constants';

/**
 * Public landing page.
 * Background sections updated to use the dimmed white tone.
 */
export default function LandingPage() {
  const navigate = useNavigate();

  return (
    <div className="bg-[#F6F7F9]">
      {/* ─── Hero Section ─── */}
      <section className="relative overflow-hidden bg-white">
        <div className="absolute inset-0 bg-gradient-to-br from-brand-50 via-white to-[#F6F7F9] -z-10" />
        <div className="absolute top-0 right-0 w-[600px] h-[600px] bg-brand-100/30 rounded-full blur-3xl -z-10 translate-x-1/2 -translate-y-1/2" />

        <div className="section-container py-20 sm:py-28 lg:py-36">
          <div className="max-w-3xl mx-auto text-center">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-brand-50 border border-brand-200 rounded-full mb-8 animate-fade-in">
              <Shield size={16} className="text-brand-600" />
              <span className="text-sm font-medium text-brand-700">
                Enterprise-grade document security
              </span>
            </div>

            <h1 className="text-display-lg font-bold text-neutral-900 text-balance animate-fade-in">
              Your Personal Documents,{' '}
              <span className="gradient-text">Organized & Queryable</span>
            </h1>

            <p className="mt-6 text-lg text-neutral-600 max-w-2xl mx-auto text-balance animate-fade-in animation-delay-100">
              Securely upload personal documents — IDs, certificates, insurance policies —
              and retrieve verified information instantly through intelligent queries.
              No hallucinations. Only facts from your documents.
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mt-10 animate-fade-in animation-delay-200">
              <Button
                variant="primary"
                size="lg"
                rightIcon={<ArrowRight size={18} />}
                onClick={() => navigate(ROUTES.SIGNUP)}
              >
                Get Started Free
              </Button>
              <Button
                variant="outline"
                size="lg"
                onClick={() => navigate(ROUTES.LOGIN)}
              >
                Sign In
              </Button>
            </div>

            <div className="flex items-center justify-center gap-8 mt-12 text-sm text-neutral-400 animate-fade-in animation-delay-300">
              <div className="flex items-center gap-1.5">
                <Lock size={14} />
                <span>AES-256 Encrypted</span>
              </div>
              <div className="flex items-center gap-1.5">
                <Server size={14} />
                <span>AWS Hosted</span>
              </div>
              <div className="flex items-center gap-1.5">
                <Eye size={14} />
                <span>Zero-Access Architecture</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ─── Features Section ─── */}
      <section id="features" className="py-20 sm:py-28 bg-[#F6F7F9]">
        <div className="section-container">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <h2 className="text-display-sm font-bold text-neutral-900">
              Everything you need to manage personal documents
            </h2>
            <p className="mt-4 text-neutral-600">
              Built for security-conscious individuals who want control over their
              important information.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, index) => (
              <Card key={index} hover className="group">
                <div className="w-11 h-11 bg-brand-50 rounded-lg flex items-center justify-center mb-4 group-hover:bg-brand-100 transition-colors">
                  <feature.icon size={22} className="text-brand-600" />
                </div>
                <h3 className="text-base font-semibold text-neutral-900 mb-2">
                  {feature.title}
                </h3>
                <p className="text-sm text-neutral-500 leading-relaxed">
                  {feature.description}
                </p>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* ─── How It Works Section ─── */}
      <section id="how-it-works" className="py-20 sm:py-28 bg-white">
        <div className="section-container">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <h2 className="text-display-sm font-bold text-neutral-900">
              How it works
            </h2>
            <p className="mt-4 text-neutral-600">
              Three simple steps to secure and query your documents.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl mx-auto">
            {steps.map((step, index) => (
              <div key={index} className="relative text-center">
                <div className="w-14 h-14 bg-brand-600 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-md">
                  <step.icon size={24} className="text-white" />
                </div>

                {index < steps.length - 1 && (
                  <div className="hidden md:block absolute top-7 left-[calc(50%+2rem)] w-[calc(100%-4rem)] h-px bg-neutral-200" />
                )}

                <div className="text-xs font-bold text-brand-600 uppercase tracking-wider mb-2">
                  Step {index + 1}
                </div>
                <h3 className="text-base font-semibold text-neutral-900 mb-2">
                  {step.title}
                </h3>
                <p className="text-sm text-neutral-500 leading-relaxed">
                  {step.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ─── Security Section ─── */}
      <section id="security" className="py-20 sm:py-28 bg-neutral-900 text-white">
        <div className="section-container">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <div className="inline-flex items-center gap-2 px-3 py-1.5 bg-white/10 rounded-full mb-6">
              <Lock size={14} className="text-brand-300" />
              <span className="text-xs font-semibold text-brand-300 uppercase tracking-wider">
                Security First
              </span>
            </div>
            <h2 className="text-display-sm font-bold">
              Your data security is non-negotiable
            </h2>
            <p className="mt-4 text-neutral-400">
              We implement multiple layers of security to ensure your documents
              remain private and protected.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 max-w-5xl mx-auto">
            {securityFeatures.map((item, index) => (
              <div
                key={index}
                className="p-6 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 transition-colors"
              >
                <item.icon size={24} className="text-brand-400 mb-4" />
                <h3 className="text-sm font-semibold text-white mb-2">
                  {item.title}
                </h3>
                <p className="text-xs text-neutral-400 leading-relaxed">
                  {item.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ─── CTA Section ─── */}
      <section className="py-20 sm:py-28 bg-white">
        <div className="section-container">
          <div className="max-w-2xl mx-auto text-center">
            <h2 className="text-display-sm font-bold text-neutral-900">
              Ready to organize your documents?
            </h2>
            <p className="mt-4 text-neutral-600">
              Join and take control of your personal information.
              Setup takes less than a minute.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mt-8">
              <Button
                variant="primary"
                size="lg"
                rightIcon={<ArrowRight size={18} />}
                onClick={() => navigate(ROUTES.SIGNUP)}
              >
                Create Your Vault
              </Button>
              <Button
                variant="ghost"
                size="lg"
                onClick={() => navigate(ROUTES.LOGIN)}
              >
                Already have an account?
              </Button>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

/* ─── Static Data ─── */

const features = [
  {
    icon: Shield,
    title: 'Secure Document Storage',
    description:
      'Your documents are encrypted and stored in isolated, enterprise-grade cloud infrastructure with strict access controls.',
  },
  {
    icon: FileSearch,
    title: 'AI-Powered Querying',
    description:
      'Ask natural language questions about your documents and receive accurate, verified answers sourced directly from your files.',
  },
  {
    icon: CheckCircle,
    title: 'Zero Hallucination',
    description:
      'Every answer is grounded in your actual documents. If the information isn\'t there, we tell you clearly — no fabricated responses.',
  },
  {
    icon: Bell,
    title: 'Expiry Reminders',
    description:
      'Set expiry dates on important documents and receive timely notifications before they expire.',
  },
  {
    icon: Database,
    title: 'Smart Organization',
    description:
      'Categorize documents by type — insurance, academic, ID, medical — and find them instantly with search and filters.',
  },
  {
    icon: Fingerprint,
    title: 'User-Controlled Access',
    description:
      'Only you can access your documents. No shared data, no third-party access, complete data sovereignty.',
  },
];

const steps = [
  {
    icon: Upload,
    title: 'Upload Documents',
    description:
      'Drag and drop your PDFs, certificates, and IDs into your secure vault. Add metadata and expiry dates.',
  },
  {
    icon: MessageSquare,
    title: 'Ask Questions',
    description:
      'Query your documents in plain English. Ask about policy details, certificate dates, or any stored information.',
  },
  {
    icon: CheckCircle,
    title: 'Get Verified Answers',
    description:
      'Receive factual, document-sourced answers with clear references. Know exactly where every answer comes from.',
  },
];

const securityFeatures = [
  {
    icon: Lock,
    title: 'End-to-End Encryption',
    description: 'All documents encrypted at rest and in transit using AES-256 encryption.',
  },
  {
    icon: Database,
    title: 'Data Isolation',
    description: 'Every user\'s data is logically isolated. No cross-user data exposure.',
  },
  {
    icon: Fingerprint,
    title: 'JWT Authentication',
    description: 'Industry-standard token-based authentication with secure session management.',
  },
  {
    icon: Eye,
    title: 'Privacy by Design',
    description: 'No data mining, no analytics on your documents. Your data is yours alone.',
  },
];