import { useState, useCallback } from 'react';

/**
 * Generic form state management hook.
 * Handles field values, validation errors, dirty tracking, and submission.
 *
 * @param {object} initialValues - Default form field values
 * @param {function} validate - Validation function that returns an errors object.
 *                              Keys should match field names, values are error strings.
 *                              Return empty object `{}` if valid.
 *
 * @returns {{
 *   values: object,
 *   errors: object,
 *   touched: object,
 *   isValid: boolean,
 *   isDirty: boolean,
 *   handleChange: (e: Event) => void,
 *   handleBlur: (e: Event) => void,
 *   setFieldValue: (name: string, value: any) => void,
 *   setFieldError: (name: string, error: string) => void,
 *   setErrors: (errors: object) => void,
 *   handleSubmit: (onSubmit: function) => (e: Event) => void,
 *   reset: () => void,
 *   resetField: (name: string) => void,
 * }}
 *
 * @example
 * const { values, errors, handleChange, handleSubmit } = useForm(
 *   { email: '', password: '' },
 *   (values) => {
 *     const errors = {};
 *     if (!values.email) errors.email = 'Required';
 *     return errors;
 *   }
 * );
 */
export default function useForm(initialValues = {}, validate = () => ({})) {
  const [values, setValues] = useState(initialValues);
  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});

  /**
   * Whether any field has been modified from its initial value.
   */
  const isDirty = Object.keys(initialValues).some(
    (key) => values[key] !== initialValues[key]
  );

  /**
   * Whether the form currently has no validation errors.
   */
  const isValid = Object.keys(errors).length === 0;

  /**
   * Handle input change events.
   * Clears the field error when the user starts typing.
   */
  const handleChange = useCallback((e) => {
    const { name, value, type, checked } = e.target;
    const fieldValue = type === 'checkbox' ? checked : value;

    setValues((prev) => ({ ...prev, [name]: fieldValue }));

    // Clear error for this field on change
    setErrors((prev) => {
      if (prev[name]) {
        const next = { ...prev };
        delete next[name];
        return next;
      }
      return prev;
    });
  }, []);

  /**
   * Handle input blur — marks field as touched and validates it.
   */
  const handleBlur = useCallback((e) => {
    const { name } = e.target;
    setTouched((prev) => ({ ...prev, [name]: true }));

    // Run validation on blur for this field
    const validationErrors = validate(values);
    if (validationErrors[name]) {
      setErrors((prev) => ({ ...prev, [name]: validationErrors[name] }));
    }
  }, [values, validate]);

  /**
   * Programmatically set a single field value.
   */
  const setFieldValue = useCallback((name, value) => {
    setValues((prev) => ({ ...prev, [name]: value }));
  }, []);

  /**
   * Programmatically set an error for a specific field.
   */
  const setFieldError = useCallback((name, error) => {
    setErrors((prev) => ({ ...prev, [name]: error }));
  }, []);

  /**
   * Create a submit handler.
   * Validates all fields before calling the onSubmit callback.
   *
   * @param {function} onSubmit - Called with form values if validation passes
   * @returns {function} Event handler for form onSubmit
   */
  const handleSubmit = useCallback(
    (onSubmit) => (e) => {
      e.preventDefault();

      // Mark all fields as touched
      const allTouched = Object.keys(values).reduce(
        (acc, key) => ({ ...acc, [key]: true }),
        {}
      );
      setTouched(allTouched);

      // Run full validation
      const validationErrors = validate(values);
      setErrors(validationErrors);

      if (Object.keys(validationErrors).length === 0) {
        onSubmit(values);
      }
    },
    [values, validate]
  );

  /**
   * Reset form to initial state.
   */
  const reset = useCallback(() => {
    setValues(initialValues);
    setErrors({});
    setTouched({});
  }, [initialValues]);

  /**
   * Reset a single field to its initial value.
   */
  const resetField = useCallback(
    (name) => {
      setValues((prev) => ({ ...prev, [name]: initialValues[name] ?? '' }));
      setErrors((prev) => {
        const next = { ...prev };
        delete next[name];
        return next;
      });
      setTouched((prev) => {
        const next = { ...prev };
        delete next[name];
        return next;
      });
    },
    [initialValues]
  );

  return {
    values,
    errors,
    touched,
    isValid,
    isDirty,
    handleChange,
    handleBlur,
    setFieldValue,
    setFieldError,
    setErrors,
    handleSubmit,
    reset,
    resetField,
  };
}