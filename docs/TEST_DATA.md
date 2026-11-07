# Test data: keeping previews away from real players

Added in PR 0 (branch `pr0-test-data-isolation`).

## Before this change

Production, Deploy Previews and branch deploys all opened the same Netlify Blobs store, `offcampus`. Testing a preview wrote real-looking players, scores, answers and crews into production. Preview pages also sent visits to the real GoatCounter.

## How each environment picks its data now

The code is in `lib/datastore.mjs`. Netlify tells each function call which deploy it belongs to (`context.deploy.context`).

| Where | Data store | Setting needed |
|---|---|---|
| Production (offcampusontario.ca, and rad-pothos-d03a2a.netlify.app, same deploy) | `offcampus`, unchanged | none |
| Deploy Preview (`deploy-preview-N--…`) | value of `OC_TEST_STORE` | yes |
| Branch deploy | value of `OC_TEST_STORE` | yes |
| Local `netlify dev` | value of `OC_TEST_STORE` | yes |
| Anything unknown or missing | value of `OC_TEST_STORE` | yes |
| `npm test` and the local test servers | in-memory, nothing on Netlify | none |

Rules:

- `OC_TEST_STORE` must be `offcampus-test` or `offcampus-test-<letters/numbers>`. Anything else is refused, including `offcampus` itself.
- **Fail closed.** If a non-production deploy has no valid `OC_TEST_STORE`, every `/api/*` request answers `503 test data store not configured` and no store is opened at all. Nothing ever falls back to production.
- Production ignores `OC_TEST_STORE` completely.

The visit counter (GoatCounter) now loads only on `offcampusontario.ca` and `www.offcampusontario.ca`. Previews and local pages don't count.

## One-time Netlify setting (Josh)

Netlify → project **rad-pothos-d03a2a** → **Project configuration → Environment variables → Add a variable → Add a single variable**.

1. **Key:** `OC_TEST_STORE`
2. **Scopes:** Functions (all scopes is fine).
3. **Values:** choose **Different value for each deploy context**.
   - **Production:** leave blank. It's ignored anyway.
   - **Deploy Previews:** `offcampus-test`
   - **Branch deploys:** `offcampus-test`
   - **Local development:** `offcampus-test`
4. Save. Then redeploy the PR preview (Deploys → the preview → **Retry deploy**) so it picks up the setting.

This isn't a secret, so no token or password goes anywhere.

## How to check isolation (from a phone browser)

Open `/api/health`:

- On the live site: `https://offcampusontario.ca/api/health` should show `"data":"production","store":"offcampus","context":"production"`. Check this right after the merge.
- On a preview: `https://deploy-preview-N--rad-pothos-d03a2a.netlify.app/api/health`
  - Before the setting: `503` with `"data":"none"`. That's the safe failure.
  - After the setting: `"data":"test","store":"offcampus-test","context":"deploy-preview"`.

Only play or test on a preview after it shows `"data":"test"`.

## How to reset test data safely

Don't delete anything. Change `OC_TEST_STORE` for Deploy Previews / Branch deploys to a new name, such as `offcampus-test-2`, then redeploy the preview. It starts empty. The old test store is just never read again.

There's deliberately no "wipe" button or route, so there's no code path that can delete production data.

## Tests

`npm test` runs `test.mjs` (the API) and `test-datastore.mjs`. The latter checks:

- which store every kind of deploy picks
- bad settings are refused
- an unconfigured deploy opens no store
- a preview's scores, answers, crews and suggestions never appear in production, and the reverse

## Remaining limits

- If Netlify ever stopped sending the deploy context, production would fail closed too (503) instead of using the wrong data. That's an outage, not a leak, and the `/api/health` check after the merge would show it straight away.
- The local test servers in the build scratchpad already use in-memory data and aren't affected.
