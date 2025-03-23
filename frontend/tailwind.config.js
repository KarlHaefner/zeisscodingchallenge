/**
 * @file tailwind.config.js
 * @description
 *   Configuration file for Tailwind CSS. This tells Tailwind where to look for class names
 *   (in .tsx or .html files under src/) and applies default settings. You can customize
 *   the theme, variants, and plugins here.
 *
 * @notes
 *   - The "content" property indicates which files Tailwind should scan.
 *   - We have not added custom themes or plugins for now, but we can easily do so later.
 *   - This is the minimum required for Tailwind to work in a typical React + Vite setup.
 *
 * @dependencies
 *   - tailwindcss
 *   - postcss
 *   - autoprefixer
 */

module.exports = {
    content: [
      "./index.html",
      "./src/**/*.{js,ts,jsx,tsx}"
    ],
    theme: {
      extend: {}
    },
    plugins: [
      require('@tailwindcss/typography'),
    ]
  };
  