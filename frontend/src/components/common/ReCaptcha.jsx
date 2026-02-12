import { useRef, useImperativeHandle, forwardRef } from 'react';
import ReCAPTCHA from 'react-google-recaptcha';

/**
 * Google reCAPTCHA v2 component wrapper.
 * 
 * @param {function} onChange - Called with token when captcha is solved
 * @param {function} onExpired - Called when captcha expires
 * @param {function} onError - Called on captcha error
 * @param {ref} ref - Forward ref to access reset() method
 */
const ReCaptcha = forwardRef(({ onChange, onExpired, onError }, ref) => {
  const recaptchaRef = useRef(null);
  const siteKey = import.meta.env.VITE_RECAPTCHA_SITE_KEY;

  // Expose reset method to parent
  useImperativeHandle(ref, () => ({
    reset: () => {
      recaptchaRef.current?.reset();
    },
    getValue: () => {
      return recaptchaRef.current?.getValue();
    }
  }));

  if (!siteKey) {
    return (
      <div className="p-4 border border-yellow-200 rounded-lg bg-yellow-50 text-center text-sm text-yellow-700">
        ⚠️ reCAPTCHA is not configured. Please add VITE_RECAPTCHA_SITE_KEY to your .env file.
      </div>
    );
  }

  return (
    <div className="flex justify-center">
      <ReCAPTCHA
        ref={recaptchaRef}
        sitekey={siteKey}
        onChange={onChange}
        onExpired={onExpired}
        onErrored={onError}
        theme="light"
      />
    </div>
  );
});

ReCaptcha.displayName = 'ReCaptcha';

export default ReCaptcha;
