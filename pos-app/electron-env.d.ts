import { PosAPI } from "./src/db/client";

declare global {
  interface Window {
    posAPI: PosAPI;
  }
}

export {};
