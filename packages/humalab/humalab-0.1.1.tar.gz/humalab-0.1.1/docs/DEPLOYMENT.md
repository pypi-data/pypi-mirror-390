# Deployment Guide

This guide covers how to deploy the HumaLab SDK documentation to various hosting platforms.

## Prerequisites

- Node.js 18+ installed
- npm or pnpm package manager
- Git repository (for automated deployments)

## Build Locally

Test the build locally before deploying:

```bash
cd docs
npm install
npm run build
```

The static site will be generated in the `out` directory.

To preview the production build locally:

```bash
npm run start
```

## Deploy to Vercel

Vercel is the recommended platform for deploying Fumadocs sites.

### Option 1: Vercel Dashboard (Recommended)

1. Push your code to GitHub, GitLab, or Bitbucket
2. Go to [vercel.com](https://vercel.com)
3. Click "New Project"
4. Import your repository
5. Configure the project:
   - **Framework Preset**: Next.js
   - **Root Directory**: `docs`
   - **Build Command**: `npm run build` (auto-detected)
   - **Output Directory**: `out` (auto-detected)
6. Click "Deploy"

### Option 2: Vercel CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy from the docs directory
cd docs
vercel

# For production deployment
vercel --prod
```

### Option 3: One-Click Deploy

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/humalab/humalab_sdk&project-name=humalab-docs&root-directory=docs)

## Deploy to Netlify

### Option 1: Netlify Dashboard

1. Push your code to GitHub, GitLab, or Bitbucket
2. Go to [netlify.com](https://netlify.com)
3. Click "Add new site" → "Import an existing project"
4. Connect to your Git provider and select your repository
5. Configure the build settings:
   - **Base directory**: `docs`
   - **Build command**: `npm run build`
   - **Publish directory**: `docs/out`
6. Click "Deploy site"

### Option 2: Netlify CLI

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Deploy from the docs directory
cd docs
netlify deploy

# For production deployment
netlify deploy --prod
```

### Option 3: Deploy Button

[![Deploy to Netlify](https://www.netlify.com/img/deploy/button.svg)](https://app.netlify.com/start/deploy?repository=https://github.com/humalab/humalab_sdk)

## Deploy to GitHub Pages

### Setup

1. Create a `.github/workflows/deploy.yml` file in your repository root:

```yaml
name: Deploy Documentation

on:
  push:
    branches:
      - main
    paths:
      - 'docs/**'

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  build:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: docs

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: docs/package-lock.json

      - name: Install dependencies
        run: npm ci

      - name: Build
        run: npm run build

      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: docs/out

  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    needs: build
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

2. Enable GitHub Pages in your repository settings:
   - Go to Settings → Pages
   - Source: GitHub Actions

3. Push to the main branch to trigger deployment

Your site will be available at `https://<username>.github.io/<repository>/`

## Deploy to AWS S3 + CloudFront

```bash
# Build the site
cd docs
npm run build

# Install AWS CLI
# Then sync to S3
aws s3 sync out/ s3://your-bucket-name --delete

# Invalidate CloudFront cache
aws cloudfront create-invalidation --distribution-id YOUR_DIST_ID --paths "/*"
```

## Deploy to Cloudflare Pages

### Option 1: Cloudflare Dashboard

1. Go to [Cloudflare Pages](https://pages.cloudflare.com/)
2. Click "Create a project"
3. Connect your Git repository
4. Configure build settings:
   - **Build command**: `cd docs && npm run build`
   - **Build output directory**: `docs/out`
   - **Root directory**: `/`
5. Click "Save and Deploy"

### Option 2: Wrangler CLI

```bash
# Install Wrangler
npm install -g wrangler

# Build
cd docs
npm run build

# Deploy
wrangler pages deploy out --project-name humalab-docs
```

## Custom Domain

### Vercel

1. Go to your project settings
2. Navigate to "Domains"
3. Add your custom domain
4. Update your DNS records as instructed

### Netlify

1. Go to your site settings
2. Navigate to "Domain management"
3. Click "Add custom domain"
4. Follow DNS configuration instructions

### GitHub Pages

1. Add a `CNAME` file to `docs/public/` with your domain
2. Configure DNS:
   - For apex domain: A records to GitHub IPs
   - For subdomain: CNAME to `<username>.github.io`

## Environment Variables

If your documentation needs environment variables:

### Vercel/Netlify

Add them in the dashboard under:
- Vercel: Project Settings → Environment Variables
- Netlify: Site Settings → Build & Deploy → Environment

### GitHub Actions

Add secrets in:
Repository Settings → Secrets and variables → Actions

## Continuous Deployment

All platforms above support automatic deployments on git push:

- **Vercel**: Automatically deploys on every push to connected branches
- **Netlify**: Automatically deploys on every push to connected branches
- **GitHub Pages**: Uses GitHub Actions workflow
- **Cloudflare Pages**: Automatically deploys on every push

## Troubleshooting

### Build Fails

Check:
- Node.js version (should be 18+)
- All dependencies are installed
- Build works locally: `npm run build`

### 404 Errors

For static exports, ensure:
- `output: 'export'` is set in `next.config.mjs`
- All routes are statically generated

### Slow Build Times

- Enable caching in CI/CD
- Use package manager cache (npm cache, pnpm store)
- Consider incremental static regeneration (ISR) if applicable

## Monitoring

After deployment, monitor:
- Build logs for errors
- Analytics for traffic patterns
- Core Web Vitals for performance

## Cost Estimates

- **Vercel**: Free for hobby projects, Pro starts at $20/month
- **Netlify**: Free for personal projects, Pro starts at $19/month
- **GitHub Pages**: Free for public repositories
- **Cloudflare Pages**: Free tier available, very generous limits
- **AWS S3**: Pay per use, typically $1-5/month for docs sites

## Best Practices

1. **Use a CDN**: All platforms above include CDN by default
2. **Enable HTTPS**: Automatically provided by all platforms
3. **Set up monitoring**: Use platform analytics or integrate Google Analytics
4. **Automate deployments**: Connect to Git for automatic deployments
5. **Preview deployments**: Use branch/PR previews for testing changes
6. **Cache headers**: Configure appropriate cache headers for static assets
7. **Compression**: Enable gzip/brotli compression (usually automatic)

## Support

For platform-specific issues:
- [Vercel Documentation](https://vercel.com/docs)
- [Netlify Documentation](https://docs.netlify.com/)
- [GitHub Pages Documentation](https://docs.github.com/pages)
- [Cloudflare Pages Documentation](https://developers.cloudflare.com/pages/)
