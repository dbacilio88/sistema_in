declare module 'react-hot-toast' {
  export interface ToastOptions {
    duration?: number;
    position?: 'top-left' | 'top-center' | 'top-right' | 'bottom-left' | 'bottom-center' | 'bottom-right';
    style?: Record<string, any>;
    className?: string;
    icon?: string;
    iconTheme?: {
      primary?: string;
      secondary?: string;
    };
  }

  export interface Toast {
    id: string;
    message: string;
    type: 'success' | 'error' | 'loading' | 'blank' | 'custom';
    duration?: number;
    visible: boolean;
  }

  export interface ToastHandler {
    (message: string, options?: ToastOptions): string;
  }

  export interface Toaster {
    success: ToastHandler;
    error: ToastHandler;
    loading: ToastHandler;
    custom: ToastHandler;
    promise: <T>(
      promise: Promise<T>,
      msgs: {
        loading: string;
        success: string | ((data: T) => string);
        error: string | ((err: any) => string);
      },
      options?: ToastOptions
    ) => Promise<T>;
    dismiss: (toastId?: string) => void;
    remove: (toastId?: string) => void;
  }

  const toast: ToastHandler & Toaster;
  export default toast;

  export function Toaster(props?: {
    position?: ToastOptions['position'];
    reverseOrder?: boolean;
    gutter?: number;
    containerStyle?: Record<string, any>;
    containerClassName?: string;
    toastOptions?: ToastOptions;
  }): any;
}
