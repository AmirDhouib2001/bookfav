/// <reference types="react" />
/// <reference types="react-dom" />

declare namespace React {
  interface CSSProperties {
    [key: string]: any;
  }
}

declare module "*.module.css" {
  const classes: { readonly [key: string]: string };
  export default classes;
}

declare module "*.module.scss" {
  const classes: { readonly [key: string]: string };
  export default classes;
}

declare module "*.module.sass" {
  const classes: { readonly [key: string]: string };
  export default classes;
} 