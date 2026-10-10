declare module "unzipper/lib/Open/directory.js" {
  import type { Readable } from "node:stream";
  import type { CentralDirectory } from "unzipper";

  export default function openDirectory(source: {
    size: () => Promise<number>;
    stream: (offset: number, length?: number) => Readable;
  }): Promise<CentralDirectory>;
}
