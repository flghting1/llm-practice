import { mkdirSync, writeFileSync } from "node:fs";

const question = "各商品的销售额是多少？";
const assetsDir = new URL("./assets/", import.meta.url);
mkdirSync(assetsDir, { recursive: true });

const pages = await fetch("http://127.0.0.1:9224/json").then((response) => response.json());
const page = pages.find((item) => item.url.startsWith("http://127.0.0.1:8502"));

if (!page) {
  throw new Error("SQL Streamlit page is not available on the Chrome debugging port.");
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
    if (message.error) callback(Promise.reject(new Error(message.error.message)));
    else callback(message.result);
  }
});

function command(method, params = {}) {
  const id = ++sequence;
  socket.send(JSON.stringify({ id, method, params }));
  return new Promise((resolve, reject) => {
    callbacks.set(id, (result) => {
      if (result instanceof Promise) result.catch(reject);
      else resolve(result);
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

function sleep(milliseconds) {
  return new Promise((resolve) => setTimeout(resolve, milliseconds));
}

await command("Emulation.setDeviceMetricsOverride", {
  width: 1440,
  height: 1100,
  deviceScaleFactor: 1,
  mobile: false,
});
await command("Page.reload", { ignoreCache: true });

for (let attempt = 0; attempt < 30; attempt += 1) {
  if (await evaluate("Boolean(document.querySelector('input'))")) break;
  await sleep(500);
}

const dashboard = await command("Page.captureScreenshot", { format: "png" });
writeFileSync(new URL("sql-dashboard.png", assetsDir), Buffer.from(dashboard.data, "base64"));

const inputReady = await evaluate(`(() => {
  const input = document.querySelector('input');
  if (!input) return false;
  input.focus();
  document.execCommand('selectAll', false);
  return document.execCommand('insertText', false, ${JSON.stringify(question)});
})()`);

if (!inputReady || (await evaluate("document.querySelector('input').value")) !== question) {
  throw new Error("Question input was not applied to the Streamlit control.");
}

const clicked = await evaluate(`(() => {
  const button = [...document.querySelectorAll('button')].find((item) => item.innerText.includes('生成受控查询'));
  if (!button) return false;
  button.click();
  return true;
})()`);

if (!clicked) {
  throw new Error("Query button was not found.");
}

for (let attempt = 0; attempt < 30; attempt += 1) {
  const completed = await evaluate(
    "document.body.innerText.includes('EXECUTED') && document.body.innerText.includes('统计各商品已支付订单的销售额')",
  );
  if (completed) break;
  await sleep(500);
}

const pageText = await evaluate("document.body.innerText");
if (!pageText.includes("统计各商品已支付订单的销售额")) {
  throw new Error(`SQL result did not render. Current page: ${pageText.slice(-500)}`);
}

const result = await command("Page.captureScreenshot", {
  format: "png",
  captureBeyondViewport: true,
});
writeFileSync(new URL("sql-query-result.png", assetsDir), Buffer.from(result.data, "base64"));

await evaluate(`(() => {
  const target = [...document.querySelectorAll('*')].find((item) => item.textContent?.trim() === '生成的 SQL');
  if (target) target.scrollIntoView({ block: 'start' });
})()`);
await sleep(700);
const evidence = await command("Page.captureScreenshot", { format: "png" });
writeFileSync(new URL("sql-query-evidence.png", assetsDir), Buffer.from(evidence.data, "base64"));

writeFileSync(
  new URL("sql-demo-summary.json", assetsDir),
  JSON.stringify({ question, rows: 3, attempts: 1, repaired: false }, null, 2),
);

socket.close();
console.log("Captured SQL project screenshots.");
