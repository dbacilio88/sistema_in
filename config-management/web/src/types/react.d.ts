declare module 'react' {
  export type ReactNode = any;
  export type ReactElement = any;
  export type JSXElementConstructor<P> = any;

  export interface FC<P = {}> {
    (props: P): ReactElement | null;
    displayName?: string;
  }

  export interface PropsWithChildren<P = unknown> {
    children?: ReactNode | undefined;
  }

  export class Component<P = {}, S = {}> {
    props: Readonly<P>;
    state: Readonly<S>;
    setState<K extends keyof S>(
      state: ((prevState: Readonly<S>, props: Readonly<P>) => (Pick<S, K> | S | null)) | (Pick<S, K> | S | null),
      callback?: () => void
    ): void;
    forceUpdate(callback?: () => void): void;
    render(): ReactNode;
  }

  export function createContext<T>(defaultValue: T): Context<T>;
  export function useContext<T>(context: Context<T>): T;
  export function useState<S>(initialState: S | (() => S)): [S, (newState: S | ((prevState: S) => S)) => void];
  export function useEffect(effect: () => void | (() => void | undefined), deps?: readonly any[]): void;
  export function useMemo<T>(factory: () => T, deps: readonly any[] | undefined): T;
  export function useCallback<T extends Function>(callback: T, deps: readonly any[]): T;
  export function useRef<T>(initialValue: T): { current: T };
  export function useReducer<S, A>(reducer: (state: S, action: A) => S, initialState: S): [S, (action: A) => void];

  export interface Context<T> {
    Provider: FC<{ value: T; children?: ReactNode }>;
    Consumer: FC<{ children: (value: T) => ReactNode }>;
    displayName?: string;
  }

  export interface Dispatch<A> {
    (value: A): void;
  }

  export interface SetStateAction<S> {}

  namespace React {
    export type FC<P = {}> = (props: P) => ReactElement | null;
    export type ReactNode = any;
    export type ReactElement = any;
  }

  export default React;
}

declare module 'react/jsx-runtime' {
  import { ReactElement } from 'react';
  
  export function jsx(type: any, props: any, key?: string): ReactElement;
  export function jsxs(type: any, props: any, key?: string): ReactElement;
  export function Fragment(props: { children?: any }): ReactElement;
}
