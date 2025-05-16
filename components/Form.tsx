import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import confetti from "canvas-confetti";
import { useEffect, useRef, useState } from "react";

interface FormData {
  name: string;
  phone: string;
  email: string;
}

interface FormProps {
  formData: FormData;
  updateFormField: (field: keyof FormData, value: string) => void;
  shouldSubmit?: boolean;
}

// Debounce hook
function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(timer);
    };
  }, [value, delay]);

  return debouncedValue;
}

export function Form({ formData, updateFormField, shouldSubmit = false }: FormProps) {
  const buttonRef = useRef<HTMLButtonElement>(null);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [localFormData, setLocalFormData] = useState<FormData>(formData);
  const isUpdatingFromParent = useRef(false);

  // Sync localFormData with incoming formData changes
  useEffect(() => {
    isUpdatingFromParent.current = true;
    setLocalFormData(formData);
    // Reset the flag after the update
    setTimeout(() => {
      isUpdatingFromParent.current = false;
    }, 0);
  }, [formData]);

  // Debounce the local form data changes
  const debouncedFormData = useDebounce(localFormData, 500); // 500ms delay

  // Update parent component when debounced value changes
  useEffect(() => {
    // Only update parent if the change came from user input
    if (!isUpdatingFromParent.current) {
      Object.entries(debouncedFormData).forEach(([field, value]) => {
        if (value !== formData[field as keyof FormData]) {
          updateFormField(field as keyof FormData, value);
        }
      });
    }
  }, [debouncedFormData, formData, updateFormField]);

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) {
      e.preventDefault();
    }

    // Get button position
    if (buttonRef.current) {
      const rect = buttonRef.current.getBoundingClientRect();
      const x = rect.left + rect.width / 2;
      const y = rect.top + rect.height / 2;

      // Convert to percentage of window size
      const xPercent = x / window.innerWidth;
      const yPercent = y / window.innerHeight;

      // Trigger confetti from button position
      confetti({
        particleCount: 100,
        spread: 70,
        origin: { x: xPercent, y: yPercent },
      });
    }

    // Clear form fields
    isUpdatingFromParent.current = true;
    setLocalFormData({ name: "", phone: "", email: "" });
    updateFormField("name", "");
    updateFormField("phone", "");
    updateFormField("email", "");
    setTimeout(() => {
      isUpdatingFromParent.current = false;
    }, 0);

    // Set submitted state
    setIsSubmitted(true);
  };

  // Watch for shouldSubmit changes
  useEffect(() => {
    if (shouldSubmit && !isSubmitted) {
      handleSubmit();
    }
  }, [shouldSubmit, isSubmitted]);

  return (
    <div className="w-full max-w-md p-6 space-y-6 bg-zinc-800 rounded-lg shadow-lg">
      {isSubmitted ? (
        <div className="text-center space-y-4">
          <p className="text-xl">You&apos;re signed up for the ice cream party! 🍦</p>
          <p className="text-sm text-gray-400">We&apos;ll send you the details soon.</p>
        </div>
      ) : (
        <>
          <h2 className="text-2xl font-bold text-center">Ice Cream Party</h2>
          <form className="space-y-4" onSubmit={handleSubmit}>
            <div className="space-y-2">
              <label htmlFor="name" className="text-sm font-medium">
                Name
              </label>
              <Input
                className="text-black"
                id="name"
                type="text"
                required
                placeholder="Name"
                value={localFormData.name}
                onChange={(e) => setLocalFormData((prev) => ({ ...prev, name: e.target.value }))}
              />
            </div>
            <div className="space-y-2">
              <label htmlFor="phone" className="text-sm font-medium">
                Phone Number
              </label>
              <Input
                className="text-black"
                id="phone"
                type="tel"
                required
                placeholder="Phone number"
                value={localFormData.phone}
                onChange={(e) => setLocalFormData((prev) => ({ ...prev, phone: e.target.value }))}
              />
            </div>
            <div className="space-y-2">
              <label htmlFor="email" className="text-sm font-medium">
                Email
              </label>
              <Input
                className="text-black"
                id="email"
                type="email"
                required
                placeholder="Email"
                value={localFormData.email}
                onChange={(e) => setLocalFormData((prev) => ({ ...prev, email: e.target.value }))}
              />
            </div>
            <Button ref={buttonRef} type="submit" className="w-full">
              Submit
            </Button>
          </form>
        </>
      )}
    </div>
  );
}
