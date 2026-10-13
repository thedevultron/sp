// Smoke test for the chat proxy. Safe to run anywhere: uses a fake key,
// so upstream calls fail fast and only the 502/429/validation paths run.
// Asserts the key and model names never leak into responses.
// Usage: node scripts/chat-smoke.mjs
import handler from '../api/chat.ts';

const FAKE_KEY = 'smoke-test-key-DO-NOT-USE';
process.env.GEMINI_API_KEY = FAKE_KEY;

function fakeReq(method, body, ip = '9.9.9.9') {
  return {
    method,
    headers: { 'x-forwarded-for': ip },
    body,
    socket: { remoteAddress: ip },
  };
}
function fakeRes() {
  const state = { status: 0, headers: {}, body: null };
  return {
    state,
    status(code) {
      state.status = code;
      return this;
    },
    json(data) {
      state.body = data;
    },
    setHeader(k, v) {
      state.headers[k] = v;
    },
  };
}
const text = (res) => JSON.stringify(res.state.body || '');
function assert(cond, msg) {
  if (!cond) {
    console.error(`[smoke] FAIL: ${msg}`);
    process.exitCode = 1;
  } else {
    console.log(`[smoke] ok: ${msg}`);
  }
}
function assertNoLeak(res, msg) {
  const t = text(res);
  assert(!t.includes(FAKE_KEY), `${msg} (no key leak)`);
  assert(!/gemini-|gemma-/i.test(t), `${msg} (no model names leak)`);
}

// 1. Wrong method.
{
  const res = fakeRes();
  await handler(fakeReq('GET'), res);
  assert(res.state.status === 405, 'GET -> 405');
}
// 2. Missing key.
{
  delete process.env.GEMINI_API_KEY;
  const res = fakeRes();
  await handler(fakeReq('POST', { messages: [{ role: 'user', content: 'hi' }] }), res);
  assert(res.state.status === 503, 'no env key -> 503');
  process.env.GEMINI_API_KEY = FAKE_KEY;
}
// 3. Bad bodies.
for (const [label, body] of [
  ['empty body', {}],
  ['empty messages', { messages: [] }],
  ['assistant last', { messages: [{ role: 'assistant', content: 'hi' }] }],
]) {
  const res = fakeRes();
  await handler(fakeReq('POST', body), res);
  assert(res.state.status === 400, `${label} -> 400`);
}
// 4. Valid shape with fake key -> upstream rejects -> generic 502, no leaks,
//    rate-limit headers present.
{
  const res = fakeRes();
  await handler(
    fakeReq('POST', { messages: [{ role: 'user', content: 'How do I install Voxula?' }] }, '9.9.9.10'),
    res
  );
  assert(res.state.status === 502, 'fake key -> 502');
  assert(res.state.headers['X-RateLimit-Limit'] === 20, 'rate-limit headers present');
  assertNoLeak(res, '502 response');
}
// 5. Rate limit: 21 rapid valid requests from one IP -> last is 429.
{
  let last;
  for (let i = 0; i < 21; i++) {
    const res = fakeRes();
    await handler(
      fakeReq('POST', { messages: [{ role: 'user', content: `rate test ${i}` }] }, '9.9.9.11'),
      res
    );
    last = res;
  }
  assert(last.state.status === 429, '21st rapid request -> 429');
  assert(typeof last.state.headers['Retry-After'] === 'number', 'Retry-After present');
  assertNoLeak(last, '429 response');
}
console.log(process.exitCode ? '[smoke] FAILED' : '[smoke] ALL PASS');
