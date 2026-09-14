#!/usr/bin/env bash
# Publish this site to S3 behind CloudFront.
#
#   BUCKET=gawg-minerva-br1 ./deploy/aws-s3-cloudfront.sh            # sync only
#   BUCKET=... DISTRIBUTION_ID=E123ABC ./deploy/aws-s3-cloudfront.sh # sync + invalidate
#
# One-time setup is in deploy/README-aws.md. The bucket stays private;
# CloudFront reads it through Origin Access Control.
set -euo pipefail

: "${BUCKET:?set BUCKET to your S3 bucket name}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

command -v python3 >/dev/null && python3 build.py

COMMON=(--exclude ".git/*" --exclude ".github/*" --exclude ".review/*"
        --exclude "deploy/*" --exclude "content/*" --exclude "build.py"
        --exclude "*.md" --exclude ".gitignore")

# Fingerprinted-ish assets: long cache. Images and CSS/JS change rarely; the
# HTML below is always revalidated, so a stale asset is the only risk and a
# CloudFront invalidation clears it.
aws s3 sync . "s3://$BUCKET" "${COMMON[@]}" \
  --exclude "*" --include "assets/*" \
  --cache-control "public, max-age=604800" \
  --delete

# HTML: never cache at the edge without revalidating.
aws s3 sync . "s3://$BUCKET" "${COMMON[@]}" \
  --exclude "assets/*" \
  --cache-control "public, max-age=0, must-revalidate" \
  --delete

if [[ -n "${DISTRIBUTION_ID:-}" ]]; then
  echo "Invalidating CloudFront $DISTRIBUTION_ID ..."
  aws cloudfront create-invalidation \
    --distribution-id "$DISTRIBUTION_ID" \
    --paths "/*" >/dev/null
  echo "Invalidation submitted."
fi

echo "Done. Bucket: s3://$BUCKET"
