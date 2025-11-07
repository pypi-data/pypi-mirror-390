# HumaLab SDK Documentation

This directory contains the Fumadocs-based documentation website for HumaLab SDK.

## Development

Install dependencies:

```bash
npm install
```

Run the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the documentation.

## Building

Build the static site:

```bash
npm run build
```

The static site will be generated in the `out` directory.

## Deployment

### Deploy to Vercel

1. Push this repository to GitHub
2. Import the project in Vercel
3. Set the root directory to `docs`
4. Deploy!

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/humalab/humalab_sdk&project-name=humalab-docs&root-directory=docs)

### Deploy to Netlify

1. Push this repository to GitHub
2. Import the project in Netlify
3. Set the base directory to `docs`
4. Set build command to `npm run build`
5. Set publish directory to `docs/out`
6. Deploy!

### Deploy to GitHub Pages

```bash
npm run build
# Copy the 'out' directory to your GitHub Pages repository
```

## Project Structure

```
docs/
├── app/                    # Next.js app directory
│   ├── docs/              # Documentation pages
│   ├── layout.tsx         # Root layout
│   └── page.tsx           # Home page
├── content/               # MDX content
│   └── docs/             # Documentation content
│       ├── index.mdx
│       ├── quickstart.mdx
│       ├── scenarios.mdx
│       ├── runs.mdx
│       ├── metrics.mdx
│       ├── api.mdx
│       └── meta.json      # Navigation structure
├── lib/                   # Utilities
│   └── source.ts         # Fumadocs source configuration
├── next.config.mjs        # Next.js configuration
├── source.config.ts       # Fumadocs MDX configuration
├── tailwind.config.js     # Tailwind CSS configuration
└── package.json           # Dependencies
```

## Writing Documentation

Documentation is written in MDX format in the `content/docs` directory.

### Creating a New Page

1. Create a new `.mdx` file in `content/docs/`
2. Add frontmatter with title and description:

```mdx
---
title: Page Title
description: Page description
---

# Page Title

Your content here...
```

3. Add the page to `content/docs/meta.json` for navigation

### Code Blocks

Use fenced code blocks with language syntax highlighting:

```python
import humalab as hl

hl.init(api_key="your_api_key")
```

## Technology Stack

- [Fumadocs](https://fumadocs.vercel.app/) - Documentation framework
- [Next.js](https://nextjs.org/) - React framework
- [Tailwind CSS](https://tailwindcss.com/) - Styling
- [MDX](https://mdxjs.com/) - Markdown + JSX

## License

MIT
