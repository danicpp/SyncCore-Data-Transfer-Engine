<script lang="ts">
    import '../app.css';
    import { createTransferEngine } from '$lib/TransferEngine.svelte';
    import Terminal from '$lib/components/Terminal.svelte';
    import { Activity, Zap, ShieldCheck, Cpu, HardDrive } from 'lucide-svelte';

    import { ScannerService } from '$lib/services/scanner';
    import { onMount } from 'svelte';

    const engine = createTransferEngine();

    onMount(() => {
        engine.initializeDevice();
    });

    async function handleStart() {
        engine.addLog('info', 'Scanning device for all files...');
        // In a real device, we would scan the root or selected folder
        // For this demo, we'll scan the dummy root but it leverages ScannerService
        const manifest = await ScannerService.scanDirectory('');
        
        if (manifest.length === 0) {
            engine.addLog('warning', 'No files found or permission denied.');
            // Fallback for demo if scanning empty path fails in webview
            const dummyManifest = [{ path: 'DCIM/Photo1.jpg', size: 1024 * 1024 * 32, hash: '', lastModified: Date.now() }];
            engine.startRealTransfer(dummyManifest);
        } else {
            engine.startRealTransfer(manifest);
        }
    }
</script>

<main class="container">
    <header>
        <div class="logo">
            <Zap class="text-accent" />
            <h1 class="glow-text">SYNC<span style="color: var(--accent-secondary)">CORE</span></h1>
        </div>
        <div class="header-status">
            <span class="status-indicator status-online"></span>
            <span class="text-secondary text-sm">Device: {engine.deviceName.toUpperCase()}</span>
        </div>
    </header>

    <div class="dashboard-grid">
        <!-- Live Throughput Card -->
        <div class="glass-card throughput-card">
            <div class="card-header">
                <Activity size={20} />
                <h3>Real-time Throughput</h3>
            </div>
            <div class="throughput-value">
                <span class="value">{engine.throughput.toFixed(1)}</span>
                <span class="unit">MB/s</span>
            </div>
            <div class="throughput-visual">
                <div class="bar-container">
                    {#each Array(20) as _, i}
                        <div 
                            class="bar" 
                            style="height: {Math.random() * (engine.throughput / 6)}px; opacity: {0.3 + (i / 20)}"
                        ></div>
                    {/each}
                </div>
            </div>
        </div>

        <!-- Health & Integrity Card -->
        <div class="glass-card health-card">
            <div class="card-header">
                <ShieldCheck size={20} />
                <h3>Transfer Health</h3>
            </div>
            <div class="health-meter">
                <svg viewBox="0 0 100 100">
                    <circle cx="50" cy="50" r="45" fill="none" stroke="#222" stroke-width="8" />
                    <circle 
                        cx="50" cy="50" r="45" 
                        fill="none" stroke="var(--accent-secondary)" 
                        stroke-width="8" 
                        stroke-dasharray="283" 
                        stroke-dashoffset={283 - (283 * engine.health / 100)}
                        style="transition: stroke-dashoffset 0.5s ease"
                    />
                </svg>
                <div class="health-value">{engine.health.toFixed(0)}%</div>
            </div>
            <div class="stats-mini">
                <div class="stat"><Cpu size={14}/> <span>SHA-256 Verified</span></div>
                <div class="stat"><HardDrive size={14}/> <span>Bridge Mode ON</span></div>
            </div>
        </div>

        <!-- Main Control Card -->
        <div class="glass-card control-card">
            <div class="card-header">
                <h3>Synchronization</h3>
            </div>
            <div class="progress-section">
                <div class="progress-info">
                    <span>Task Progress</span>
                    <span>{engine.progress}%</span>
                </div>
                <div class="progress-bg">
                    <div class="progress-fill" style="width: {engine.progress}%"></div>
                </div>
            </div>
            <button 
                class="btn-primary" 
                onclick={handleStart} 
                disabled={engine.isTransferring}
            >
                {engine.isTransferring ? 'SYNCING...' : 'START SYNC'}
            </button>
        </div>

        <!-- Terminal Section -->
        <div class="terminal-section">
            <Terminal logs={engine.logs} />
        </div>
    </div>
</main>

<style>
    .container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 2rem;
    }
    header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 3rem;
    }
    .logo {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .logo h1 { margin: 0; font-size: 1.5rem; }
    
    .dashboard-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 24px;
    }

    .throughput-card { grid-column: span 2; position: relative; }
    .throughput-value {
        font-size: 4rem;
        font-weight: 800;
        margin: 1.5rem 0;
        display: flex;
        align-items: baseline;
        gap: 12px;
    }
    .unit { font-size: 1.2rem; color: var(--text-secondary); }
    .throughput-visual {
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        height: 60px;
        padding: 0 1.5rem;
    }
    .bar-container {
        display: flex;
        align-items: flex-end;
        gap: 4px;
        height: 100%;
    }
    .bar {
        flex: 1;
        background: var(--accent-primary);
        border-radius: 2px 2px 0 0;
        transition: height 0.3s ease;
    }

    .health-card {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: space-between;
    }
    .card-header {
        width: 100%;
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 1rem;
    }
    .health-meter {
        width: 140px;
        height: 140px;
        position: relative;
    }
    .health-value {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--accent-secondary);
    }
    .stats-mini {
        width: 100%;
        display: flex;
        justify-content: space-around;
        margin-top: 1rem;
    }
    .stat {
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 0.7rem;
        color: var(--text-secondary);
    }

    .control-card {
        grid-column: span 1;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .progress-section { margin: 1.5rem 0; }
    .progress-info {
        display: flex;
        justify-content: space-between;
        font-size: 0.8rem;
        margin-bottom: 8px;
    }
    .progress-bg {
        height: 8px;
        background: #222;
        border-radius: 4px;
        overflow: hidden;
    }
    .progress-fill {
        height: 100%;
        background: var(--accent-primary);
        transition: width 0.3s ease;
    }

    .terminal-section { grid-column: span 3; }

    @media (max-width: 900px) {
        .dashboard-grid { grid-template-columns: 1fr; }
        .throughput-card, .health-card, .control-card, .terminal-section { grid-column: span 1; }
    }
</style>
