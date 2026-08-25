import { writeFileSync } from "node:fs";

const appUrl = "http://127.0.0.1:8504";
const debugPort = process.env.RAG_DEBUG_PORT ?? "9222";
const assetsDir = new URL("./assets/", import.meta.url);
const pages = await fetch(`http://127.0.0.1:${debugPort}/json`).then((response) => response.json());
const page = pages.find((item) => item.url.startsWith(appUrl));

if (!page) {
  throw new Error("The RAG demo page is not available on the Chrome debugging port.");
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
    callback(message.result);
  }
});

function command(method, params = {}) {
  const id = ++sequence;
  socket.send(JSON.stringify({ id, method, params }));
  return new Promise((resolve) => callbacks.set(id, resolve));
}

await command("Runtime.evaluate", {
  expression: `(() => {
    const target = [...document.querySelectorAll('*')].find((item) => item.textContent?.trim() === '引用来源');
    if (target) target.scrollIntoView({ block: 'start' });
  })()`,
});

await new Promise((resolve) => setTimeout(resolve, 700));
const screenshot = await command("Page.captureScreenshot", { format: "png" });
writeFileSync(new URL("rag-llm-sources.png", assetsDir), Buffer.from(screenshot.data, "base64"));
writeFileSync(new URL("rag-demo-frame-2.png", assetsDir), Buffer.from(screenshot.data, "base64"));
socket.close();
console.log("Captured assets/rag-llm-sources.png");
