// Which data store the API uses. Real players only ever live in the production store.
//
//   Production deploy (offcampusontario.ca)    -> store "offcampus", exactly as before. Needs no setting.
//   Anything else (deploy previews, branch deploys, local `netlify dev`, unknown)
//                                               -> the store named in the OC_TEST_STORE setting.
//                                                  It must start with "offcampus-test".
//                                                  If it's missing or wrong, the API refuses every request (503).
//                                                  It never falls back to the production store.
//
// To wipe test data: change OC_TEST_STORE to a new name (offcampus-test-2, -3, ...) and redeploy the preview.
// Nothing is deleted, the old test store is simply no longer used. See docs/TEST_DATA.md.

// ---------- settings ----------
export const PRODUCTION_STORE = 'offcampus';
export const TEST_STORE_SETTING = 'OC_TEST_STORE';
export const TEST_STORE_RULE = /^offcampus-test(-[a-z0-9]{1,20})?$/;   // offcampus-test, offcampus-test-2, offcampus-test-nov ...

// deployContext: Netlify's context.deploy.context ("production", "deploy-preview", "branch-deploy", "dev").
// env: the environment settings (process.env).
export function chooseStore(deployContext, env){
  if (deployContext === 'production') return { ok:true, data:'production', name:PRODUCTION_STORE };
  const name = String((env && env[TEST_STORE_SETTING]) || '').trim();
  if (!name) return { ok:false, data:'none', reason:`${TEST_STORE_SETTING} is not set for this ${deployContext || 'unknown'} deploy` };
  if (name === PRODUCTION_STORE || !TEST_STORE_RULE.test(name)) return { ok:false, data:'none', reason:`${TEST_STORE_SETTING} must start with "offcampus-test"` };
  return { ok:true, data:'test', name };
}

// Wraps the API. getStoreFn is Netlify's getStore (or a stand-in in tests), handle is lib/crews.mjs handle.
export function makeApi({ getStoreFn, handle, env }){
  return async (req, context) => {
    const deployContext = context && context.deploy ? context.deploy.context : undefined;
    const pick = chooseStore(deployContext, env);
    const isHealth = new URL(req.url).pathname === '/api/health';
    if (!pick.ok) {
      // Fail closed: no store is opened at all.
      return new Response(JSON.stringify({ ok:false, error:'test data store not configured', reason:pick.reason, data:'none', context:deployContext || 'unknown' }),
        { status:503, headers:{ 'content-type':'application/json', 'cache-control':'no-store' } });
    }
    const res = await handle(req, getStoreFn({ name:pick.name, consistency:'strong' }));
    if (!isHealth || res.status !== 200) return res;
    // /api/health also says which data this deploy uses, so isolation can be checked from a browser.
    const body = await res.json();
    return new Response(JSON.stringify({ ...body, data:pick.data, store:pick.name, context:deployContext }),
      { status:200, headers:{ 'content-type':'application/json', 'cache-control':'no-store' } });
  };
}
