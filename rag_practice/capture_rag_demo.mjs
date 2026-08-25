import { mkdirSync, writeFileSync } from "node:fs";

const question = "怎样把项目上线？";
const appUrl = process.env.RAG_DEMO_URL ?? "http://127.0.0.1:8503";
const pageUrl = process.env.RAG_DEMO_PAGE_URL ?? appUrl;
const debugPort = process.env.RAG_DEBUG_PORT ?? "9222";
const assetsDir = new URL("./assets/", import.meta.url);
mkdirSync(assetsDir, { recursive: true });

const pages = await fetch(`http://127.0.0.1:${debugPort}/json`).then((response) => response.json());
const page = pages.find(
  (item) => item.url.startsWith(appUrl) || item.url.startsWith(pageUrl),
);

if (!page) {
  throw new Error("RAG Streamlit page is not available on the Chrome debugging port.");
}

const socket = new WebSocket(page.webSocketDebuggerUrl);
const callbacks = new Map();
let sequence = 0;

await new Promise((resolve, reject) => {
  socket.addEventListener("open", resolve, { once: true });
  socket.addEventListener("error", reject, { once: true });
});

socket.addEventListener("message", (event) => {
  const message = JSON.parse(event.data);
  const callback = callbacks.get(message.id);
  if (callback) {
    callbacks.delete(message.id);
    callback(message);
  }
});

function command(method, params = {}) {
  const id = ++sequence;
  socket.send(JSON.stringify({ id, method, params }));
  return new Promise((resolve, reject) => {
    callbacks.set(id, (message) => {
      if (message.error) {
        reject(new Error(message.error.message));
      } else {
        resolve(message.result);
      }
    });
  });
}

async function evaluate(expression) {
  const result = await command("Runtime.evaluate", {
    expression,
    awaitPromise: true,
    returnByValue: true,
  });
  return result.result.value;
}

async function sleep(milliseconds) {
  await new Promise((resolve) => setTimeout(resolve, milliseconds));
}

await command("Emulation.setDeviceMetricsOverride", {
  width: 1440,
  height: 1100,
  deviceScaleFactor: 1,
  mobile: false,
});

if (page.url.startsWith(appUrl)) {
  await command("Page.reload", { ignoreCache: true });
} else {
  await command("Page.navigate", { url: appUrl });
}

for (let attempt = 0; attempt < 30; attempt += 1) {
  const ready = await evaluate("Boolean(document.querySelector('textarea'))");
  if (ready) break;
  await sleep(500);
}

const entryFrame = await command("Page.captureScreenshot", { format: "png" });
writeFileSync(new URL("rag-demo-frame-1.png", assetsDir), Buffer.from(entryFrame.data, "base64"));

const focused = await evaluate(`(() => {
  const textarea = document.querySelector('textarea');
  if (!textarea) return false;
  textarea.focus();
  return document.activeElement === textarea;
})()`);

if (!focused) {
  throw new Error("Question input was not found.");
}

const entered = await evaluate(`document.execCommand('insertText', false, ${JSON.stringify(question)})`);
if (!entered || (await evaluate("document.querySelector('textarea').value")) !== question) {
  throw new Error("Question input was not applied to the Streamlit control.");
}
await sleep(500);
const clicked = await evaluate(`(() => {
  const button = [...document.querySelectorAll('button')].find((item) => item.innerText.includes('检索并生成回答'));
  if (!button) return false;
  button.click();
  return true;
})()`);

if (!clicked) {
  throw new Error("Submit button was not found.");
}

for (let attempt = 0; attempt < 24; attempt += 1) {
  const completed = await evaluate(
    "document.body.innerText.includes('LLM | 基于检索证据生成') && !document.body.innerText.includes('正在检索资料')",
  );
  if (completed) break;
  await sleep(500);
}

const pageText = await evaluate("document.body.innerText");
if (!pageText.includes("LLM | 基于检索证据生成")) {
  throw new Error(`Model-generated response did not render in Streamlit. Current page: ${pageText.slice(-500)}`);
}

const screenshot = await command("Page.captureScreenshot", {
  format: "png",
  captureBeyondViewport: true,
});
writeFileSync(new URL("rag-llm-demo.png", assetsDir), Buffer.from(screenshot.data, "base64"));

const answerFrame = await command("Page.captureScreenshot", { format: "png" });
writeFileSync(new URL("rag-demo-frame-2.png", assetsDir), Buffer.from(answerFrame.data, "base64"));

await evaluate(`(() => {
  const candidates = [
    document.scrollingElement,
    document.querySelector('[data-testid="stAppViewContainer"]'),
    document.querySelector('section.main'),
  ].filter(Boolean);
  for (const candidate of candidates) candidate.scrollTop = candidate.scrollHeight;
  window.scrollTo(0, document.documentElement.scrollHeight);
})()`);
await sleep(700);
const sourcesFrame = await command("Page.captureScreenshot", { format: "png" });
writeFileSync(new URL("rag-llm-sources.png", assetsDir), Buffer.from(sourcesFrame.data, "base64"));

writeFileSync(
  new URL("rag-llm-demo-summary.json", assetsDir),
  JSON.stringify(
    {
      captured_at: new Date().toISOString(),
      question,
      answer_mode: pageText.includes("LLM | 基于检索证据生成") ? "llm" : "unknown",
      source_section_present: pageText.includes("引用来源"),
    },
    null,
    2,
  ),
);

socket.close();
console.log("Captured assets/rag-llm-demo.png");
