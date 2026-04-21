import { Filesystem, Directory } from '@capacitor/filesystem';

export interface ManifestItem {
    path: string;
    size: number;
    hash: string;
    lastModified: number;
}

export class ScannerService {
    static async requestPermissions() {
        const status = await Filesystem.requestPermissions();
        return status.publicStorage === 'granted';
    }

    /**
     * Recursively scan a directory and build a manifest.
     * For "All Files" access on Android 11+, this often points to the root '/' 
     * but limited by OS scoped storage unless MANAGE_EXTERNAL_STORAGE is granted.
     */
    static async scanDirectory(path: string, manifest: ManifestItem[] = []): Promise<ManifestItem[]> {
        try {
            const result = await Filesystem.readdir({
                path,
                directory: Directory.External
            });

            for (const file of result.files) {
                const fullPath = path === '' ? file.name : `${path}/${file.name}`;
                
                if (file.type === 'directory') {
                    await this.scanDirectory(fullPath, manifest);
                } else {
                    // Get file metadata
                    const stat = await Filesystem.stat({
                        path: fullPath,
                        directory: Directory.External
                    });

                    manifest.push({
                        path: fullPath,
                        size: stat.size,
                        hash: '', // Will be calculated during transfer or pre-scan
                        lastModified: stat.mtime
                    });
                }
            }
        } catch (e) {
            console.error(`Error scanning ${path}:`, e);
        }
        return manifest;
    }
}
