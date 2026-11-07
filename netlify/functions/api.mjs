// Netlify Function: everything under /api/ goes to lib/crews.mjs. Data lives in Netlify Blobs.
// Production uses the store "offcampus". Previews, branch deploys and local dev use a separate test store
// (the OC_TEST_STORE setting) and refuse to run without it. See lib/datastore.mjs and docs/TEST_DATA.md.
import { getStore } from '@netlify/blobs';
import { handle } from '../../lib/crews.mjs';
import { makeApi } from '../../lib/datastore.mjs';

export default makeApi({ getStoreFn: getStore, handle, env: process.env });

export const config = { path: '/api/*' };
