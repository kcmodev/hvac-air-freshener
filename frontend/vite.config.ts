import react from '@vitejs/plugin-react';
import { loadEnv } from 'vite';
import { defineConfig } from 'vitest/config';

export default defineConfig(({ mode }) => {
    // Where /api requests go during development, from .env or the environment.
    // The default is the controller running on this machine.
    const { API_PROXY_TARGET = 'http://127.0.0.1:8000' } = loadEnv(
        mode,
        '.',
        '',
    );
    const proxy = { '/api': API_PROXY_TARGET };

    return {
        plugins: [react()],
        server: { port: 3000, proxy },
        preview: { port: 3000, proxy },
        test: {
            environment: 'jsdom',
            setupFiles: './src/setupTests.ts',
        },
    };
});
