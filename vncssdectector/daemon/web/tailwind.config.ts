import type { Config } from 'tailwindcss';
import { breakpoints } from './src/theme';

export default {
    content: ['./src/**/*.{html,js,svelte,ts}'],

    theme: {
        extend: {
            colors: {
                'vncssdetector-blue': '#4e4eb1',
                'vncssdetector-dark-blue': '#3f3da0',
                'vncssdetector-green': '#94ea18',
            },
            screens: breakpoints,
        },
    },

    plugins: [],
} as Config;
