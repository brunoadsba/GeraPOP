import fs from 'node:fs';
import path from 'node:path';

export default function globalSetup(): void {
  const dataDir = path.resolve(import.meta.dirname, '..', '..', '.e2e-data');
  fs.rmSync(dataDir, { recursive: true, force: true });
}