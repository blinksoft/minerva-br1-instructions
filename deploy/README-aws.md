# Deploying to AWS

The whole site is static files. That rules out most of the AWS surface area:

| Option | Verdict |
| --- | --- |
| **S3 + CloudFront** | **Recommended.** Pennies a month, global CDN, free TLS via ACM, no servers. |
| S3 website endpoint only | Works, but HTTP-only and no custom-domain TLS. Fine for a scratch test, not for cadets. |
| Amplify Hosting | Git-connected and pleasant, but it is CloudFront underneath with a build pipeline you do not need. |
| Lightsail / EC2 | A server you have to patch, for files that never change. Don't. |

## One-time setup

```bash
BUCKET=gawg-minerva-br1          # must be globally unique
REGION=us-east-1

# 1. Private bucket. CloudFront reads it via OAC; nothing is public directly.
aws s3api create-bucket --bucket "$BUCKET" --region "$REGION"
aws s3api put-public-access-block --bucket "$BUCKET" \
  --public-access-block-configuration \
  BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true

# 2. Upload once so the distribution has something to serve.
BUCKET="$BUCKET" ./deploy/aws-s3-cloudfront.sh
```

Then create the distribution in the console (fastest path):

* **Origin** → your S3 bucket → **Origin access: Origin access control**, create a new
  OAC, and click the button to copy the generated bucket policy onto the bucket.
* **Default root object**: `index.html`
* **Viewer protocol policy**: Redirect HTTP to HTTPS
* **Cache policy**: `CachingOptimized`
* Custom error responses (so a bad path lands on the guide rather than XML):
  403 → `/index.html` (200), 404 → `/index.html` (200)

Grab the distribution ID from the console.

## Every deploy after that

```bash
BUCKET=gawg-minerva-br1 DISTRIBUTION_ID=E1234567890ABC ./deploy/aws-s3-cloudfront.sh
```

The script rebuilds `index.html`, syncs with `--delete`, sets a one-week cache on
`assets/*` and `must-revalidate` on the HTML, then invalidates the distribution.

## Custom domain

1. `aws acm request-certificate --domain-name rocketry.example.org --validation-method DNS --region us-east-1`
   — the cert **must** be in `us-east-1` for CloudFront, regardless of where the bucket lives.
2. Add the CNAME that ACM gives you at your DNS provider and wait for `ISSUED`.
3. Add the domain as an Alternate Domain Name on the distribution and attach the cert.
4. Point the domain at the distribution: a Route 53 A/AAAA alias, or a CNAME at any
   other registrar.

## Cost

At Civil Air Patrol traffic levels — a few hundred cadets and mentors, ~5 MB of images
per full page load — this lands in the "under a dollar a month" range. CloudFront's free
tier covers the first 1 TB out per month.
