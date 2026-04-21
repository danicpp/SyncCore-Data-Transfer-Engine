<script lang="ts">
    import { Terminal as TerminalIcon, Play, AlertCircle } from 'lucide-svelte';
    let { logs } = $props();
</script>

<div class="glass-card terminal-container">
    <div class="terminal-header">
        <TerminalIcon size={18} />
        <span>Troubleshooting Terminal</span>
    </div>
    <div class="terminal-body" id="terminal-scroll">
        {#each logs as log}
            <div class="log-entry {log.type}">
                <span class="prompt">></span>
                <span class="message">{log.msg}</span>
            </div>
        {/each}
        <div class="log-entry current">
            <span class="prompt">></span>
            <span class="cursor">_</span>
        </div>
    </div>
</div>

<style>
    .terminal-container {
        height: 300px;
        display: flex;
        flex-direction: column;
        background: #000;
        border: 1px solid #333;
        font-family: 'Fira Code', monospace;
    }
    .terminal-header {
        display: flex;
        align-items: center;
        gap: 8px;
        padding-bottom: 12px;
        border-bottom: 1px solid #222;
        color: #888;
        font-size: 0.8rem;
    }
    .terminal-body {
        flex: 1;
        overflow-y: auto;
        padding: 12px 0;
        font-size: 0.85rem;
    }
    .log-entry {
        margin-bottom: 4px;
        line-height: 1.4;
    }
    .prompt { color: var(--accent-primary); margin-right: 8px; }
    .info { color: #fff; }
    .success { color: var(--accent-secondary); }
    .error { color: var(--danger); }
    .cursor {
        animation: blink 1s infinite;
        color: var(--accent-primary);
    }
    @keyframes blink { 50% { opacity: 0; } }
</style>
