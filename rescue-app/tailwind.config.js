/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                primary: '#ef4444', // Red for emergency
                secondary: '#3b82f6', // Blue for info
                dark: '#1f2937',
                light: '#f3f4f6'
            }
        },
    },
    plugins: [],
}
