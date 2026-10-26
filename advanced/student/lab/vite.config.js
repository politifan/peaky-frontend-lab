import {defineConfig} from 'vite';

// Keep complete modules for the reproducible teaching build. Minification stays
// enabled; measure the resulting artifact rather than assuming unused removal.
export default defineConfig({build:{rollupOptions:{treeshake:false}}});
