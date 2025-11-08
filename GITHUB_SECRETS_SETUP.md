# Setting Up GitHub Secrets for CI/CD

## Overview

Your GitHub Actions workflow needs access to environment variables (secrets) to run the ingestion script. **GitHub Secrets work in both public and private repositories** - they are always encrypted and never exposed in logs.

## Should You Make Your Repo Private?

**You don't need to make it private** - GitHub Secrets are secure in public repos too. However, you might want to make it private if:
- You don't want the codebase to be publicly visible
- You want to limit who can see the repository structure
- You prefer additional privacy

**Secrets are always encrypted** regardless of repo visibility.

## How to Add GitHub Secrets

### Step 1: Go to Repository Settings

1. Navigate to your repository: https://github.com/rbhagat518/PodCharts
2. Click on **Settings** (top menu)
3. In the left sidebar, click **Secrets and variables** → **Actions**

### Step 2: Add Required Secrets

Click **"New repository secret"** and add these secrets:

#### Required Secrets:

1. **`DATABASE_URL`**
   - Value: Your Supabase database connection string
   - Example: `postgresql://postgres.akqrotmlgaqqgaomvlnh:YOUR_PASSWORD@aws-1-us-east-2.pooler.supabase.com:6543/postgres`
   - **Important**: Make sure the password is URL-encoded (replace `@` with `%40`)

2. **`LISTENNOTES_API_KEY`**
   - Value: Your ListenNotes API key
   - Get it from: https://www.listennotes.com/api/docs/

#### Optional Secrets (for future features):

3. **`SUPABASE_URL`** (if needed for auth)
   - Value: `https://akqrotmlgaqqgaomvlnh.supabase.co`

4. **`SUPABASE_SERVICE_KEY`** (if needed for auth)
   - Value: Your Supabase service role key

5. **`STRIPE_SECRET_KEY`** (if using subscriptions)
   - Value: Your Stripe secret key

6. **`STRIPE_WEBHOOK_SECRET`** (if using webhooks)
   - Value: Your Stripe webhook secret

### Step 3: Verify Secrets Are Added

After adding secrets, you should see them listed in the **Secrets and variables** → **Actions** page (values are hidden for security).

## Testing the Workflow

Once secrets are added:

1. Go to **Actions** tab in your repository
2. Click on **"Daily Ingestion"** workflow
3. Click **"Run workflow"** button (top right)
4. Select branch: `main`
5. Click **"Run workflow"**

The workflow should now run successfully!

## Security Best Practices

✅ **DO:**
- Use GitHub Secrets for all sensitive data
- Keep secrets updated if they change
- Use different secrets for different environments (if you have staging/prod)

❌ **DON'T:**
- Commit secrets to the repository
- Hardcode secrets in workflow files
- Share secrets in issues or pull requests

## Troubleshooting

### Error: "DATABASE_URL is required"
- Make sure you added `DATABASE_URL` secret
- Check that the secret name matches exactly (case-sensitive)

### Error: "LISTENNOTES_API_KEY is required"
- Make sure you added `LISTENNOTES_API_KEY` secret
- Verify the API key is valid

### Workflow runs but fails
- Check the Actions logs for detailed error messages
- Verify your database connection string is correct
- Make sure your ListenNotes API key has remaining quota

## Current Workflow Configuration

The workflow (`ingest.yml`) is configured to:
- Run daily at 3:00 AM UTC
- Use Poetry for dependency management
- Run the ingestion script with secrets from GitHub Secrets

Required secrets:
- `DATABASE_URL`
- `LISTENNOTES_API_KEY`

